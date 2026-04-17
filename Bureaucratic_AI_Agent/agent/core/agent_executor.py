import logging
import time
from dataclasses import dataclass
from langchain_core.messages import HumanMessage, ToolMessage

from config import settings
from core.security import scan_for_injection, _INJECTION_REJECT
from core.tools import ToolRegistry

logger = logging.getLogger(__name__)

_REFLECTION_PROMPT = (
    "You have received the tool results above.\n"
    "Reflect: what have you established so far about this application?\n"
    "Consider both the submitted document and the form data provided by the applicant.\n"
    "If you have enough information to decide (including REJECT) — call submit_report now.\n"
    "If not, specify exactly what is still missing and call the appropriate tool."
)


@dataclass
class TraceEvent:
    iteration: int
    step: str
    tool_name: str | None = None
    tool_args: dict | None = None
    result: str | None = None


def _sandbox(text: str, tool_name: str) -> str:
    """Wrap untrusted tool output so the model treats it as applicant data."""
    return (
        f'<untrusted_document_content tool="{tool_name}">\n'
        f'{text}\n'
        f'</untrusted_document_content>'
    )


def _capture_sentry(message: str, level: str) -> None:
    """Send a Sentry message. No-op if Sentry is not initialised."""
    try:
        import sentry_sdk
        sentry_sdk.capture_message(message, level=level)
    except Exception:
        pass


