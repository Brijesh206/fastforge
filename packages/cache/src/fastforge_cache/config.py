"""Cache configuration."""

from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class CacheSettings(BaseSettings):
    """Provider and connection settings, loaded from the environment.

    Defaults to the in-memory provider so a fresh checkout needs no Redis
    until it's configured deliberately.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    provider: Literal["memory", "redis"] = Field(default="memory", alias="CACHE_PROVIDER")
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")
