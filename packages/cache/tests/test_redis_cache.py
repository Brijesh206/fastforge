"""End-to-end tests against a real Redis.

Requires Redis reachable at REDIS_URL (default redis://localhost:6379/0).
Excluded from the default gate: `pytest -m "not integration"`.
"""

import asyncio
import os
import uuid

import pytest
from fastforge_cache.adapters.redis_cache import RedisCache

pytestmark = pytest.mark.integration


def _cache() -> RedisCache:
    return RedisCache(os.environ.get("REDIS_URL", "redis://localhost:6379/0"))


def _key(name: str) -> str:
    # Unique per test run so parallel/repeated runs never collide.
    return f"fastforge:test:{uuid.uuid4().hex[:8]}:{name}"


async def test_set_then_get_round_trips() -> None:
    cache = _cache()
    key = _key("roundtrip")

    await cache.set(key, "value")

    assert await cache.get(key) == "value"
    await cache.delete(key)


async def test_get_returns_none_for_missing_key() -> None:
    cache = _cache()

    assert await cache.get(_key("missing")) is None


async def test_delete_removes_the_key() -> None:
    cache = _cache()
    key = _key("delete")
    await cache.set(key, "value")

    await cache.delete(key)

    assert await cache.get(key) is None


async def test_set_with_ttl_expires() -> None:
    cache = _cache()
    key = _key("ttl")

    await cache.set(key, "value", ttl_seconds=1)
    assert await cache.get(key) == "value"
    await asyncio.sleep(1.2)

    assert await cache.get(key) is None


async def test_incr_accumulates_and_applies_ttl_once() -> None:
    cache = _cache()
    key = _key("incr")

    first = await cache.incr(key, ttl_seconds=60)
    second = await cache.incr(key, ttl_seconds=60)

    assert (first, second) == (1, 2)
    ttl = await cache._client.ttl(key)
    assert 0 < ttl <= 60
    await cache.delete(key)


async def test_incr_is_atomic_under_concurrency() -> None:
    cache = _cache()
    key = _key("concurrent")

    await asyncio.gather(*(cache.incr(key) for _ in range(50)))

    assert await cache.get(key) == "50"
    await cache.delete(key)
