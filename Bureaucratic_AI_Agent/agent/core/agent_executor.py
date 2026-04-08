import logging
from langchain_core.messages import HumanMessage, ToolMessage

from core.tools import ToolRegistry

logger = logging.getLogger(__name__)

_REFLECTION_PROMPT = (
    "You have received the tool results above.\n"
    "Reflect: what have you established so far about this application?\n"
    "Consider both the submitted document and the form data provided by the applicant.\n"
    "If you have enough information to decide (including REJECT) — call submit_report now.\n"
    "If not, specify exactly what is still missing and call the appropriate tool."
)


class AgentExecutor:
    """
    Implements the ReAct loop: Action → Observation → Reflection.

    Each iteration:
      1. model.ainvoke()     — Planning + Action (tool calls)
      2. execute tools       — Observation
      3. inject reflection   — HumanMessage prompting self-evaluation
      4. model.ainvoke()     — Reflection (text or submit_report)

    submit_report can be called at step 1 or step 4.
    """

    def __init__(
        self,
        model,
        tool_registry: ToolRegistry,
        max_iterations: int = 10,
    ) -> None:
        self._model = model
        self._tool_registry = tool_registry
        self._max_iterations = max_iterations

    async def run(self, messages: list) -> dict | None:
        """
        Runs the loop. Returns submit_report args dict on success,
        or None if max_iterations reached without submit_report.
        """
        for iteration in range(self._max_iterations):
            logger.info("--- Iteration %d/%d ---", iteration + 1, self._max_iterations)

            # Step 1: Action
            response = await self._model.ainvoke(messages)
            messages.append(response)

            if response.content:
                logger.info("Agent: %s", response.content[:300])

            # submit_report in action step
            submit_args = self._find_submit(response)
            if submit_args is not None:
                logger.info("Agent → submit_report(%s)", submit_args.get("decision"))
                return submit_args

            # Step 2: Observation — execute tool calls
            tool_messages = []
            for tc in (response.tool_calls or []):
                logger.info("Agent → %s(%s)", tc["name"], tc["args"])
                result = await self._tool_registry.execute(tc["name"], tc["args"])
                logger.info("Result: %.200s", result)
                tool_messages.append(
                    ToolMessage(content=result, tool_call_id=tc["id"])
                )

            messages.extend(tool_messages)

            # Step 3: Reflection — always inject after observations
            messages.append(HumanMessage(_REFLECTION_PROMPT))

            # Step 4: Reflection response
            reflection = await self._model.ainvoke(messages)
            messages.append(reflection)

            if reflection.content:
                logger.info("Reflection: %s", reflection.content[:300])

            # submit_report in reflection step
            submit_args = self._find_submit(reflection)
            if submit_args is not None:
                logger.info(
                    "Agent → submit_report(%s) [via reflection]",
                    submit_args.get("decision"),
                )
                return submit_args

            # If reflection called any regular tools, execute them.
            # Every AIMessage with tool_calls MUST be followed by ToolMessages —
            # otherwise OpenAI returns 400 on the next ainvoke call.
            reflection_tool_messages = []
            for tc in (reflection.tool_calls or []):
                if tc["name"] == "submit_report":
                    continue
                logger.info("Reflection → %s(%s)", tc["name"], tc["args"])
                result = await self._tool_registry.execute(tc["name"], tc["args"])
                logger.info("Result: %.200s", result)
                reflection_tool_messages.append(
                    ToolMessage(content=result, tool_call_id=tc["id"])
                )
            messages.extend(reflection_tool_messages)

        logger.warning("Max iterations (%d) reached without submit_report", self._max_iterations)
        return None

    @staticmethod
    def _find_submit(response) -> dict | None:
        for tc in (response.tool_calls or []):
            if tc["name"] == "submit_report":
                return tc["args"]
        return None