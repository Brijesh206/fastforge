"""Tests for ApiKeyService: issuance, authentication, rate limiting, revocation."""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import uuid4

import pytest
from fastforge_api_keys.config import ApiKeySettings
from fastforge_api_keys.constants import API_KEY_PREFIX
from fastforge_api_keys.exceptions import ApiKeyNotFoundError, InvalidApiKeyError
from fastforge_api_keys.services.api_key_service import ApiKeyService
from fastforge_cache import InMemoryCache
from fastforge_common.exceptions import RateLimitError
from fastforge_common.tokens import hash_secret

if TYPE_CHECKING:
    from conftest import FakeApiKeyRepository


async def test_create_key_returns_a_prefixed_key_and_matching_hash(
    api_key_service: ApiKeyService, fake_keys: FakeApiKeyRepository
) -> None:
    user_id = uuid4()

    api_key, raw_key = await api_key_service.create_key(user_id, "CI token")

    assert raw_key.startswith(API_KEY_PREFIX)
    assert api_key.key_hash == hash_secret(raw_key)
    assert raw_key.startswith(api_key.key_prefix)
    assert api_key.user_id == user_id
    assert api_key.name == "CI token"
    assert fake_keys.rows[api_key.id] is api_key


async def test_create_key_never_persists_the_raw_key(api_key_service: ApiKeyService) -> None:
    api_key, raw_key = await api_key_service.create_key(uuid4(), "token")

    assert raw_key != api_key.key_hash
    assert raw_key not in vars(api_key).values()


async def test_authenticate_returns_the_owning_user_id(api_key_service: ApiKeyService) -> None:
    user_id = uuid4()
    _, raw_key = await api_key_service.create_key(user_id, "token")

    resolved = await api_key_service.authenticate(raw_key)

    assert resolved == user_id


async def test_authenticate_rejects_an_unknown_key(api_key_service: ApiKeyService) -> None:
    with pytest.raises(InvalidApiKeyError):
        await api_key_service.authenticate(f"{API_KEY_PREFIX}not-a-real-key")


async def test_authenticate_rejects_a_key_without_the_expected_prefix(
    api_key_service: ApiKeyService,
) -> None:
    with pytest.raises(InvalidApiKeyError):
        await api_key_service.authenticate("sk_not_our_format")


async def test_authenticate_rejects_a_revoked_key(
    api_key_service: ApiKeyService, fake_keys: FakeApiKeyRepository
) -> None:
    api_key, raw_key = await api_key_service.create_key(uuid4(), "token")
    await api_key_service.revoke_key(api_key.user_id, api_key.id)

    with pytest.raises(InvalidApiKeyError):
        await api_key_service.authenticate(raw_key)


async def test_authenticate_records_last_used_at(
    api_key_service: ApiKeyService, fake_keys: FakeApiKeyRepository
) -> None:
    api_key, raw_key = await api_key_service.create_key(uuid4(), "token")
    assert api_key.last_used_at is None

    await api_key_service.authenticate(raw_key)

    assert fake_keys.rows[api_key.id].last_used_at is not None


async def test_authenticate_enforces_the_per_key_rate_limit(
    fake_keys: FakeApiKeyRepository, cache: InMemoryCache
) -> None:
    settings = ApiKeySettings(
        API_KEY_RATE_LIMIT_PER_MINUTE=2, API_KEY_RATE_LIMIT_WINDOW_SECONDS=60, _env_file=None
    )
    service = ApiKeyService(fake_keys, cache, settings)  # type: ignore[arg-type]
    _, raw_key = await service.create_key(uuid4(), "token")

    await service.authenticate(raw_key)
    await service.authenticate(raw_key)  # exactly at the limit — allowed

    with pytest.raises(RateLimitError) as exc_info:
        await service.authenticate(raw_key)

    assert exc_info.value.retry_after_seconds == 60


async def test_rate_limit_is_scoped_per_key_not_global(
    fake_keys: FakeApiKeyRepository, cache: InMemoryCache
) -> None:
    settings = ApiKeySettings(API_KEY_RATE_LIMIT_PER_MINUTE=1, _env_file=None)
    service = ApiKeyService(fake_keys, cache, settings)  # type: ignore[arg-type]
    _, key_a = await service.create_key(uuid4(), "a")
    _, key_b = await service.create_key(uuid4(), "b")

    await service.authenticate(key_a)  # uses up key_a's limit

    await service.authenticate(key_b)  # key_b is unaffected


async def test_revoke_key_sets_revoked_at(
    api_key_service: ApiKeyService, fake_keys: FakeApiKeyRepository
) -> None:
    api_key, _ = await api_key_service.create_key(uuid4(), "token")

    await api_key_service.revoke_key(api_key.user_id, api_key.id)

    assert fake_keys.rows[api_key.id].revoked_at is not None


async def test_revoke_key_raises_for_an_unknown_key(api_key_service: ApiKeyService) -> None:
    with pytest.raises(ApiKeyNotFoundError):
        await api_key_service.revoke_key(uuid4(), uuid4())


async def test_revoke_key_raises_when_the_key_belongs_to_someone_else(
    api_key_service: ApiKeyService,
) -> None:
    api_key, _ = await api_key_service.create_key(uuid4(), "token")

    with pytest.raises(ApiKeyNotFoundError):
        await api_key_service.revoke_key(uuid4(), api_key.id)


async def test_list_keys_returns_only_the_requested_users_keys(
    api_key_service: ApiKeyService,
) -> None:
    user_a, user_b = uuid4(), uuid4()
    await api_key_service.create_key(user_a, "a1")
    await api_key_service.create_key(user_a, "a2")
    await api_key_service.create_key(user_b, "b1")

    keys = await api_key_service.list_keys(user_a)

    assert {k.name for k in keys} == {"a1", "a2"}
