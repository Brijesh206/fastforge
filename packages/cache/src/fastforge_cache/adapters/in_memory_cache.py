"""In-memory cache adapter — the default so a fresh checkout needs no Redis.

Process-local and non-persistent: fine for local dev and tests, wrong for
anything that must be shared across workers or survive a restart (real rate
limiting, real sessions). Switch to RedisCache for that.
"""

import asyncio
import time

from fastforge_cache.interfaces.cache import Cache


class InMemoryCache(Cache):
    """Dict-backed Cache. A single lock keeps incr atomic under concurrency."""

    def __init__(self) -> None:
        self._values: dict[str, str] = {}
        self._expires_at: dict[str, float] = {}
        self._lock = asyncio.Lock()

    def _is_expired(self, key: str) -> bool:
        expires_at = self._expires_at.get(key)
        return expires_at is not None and expires_at <= time.monotonic()

    def _evict_if_expired(self, key: str) -> None:
        if self._is_expired(key):
            self._values.pop(key, None)
            self._expires_at.pop(key, None)

    async def get(self, key: str) -> str | None:
        async with self._lock:
            self._evict_if_expired(key)
            return self._values.get(key)

    async def set(self, key: str, value: str, *, ttl_seconds: int | None = None) -> None:
        async with self._lock:
            self._values[key] = value
            if ttl_seconds is not None:
                self._expires_at[key] = time.monotonic() + ttl_seconds
            else:
                self._expires_at.pop(key, None)

    async def delete(self, key: str) -> None:
        async with self._lock:
            self._values.pop(key, None)
            self._expires_at.pop(key, None)

    async def incr(self, key: str, *, ttl_seconds: int | None = None) -> int:
        async with self._lock:
            self._evict_if_expired(key)
            new_value = int(self._values.get(key, "0")) + 1
            self._values[key] = str(new_value)
            if new_value == 1 and ttl_seconds is not None:
                self._expires_at[key] = time.monotonic() + ttl_seconds
            return new_value

    async def close(self) -> None:
        """No resources to release — kept for interface parity with RedisCache."""
