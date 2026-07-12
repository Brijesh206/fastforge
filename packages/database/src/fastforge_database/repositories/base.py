"""Base repository for database access."""

from uuid import UUID

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.interfaces import ORMOption

from fastforge_database.models.base import BaseModel, SoftDeleteMixin
from fastforge_database.utils.pagination import PaginatedResult, PaginationParams
from fastforge_database.utils.sorting import SortParams


class BaseRepository[ModelT: BaseModel]:
    """Generic repository providing CRUD, pagination, and soft delete operations.

    Repositories own persistence only. They must not contain business logic,
    permission checks, or commit/rollback transactions.
    """

    model: type[ModelT]
    allowed_sort_fields: set[str] = {"created_at", "updated_at"}

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _base_query(self, *, include_deleted: bool = False) -> Select[tuple[ModelT]]:
        """Build the base select query, excluding soft-deleted records by default."""
        query = select(self.model)
        if not include_deleted and issubclass(self.model, SoftDeleteMixin):
            query = query.where(self.model.deleted_at.is_(None))
        return query

    async def get_by_id(
        self,
        record_id: UUID,
        *,
        include_deleted: bool = False,
        options: list[ORMOption] | None = None,
    ) -> ModelT | None:
        """Fetch a single record by primary key."""
        query = self._base_query(include_deleted=include_deleted).where(
            self.model.id == record_id
        )
        if options:
            query = query.options(*options)
        result = await self._session.execute(query)
        return result.scalar_one_or_none()

    async def count(self, *, include_deleted: bool = False) -> int:
        """Return the total count of records."""
        query = select(func.count()).select_from(self.model)
        if not include_deleted and issubclass(self.model, SoftDeleteMixin):
            query = query.where(self.model.deleted_at.is_(None))
        result = await self._session.execute(query)
        return result.scalar_one()

    async def list_paginated(
        self,
        pagination: PaginationParams,
        *,
        sort: SortParams | None = None,
        include_deleted: bool = False,
        options: list[ORMOption] | None = None,
    ) -> PaginatedResult[ModelT]:
        """Return a paginated list of records with optional sorting."""
        if sort is not None:
            sort.validate_field(self.allowed_sort_fields)

        count_query = select(func.count()).select_from(self.model)
        if not include_deleted and issubclass(self.model, SoftDeleteMixin):
            count_query = count_query.where(self.model.deleted_at.is_(None))

        total_result = await self._session.execute(count_query)
        total = total_result.scalar_one()

        query = self._base_query(include_deleted=include_deleted)
        if sort is not None:
            column = getattr(self.model, sort.field)
            query = query.order_by(column.desc() if sort.is_descending else column.asc())
        else:
            query = query.order_by(self.model.created_at.desc())

        query = query.offset(pagination.offset).limit(pagination.limit)
        if options:
            query = query.options(*options)

        result = await self._session.execute(query)
        items = list(result.scalars().all())

        return PaginatedResult(
            items=items,
            total=total,
            page=pagination.page,
            page_size=pagination.page_size,
        )

    async def create(self, instance: ModelT) -> ModelT:
        """Add a new record to the session and flush to obtain generated values."""
        self._session.add(instance)
        await self._session.flush()
        await self._session.refresh(instance)
        return instance

    async def update(self, instance: ModelT) -> ModelT:
        """Merge changes for an existing record and flush."""
        instance.touch()
        merged = await self._session.merge(instance)
        await self._session.flush()
        await self._session.refresh(merged)
        return merged

    async def delete(self, instance: ModelT) -> None:
        """Hard delete a record from the database."""
        await self._session.delete(instance)
        await self._session.flush()

    async def soft_delete(self, instance: ModelT) -> ModelT:
        """Soft delete a record by setting deleted_at."""
        if not issubclass(self.model, SoftDeleteMixin):
            msg = f"{self.model.__name__} does not support soft delete"
            raise TypeError(msg)
        if isinstance(instance, SoftDeleteMixin):
            instance.soft_delete()
        instance.touch()
        await self._session.flush()
        await self._session.refresh(instance)
        return instance

    async def restore(self, instance: ModelT) -> ModelT:
        """Restore a soft-deleted record."""
        if not issubclass(self.model, SoftDeleteMixin):
            msg = f"{self.model.__name__} does not support soft delete"
            raise TypeError(msg)
        if isinstance(instance, SoftDeleteMixin):
            instance.deleted_at = None
        instance.touch()
        await self._session.flush()
        await self._session.refresh(instance)
        return instance
