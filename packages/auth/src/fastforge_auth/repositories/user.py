"""User repository."""

from fastforge_database.repositories.base import BaseRepository

from fastforge_auth.models.user import User


class UserRepository(BaseRepository[User]):
    """Persistence for User records.

    Owns database access only; permission checks and workflows belong in
    the service layer.
    """

    model = User
    allowed_sort_fields = {"created_at", "updated_at", "email"}

    async def get_by_email(self, email: str, *, include_deleted: bool = False) -> User | None:
        """Fetch a user by exact email match."""
        query = self._base_query(include_deleted=include_deleted).where(User.email == email)
        result = await self._session.execute(query)
        return result.scalar_one_or_none()
