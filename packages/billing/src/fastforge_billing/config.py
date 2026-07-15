"""Billing configuration."""

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class BillingSettings(BaseSettings):
    """Stripe credentials and the default plan price.

    All values default to empty so the API can boot without billing
    configured; the Stripe adapter raises BillingNotConfiguredError if a
    credential is actually needed at call time.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    secret_key: SecretStr = Field(default=SecretStr(""), alias="STRIPE_SECRET_KEY")
    webhook_secret: SecretStr = Field(default=SecretStr(""), alias="STRIPE_WEBHOOK_SECRET")
    price_id: str = Field(default="", alias="STRIPE_PRICE_ID")
