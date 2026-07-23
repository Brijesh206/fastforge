"""API key dependencies for the API application."""

from uuid import UUID

from fastapi import Depends, Request
from fastforge_api_keys import ApiKeyRepository, ApiKeyService, ApiKeySettings
from fastforge_cache import Cache
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_db_transaction


def get_cache(request: Request) -> Cache:
    """Return the process-wide cache created during startup."""
    return request.app.state.cache


def get_api_key_settings(request: Request) -> ApiKeySettings:
    """Return the API key settings resolved during startup."""
    return request.app.state.api_key_settings


def get_api_key_service(
    session: AsyncSession = Depends(get_db_transaction),
    cache: Cache = Depends(get_cache),
    settings: ApiKeySettings = Depends(get_api_key_settings),
) -> ApiKeyService:
    """Build the API key service for the key-management endpoints."""
    return ApiKeyService(ApiKeyRepository(session), cache, settings)


async def authenticate_via_api_key(request: Request, raw_key: str) -> UUID:
    """Verify an API key and return the owning user's id.

    Deliberately bypasses FastAPI's Depends graph and opens its own
    transaction, so a JWT-authenticated request — the common case — never
    pays for a transactional session it doesn't need. Only requests that
    actually present an API key incur this cost.
    """
    manager = request.app.state.database_manager
    async with manager.transaction() as session:
        service = ApiKeyService(
            ApiKeyRepository(session),
            request.app.state.cache,
            request.app.state.api_key_settings,
        )
        return await service.authenticate(raw_key)