class AgentExecutor:
    """
    Implements the ReAct loop: Action → Observation → Reflection.

    Each iteration:
      1. model.ainvoke()   — Planning + Action (tool calls)
      2. execute tools     — Observation
      3. inject prompt     — HumanMessage prompting self-evaluation
      4. model.ainvoke()   — Reflection (text or submit_report)

    submit_report can be called at step 1 or step 4.
    """

    def __init__(
        self,
        model,
        tool_registry: ToolRegistry,
        max_iterations: int = 10,
        trace=None,
        model_name: str = "unknown",
    ) -> None:
        self._model = model
        self._tool_registry = tool_registry
        self._max_iterations = max_iterations
        self._trace = trace  # duck-typed: _LangFuseTrace | _NoOpTrace | None
        self._model_name = model_name

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def run(self, messages: list) -> tuple[dict | None, list[TraceEvent], int]:
        """
        Run the ReAct loop.
        Returns (submit_args, events, iterations) on success, or
        (None, events, iterations) if max_iterations is reached.
        """
        events: list[TraceEvent] = []

        for iteration in range(self._max_iterations):
            logger.info("--- Iteration %d/%d ---", iteration + 1, self._max_iterations)

            # ── Step 1: Action ─────────────────────────────────────────
            response, latency_ms, t_start, t_end = await self._invoke(messages)
            messages.append(response)

            if response.content:
                logger.info("Agent: %s", response.content)

            self._record_generation(
                response,
                name="action",
                messages=messages,
                latency_ms=latency_ms,
                start_time=t_start,
                end_time=t_end
            )

            submit_args = self._find_submit(response)
            if submit_args is not None:
                logger.info("Agent → submit_report(%s)", submit_args.get("decision"))
                return submit_args, events, iteration + 1

            # ── Step 2: Observation ────────────────────────────────────
            tool_messages = []
            for tc in (response.tool_calls or []):
                msg, hard_stop = await self._execute_tool(tc, iteration, step="action", events=events)
                if hard_stop:
                    return _INJECTION_REJECT, events
                tool_messages.append(msg)
            messages.extend(tool_messages)

            # ── Step 3: Reflection prompt ──────────────────────────────
            messages.append(HumanMessage(_REFLECTION_PROMPT))

            # ── Step 4: Reflection ─────────────────────────────────────
            reflection, latency_ms, t_start, t_end = await self._invoke(messages)
            messages.append(reflection)

            if reflection.content:
                logger.info("Reflection: %s", reflection.content)
                events.append(TraceEvent(
                    iteration=iteration,
                    step="reflection",
                    result=reflection.content,
                ))

            self._record_generation(
                reflection,
                name="reflection",
                messages=messages,
                latency_ms=latency_ms,
                start_time=t_start,
                end_time=t_end
            )

            submit_args = self._find_submit(reflection)
            if submit_args is not None:
                logger.info("Agent → submit_report(%s) [via reflection]", submit_args.get("decision"))
                return submit_args, events, iteration + 1

            # Reflection may call tools — every AIMessage with tool_calls
            # must be followed by ToolMessages or the LLM API returns 400.
            reflection_tool_messages = []
            for tc in (reflection.tool_calls or []):
                if tc["name"] == "submit_report":
                    continue
                msg, hard_stop = await self._execute_tool(
                    tc, iteration, step="reflection_action", events=events,
                )
                if hard_stop:
                    return _INJECTION_REJECT, events
                reflection_tool_messages.append(msg)
            messages.extend(reflection_tool_messages)

        logger.warning("Max iterations (%d) reached without submit_report", self._max_iterations)
        return None, events, self._max_iterations

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    async def _invoke(self, messages: list) -> tuple:
        """Call the model and return (response, latency_ms, start_time, end_time)."""
        start_time = self._trace.now() if self._trace else None
        t0 = time.monotonic()
        response = await self._model.ainvoke(messages)
        latency_ms = int((time.monotonic() - t0) * 1000)
        end_time = self._trace.now() if self._trace else None
        return response, latency_ms, start_time, end_time

    def _record_generation(
        self,
        response,
        name: str,
        messages: list,
        latency_ms: int,
        start_time=None,
        end_time=None
    ) -> None:
        """Forward LLM call metadata to the observability trace."""
        if not self._trace:
            return
        usage = getattr(response, "usage_metadata", None) or {}
        self._trace.record_generation(
            name=name,
            model=self._model_name,
            input_messages=[str(m)[:300] for m in messages[-3:]],
            output=response.content or "",
            input_tokens=usage.get("input_tokens", 0),
            output_tokens=usage.get("output_tokens", 0),
            latency_ms=latency_ms,
            start_time=start_time,
            end_time=end_time,
        )

    async def _execute_tool(
        self,
        tc: dict,
        iteration: int,
        step: str,
        events: list[TraceEvent],
    ) -> tuple[ToolMessage, bool]:
        """
        Execute one tool call, run security checks, and return (ToolMessage, hard_stop).

        hard_stop=True means an injection hard-stop was triggered.
        The caller must return _INJECTION_REJECT immediately in that case.
        The returned ToolMessage is a placeholder and must not be used when hard_stop=True.
        """
        obs_step = "observation" if step == "action" else "reflection_observation"
        prefix = "Agent" if step == "action" else "Reflection"

        logger.info("%s → %s(%s)", prefix, tc["name"], tc["args"])
        events.append(TraceEvent(
            iteration=iteration, step=step,
            tool_name=tc["name"], tool_args=tc["args"],
        ))

        t_tool_start = self._trace.now() if self._trace else None
        result = await self._tool_registry.execute(tc["name"], tc["args"])
        t_tool_end = self._trace.now() if self._trace else None
        logger.info("Result: %.2000s", result)
        events.append(TraceEvent(
            iteration=iteration, step=obs_step,
            tool_name=tc["name"], tool_args=tc["args"], result=result,
        ))

        if self._trace:
            self._trace.record_tool(
                name=tc["name"],
                args=tc["args"],
                result=result,
                start_time=t_tool_start,
                end_time=t_tool_end
            )

        tool = self._tool_registry._tools.get(tc["name"])
        if tool and tool.untrusted:
            if settings.enable_injection_scanner:
                detected, result = scan_for_injection(result, source=tc["name"])
                if detected:
                    if settings.injection_scanner_hard_stop:
                        _capture_sentry(f"Injection hard-stop triggered: {tc['name']}", level="error")
                        logger.warning("Hard stop: returning _INJECTION_REJECT")
                        return ToolMessage(content="", tool_call_id=tc["id"]), True
                    _capture_sentry(f"Injection pattern detected in tool result: {tc['name']}", level="warning")
            result = _sandbox(result, tc["name"])

        return ToolMessage(content=result, tool_call_id=tc["id"]), False

    @staticmethod
    def _find_submit(response) -> dict | None:
        for tc in (response.tool_calls or []):
            if tc["name"] == "submit_report":
                return tc["args"]
        return None
