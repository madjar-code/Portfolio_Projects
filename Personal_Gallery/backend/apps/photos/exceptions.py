"""Custom exceptions for photos app with automatic handler support."""

from rest_framework import status
from rest_framework.exceptions import APIException


class PhotosAPIException(APIException):
    """Base exception for photos app with automatic error handling.

    Subclasses should define:
    - status_code: HTTP status code (default: 400)
    - default_code: Error code for API response (default: 'error')
    - default_detail: Default error message
    """
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = 'photos_error'
    default_detail = 'An error occurred in photos app'


class InvalidPhotoFormatError(PhotosAPIException):
    """Raised when photo format is not allowed."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = 'invalid_photo_format'
    default_detail = 'Invalid photo format. Allowed formats: JPEG, PNG, WebP'


class PhotoSizeTooLargeError(PhotosAPIException):
    """Raised when photo size exceeds limit."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = 'photo_size_too_large'
    default_detail = 'Photo size exceeds the maximum allowed limit'


class MaxPhotosExceededError(PhotosAPIException):
    """Raised when max photos per entry limit is exceeded."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = 'max_photos_exceeded'
    default_detail = 'Maximum number of photos per entry exceeded'
