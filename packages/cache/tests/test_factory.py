"""Tests for cache provider selection."""

from fastforge_cache.adapters.in_memory_cache import InMemoryCache
from fastforge_cache.adapters.redis_cache import RedisCache
from fastforge_cache.config import CacheSettings
from fastforge_cache.factory import create_cache


def test_create_cache_defaults_to_in_memory() -> None:
    cache = create_cache(CacheSettings(_env_file=None))

    assert isinstance(cache, InMemoryCache)


def test_create_cache_returns_redis_when_configured() -> None:
    cache = create_cache(CacheSettings(CACHE_PROVIDER="redis", _env_file=None))

    assert isinstance(cache, RedisCache)
