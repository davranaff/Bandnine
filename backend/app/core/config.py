from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Bandnine API"
    environment: str = "development"
    debug: bool = False
    api_prefix: str = "/api/v1"

    secret_key: str = "change-this-secret"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 30
    confirm_token_expire_hours: int = 24
    reset_token_expire_hours: int = 1

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/bandnine"
    redis_url: str = "redis://localhost:6379/0"

    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_username: str | None = None
    smtp_password: str | None = None
    smtp_use_tls: bool = True
    smtp_from_email: str = "noreply@example.com"

    frontend_base_url: str = "http://localhost:3000"
    openai_api_key: str | None = None
    openai_model: str = "gpt-4.1-mini"

    rate_limit_sign_in: int = 10
    rate_limit_reset: int = 5
    rate_limit_window_seconds: int = 60

    expose_debug_tokens: bool = Field(default=False)


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
