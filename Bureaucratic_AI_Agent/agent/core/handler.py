import asyncio
import logging

from core.knowledge_base import knowledge_base, KnowledgeBaseError
from models import TaskMessage, AIReportPayload

logger = logging.getLogger(__name__)

_STUB_PROCESSING_SECONDS = 2


async def handle_task(task: TaskMessage) -> AIReportPayload:
    logger.info(
        "Handling task: application=%s procedure=%s",
        task.application_id,
        task.procedure,
    )

    try:
        instructions = knowledge_base.load(task.procedure)
        logger.info("Loaded procedure instructions (%d chars)", len(instructions))
    except KnowledgeBaseError as exc:
        logger.error("Knowledge base error: %s", exc)
        return AIReportPayload(
            application_id=task.application_id,
            decision="REJECT",
            validation_result={"error": str(exc)},
            extracted_data={},
            issues_found=[{"type": "configuration_error", "detail": str(exc)}],
            recommendations="Procedure instructions not found. Contact system administrator.",
            processing_time_seconds=0,
            ai_model_used="stub",
        )

    # TODO: pass `instructions` to prompt builder + LLM (next spec)
    await asyncio.sleep(_STUB_PROCESSING_SECONDS)

    return AIReportPayload(
        application_id=task.application_id,
        decision="ACCEPT",
        validation_result={"is_complete": True, "procedure": task.procedure},
        extracted_data={},
        issues_found=[],
        recommendations="Stub: procedure instructions loaded successfully.",
        processing_time_seconds=_STUB_PROCESSING_SECONDS,
        ai_model_used="stub",
    )
