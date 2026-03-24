from __future__ import annotations

from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


SUPPORTED_LANGUAGES = {"en", "am", "om"}
SUPPORTED_LOG_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    bot_token: str = Field(..., alias="BOT_TOKEN")
    database_url: str = Field(..., alias="DATABASE_URL")
    admin_group_id: int = Field(..., alias="ADMIN_GROUP_ID")
    bank_website: str = Field(..., alias="BANK_WEBSITE")

    default_language: str = Field("en", alias="DEFAULT_LANGUAGE")
    max_nearest_results: int = Field(5, alias="MAX_NEAREST_RESULTS")
    log_level: str = Field("INFO", alias="LOG_LEVEL")

    support_enabled: bool = Field(True, alias="SUPPORT_ENABLED")
    app_name: str = Field("Banking Telegram Bot", alias="APP_NAME")

    @field_validator("bot_token")
    @classmethod
    def validate_bot_token(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("BOT_TOKEN cannot be empty")
        return value

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("DATABASE_URL cannot be empty")
        if not (
            value.startswith("postgresql://")
            or value.startswith("postgresql+asyncpg://")
            or value.startswith("sqlite://")
            or value.startswith("sqlite+aiosqlite://")
        ):
            raise ValueError(
                "DATABASE_URL must start with postgresql://, "
                "postgresql+asyncpg://, sqlite://, or sqlite+aiosqlite://"
            )
        return value

    @field_validator("bank_website")
    @classmethod
    def validate_bank_website(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("BANK_WEBSITE cannot be empty")
        if not (value.startswith("http://") or value.startswith("https://")):
            raise ValueError("BANK_WEBSITE must start with http:// or https://")
        return value

    @field_validator("default_language")
    @classmethod
    def validate_default_language(cls, value: str) -> str:
        value = value.strip().lower()
        if value not in SUPPORTED_LANGUAGES:
            raise ValueError(
                f"DEFAULT_LANGUAGE must be one of: {', '.join(sorted(SUPPORTED_LANGUAGES))}"
            )
        return value

    @field_validator("max_nearest_results")
    @classmethod
    def validate_max_nearest_results(cls, value: int) -> int:
        if value < 1:
            raise ValueError("MAX_NEAREST_RESULTS must be at least 1")
        if value > 20:
            raise ValueError("MAX_NEAREST_RESULTS must not be greater than 20")
        return value

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, value: str) -> str:
        value = value.strip().upper()
        if value not in SUPPORTED_LOG_LEVELS:
            raise ValueError(
                f"LOG_LEVEL must be one of: {', '.join(sorted(SUPPORTED_LOG_LEVELS))}"
            )
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()