"""
Error taxonomy for the reliability layer.

Classification distinguishes transient errors (worth a retry / fallback) from
terminal errors (surface them; retrying will only hide a bug).
"""

import httpx


class LLMTransportError(Exception):
    """
    Wraps a transient error from an LLM provider.

    Transient = rate-limit, server error, connection error, timeout.
    The cure is to try a different model or, within the same model,
    to wait and retry (LangChain's internal retry already does the latter).
    """


class LLMTerminalError(Exception):
    """
    Wraps a non-retryable error from an LLM provider.

    Terminal = auth (401/403), bad request (400), schema violations.
    Surface these; they indicate a bug in configuration or payload.
    """


_TRANSIENT_STATUSES = {408, 425, 429, 500, 502, 503, 504}
_TERMINAL_STATUSES = {400, 401, 403, 404}


def _extract_status_code(exc: BaseException) -> int | None:
    """
    Best-effort status-code extraction across SDKs.

    httpx wraps HTTP errors in HTTPStatusError(response=...).
    openai and anthropic wrap them in their own APIStatusError subclasses
    that expose .status_code directly on the exception.
    """
    if isinstance(exc, httpx.HTTPStatusError):
        return exc.response.status_code
    status = getattr(exc, "status_code", None)
    if isinstance(status, int):
        return status
    return None


def classify_llm_error(exc: BaseException) -> type[Exception]:
    """
    Return LLMTransportError or LLMTerminalError based on the exception.

    If we cannot confidently classify (unknown exception, missing status),
    default to transport error so the fallback chain gets a chance.
    """
    status = _extract_status_code(exc)
    if status is not None:
        if status in _TERMINAL_STATUSES:
            return LLMTerminalError
        if status in _TRANSIENT_STATUSES:
            return LLMTransportError

    # Network-level errors: httpx transport failures, asyncio timeouts — all transient.
    if isinstance(exc, (httpx.TimeoutException, httpx.ConnectError, httpx.RemoteProtocolError)):
        return LLMTransportError
    if isinstance(exc, TimeoutError):
        return LLMTransportError

    # Unknown: default to transient so we still try the fallback chain once.
    return LLMTransportError
