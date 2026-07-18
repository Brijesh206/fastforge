"""Cache foundation for FastForge — sessions, rate limiting, OTPs, caching."""

from fastforge_cache.adapters.in_memory_cache import InMemoryCache
from fastforge_cache.adapters.redis_cache import RedisCache
from fastforge_cache.config import CacheSettings
from fastforge_cache.factory import create_cache
from fastforge_cache.interfaces.cache import Cache

__all__ = [
    "Cache",
    "CacheSettings",
    "InMemoryCache",
    "RedisCache",
    "create_cache",
]
