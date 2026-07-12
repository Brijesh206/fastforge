"""Tests for pagination utilities."""

import pytest
from fastforge_database.utils.pagination import PaginatedResult, PaginationParams
from pydantic import ValidationError


def test_pagination_params_calculate_offset_and_limit() -> None:
    pagination = PaginationParams(page=3, page_size=25)

    assert pagination.offset == 50
    assert pagination.limit == 25


def test_pagination_params_validate_bounds() -> None:
    with pytest.raises(ValidationError):
        PaginationParams(page=0)

    with pytest.raises(ValidationError):
        PaginationParams(page_size=101)


def test_paginated_result_metadata() -> None:
    result = PaginatedResult(items=["first", "second"], total=42, page=2, page_size=20)

    assert result.total_pages == 3
    assert result.has_next is True
    assert result.has_previous is True
