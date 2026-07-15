"""Authentication configuration."""

from pydantic import Field, SecretStr
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
