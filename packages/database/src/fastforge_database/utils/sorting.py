"""Sorting utilities."""

from enum import StrEnum

from pydantic import Field
from pydantic.dataclasses import dataclass as pydantic_dataclass


class SortOrder(StrEnum):
    """Allowed sort directions."""

    ASC = "asc"
    DESC = "desc"


@pydantic_dataclass(frozen=True)
class SortParams:
    """Sorting parameters with a validated field name."""

    field: str
    order: SortOrder = SortOrder.ASC

    def validate_field(self, allowed_fields: set[str]) -> None:
        """Raise ValueError if the sort field is not allowed."""
        if self.field not in allowed_fields:
            msg = f"Invalid sort field: {self.field}. Allowed: {sorted(allowed_fields)}"
            raise ValueError(msg)

    @property
    def is_descending(self) -> bool:
        """Return True if sort order is descending."""
        return self.order == SortOrder.DESC
