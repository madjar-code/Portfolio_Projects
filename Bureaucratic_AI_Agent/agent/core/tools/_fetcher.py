import pathlib
import httpx


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
            content = pathlib.Path(url[7:]).read_bytes()
        else:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.get(url)
                response.raise_for_status()
                content = response.content

        self._cache[url] = content
        return content
