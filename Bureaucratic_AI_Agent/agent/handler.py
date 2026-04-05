import asyncio
import logging
from models import TaskMessage, AIReportPayload

logger = logging.getLogger(__name__)

_STUB_PROCESSING_SECONDS = 2


async def handle_task(task: TaskMessage) -> AIReportPayload:
    """
    Stub handler — simulates processing delay and returns a fake ACCEPT report.
    Replace this with actual AI agent logic in the next iteration.
    """
    logger.info(
        "Handling task for application %s (procedure: %s)",
        task.application_id,
        task.procedure,
    )

    await asyncio.sleep(_STUB_PROCESSING_SECONDS)

    return AIReportPayload(
        application_id=task.application_id,
        decision="ACCEPT",
        validation_result={
            "is_complete": True,
            "checks_performed": ["document_present", "form_data_valid"],
            "passed_checks": ["document_present", "form_data_valid"],
            "failed_checks": [],
        },
        extracted_data={},
        issues_found=[],
        recommendations="All checks passed. Application is complete.",
        processing_time_seconds=_STUB_PROCESSING_SECONDS,
        ai_model_used="stub",
    )
