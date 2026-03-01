import logging
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError, NotFound, PermissionDenied

from apps.photos.exceptions import PhotosAPIException

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    view = context.get("view")
    request = context.get("request")
    view_name = view.__class__.__name__ if view else "Unknown"
    user_id = request.user.id if request and hasattr(request, "user") and request.user.is_authenticated else "Anonymous"

    if response is not None:
        custom_response_data = {
            "error": {
                "message": _get_error_message(exc, response),
                "code": _get_error_code(exc),
                "status": response.status_code,
                "details": response.data if isinstance(response.data, dict) else {"detail": response.data}
            }
        }

        # Determine log level based on status code
        # Client errors (4xx) are expected and logged as warnings without traceback
        # Server errors (5xx) are unexpected and logged as errors with traceback
        if 400 <= response.status_code < 500:
            # Client errors - expected errors that should be handled gracefully
            logger.warning(
                f"Client error in {view_name}: {exc.__class__.__name__} - {str(exc)}",
                extra={
                    "view": view_name,
                    "user_id": user_id,
                    "path": request.path if request else None,
                    "method": request.method if request else None,
                    "status_code": response.status_code,
                }
            )
        else:
            # Server errors (5xx) - unexpected errors that need investigation
            logger.error(
                f"Server error in {view_name}: {exc.__class__.__name__} - {str(exc)}",
                extra={
                    "view": view_name,
                    "user_id": user_id,
                    "path": request.path if request else None,
                    "method": request.method if request else None,
                    "status_code": response.status_code,
                },
                exc_info=True
            )

        response.data = custom_response_data
        return response

    # Handle unexpected exceptions
    logger.critical(
        f"Unhandled exception in {view_name}: {exc.__class__.__name__} - {str(exc)}",
        extra={
            "view": view_name,
            "user_id": user_id,
            "path": request.path if request else None,
        },
        exc_info=True
    )

    return Response(
        {
            "error": {
                "message": "Internal server error",
                "code": "internal_error",
                "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "details": {}
            }
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR
    )


def _get_error_message(exc, response):
    if isinstance(exc, ValidationError):
        if isinstance(response.data, dict):
            first_key = next(iter(response.data))
            first_error = response.data[first_key]
            if isinstance(first_error, list) and first_error:
                return first_error[0]
        return "Validation error"
    return str(exc)


def _get_error_code(exc):
    """Get error code from exception.

    For PhotosAPIException subclasses, use their default_code attribute.
    For standard DRF exceptions, use predefined codes.
    """
    # Check if it's a PhotosAPIException (has default_code attribute)
    if isinstance(exc, PhotosAPIException):
        return exc.default_code

    # Standard DRF exceptions
    error_code_map = {
        NotFound: "not_found",
        PermissionDenied: "permission_denied",
        ValidationError: "validation_error",
    }
    return error_code_map.get(type(exc), "error")
