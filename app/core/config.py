from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Velra"
    app_version: str = "1.0.0"
    environment: str = "development"
    log_level: str = "INFO"

    database_url: str = "postgresql+asyncpg://velra:velra@postgres:5432/velra"
    redis_url: str = "redis://redis:6379/0"
    jwt_secret: str = "velra_super_secret_key_change_me"
    cache_ttl_seconds: int = 900

    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"
    openai_timeout_seconds: float = 30.0

    gemini_api_key: str | None = None

    use_chroma_http: bool = False
    chroma_host: str = "chroma"
    chroma_port: int = 8000
    chroma_ssl: bool = False
    chroma_persist_directory: str = "./.chroma"
    chroma_collection_name: str = "chat_analyses"

    google_client_id: str | None = None
    google_client_secret: str | None = None
    smtp_password: str | None = None
    upstash_redis_rest_url: str | None = None
    upstash_redis_rest_token: str | None = None

    supabase_url: str = "https://duwxmxubtygvtwgspdgd.supabase.co"
    supabase_service_role_key: str | None = None

    scoring_rules_path: Path = Field(
        default=Path("app/features/chat_analysis/scoring_rules.json")
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def openai_enabled(self) -> bool:
        return bool(self.openai_api_key or self.gemini_api_key)


@lru_cache
def get_settings() -> Settings:
    return Settings()
