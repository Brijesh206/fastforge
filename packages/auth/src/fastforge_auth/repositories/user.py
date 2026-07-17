"""User repository."""

from fastforge_database.repositories.base import BaseRepository
from fastforge_database.utils.pagination import PaginatedResult, PaginationParams
from sqlalchemy import func, select

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

    async def search_paginated(
        self, pagination: PaginationParams, *, email_query: str | None = None
    ) -> PaginatedResult[User]:
        """Paginated users, newest first, optionally filtered by an email substring."""
        query = self._base_query()
        if email_query and email_query.strip():
            query = query.where(User.email.ilike(f"%{email_query.strip()}%"))

        count = select(func.count()).select_from(query.subquery())
        total = (await self._session.execute(count)).scalar_one()

        page = query.order_by(User.created_at.desc()).offset(pagination.offset).limit(
            pagination.limit
        )
        items = list((await self._session.execute(page)).scalars().all())
        return PaginatedResult(
            items=items,
            total=total,
            page=pagination.page,
            page_size=pagination.page_size,
        )
