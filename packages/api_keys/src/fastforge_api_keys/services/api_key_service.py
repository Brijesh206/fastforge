"""API key service — issuance, listing, revocation, and request authentication."""

from datetime import UTC, datetime
from uuid import UUID

from fastforge_cache import Cache
from fastforge_common.exceptions import RateLimitError
from fastforge_common.tokens import generate_secret, hash_secret

from fastforge_api_keys.config import ApiKeySettings
from fastforge_api_keys.constants import API_KEY_PREFIX, DISPLAY_PREFIX_LENGTH
from fastforge_api_keys.exceptions import ApiKeyNotFoundError, InvalidApiKeyError
from fastforge_api_keys.models.api_key import ApiKey
from fastforge_api_keys.repositories.api_key import ApiKeyRepository


class ApiKeyService:
    """Owns API key business logic.

    Depends on the Cache interface for rate-limit counters, never on Redis
    directly, so the rate limiter works (in-process) even before Redis is
    configured.
    """

    def __init__(
        self,
        repository: ApiKeyRepository,
        cache: Cache,
        settings: ApiKeySettings,
    ) -> None:
        self._repository = repository
        self._cache = cache
        self._settings = settings

    async def create_key(self, user_id: UUID, name: str) -> tuple[ApiKey, str]:
        """Issue a new key for the user.

        Returns (row, raw_key). raw_key is shown to the caller exactly once —
        only its hash is persisted, so it cannot be recovered later.
        """
        raw_key = API_KEY_PREFIX + generate_secret()
        api_key = ApiKey(
            user_id=user_id,
            name=name,
            key_prefix=raw_key[:DISPLAY_PREFIX_LENGTH],
            key_hash=hash_secret(raw_key),
        )
        created = await self._repository.create(api_key)
        return created, raw_key

    async def list_keys(self, user_id: UUID) -> list[ApiKey]:
        """Return all of the user's keys, newest first. Never includes raw values."""
        return await self._repository.list_for_user(user_id)

    async def revoke_key(self, user_id: UUID, key_id: UUID) -> None:
        """Revoke a key. Raises ApiKeyNotFoundError if it isn't the user's."""
        key = await self._repository.get_by_id(key_id)
        if key is None or key.user_id != user_id:
            raise ApiKeyNotFoundError()
        key.revoked_at = datetime.now(UTC)
        await self._repository.update(key)

    async def authenticate(self, raw_key: str) -> UUID:
        """Verify a raw key, enforce its rate limit, and record usage.

        Raises InvalidApiKeyError if the key is malformed, unknown, or
        revoked. Raises RateLimitError (with retry_after_seconds) if the
        key's request rate limit is exceeded. Returns the owning user's id.
        """
        if not raw_key.startswith(API_KEY_PREFIX):
            raise InvalidApiKeyError()

        api_key = await self._repository.get_by_hash(hash_secret(raw_key))
        if api_key is None or api_key.is_revoked:
            raise InvalidApiKeyError()

        await self._enforce_rate_limit(api_key.id)

        api_key.last_used_at = datetime.now(UTC)
        await self._repository.update(api_key)
        return api_key.user_id

    async def _enforce_rate_limit(self, api_key_id: UUID) -> None:
        window = self._settings.rate_limit_window_seconds
        count = await self._cache.incr(f"apikey_rate_limit:{api_key_id}", ttl_seconds=window)
        if count > self._settings.rate_limit_per_minute:
            raise RateLimitError(
                f"Rate limit of {self._settings.rate_limit_per_minute} requests "
                f"per {window}s exceeded for this API key.",
                retry_after_seconds=window,
            )
