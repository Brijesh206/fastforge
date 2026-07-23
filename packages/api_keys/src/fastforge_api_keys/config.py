"""API key configuration."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from fastforge_api_keys.constants import (
    DEFAULT_RATE_LIMIT_PER_MINUTE,
    DEFAULT_RATE_LIMIT_WINDOW_SECONDS,
)


class ApiKeySettings(BaseSettings):
    """Per-key rate limit settings, loaded from the environment."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    rate_limit_per_minute: int = Field(
        default=DEFAULT_RATE_LIMIT_PER_MINUTE, ge=1, alias="API_KEY_RATE_LIMIT_PER_MINUTE"
    )
    rate_limit_window_seconds: int = Field(
        default=DEFAULT_RATE_LIMIT_WINDOW_SECONDS,
        ge=1,
        alias="API_KEY_RATE_LIMIT_WINDOW_SECONDS",
    )
