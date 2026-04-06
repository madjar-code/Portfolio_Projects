import hashlib
import hmac
import json
import logging
import time

import httpx
from models import AIReportPayload
from config import settings

logger = logging.getLogger(__name__)


def _sign(body: bytes, secret: str) -> tuple[str, str]:
    """Return (timestamp, hex_signature) for the given body."""
    ts = str(int(time.time()))
    message = f"{ts}.".encode() + body
    sig = hmac.new(secret.encode(), message, hashlib.sha256).hexdigest()
    return ts, sig


async def send_callback(report: AIReportPayload) -> None:
    """Send AIReport to Backend API callback endpoint."""
    body = json.dumps(report.model_dump()).encode()
    ts, sig = _sign(body, settings.agent_api_key)

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            settings.backend_callback_url,
            content=body,
            headers={
                "Content-Type": "application/json",
                "X-Timestamp": ts,
                "X-Signature": sig,
            },
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
