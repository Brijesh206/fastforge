"""Database dependencies."""

from collections.abc import AsyncGenerator
from typing import cast

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from fastforge_database import DatabaseManager


def get_database_manager(request: Request) -> DatabaseManager:
    """Return the application database manager."""
    return cast(DatabaseManager, request.app.state.database_manager)


async def get_db_session(request: Request) -> AsyncGenerator[AsyncSession, None]:
    """Yield a read-scoped database session (no automatic commit)."""
    manager = get_database_manager(request)
    async with manager.session() as session:
        yield session


async def get_db_transaction(request: Request) -> AsyncGenerator[AsyncSession, None]:
    """Yield a transactional session that commits on success, rolls back on error.

    Use this for endpoints that write to the database. Services still own the
    business logic; this dependency owns the transaction boundary.
    """
    manager = get_database_manager(request)
    async with manager.transaction() as session:
        yield session
