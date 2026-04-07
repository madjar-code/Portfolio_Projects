from typing import Any
from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI
from config import settings

PRODUCTION = settings.production


class LLMRegistry:
    LLMS = [
        {
            "name": "gpt-4o-mini",
            "llm": ChatOpenAI(
                model="gpt-4o-mini",
                temperature=0.2,
                api_key=settings.openai_api_key,
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
            ),
        },
    ]

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
