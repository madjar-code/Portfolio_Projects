"""
Development settings.
"""
from .base import *

DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

# Development-specific apps
INSTALLED_APPS += [
    # "debug_toolbar",
]

# Development-specific middleware
MIDDLEWARE += [
    # "debug_toolbar.middleware.DebugToolbarMiddleware",
]

# Database for development (можно использовать SQLite)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# CORS settings for development
CORS_ALLOW_ALL_ORIGINS = True

# REST Framework - Development (allow unauthenticated access for testing)
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.AllowAny",  # Открытый доступ в dev
    ),
    "DEFAULT_RENDERER_CLASSES": (
        "rest_framework.renderers.JSONRenderer",
    ),
    "DEFAULT_PARSER_CLASSES": (
        "rest_framework.parsers.JSONParser",
        "rest_framework.parsers.MultiPartParser",
        "rest_framework.parsers.FormParser",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DATETIME_FORMAT": "%Y-%m-%dT%H:%M:%SZ",
    "EXCEPTION_HANDLER": "rest_framework.views.exception_handler",
}

# Logging
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "DEBUG",
    },
}

# API Documentation - Development
API_DESCRIPTION = """
**DEVELOPMENT ENVIRONMENT**

Personal Gallery API - Educational project for managing personal photo gallery.

## Features
- **Authentication**: Email/Password and Google OAuth
- **JWT Tokens**: Access and refresh tokens
- **Photo Management**: Upload, view, and manage photos
- **Entries**: Organize photos into entries/albums

## Development Notes
- Email backend: Console (check terminal for emails)
- Database: SQLite
- CORS: Enabled for all origins
- Debug mode: ON

## Authentication
Use the **Authorize** button to add your JWT token:
```
Bearer <your_access_token>
```

Get your token from `/api/auth/jwt/create/` endpoint.

## Quick Test User
You can create a test user via `/api/auth/users/` endpoint.
"""

# Swagger settings for development
SWAGGER_SETTINGS = {
    "SECURITY_DEFINITIONS": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "JWT Authorization header using the Bearer scheme. Example: \"Bearer {token}\"",
        }
    },
    "USE_SESSION_AUTH": False,
    "JSON_EDITOR": True,
    "SUPPORTED_SUBMIT_METHODS": ["get", "post", "put", "delete", "patch"],
    "DEFAULT_MODEL_RENDERING": "example",
    "DEFAULT_MODEL_DEPTH": 3,
}

# ReDoc settings
REDOC_SETTINGS = {
    "LAZY_RENDERING": True,
    "HIDE_HOSTNAME": False,
    "EXPAND_RESPONSES": ["200", "201"],
    "PATH_IN_MIDDLE": True,
}