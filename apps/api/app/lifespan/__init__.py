"""Application lifespan management."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastforge_api_keys import ApiKeySettings
from fastforge_auth import Argon2PasswordHasher, AuthSettings, JwtTokenService
from fastforge_billing import BillingSettings, StripeBillingProvider
from fastforge_cache import CacheSettings, create_cache
from fastforge_database import DatabaseManager, DatabaseSettings
from fastforge_logging import LoggingSettings, configure_logging, get_logger
from fastforge_mail import EmailService, MailSettings, create_email_provider

logger = get_logger("app.lifespan")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """Initialize and dispose application infrastructure."""
    configure_logging(LoggingSettings(service_name="api"))
    auth_settings = AuthSettings()
    mail_settings = MailSettings()
    billing_settings = BillingSettings()
    cache_settings = CacheSettings()

    app.state.database_manager = DatabaseManager(DatabaseSettings())
    app.state.password_hasher = Argon2PasswordHasher()
    app.state.token_service = JwtTokenService(auth_settings)
    app.state.auth_settings = auth_settings
    app.state.email_service = EmailService(create_email_provider(mail_settings), mail_settings)
    app.state.billing_settings = billing_settings
    app.state.billing_provider = StripeBillingProvider(billing_settings)
    app.state.cache = create_cache(cache_settings)
    app.state.api_key_settings = ApiKeySettings()
    logger.info(
        "API startup complete",
        mail_provider=mail_settings.provider,
        cache_provider=cache_settings.provider,
    )
    try:
        yield
    finally:
        await app.state.cache.close()
        await app.state.database_manager.close()
        logger.info("API shutdown complete")
