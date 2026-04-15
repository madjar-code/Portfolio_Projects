import pathlib
import httpx

from config import settings


class DocumentFetcher:
    """Fetches document bytes by URL scheme.

    Caches the result in memory so each document is downloaded at most once
    per task, regardless of how many tools request it.
    """

    def __init__(self) -> None:
        self._cache: dict[str, bytes] = {}

    async def fetch(self, url: str) -> bytes:
        if url in self._cache:
            return self._cache[url]

        if url.startswith("file://"):
            path = pathlib.Path(url[7:])
            size_bytes = path.stat().st_size
            self._check_size(size_bytes)
            content = path.read_bytes()
        else:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.get(url)
                response.raise_for_status()
                content = response.content
            self._check_size(len(content))

        self._cache[url] = content
        return content

    @staticmethod
    def _check_size(size_bytes: int) -> None:
        limit_bytes = settings.max_document_size_mb * 1024 * 1024
        if size_bytes > limit_bytes:
            size_mb = size_bytes / (1024 * 1024)
            raise ValueError(
                f"Document size ({size_mb:.1f} MB) exceeds the allowed maximum "
                f"({settings.max_document_size_mb} MB). "
                "Reject this submission immediately — the document cannot be processed."
            )
