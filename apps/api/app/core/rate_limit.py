"""Fixed-window, per-IP rate limiting for unauthenticated endpoints.

Backed by the platform Cache (Redis in production, in-memory in dev), the same
counter primitive the API-key limiter uses. Keyed by client IP: behind a
reverse proxy, run uvicorn with ``--proxy-headers`` (and a trusted proxy) so
``request.client.host`` is the real client, not the proxy.

ponytail: fixed window, not sliding — a burst can straddle two windows and
briefly double the limit. Upgrade to a sliding window only if that ever
matters for abuse seen in practice.
"""

from collections.abc import Awaitable, Callable

from fastapi import Request
from fastforge_common.exceptions import RateLimitError


def rate_limit(
    name: str, *, limit: int, window_seconds: int
) -> Callable[[Request], Awaitable[None]]:
    """Return a FastAPI dependency enforcing ``limit`` requests per window per IP."""

    async def dependency(request: Request) -> None:
        client_ip = request.client.host if request.client is not None else "unknown"
        count = await request.app.state.cache.incr(
            f"rate_limit:{name}:{client_ip}", ttl_seconds=window_seconds
        )
        if count > limit:
            raise RateLimitError(retry_after_seconds=window_seconds)

    return dependency
