"""Cache interface."""

from abc import ABC, abstractmethod


class Cache(ABC):
    """A key-value store with expiry, for sessions, rate limiting, and OTPs.

    Services depend on this interface only. Swapping Redis for another
    backend must not require a change above this line.
    """

    @abstractmethod
    async def get(self, key: str) -> str | None:
        """Return the value for key, or None if it doesn't exist or has expired."""

    @abstractmethod
    async def set(self, key: str, value: str, *, ttl_seconds: int | None = None) -> None:
        """Store value under key, expiring after ttl_seconds if given."""

    @abstractmethod
    async def delete(self, key: str) -> None:
        """Remove key. A no-op if it doesn't exist."""

    @abstractmethod
    async def incr(self, key: str, *, ttl_seconds: int | None = None) -> int:
        """Atomically increment key by 1 and return the new value.

        Starts at 0 if the key doesn't exist. If ttl_seconds is given, it is
        applied only on the increment that creates the key (result == 1) —
        later calls extend neither the value's life nor reset it. This makes
        incr safe to use directly as a fixed-window rate-limit counter:
        ``count = await cache.incr(f"rl:{key}", ttl_seconds=60)``.
        """

    @abstractmethod
    async def close(self) -> None:
        """Release any held resources (connections, pools). Call at shutdown."""
