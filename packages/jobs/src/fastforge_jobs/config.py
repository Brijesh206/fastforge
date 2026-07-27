"""Background jobs configuration."""

from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

JobsProvider = Literal["memory", "taskiq", "celery"]


class JobsSettings(BaseSettings):
    """Provider and broker settings, loaded from the environment.

    Defaults to the in-memory provider so a fresh checkout runs with no broker
    and no worker process — same principle as CACHE_PROVIDER=memory.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    provider: JobsProvider = Field(default="memory", alias="JOBS_PROVIDER")
    # Both taskiq and celery use this as the broker URL. Defaults to the same
    # Redis the cache uses; point at a separate database (or RabbitMQ for
    # celery) if you'd rather keep queues and cache apart.
    broker_url: str = Field(default="redis://localhost:6379/1", alias="JOBS_BROKER_URL")
    result_backend_url: str | None = Field(default=None, alias="JOBS_RESULT_BACKEND_URL")
