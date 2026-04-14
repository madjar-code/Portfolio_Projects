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

    model_config = SettingsConfigDict(env_file=_ENV_FILE)


settings = Settings()