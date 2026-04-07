from pathlib import Path

_DEFAULT_ROOT = Path(__file__).resolve().parent.parent / "knowledge_base" / "procedures"


class KnowledgeBaseError(Exception):
    pass


class KnowledgeBase:
    def __init__(self, root: Path = _DEFAULT_ROOT) -> None:
        self._root = root

    def load(self, procedure: str) -> str:
        """
        Load procedure instructions by procedure type string.
        Returns the raw Markdown content.
        Raises KnowledgeBaseError if the file does not exist.
        """
        path = self._root / f"{procedure}.md"
        if not path.exists():
            raise KnowledgeBaseError(
                f"No instruction file found for procedure '{procedure}'. "
                f"Expected: {path}"
            )
        return path.read_text(encoding="utf-8")


knowledge_base = KnowledgeBase()