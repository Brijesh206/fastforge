# TODO: Application startup/shutdown lifecycle events.
# See docs/04-folder-structure.md
"""Application lifespan management."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastforge_auth import Argon2PasswordHasher, AuthSettings, JwtTokenService
from fastforge_database import DatabaseManager, DatabaseSettings
from fastforge_logging import LoggingSettings, configure_logging, get_logger

logger = get_logger("app.lifespan")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """Initialize and dispose application infrastructure."""
    configure_logging(LoggingSettings(service_name="api"))
    app.state.database_manager = DatabaseManager(DatabaseSettings())
    app.state.password_hasher = Argon2PasswordHasher()
    app.state.token_service = JwtTokenService(AuthSettings())
    logger.info("API startup complete")
    try:
        yield
    finally:
        await app.state.database_manager.close()
        logger.info("API shutdown complete")
