"""Shared in-memory fakes for ApiKeyService unit tests.

Uses the real InMemoryCache rather than a fake — it's pure in-process state
with no I/O, so faking it would just be re-testing a mock instead of the
actual rate-limit arithmetic.
"""

from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest
from fastforge_api_keys.config import ApiKeySettings
from fastforge_api_keys.models.api_key import ApiKey
from fastforge_api_keys.services.api_key_service import ApiKeyService
from fastforge_cache import InMemoryCache


class FakeApiKeyRepository:
    """In-memory stand-in for ApiKeyRepository."""

    def __init__(self) -> None:
        self.rows: dict[UUID, ApiKey] = {}

    async def get_by_id(self, record_id: UUID, *, include_deleted: bool = False) -> ApiKey | None:
        return self.rows.get(record_id)

    async def get_by_hash(self, key_hash: str) -> ApiKey | None:
        return next((k for k in self.rows.values() if k.key_hash == key_hash), None)

    async def list_for_user(self, user_id: UUID) -> list[ApiKey]:
        rows = [k for k in self.rows.values() if k.user_id == user_id]
        return sorted(rows, key=lambda k: k.created_at, reverse=True)

    async def create(self, instance: ApiKey) -> ApiKey:
        # created_at/updated_at are DB server_defaults in production, only
        # populated on a real flush+refresh — set them here so a fake create
        # behaves like the real repository from the caller's perspective.
        instance.id = uuid4()
        instance.created_at = datetime.now(UTC)
        instance.updated_at = instance.created_at
        self.rows[instance.id] = instance
        return instance

    async def update(self, instance: ApiKey) -> ApiKey:
        self.rows[instance.id] = instance
        return instance


@pytest.fixture
def fake_keys() -> FakeApiKeyRepository:
    return FakeApiKeyRepository()


@pytest.fixture
def cache() -> InMemoryCache:
    return InMemoryCache()


@pytest.fixture
def api_key_settings() -> ApiKeySettings:
    return ApiKeySettings(_env_file=None)


@pytest.fixture
def api_key_service(
    fake_keys: FakeApiKeyRepository, cache: InMemoryCache, api_key_settings: ApiKeySettings
) -> ApiKeyService:
    return ApiKeyService(fake_keys, cache, api_key_settings)  # type: ignore[arg-type]
