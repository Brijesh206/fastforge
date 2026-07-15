"""Tests for AuthService registration and authentication workflows.

Shared in-memory fakes live in conftest.py and are injected via the
``auth_service`` / ``fake_users`` fixtures.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import uuid4

import pytest
from fastforge_auth.exceptions import (
    InactiveUserError,
    InvalidCredentialsError,
    UserAlreadyExistsError,
)
from fastforge_auth.models.user import User
from fastforge_auth.schemas.auth import LoginRequest
from fastforge_auth.schemas.user import UserCreate
from fastforge_auth.services.auth_service import AuthService

if TYPE_CHECKING:
    from conftest import FakeUserRepository


async def test_register_user_creates_user_with_hashed_password(
    auth_service: AuthService, fake_users: FakeUserRepository
) -> None:
    user = await auth_service.register_user(
        UserCreate(email="new@example.com", password="a-strong-pass")
    )

    assert user.email == "new@example.com"
    assert user.password_hash == "hashed:a-strong-pass"
    assert fake_users.users_by_email["new@example.com"] is user


async def test_register_user_raises_when_email_already_exists(
    auth_service: AuthService, fake_users: FakeUserRepository
) -> None:
    fake_users.users_by_email["taken@example.com"] = User(
        email="taken@example.com", password_hash="hashed:existing"
    )

    with pytest.raises(UserAlreadyExistsError):
        await auth_service.register_user(
            UserCreate(email="taken@example.com", password="a-strong-pass")
        )


async def test_authenticate_user_returns_token_pair_for_valid_credentials(
    auth_service: AuthService, fake_users: FakeUserRepository
) -> None:
    existing = User(email="user@example.com", password_hash="hashed:a-strong-pass", is_active=True)
    existing.id = uuid4()
    fake_users.users_by_email["user@example.com"] = existing

    tokens = await auth_service.authenticate_user(
        LoginRequest(email="user@example.com", password="a-strong-pass")
    )

    assert tokens.access_token == f"access:{existing.id}"


async def test_authenticate_user_raises_for_unknown_email(auth_service: AuthService) -> None:
    with pytest.raises(InvalidCredentialsError):
        await auth_service.authenticate_user(
            LoginRequest(email="ghost@example.com", password="whatever")
        )


async def test_authenticate_user_raises_for_wrong_password(
    auth_service: AuthService, fake_users: FakeUserRepository
) -> None:
    existing = User(email="user@example.com", password_hash="hashed:a-strong-pass", is_active=True)
    existing.id = uuid4()
    fake_users.users_by_email["user@example.com"] = existing

    with pytest.raises(InvalidCredentialsError):
        await auth_service.authenticate_user(
            LoginRequest(email="user@example.com", password="wrong")
        )


async def test_authenticate_user_raises_for_inactive_user(
    auth_service: AuthService, fake_users: FakeUserRepository
) -> None:
    existing = User(email="user@example.com", password_hash="hashed:a-strong-pass", is_active=False)
    existing.id = uuid4()
    fake_users.users_by_email["user@example.com"] = existing

    with pytest.raises(InactiveUserError):
        await auth_service.authenticate_user(
            LoginRequest(email="user@example.com", password="a-strong-pass")
        )


def _add_user(fake_users: FakeUserRepository, *, is_active: bool = True) -> User:
    user = User(email="user@example.com", password_hash="hashed:a-strong-pass", is_active=is_active)
    user.id = uuid4()
    fake_users.users_by_email[user.email] = user
    fake_users.users_by_id[user.id] = user
    return user


async def test_refresh_tokens_returns_new_pair_for_valid_token(
    auth_service: AuthService, fake_users: FakeUserRepository
) -> None:
    user = _add_user(fake_users)

    pair = await auth_service.refresh_tokens(f"refresh:{user.id}")

    assert pair.access_token == f"access:{user.id}"
    assert pair.refresh_token == f"refresh:{user.id}"


async def test_refresh_tokens_raises_when_user_missing(auth_service: AuthService) -> None:
    with pytest.raises(InvalidCredentialsError):
        await auth_service.refresh_tokens(f"refresh:{uuid4()}")


async def test_refresh_tokens_raises_for_inactive_user(
    auth_service: AuthService, fake_users: FakeUserRepository
) -> None:
    user = _add_user(fake_users, is_active=False)

    with pytest.raises(InactiveUserError):
        await auth_service.refresh_tokens(f"refresh:{user.id}")
