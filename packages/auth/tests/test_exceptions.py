"""Tests for auth exceptions."""

from http import HTTPStatus

from fastforge_common.exceptions import ErrorCode

from fastforge_auth.exceptions import (
    InactiveUserError,
    InvalidCredentialsError,
    InvalidTokenError,
    UserAlreadyExistsError,
    UserNotFoundError,
)


def test_user_already_exists_error_maps_to_conflict() -> None:
    error = UserAlreadyExistsError()

    assert error.status_code == HTTPStatus.CONFLICT
    assert error.code == ErrorCode.CONFLICT
    assert error.message == "A user with this email already exists."


def test_user_not_found_error_maps_to_not_found() -> None:
    error = UserNotFoundError()

    assert error.status_code == HTTPStatus.NOT_FOUND
    assert error.code == ErrorCode.NOT_FOUND


def test_invalid_credentials_error_maps_to_authentication_error() -> None:
    error = InvalidCredentialsError()

    assert error.status_code == HTTPStatus.UNAUTHORIZED
    assert error.code == ErrorCode.AUTHENTICATION_ERROR


def test_inactive_user_error_maps_to_authentication_error() -> None:
    error = InactiveUserError()

    assert error.status_code == HTTPStatus.UNAUTHORIZED


def test_invalid_token_error_maps_to_authentication_error() -> None:
    error = InvalidTokenError()

    assert error.status_code == HTTPStatus.UNAUTHORIZED
