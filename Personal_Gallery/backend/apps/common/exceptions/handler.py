import logging
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError, NotFound, PermissionDenied

from apps.photos.exceptions import (
    PhotosError,
    EntryNotFoundError,
    PhotoNotFoundError,
    MaxPhotosExceededError,
    InvalidPhotoFormatError,
    PhotoSizeTooLargeError,
)

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
        
        logger.error(
            f"API Error in {view_name}: {exc.__class__.__name__} - {str(exc)}",
            extra={
                "view": view_name,
                "user_id": user_id,
                "path": request.path if request else None,
                "method": request.method if request else None,
            },
            exc_info=True
        )
        
        response.data = custom_response_data
        return response
    
    if isinstance(exc, EntryNotFoundError):
        logger.warning(f"Entry not found - User {user_id} in {view_name}")
        return Response(
            {
                "error": {
                    "message": str(exc) or "Entry not found",
                    "code": "entry_not_found",
                    "status": status.HTTP_404_NOT_FOUND,
                    "details": {}
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    
    if isinstance(exc, PhotoNotFoundError):
        logger.warning(f"Photo not found - User {user_id} in {view_name}")
        return Response(
            {
                "error": {
                    "message": str(exc) or "Photo not found",
                    "code": "photo_not_found",
                    "status": status.HTTP_404_NOT_FOUND,
                    "details": {}
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    
    if isinstance(exc, MaxPhotosExceededError):
        logger.warning(f"Max photos exceeded - User {user_id} in {view_name}: {str(exc)}")
        return Response(
            {
                "error": {
                    "message": str(exc),
                    "code": "max_photos_exceeded",
                    "status": status.HTTP_400_BAD_REQUEST,
                    "details": {}
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if isinstance(exc, InvalidPhotoFormatError):
        logger.warning(f"Invalid photo format - User {user_id} in {view_name}: {str(exc)}")
        return Response(
            {
                "error": {
                    "message": str(exc),
                    "code": "invalid_photo_format",
                    "status": status.HTTP_400_BAD_REQUEST,
                    "details": {}
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if isinstance(exc, PhotoSizeTooLargeError):
        logger.warning(f"Photo size too large - User {user_id} in {view_name}: {str(exc)}")
        return Response(
            {
                "error": {
                    "message": str(exc),
                    "code": "photo_size_too_large",
                    "status": status.HTTP_400_BAD_REQUEST,
                    "details": {}
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if isinstance(exc, PhotosError):
        logger.error(f"PhotosError - User {user_id} in {view_name}: {str(exc)}", exc_info=True)
        return Response(
            {
                "error": {
                    "message": str(exc),
                    "code": "photos_error",
                    "status": status.HTTP_400_BAD_REQUEST,
                    "details": {}
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
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
    error_code_map = {
        NotFound: "not_found",
        PermissionDenied: "permission_denied",
        ValidationError: "validation_error",
    }
    return error_code_map.get(type(exc), "error")

