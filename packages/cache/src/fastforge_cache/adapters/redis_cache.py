"""Redis cache adapter.

The only module in the platform that imports the redis client. Everything
above the Cache interface stays backend-agnostic.
"""

from typing import cast

from redis.asyncio import Redis, from_url

from fastforge_cache.interfaces.cache import Cache


class RedisCache(Cache):
    """Cache backed by a single shared Redis connection pool."""

    def __init__(self, redis_url: str) -> None:
        # from_url lacks type hints in the redis client.
        self._client: Redis = from_url(redis_url, decode_responses=True)  # type: ignore[no-untyped-call]

    async def get(self, key: str) -> str | None:
        return cast(str | None, await self._client.get(key))

    async def set(self, key: str, value: str, *, ttl_seconds: int | None = None) -> None:
        await self._client.set(key, value, ex=ttl_seconds)

    async def delete(self, key: str) -> None:
        await self._client.delete(key)

    async def incr(self, key: str, *, ttl_seconds: int | None = None) -> int:
        value: int = await self._client.incr(key)
        # ponytail: INCR then EXPIRE is two round trips, not one atomic op — a
        # crash in between leaves the key without a TTL (harmless: it just
        # never expires until overwritten). A Lua script would close that gap;
        # upgrade to one only if unbounded-key leakage is ever actually seen.
        if value == 1 and ttl_seconds is not None:
            await self._client.expire(key, ttl_seconds)
        return value

    async def close(self) -> None:
        """Close the underlying connection pool. Call once at app shutdown."""
        await self._client.aclose()
