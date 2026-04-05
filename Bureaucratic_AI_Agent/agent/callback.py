import logging
import httpx
from models import AIReportPayload
from config import settings

logger = logging.getLogger(__name__)


async def send_callback(report: AIReportPayload) -> None:
    """Send AIReport to Backend API callback endpoint."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            settings.backend_callback_url,
            json=report.model_dump(),
            headers={"X-API-Key": settings.agent_api_key},
        )

    if response.status_code == 200:
        logger.info("Callback sent successfully for application %s", report.application_id)
    else:
        logger.error(
            "Callback failed for application %s: %s %s",
            report.application_id,
            response.status_code,
            response.text,
        )
        response.raise_for_status()
