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

_S3_OPTIONS_BASE = {
    "access_key": AWS_ACCESS_KEY_ID,         # noqa: F405
    "secret_key": AWS_SECRET_ACCESS_KEY,     # noqa: F405
    "region_name": AWS_S3_REGION_NAME,       # noqa: F405
    "signature_version": AWS_S3_SIGNATURE_VERSION,  # noqa: F405
    "addressing_style": "path",
    "file_overwrite": AWS_S3_FILE_OVERWRITE,  # noqa: F405
    "querystring_auth": True,
    "default_acl": AWS_DEFAULT_ACL,          # noqa: F405
}

STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
        "OPTIONS": {**_S3_OPTIONS_BASE, "bucket_name": AWS_S3_BUCKET_MEDIA},   # noqa: F405
    },
    "staticfiles": {
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
        "OPTIONS": {**_S3_OPTIONS_BASE, "bucket_name": AWS_S3_BUCKET_STATIC},  # noqa: F405
    },
}

MEDIA_URL = f"https://s3.{AWS_S3_REGION_NAME}.amazonaws.com/{AWS_S3_BUCKET_MEDIA}/"   # noqa: F405
STATIC_URL = f"https://s3.{AWS_S3_REGION_NAME}.amazonaws.com/{AWS_S3_BUCKET_STATIC}/"  # noqa: F405

SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
