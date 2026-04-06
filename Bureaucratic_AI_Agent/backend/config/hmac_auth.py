"""
HMAC-SHA256 request signing utilities for agent → backend callback.

Signature covers: timestamp + "." + raw request body.
Requests older than MAX_AGE_SECONDS are rejected (replay protection).
"""
import hashlib
import hmac
import time

from django.conf import settings

MAX_AGE_SECONDS = 60


def verify_hmac_signature(body: bytes, timestamp_header: str, signature_header: str) -> bool:
    """
    Returns True if the request signature is valid and fresh.
    Always returns False on any error so callers never crash.
    """
    try:
        ts = int(timestamp_header)
    except (TypeError, ValueError):
        return False

    if abs(time.time() - ts) > MAX_AGE_SECONDS:
        return False

    secret = settings.AGENT_API_KEY.encode()
    message = f"{ts}.".encode() + body
    expected = hmac.new(secret, message, hashlib.sha256).hexdigest()

    return hmac.compare_digest(expected, signature_header)
