import os

from .base import *  # noqa: F401, F403

DEBUG = False

ALLOWED_HOSTS = os.environ["ALLOWED_HOSTS"].split(",")

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# boto3 uses this to connect to MinIO inside Docker (e.g. http://minio:9000)
_S3_ENDPOINT_INTERNAL = os.environ.get("AWS_S3_ENDPOINT_URL", "")
# Browser uses this as the URL prefix for media/static files (e.g. http://<droplet-ip>:9000)
_S3_ENDPOINT_PUBLIC = os.environ.get("AWS_S3_PUBLIC_URL", _S3_ENDPOINT_INTERNAL)

_S3_OPTIONS_BASE = {
    "endpoint_url": _S3_ENDPOINT_INTERNAL or None,
    "access_key": AWS_ACCESS_KEY_ID,         # noqa: F405
    "secret_key": AWS_SECRET_ACCESS_KEY,     # noqa: F405
    "region_name": AWS_S3_REGION_NAME,       # noqa: F405
    "signature_version": AWS_S3_SIGNATURE_VERSION,  # noqa: F405
    "addressing_style": "path",
    "file_overwrite": AWS_S3_FILE_OVERWRITE,  # noqa: F405
    "querystring_auth": False,
    "default_acl": AWS_DEFAULT_ACL,          # noqa: F405
}

STORAGES = {
    "default": {
        "BACKEND": "config.storage.PublicMinIOStorage",
        "OPTIONS": {**_S3_OPTIONS_BASE, "bucket_name": AWS_S3_BUCKET_MEDIA},   # noqa: F405
    },
    "staticfiles": {
        "BACKEND": "config.storage.PublicMinIOStorage",
        "OPTIONS": {**_S3_OPTIONS_BASE, "bucket_name": AWS_S3_BUCKET_STATIC},  # noqa: F405
    },
}

MEDIA_URL = f"{_S3_ENDPOINT_PUBLIC}/{AWS_S3_BUCKET_MEDIA}/"   # noqa: F405
STATIC_URL = f"{_S3_ENDPOINT_PUBLIC}/{AWS_S3_BUCKET_STATIC}/"  # noqa: F405

# Set to True only after SSL is configured (Let's Encrypt / load balancer)
SECURE_SSL_REDIRECT = os.environ.get("SECURE_SSL_REDIRECT", "False") == "True"
SESSION_COOKIE_SECURE = SECURE_SSL_REDIRECT
CSRF_COOKIE_SECURE = SECURE_SSL_REDIRECT
SECURE_HSTS_SECONDS = 31536000 if SECURE_SSL_REDIRECT else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = SECURE_SSL_REDIRECT

# Trust X-Forwarded-Proto from nginx
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Disable DRF browsable API — JSON only in production
REST_FRAMEWORK = {
    **REST_FRAMEWORK,  # noqa: F405
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
}
