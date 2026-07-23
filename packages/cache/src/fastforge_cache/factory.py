"""Cache provider selection."""

from fastforge_cache.adapters.in_memory_cache import InMemoryCache
from fastforge_cache.adapters.redis_cache import RedisCache
from fastforge_cache.config import CacheSettings
from fastforge_cache.interfaces.cache import Cache


def create_cache(settings: CacheSettings) -> Cache:
    """Build the cache backend named by configuration."""
    if settings.provider == "redis":
        return RedisCache(settings.redis_url)
    return InMemoryCache()
