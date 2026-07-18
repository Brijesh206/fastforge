"""Tests for the in-memory Cache adapter."""

import asyncio

from fastforge_cache.adapters.in_memory_cache import InMemoryCache


async def test_get_returns_none_for_missing_key() -> None:
    cache = InMemoryCache()

    assert await cache.get("missing") is None


async def test_set_then_get_round_trips() -> None:
    cache = InMemoryCache()

    await cache.set("key", "value")

    assert await cache.get("key") == "value"


async def test_delete_removes_the_key() -> None:
    cache = InMemoryCache()
    await cache.set("key", "value")

    await cache.delete("key")

    assert await cache.get("key") is None


async def test_delete_is_a_noop_for_a_missing_key() -> None:
    cache = InMemoryCache()

    await cache.delete("missing")  # does not raise


async def test_set_with_ttl_expires() -> None:
    cache = InMemoryCache()

    await cache.set("key", "value", ttl_seconds=0)
    await asyncio.sleep(0.01)

    assert await cache.get("key") is None


async def test_set_without_ttl_persists() -> None:
    cache = InMemoryCache()

    await cache.set("key", "value")
    await asyncio.sleep(0.01)

    assert await cache.get("key") == "value"


async def test_incr_starts_at_one() -> None:
    cache = InMemoryCache()

    assert await cache.incr("counter") == 1


async def test_incr_accumulates() -> None:
    cache = InMemoryCache()

    await cache.incr("counter")
    await cache.incr("counter")
    result = await cache.incr("counter")

    assert result == 3


async def test_incr_applies_ttl_only_on_first_hit() -> None:
    cache = InMemoryCache()

    await cache.incr("counter", ttl_seconds=0)
    await asyncio.sleep(0.01)

    # The key expired after the first hit; a fresh window starts at 1 again,
    # not accumulating across the expiry.
    assert await cache.incr("counter", ttl_seconds=60) == 1


async def test_incr_is_atomic_under_concurrency() -> None:
    cache = InMemoryCache()

    await asyncio.gather(*(cache.incr("counter") for _ in range(50)))

    assert await cache.get("counter") == "50"
