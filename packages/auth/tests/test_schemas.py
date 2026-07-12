"""Tests for auth schemas."""

import pytest
from fastforge_auth.schemas.auth import LoginRequest, TokenPair
from fastforge_auth.schemas.user import UserCreate
from pydantic import ValidationError


def test_user_create_normalizes_email() -> None:
    user = UserCreate(email="  User@Example.com  ", password="a-very-strong-pass")

    assert user.email == "user@example.com"


def test_user_create_rejects_short_password() -> None:
    with pytest.raises(ValidationError):
        UserCreate(email="user@example.com", password="short")


def test_user_create_rejects_extra_fields() -> None:
    with pytest.raises(ValidationError):
        UserCreate(
            email="user@example.com",
            password="a-very-strong-pass",
            is_admin=True,
        )


def test_login_request_normalizes_email() -> None:
    login = LoginRequest(email="User@Example.com", password="anything")

    assert login.email == "user@example.com"


def test_token_pair_defaults_to_bearer_type() -> None:
    tokens = TokenPair(access_token="access", refresh_token="refresh")

    assert tokens.token_type == "bearer"
