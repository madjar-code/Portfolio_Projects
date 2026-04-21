import asyncio
import hashlib
import hmac
import json
import logging
import time

import httpx

from models import AIReportPayload
from config import settings

logger = logging.getLogger(__name__)

MAX_ATTEMPTS = 3
BACKOFF_SECONDS = [1, 4, 16]  # between attempt N and N+1

_RETRYABLE_STATUSES = {408, 425, 429, 500, 502, 503, 504}


def _sign(body: bytes, secret: str) -> tuple[str, str]:
    """Return (timestamp, hex_signature) for the given body."""
    ts = str(int(time.time()))
    message = f"{ts}.".encode() + body
    sig = hmac.new(secret.encode(), message, hashlib.sha256).hexdigest()
    return ts, sig


async def send_callback(report: AIReportPayload) -> None:
    """
    Deliver AIReport to Backend with bounded retry.

    Retries on network errors and 5xx. Does NOT retry on 4xx — those indicate
    a bug (bad signature, malformed body, 404) that retries will only hide.
    On final exhaustion, raises — caller (consumer) will trigger redelivery /
    DLQ through the transport layer.
    """
    body = json.dumps(report.model_dump()).encode()
    last_error: Exception | None = None

    for attempt in range(1, MAX_ATTEMPTS + 1):
        ts, sig = _sign(body, settings.agent_api_key)
        try:
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
                logger.info(
                    "callback=ok application=%s attempt=%d",
                    report.application_id, attempt,
                )
                return
            if response.status_code in _RETRYABLE_STATUSES:
                logger.warning(
                    "callback=retryable application=%s attempt=%d/%d status=%d",
                    report.application_id, attempt, MAX_ATTEMPTS, response.status_code,
                )
                last_error = httpx.HTTPStatusError(
                    f"status {response.status_code}",
                    request=response.request, response=response,
                )
            else:
                # 4xx / other — not retryable, surface immediately.
                logger.error(
                    "callback=terminal application=%s status=%d body=%s",
                    report.application_id, response.status_code, response.text[:500],
                )
                response.raise_for_status()
                return
        except (httpx.TimeoutException, httpx.ConnectError, httpx.RemoteProtocolError) as exc:
            logger.warning(
                "callback=network_error application=%s attempt=%d/%d error=%s",
                report.application_id, attempt, MAX_ATTEMPTS, exc,
            )
            last_error = exc

        # Sleep before next attempt (if any)
        if attempt < MAX_ATTEMPTS:
            await asyncio.sleep(BACKOFF_SECONDS[attempt - 1])

    logger.error(
        "callback=exhausted application=%s attempts=%d last_error=%s",
        report.application_id, MAX_ATTEMPTS, last_error,
    )
    raise RuntimeError(f"Callback exhausted after {MAX_ATTEMPTS} attempts: {last_error}")
