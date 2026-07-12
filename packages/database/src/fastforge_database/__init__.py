"""Database foundation for FastForge."""

from fastforge_database.config import DatabaseSettings
from fastforge_database.models.base import (
    AuditMixin,
    Base,
    BaseModel,
    SoftDeleteMixin,
    TimestampMixin,
)
from fastforge_database.repositories.base import BaseRepository
from fastforge_database.session import DatabaseManager, get_session
from fastforge_database.utils.pagination import PaginatedResult, PaginationParams
from fastforge_database.utils.sorting import SortOrder, SortParams
from fastforge_database.utils.uuid import generate_uuid7

__all__ = [
    "AuditMixin",
    "Base",
    "BaseModel",
    "BaseRepository",
    "DatabaseManager",
    "DatabaseSettings",
    "PaginatedResult",
    "PaginationParams",
    "SoftDeleteMixin",
    "SortOrder",
    "SortParams",
    "TimestampMixin",
    "generate_uuid7",
    "get_session",
]
