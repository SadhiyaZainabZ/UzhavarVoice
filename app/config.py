from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "UzhavarVoice"
    environment: str = "local"

    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"
    fallback_model: str = "gemini-2.5-flash-lite"
    request_timeout: float = 30.0
    max_retries: int = 2

    input_cost_per_million: float = 0.0
    output_cost_per_million: float = 0.0


@lru_cache
def get_settings() -> Settings:
    return Settings()
