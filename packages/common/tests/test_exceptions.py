"""Tests for shared application exceptions."""

from http import HTTPStatus

from fastforge_common.exceptions import ErrorCode, NotFoundError


def test_app_error_converts_to_error_response() -> None:
    error = NotFoundError("Project not found.", details={"resource": "project"})
    response = error.to_response()

    assert error.status_code == HTTPStatus.NOT_FOUND
    assert response.error.code == ErrorCode.NOT_FOUND
    assert response.error.message == "Project not found."
    assert response.error.details == {"resource": "project"}
