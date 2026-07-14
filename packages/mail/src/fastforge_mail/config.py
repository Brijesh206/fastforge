"""Mail configuration."""

from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class MailSettings(BaseSettings):
    """Provider, sender, and branding settings, loaded from the environment.

    Defaults to the console provider so a fresh checkout sends nothing to a
    real inbox until SMTP is configured deliberately.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    provider: Literal["console", "smtp"] = Field(default="console", alias="MAIL_PROVIDER")

    smtp_host: str = Field(default="localhost", alias="MAIL_SMTP_HOST")
    smtp_port: int = Field(default=1025, ge=1, le=65535, alias="MAIL_SMTP_PORT")
    smtp_username: str | None = Field(default=None, alias="MAIL_SMTP_USERNAME")
    smtp_password: SecretStr | None = Field(default=None, alias="MAIL_SMTP_PASSWORD")
    smtp_use_tls: bool = Field(default=True, alias="MAIL_SMTP_USE_TLS")
    smtp_timeout_seconds: int = Field(default=10, ge=1, alias="MAIL_SMTP_TIMEOUT_SECONDS")

    from_address: str = Field(default="no-reply@fastforge.dev", alias="MAIL_FROM_ADDRESS")
    from_name: str = Field(default="FastForge", alias="MAIL_FROM_NAME")
    reply_to: str | None = Field(default=None, alias="MAIL_REPLY_TO")

    product_name: str = Field(default="FastForge", alias="MAIL_PRODUCT_NAME")
    support_email: str = Field(default="support@fastforge.dev", alias="MAIL_SUPPORT_EMAIL")
