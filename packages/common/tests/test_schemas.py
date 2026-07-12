"""Tests for shared schemas."""

import pytest
from fastforge_common.schemas import ErrorDetail, ErrorResponse
from pydantic import ValidationError


def test_error_response_uses_standard_envelope() -> None:
    response = ErrorResponse(
        error=ErrorDetail(code="NOT_FOUND", message="The resource was not found.")
    )

    assert response.model_dump() == {
        "error": {
            "code": "NOT_FOUND",
            "message": "The resource was not found.",
            "details": None,
        }
    }


def test_error_detail_forbids_extra_fields() -> None:
    with pytest.raises(ValidationError):
        ErrorDetail(code="BAD", message="Bad request.", extra="ignored")
