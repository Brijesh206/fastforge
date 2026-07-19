"""Authentication configuration."""

from fastforge_common.config import PLACEHOLDER_SECRET_MARKERS
from fastforge_common.enums import AppEnvironment
from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from fastforge_auth.constants import (
    DEFAULT_ACCESS_TOKEN_EXPIRE_MINUTES,
    DEFAULT_EMAIL_VERIFICATION_EXPIRE_HOURS,
    DEFAULT_JWT_ALGORITHM,
    DEFAULT_PASSWORD_RESET_EXPIRE_MINUTES,
    DEFAULT_REFRESH_TOKEN_EXPIRE_DAYS,
)


class AuthSettings(BaseSettings):
    """Settings for token issuance and verification, loaded from the environment."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    # Read so the validator below can refuse placeholder JWT secrets in production.
    app_env: AppEnvironment = Field(default=AppEnvironment.DEVELOPMENT, alias="APP_ENV")
    jwt_secret_key: SecretStr = Field(..., alias="JWT_SECRET_KEY", min_length=16)
    jwt_algorithm: str = Field(default=DEFAULT_JWT_ALGORITHM, alias="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(
        default=DEFAULT_ACCESS_TOKEN_EXPIRE_MINUTES,
        ge=1,
        alias="JWT_ACCESS_TOKEN_EXPIRE_MINUTES",
    )
    refresh_token_expire_days: int = Field(
        default=DEFAULT_REFRESH_TOKEN_EXPIRE_DAYS,
        ge=1,
        alias="JWT_REFRESH_TOKEN_EXPIRE_DAYS",
    )
    email_verification_expire_hours: int = Field(
        default=DEFAULT_EMAIL_VERIFICATION_EXPIRE_HOURS,
        ge=1,
        alias="EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS",
    )
    password_reset_expire_minutes: int = Field(
        default=DEFAULT_PASSWORD_RESET_EXPIRE_MINUTES,
        ge=1,
        alias="PASSWORD_RESET_TOKEN_EXPIRE_MINUTES",
    )

    @model_validator(mode="after")
    def _enforce_production_safety(self) -> "AuthSettings":
        """Refuse to sign production tokens with a placeholder or weak secret."""
        if self.app_env != AppEnvironment.PRODUCTION:
            return self
        secret = self.jwt_secret_key.get_secret_value().lower()
        if len(secret) < 32 or any(marker in secret for marker in PLACEHOLDER_SECRET_MARKERS):
            msg = (
                "JWT_SECRET_KEY looks like a placeholder or is shorter than 32 chars; "
                "set a strong random value in production (e.g. `openssl rand -hex 32`)."
            )
            raise ValueError(msg)
        return self
