"""Shared application configuration primitives."""

from pydantic import Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from fastforge_common.enums import AppEnvironment

# Placeholder secrets shipped in .env.example — never valid in production.
PLACEHOLDER_SECRET_MARKERS = ("change-me", "changeme", "secret", "password", "example")


class BaseAppSettings(BaseSettings):
    """Base settings used by applications and reusable packages."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    app_name: str = Field(default="FastForge", alias="APP_NAME")
    app_env: AppEnvironment = Field(default=AppEnvironment.DEVELOPMENT, alias="APP_ENV")
    app_debug: bool = Field(default=False, alias="APP_DEBUG")
    app_secret_key: SecretStr = Field(..., alias="APP_SECRET_KEY", min_length=16)

    @field_validator("app_name")
    @classmethod
    def validate_app_name(cls, value: str) -> str:
        """Ensure application names are meaningful."""
        normalized = value.strip()
        if not normalized:
            msg = "APP_NAME must not be empty"
            raise ValueError(msg)
        return normalized

    @model_validator(mode="after")
    def _enforce_production_safety(self) -> "BaseAppSettings":
        """Refuse to start production with debug enabled or a placeholder secret."""
        if self.app_env != AppEnvironment.PRODUCTION:
            return self
        if self.app_debug:
            msg = "APP_DEBUG must be false in production (it leaks stack traces)."
            raise ValueError(msg)
        secret = self.app_secret_key.get_secret_value().lower()
        if len(secret) < 32 or any(marker in secret for marker in PLACEHOLDER_SECRET_MARKERS):
            msg = (
                "APP_SECRET_KEY looks like a placeholder or is shorter than 32 chars; "
                "set a strong random value in production (e.g. `openssl rand -hex 32`)."
            )
            raise ValueError(msg)
        return self

    @property
    def is_development(self) -> bool:
        """Return True in development environments."""
        return self.app_env == AppEnvironment.DEVELOPMENT

    @property
    def is_testing(self) -> bool:
        """Return True in test environments."""
        return self.app_env == AppEnvironment.TESTING

    @property
    def is_production(self) -> bool:
        """Return True in production environments."""
        return self.app_env == AppEnvironment.PRODUCTION
