"""Database session management."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from fastforge_database.config import DatabaseSettings


class DatabaseManager:
    """Manages async database engine and session factory."""

    def __init__(self, settings: DatabaseSettings) -> None:
        self._settings = settings
        self._engine: AsyncEngine = create_async_engine(
            settings.async_url,
            echo=settings.echo,
            pool_size=settings.pool_size,
            max_overflow=settings.max_overflow,
            pool_timeout=settings.pool_timeout,
            pool_pre_ping=True,
            connect_args=settings.connect_args,
        )
        self._session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(
            bind=self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
            autocommit=False,
        )

    @property
    def engine(self) -> AsyncEngine:
        """Return the async SQLAlchemy engine."""
        return self._engine

    @property
    def session_factory(self) -> async_sessionmaker[AsyncSession]:
        """Return the async session factory."""
        return self._session_factory

    async def close(self) -> None:
        """Dispose of the database engine and connection pool."""
        await self._engine.dispose()

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession]:
        """Provide a database session without auto-commit.

        Services are responsible for committing or rolling back transactions.
        """
        async with self._session_factory() as db_session:
            try:
                yield db_session
            except Exception:
                await db_session.rollback()
                raise

    @asynccontextmanager
    async def transaction(self) -> AsyncGenerator[AsyncSession]:
        """Provide a database session with automatic commit on success."""
        async with self._session_factory() as db_session:
            try:
                yield db_session
                await db_session.commit()
            except Exception:
                await db_session.rollback()
                raise


async def get_session(
    manager: DatabaseManager,
) -> AsyncGenerator[AsyncSession]:
    """FastAPI dependency that yields a database session.

    The session is not auto-committed. Services must commit explicitly.
    """
    async with manager.session() as db_session:
        yield db_session
