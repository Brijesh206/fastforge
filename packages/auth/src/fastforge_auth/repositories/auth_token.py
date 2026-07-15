"""Auth token repository."""

from datetime import datetime
from uuid import UUID

from fastforge_database.repositories.base import BaseRepository
from sqlalchemy import update

from fastforge_auth.enums import AuthTokenPurpose
from fastforge_auth.models.auth_token import AuthToken


class AuthTokenRepository(BaseRepository[AuthToken]):
    """Persistence for single-use auth tokens.

    Owns database access only. Expiry and single-use rules are enforced by
    the service, which reads ``expires_at``/``used_at`` from the returned row.
    """

    model = AuthToken

    async def get_by_hash(self, token_hash: str, purpose: AuthTokenPurpose) -> AuthToken | None:
        """Fetch a token by its stored hash and purpose, if one exists."""
        query = self._base_query().where(
            AuthToken.token_hash == token_hash,
            AuthToken.purpose == purpose.value,
        )
        result = await self._session.execute(query)
        return result.scalar_one_or_none()

    async def invalidate_unused(
        self, user_id: UUID, purpose: AuthTokenPurpose, *, now: datetime
    ) -> None:
        """Mark every unused token of this purpose for the user as used.

        Called before issuing a new token so a user never holds more than one
        live link — important for password reset.
        """
        await self._session.execute(
            update(AuthToken)
            .where(
                AuthToken.user_id == user_id,
                AuthToken.purpose == purpose.value,
                AuthToken.used_at.is_(None),
            )
            .values(used_at=now)
        )
