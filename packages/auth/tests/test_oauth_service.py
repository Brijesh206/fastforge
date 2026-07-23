"""Tests for AuthService.login_or_register_oauth_user.

Shared in-memory fakes live in conftest.py and are injected via the
``auth_service`` / ``fake_users`` fixtures.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from fastforge_auth.exceptions import InactiveUserError
from fastforge_auth.interfaces.oauth_provider import OAuthUserInfo
from fastforge_auth.models.user import User

if TYPE_CHECKING:
    from conftest import FakeUserRepository
    from fastforge_auth.services.auth_service import AuthService


async def test_creates_a_new_verified_user_without_a_password(
    auth_service: AuthService, fake_users: FakeUserRepository
) -> None:
    info = OAuthUserInfo(email="ada@example.com", full_name="Ada", avatar_url="https://img")

    tokens = await auth_service.login_or_register_oauth_user(info)

    user = fake_users.users_by_email["ada@example.com"]
    assert user.password_hash is None
    assert user.is_verified is True
    assert user.full_name == "Ada"
    assert user.avatar_url == "https://img"
    assert user.last_login_at is not None
    assert tokens.access_token == f"access:{user.id}:0"


async def test_links_an_existing_account_by_email_instead_of_duplicating_it(
    auth_service: AuthService, fake_users: FakeUserRepository
) -> None:
    existing = await fake_users.create(
        User(email="ada@example.com", password_hash="hashed:secret", is_verified=True)
    )

    info = OAuthUserInfo(email="ada@example.com", full_name="Ada", avatar_url=None)
    tokens = await auth_service.login_or_register_oauth_user(info)

    assert tokens.access_token == f"access:{existing.id}:0"
    assert len(fake_users.users_by_email) == 1


async def test_marks_an_unverified_existing_account_verified(
    auth_service: AuthService, fake_users: FakeUserRepository
) -> None:
    await fake_users.create(User(email="ada@example.com", password_hash="hashed:secret"))

    info = OAuthUserInfo(email="ada@example.com", full_name=None, avatar_url=None)
    await auth_service.login_or_register_oauth_user(info)

    assert fake_users.users_by_email["ada@example.com"].is_verified is True


async def test_raises_for_an_inactive_account(
    auth_service: AuthService, fake_users: FakeUserRepository
) -> None:
    await fake_users.create(User(email="ada@example.com", is_verified=True, is_active=False))
    info = OAuthUserInfo(email="ada@example.com", full_name=None, avatar_url=None)

    with pytest.raises(InactiveUserError):
        await auth_service.login_or_register_oauth_user(info)
