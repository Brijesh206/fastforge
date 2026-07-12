"""Logging configuration."""

from enum import StrEnum
from logging import CRITICAL, DEBUG, ERROR, INFO, WARNING

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class LogFormat(StrEnum):
    """Supported log output formats."""

    JSON = "json"
    TEXT = "text"


LOG_LEVELS = {
    "DEBUG": DEBUG,
    "INFO": INFO,
    "WARNING": WARNING,
    "ERROR": ERROR,
    "CRITICAL": CRITICAL,
}


class LoggingSettings(BaseSettings):
    """Settings for platform logging."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    service_name: str = Field(default="fastforge", alias="LOG_SERVICE_NAME")
    environment: str = Field(default="development", alias="APP_ENV")
    level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_format: LogFormat = Field(default=LogFormat.TEXT, alias="LOG_FORMAT")
    enable_console: bool = Field(default=True, alias="LOG_ENABLE_CONSOLE")

    @field_validator("service_name")
    @classmethod
    def validate_service_name(cls, value: str) -> str:
        """Ensure the service name is usable in logs."""
        normalized = value.strip()
        if not normalized:
            msg = "LOG_SERVICE_NAME must not be empty"
            raise ValueError(msg)
        return normalized

    @field_validator("level")
    @classmethod
    def validate_level(cls, value: str) -> str:
        """Normalize and validate log level names."""
        normalized = value.strip().upper()
        if normalized not in LOG_LEVELS:
            msg = f"LOG_LEVEL must be one of: {sorted(LOG_LEVELS)}"
            raise ValueError(msg)
        return normalized

    @property
    def level_number(self) -> int:
        """Return the stdlib logging level number."""
        return LOG_LEVELS[self.level]
