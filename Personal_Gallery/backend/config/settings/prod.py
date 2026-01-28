"""
Production settings.
"""
from .base import *

DEBUG = False

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "").split(",")

# Security settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

# Static and media files (for production with S3)
# AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
# AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
# AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME")
# AWS_S3_REGION_NAME = os.getenv("AWS_S3_REGION_NAME", "us-east-1")

# Logging
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "file": {
            "class": "logging.FileHandler",
            "filename": BASE_DIR / "logs" / "django.log",
        },
    },
    "root": {
        "handlers": ["file"],
        "level": "INFO",
    },
}

# API Documentation - Production
API_DESCRIPTION = """
**PRODUCTION ENVIRONMENT**

Personal Gallery API - Educational project for managing personal photo gallery.

## Features
- **Authentication**: Email/Password and Google OAuth
- **JWT Tokens**: Access and refresh tokens
- **Photo Management**: Upload, view, and manage photos
- **Entries**: Organize photos into entries/albums

## Authentication
Use the **Authorize** button to add your JWT token:
```
Bearer <your_access_token>
```

Get your token from `/api/auth/jwt/create/` endpoint.
"""

# Swagger settings for production
SWAGGER_SETTINGS = {
    "SECURITY_DEFINITIONS": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "JWT Authorization header using the Bearer scheme. Example: \"Bearer {token}\"",
        }
    },
    "USE_SESSION_AUTH": False,  # Disable session auth in production
    "JSON_EDITOR": False,
    "SUPPORTED_SUBMIT_METHODS": ["get", "post", "put", "delete", "patch"],
    "DEFAULT_MODEL_RENDERING": "example",
    "DEFAULT_MODEL_DEPTH": 2,
}

# ReDoc settings
REDOC_SETTINGS = {
    "LAZY_RENDERING": True,
    "HIDE_HOSTNAME": True,
    "EXPAND_RESPONSES": ["200", "201"],
    "PATH_IN_MIDDLE": True,
}