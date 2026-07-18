"""API key repository."""

from uuid import UUID

from fastforge_database.repositories.base import BaseRepository

from fastforge_api_keys.models.api_key import ApiKey


class ApiKeyRepository(BaseRepository[ApiKey]):
    """Persistence for ApiKey records. Owns database access only."""

    model = ApiKey

    async def get_by_hash(self, key_hash: str) -> ApiKey | None:
        """Fetch a key by its hash — the verification path for an incoming request."""
        query = self._base_query().where(ApiKey.key_hash == key_hash)
        result = await self._session.execute(query)
        return result.scalar_one_or_none()

    async def list_for_user(self, user_id: UUID) -> list[ApiKey]:
        """Return all keys belonging to a user, newest first."""
        query = (
            self._base_query()
            .where(ApiKey.user_id == user_id)
            .order_by(ApiKey.created_at.desc())
        )
        result = await self._session.execute(query)
        return list(result.scalars().all())
