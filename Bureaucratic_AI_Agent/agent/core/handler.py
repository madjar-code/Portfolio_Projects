import time
import logging
from pydantic import BaseModel
from langchain_core.messages import (
    SystemMessage,
    HumanMessage,
    ToolMessage,
)
from langchain_core.tools import StructuredTool

from config import settings
from core.knowledge_base import knowledge_base, KnowledgeBaseError
from core.llm_registry import LLMRegistry
from core.tools.stubs import build_default_registry
from core.prompt_builder import prompt_builder
from core.prompt_version_registry import PromptVersionNotFoundError
from models import TaskMessage, AIReportPayload

logger = logging.getLogger(__name__)

MAX_ITERATIONS = 10


# ---------------------------------------------------------------------------
# submit_report tool
# ---------------------------------------------------------------------------

class _SubmitReportArgs(BaseModel):
    decision: str
    validation_result: dict
    extracted_data: dict
    issues_found: list[dict]
    recommendations: str


def _make_submit_report_tool() -> StructuredTool:
    async def _noop(**kwargs) -> str:
        return "submitted"

    return StructuredTool.from_function(
        coroutine=_noop,
        name="submit_report",
        description=(
            "Submit the final validation report. Call this once you have completed "
            "all required checks. This terminates the task."
        ),
        args_schema=_SubmitReportArgs,
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _to_lc_messages(raw: list[dict]) -> list:
    mapping = {"system": SystemMessage, "user": HumanMessage}
    return [mapping[m["role"]](content=m["content"]) for m in raw]


def _build_report(
    task: TaskMessage,
    args: dict,
    model_name: str,
    version: str,
    elapsed: int,
) -> AIReportPayload:
    return AIReportPayload(
        application_id=task.application_id,
        decision=args.get("decision", "REJECT"),
        validation_result=args.get("validation_result", {}),
        extracted_data=args.get("extracted_data", {}),
        issues_found=args.get("issues_found", []),
        recommendations=args.get("recommendations", "No recommendations provided."),
        processing_time_seconds=elapsed,
        ai_model_used=model_name,
        prompt_version=version,
    )

def _error_report(
    task: TaskMessage,
    error_type: str,
    detail: str,
    version: str,
    model_name: str,
    elapsed: int,
) -> AIReportPayload:
    return AIReportPayload(
        application_id=task.application_id,
        decision="REJECT",
        validation_result={"error": error_type},
        extracted_data={},
        issues_found=[{"type": error_type, "detail": detail, "severity": "critical"}],
        recommendations=detail,
        processing_time_seconds=elapsed,
        ai_model_used=model_name,
        prompt_version=version,
    )


# ---------------------------------------------------------------------------
# Main handler
# ---------------------------------------------------------------------------

async def handle_task(task: TaskMessage, prompt_version: str | None = None) -> AIReportPayload:
    version = prompt_version or settings.prompt_version
    model_name = settings.default_model

    logger.info(
        "Handling task: application=%s procedure=%s prompt_version=%s model=%s",
        task.application_id,
        task.procedure,
        version,
        model_name,
    )

    start = time.monotonic()

    # 1. Load procedure instructions
    try:
        instructions = knowledge_base.load(task.procedure)
        logger.info("Loaded procedure instructions (%d chars)", len(instructions))
    except KnowledgeBaseError as exc:
        logger.error("Knowledge base error: %s", exc)
        return _error_report(
            task,
            "configuration_error",
            "Procedure instructions not found. Contact system administrator.",
            version,
            model_name,
            0,
        )

    # 2. Build messages
    try:
        raw_messages = prompt_builder.build(task, instructions, version)
    except PromptVersionNotFoundError as exc:
        logger.error("Prompt version error: %s", exc)
        return _error_report(
            task, "configuration_error", str(exc), version, model_name, 0
        )

    messages = _to_lc_messages(raw_messages)

    # 3. Build tool-bound model
    tool_registry = build_default_registry()
    submit_tool = _make_submit_report_tool()
    all_tools = tool_registry.as_langchain_tools() + [submit_tool]
    model = LLMRegistry.get(model_name).bind_tools(all_tools)

    # 4. ReAct loop
    try:
        for iteration in range(MAX_ITERATIONS):
            logger.debug("Iteration %d/%d", iteration, MAX_ITERATIONS)

            response = await model.ainvoke(messages)
            messages.append(response)

            submit_args = None
            tool_messages = []

            for tc in (response.tool_calls or []):
                if tc["name"] == "submit_report":
                    submit_args = tc["args"]
                else:
                    result = await tool_registry.execute(tc["name"], tc["args"])
                    logger.debug("Tool %s → %.80s", tc["name"], result)
                    tool_messages.append(
                        ToolMessage(content=result, tool_call_id=tc["id"])
                    )

            messages.extend(tool_messages)

            if submit_args is not None:
                elapsed = int(time.monotonic() - start)
                logger.info(
                    "Task complete: application=%s decision=%s time=%ds",
                    task.application_id,
                    submit_args.get("decision"),
                    elapsed,
                )
                return _build_report(task, submit_args, model_name, version, elapsed)

    except Exception as exc:
        logger.exception("LLM error during loop: %s", exc)
        return _error_report(
            task,
            "llm_error",
            f"Unexpected error during processing: {exc}",
            version,
            model_name,
            int(time.monotonic() - start),
        )

    # Max iterations exceeded
    logger.warning(
        "Max iterations (%d) reached without submit_report: application=%s",
        MAX_ITERATIONS,
        task.application_id,
    )
    return _error_report(
        task,
        "max_iterations_reached",
        "Agent reached the iteration limit without submitting a report. Please retry.",
        version,
        model_name,
        int(time.monotonic() - start),
    )
