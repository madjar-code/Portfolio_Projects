import os

from .base import *  # noqa: F401, F403

DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "host.docker.internal"]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

AUTH_PASSWORD_VALIDATORS = []

_MINIO_ENDPOINT = os.environ.get("AWS_S3_ENDPOINT_URL", "http://localhost:9000")

_S3_OPTIONS_BASE = {
    "endpoint_url": _MINIO_ENDPOINT,
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
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
        "OPTIONS": {**_S3_OPTIONS_BASE, "bucket_name": AWS_S3_BUCKET_MEDIA},   # noqa: F405
    },
    "staticfiles": {
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
        "OPTIONS": {**_S3_OPTIONS_BASE, "bucket_name": AWS_S3_BUCKET_STATIC},  # noqa: F405
    },
}

MEDIA_URL = f"{_MINIO_ENDPOINT}/{AWS_S3_BUCKET_MEDIA}/"   # noqa: F405
STATIC_URL = f"{_MINIO_ENDPOINT}/{AWS_S3_BUCKET_STATIC}/"  # noqa: F405
