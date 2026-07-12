"""Pagination utilities."""

from dataclasses import dataclass
from math import ceil

from pydantic import Field
from pydantic.dataclasses import dataclass as pydantic_dataclass


@pydantic_dataclass(frozen=True)
class PaginationParams:
    """Standard pagination parameters for list endpoints."""

    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)

    @property
    def offset(self) -> int:
        """Calculate the SQL offset from page and page_size."""
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        """Return the page size as SQL limit."""
        return self.page_size


@dataclass(frozen=True)
class PaginatedResult[T]:
    """Paginated query result with metadata."""

    items: list[T]
    total: int
    page: int
    page_size: int

    @property
    def total_pages(self) -> int:
        """Calculate total number of pages."""
        if self.page_size == 0:
            return 0
        return ceil(self.total / self.page_size)

    @property
    def has_next(self) -> bool:
        """Return True if there is a next page."""
        return self.page < self.total_pages

    @property
    def has_previous(self) -> bool:
        """Return True if there is a previous page."""
        return self.page > 1
