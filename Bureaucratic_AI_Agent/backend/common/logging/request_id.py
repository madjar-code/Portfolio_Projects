import logging
import uuid
from contextvars import ContextVar

_request_id_var: ContextVar[str | None] = ContextVar("request_id", default=None)


def get_request_id() -> str | None:
    return _request_id_var.get()


def set_request_id(value: str | None) -> None:
    _request_id_var.set(value)


class RequestIdMiddleware:
    HEADER = "X-Request-Id"

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        incoming = request.headers.get(self.HEADER) or str(uuid.uuid4())
        # Don't reset in a try/finally: Django's django.server access log fires
        # *after* middleware returns, so a reset would blank the contextvar
        # before the access-log LogRecord is formatted. The next request's
        # __call__ overwrites the value, so leaking across requests is safe
        # enough for sync WSGI.
        _request_id_var.set(incoming)
        request.request_id = incoming
        response = self.get_response(request)
        response[self.HEADER] = incoming
        return response


class RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = get_request_id() or "-"
        return True
