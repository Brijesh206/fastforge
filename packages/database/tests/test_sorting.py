"""Tests for sorting utilities."""

import pytest
from fastforge_database.utils.sorting import SortOrder, SortParams


def test_sort_params_validate_allowed_field() -> None:
    sort = SortParams(field="created_at", order=SortOrder.DESC)

    sort.validate_field({"created_at", "updated_at"})

    assert sort.is_descending is True


def test_sort_params_reject_unknown_field() -> None:
    sort = SortParams(field="email")

    with pytest.raises(ValueError, match="Invalid sort field"):
        sort.validate_field({"created_at", "updated_at"})
