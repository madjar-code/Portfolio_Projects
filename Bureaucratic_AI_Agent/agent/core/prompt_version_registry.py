import re
from pathlib import Path

_PROMPTS_ROOT = Path(__file__).resolve().parent.parent / "prompts" / "system"
_VERSION_PATTERN = re.compile(r"^v(\d+)\.md$")


class PromptVersionNotFoundError(Exception):
    pass


class PromptVersionRegistry:
    def __init__(self, root: Path = _PROMPTS_ROOT) -> None:
        self._root = root

    def list_versions(self) -> list[str]:
        """Return all available versions sorted numerically, e.g. ['v1', 'v2']."""
        versions = []
        for path in self._root.glob("v*.md"):
            match = _VERSION_PATTERN.match(path.name)
            if match:
                versions.append((int(match.group(1)), path.stem))
        return [v for _, v in sorted(versions)]

    def load(self, version: str) -> str:
        """Return system prompt text for the given version.
        Raises PromptVersionNotFoundError if the file does not exist."""
        path = self._root / f"{version}.md"
        if not path.exists():
            raise PromptVersionNotFoundError(
                f"Prompt version '{version}' not found. "
                f"Available: {self.list_versions()}"
            )
        return path.read_text(encoding="utf-8")

    def latest(self) -> str:
        """Return the highest available version string."""
        versions = self.list_versions()
        if not versions:
            raise PromptVersionNotFoundError("No prompt versions found.")
        return versions[-1]


prompt_version_registry = PromptVersionRegistry()