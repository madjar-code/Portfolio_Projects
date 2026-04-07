from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    rabbitmq_url: str
    agent_queue: str = "agent_tasks"
    backend_callback_url: str
    agent_api_key: str

    openai_api_key: str
    production: bool = False
    prompt_version: str = "v1"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()