from typing import Any
from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI
from config import settings

PRODUCTION = settings.production

_LLM_REQUEST_TIMEOUT = 60  # seconds per LLM HTTP call


def _build_registry() -> list[dict]:
    entries: list[dict] = []

    entries += [
        {
            "name": "gpt-4o-mini",
            "llm": ChatOpenAI(
                model="gpt-4o-mini",
                temperature=0.2,
                api_key=settings.openai_api_key,
                timeout=_LLM_REQUEST_TIMEOUT,
            ),
        },
        {
            "name": "gpt-4o",
            "llm": ChatOpenAI(
                model="gpt-4o",
                temperature=0.2,
                top_p=0.95 if PRODUCTION else 0.8,
                presence_penalty=0.1 if PRODUCTION else 0.0,
                api_key=settings.openai_api_key,
                timeout=_LLM_REQUEST_TIMEOUT,
            ),
        },
    ]

    if settings.anthropic_api_key:
        from langchain_anthropic import ChatAnthropic
        entries += [
            {
                "name": "claude-haiku-4-5",
                "llm": ChatAnthropic(
                    model="claude-haiku-4-5-20251001",
                    temperature=0.2,
                    api_key=settings.anthropic_api_key,
                    timeout=_LLM_REQUEST_TIMEOUT,
                ),
            },
            {
                "name": "claude-sonnet-4-6",
                "llm": ChatAnthropic(
                    model="claude-sonnet-4-6",
                    temperature=0.2,
                    api_key=settings.anthropic_api_key,
                    timeout=_LLM_REQUEST_TIMEOUT,
                ),
            },
        ]

    if settings.ollama_base_url:
        entries += [
            {
                "name": settings.ollama_model,
                "llm": ChatOpenAI(
                    model=settings.ollama_model,
                    base_url=f"{settings.ollama_base_url}/v1",
                    api_key="ollama",
                    temperature=0.2,
                    timeout=_LLM_REQUEST_TIMEOUT,
                ),
            },
        ]

    return entries

class LLMRegistry:
    LLMS = _build_registry()

    @classmethod
    def get(cls, model_name: str) -> BaseChatModel:
        """Return a model instance by name. Raises KeyError if not found."""
        for entry in cls.LLMS:
            if entry["name"] == model_name:
                return entry["llm"]
        raise KeyError(f"Model '{model_name}' not registered in LLMRegistry.")

    @classmethod
    def get_model_at_index(cls, index: int) -> dict[str, Any]:
        """Return full entry {name, llm} at index. Used for fallback chains."""
        return cls.LLMS[index]

    @classmethod
    def available_models(cls) -> list[str]:
        return [entry["name"] for entry in cls.LLMS]

    @classmethod
    def fallback_chain(cls, preferred: str | None = None) -> list[dict]:
        """Return the list of entries to try in order, starting from preferred."""
        if not preferred:
            return list(cls.LLMS)
        preferred_entry = next((e for e in cls.LLMS if e["name"] == preferred), None)
        others = [e for e in cls.LLMS if e["name"] != preferred]
        return ([preferred_entry] + others) if preferred_entry else list(cls.LLMS)