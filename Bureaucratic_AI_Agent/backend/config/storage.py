import os

from storages.backends.s3boto3 import S3Boto3Storage


class PublicMinIOStorage(S3Boto3Storage):
    """
    S3Boto3Storage that rewrites internal MinIO URLs to the public-facing URL.

    boto3 constructs file URLs from endpoint_url (e.g. http://minio:9000),
    which is only reachable inside Docker. This subclass replaces that prefix
    with AWS_S3_PUBLIC_URL so browsers can actually fetch the files.
    """

    def url(self, name, parameters=None, expire=None, http_method=None):
        url = super().url(name, parameters=parameters, expire=expire, http_method=http_method)
        internal = os.environ.get("AWS_S3_ENDPOINT_URL", "")
        public = os.environ.get("AWS_S3_PUBLIC_URL", internal)
        if internal and internal != public:
            url = url.replace(internal, public, 1)
        return url
