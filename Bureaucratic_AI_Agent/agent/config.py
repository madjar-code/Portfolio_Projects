from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

_ENV_FILE = Path(__file__).parent / ".env"


class Settings(BaseSettings):
    rabbitmq_url: str
    agent_queue: str = "agent_tasks"
    backend_callback_url: str
    agent_api_key: str

    openai_api_key: str
    anthropic_api_key: str | None = None
    production: bool = False
    prompt_version: str = "v1"
    default_model: str = "gpt-4o-mini"
    eval_judge_model: str = "gpt-4o-mini"

    enable_injection_scanner: bool = False   # set True to activate core/security.py scanner
    injection_scanner_hard_stop: bool = False  # if True, detected injection → immediate REJECT without LLM
    max_document_size_mb: int = 20           # documents exceeding this size are rejected before reading

    model_config = SettingsConfigDict(env_file=_ENV_FILE)


settings = Settings()