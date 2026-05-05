from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


ROOT_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    database_url: str
    redis_url: str = "redis://localhost:6379/0"
    openai_api_key: str = ""
    deepseek_api_key: str = ""
    ai_model_provider: str = "openai"
    ai_model_name: str = ""
    ai_pipeline_mode: str = "mock"
    db_worker_poll_interval_seconds: int = 5
    db_worker_batch_size: int = 10

    model_config = SettingsConfigDict(
        env_file=ROOT_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
