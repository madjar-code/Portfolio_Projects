"""
drf-yasg configuration for API documentation.

This module provides OpenAPI/Swagger schema configuration
with different settings for development and production environments.
"""
from django.conf import settings
from drf_yasg import openapi

# API Information from settings
API_TITLE = settings.API_TITLE
API_VERSION = settings.API_VERSION
API_DESCRIPTION = settings.API_DESCRIPTION
API_TERMS_OF_SERVICE = settings.API_TERMS_OF_SERVICE
API_CONTACT_EMAIL = settings.API_CONTACT_EMAIL
API_LICENSE_NAME = settings.API_LICENSE_NAME


# OpenAPI Info object
info = openapi.Info(
    title=API_TITLE,
    default_version=API_VERSION,
    description=API_DESCRIPTION,
    terms_of_service=API_TERMS_OF_SERVICE,
    contact=openapi.Contact(email=API_CONTACT_EMAIL),
    license=openapi.License(name=API_LICENSE_NAME),
)


# Common responses for documentation
COMMON_RESPONSES = {
    400: openapi.Response(
        description="Bad Request",
        examples={
            "application/json": {
                "detail": "Invalid input data",
                "errors": {
                    "field_name": ["Error message"]
                }
            }
        }
    ),
    401: openapi.Response(
        description="Unauthorized",
        examples={
            "application/json": {
                "detail": "Authentication credentials were not provided."
            }
        }
    ),
    403: openapi.Response(
        description="Forbidden",
        examples={
            "application/json": {
                "detail": "You do not have permission to perform this action."
            }
        }
    ),
    404: openapi.Response(
        description="Not Found",
        examples={
            "application/json": {
                "detail": "Not found."
            }
        }
    ),
    500: openapi.Response(
        description="Internal Server Error",
        examples={
            "application/json": {
                "detail": "Internal server error occurred."
            }
        }
    ),
}
