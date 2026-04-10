import time
import logging
from typing import Any
from pydantic import BaseModel, Field
from langchain_core.messages import (
    SystemMessage,
    HumanMessage,
)
from langchain_core.tools import StructuredTool

from config import settings
from core.agent_executor import AgentExecutor
from core.knowledge_base import knowledge_base, KnowledgeBaseError
from core.llm_registry import LLMRegistry
from core.tools.factory import build_registry_for_task
from core.prompt_builder import prompt_builder
from core.prompt_version_registry import PromptVersionNotFoundError
from models import TaskMessage, AIReportPayload

logger = logging.getLogger(__name__)

MAX_ITERATIONS = 20


# ---------------------------------------------------------------------------
# submit_report tool
# ---------------------------------------------------------------------------

class _IssueArg(BaseModel):
    field: str = Field(description="The field or area where the issue was found")
    detail: str = Field(description="Human-readable description of the problem")
    severity: str = Field(description='"critical", "warning", or "info"')


class _SubmitReportArgs(BaseModel):
    decision: str = Field(description='"ACCEPT" or "REJECT"')
    confidence_score: float = Field(description="Your confidence in the decision, from 0.0 (uncertain) to 1.0 (certain)")
    extracted_data: dict[str, Any] = Field(
        description="Key-value pairs extracted from the document or form, e.g. {'first_name': 'Ion', 'idno': '1234567890123'}"
    )
    issues_found: list[_IssueArg] = Field(
        description="Validation failures found. Empty list if decision is ACCEPT."
    )
    recommendations: str | None = Field(
        default=None,
        description="Optional suggestion for the applicant on how to correct the application."
    )


def _make_submit_report_tool() -> StructuredTool:
    async def _noop(**_: object) -> str:
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
    from models import ValidationIssue
    return AIReportPayload(
        application_id=task.application_id,
        decision=args.get("decision", "REJECT"),
        confidence_score=args.get("confidence_score", 0.5),
        extracted_data=args.get("extracted_data", {}),
        issues_found=[ValidationIssue(**i) if isinstance(i, dict) else i for i in args.get("issues_found", [])],
        recommendations=args.get("recommendations") or None,
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
    from models import ValidationIssue
    return AIReportPayload(
        application_id=task.application_id,
        decision="ERROR",
        confidence_score=0.0,
        extracted_data={},
        issues_found=[ValidationIssue(field=error_type, detail=detail, severity="critical")],
        recommendations=None,
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
    tool_registry = build_registry_for_task(task)
    submit_tool = _make_submit_report_tool()
    all_tools = tool_registry.as_langchain_tools() + [submit_tool]
    model = LLMRegistry.get(model_name).bind_tools(all_tools)

    # 4. Run agent
    executor = AgentExecutor(model, tool_registry, max_iterations=MAX_ITERATIONS)
    try:
        submit_args, _trace = await executor.run(messages)
    except Exception as exc:
        logger.exception("Agent error: %s", exc)
        return _error_report(
            task,
            "llm_error",
            f"Unexpected error during processing: {exc}",
            version,
            model_name,
            int(time.monotonic() - start),
        )

    elapsed = int(time.monotonic() - start)

    if submit_args is None:
        logger.warning(
            "Max iterations reached without submit_report: application=%s",
            task.application_id,
        )
        return _error_report(
            task,
            "max_iterations_reached",
            "Agent reached the iteration limit without submitting a report. Please retry.",
            version,
            model_name,
            elapsed,
        )

    logger.info(
        "Task complete: application=%s decision=%s time=%ds",
        task.application_id,
        submit_args.get("decision"),
        elapsed,
    )
    return _build_report(task, submit_args, model_name, version, elapsed)
