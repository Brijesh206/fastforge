"""Tests for email verification and password reset in AuthService.

Shared in-memory fakes live in conftest.py and are injected via the
``auth_service`` / ``fake_users`` / ``fake_tokens`` fixtures.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING
from uuid import uuid4

import pytest
from fastforge_auth.exceptions import InvalidCredentialsError, InvalidTokenError, UserNotFoundError
from fastforge_auth.models.user import User
from fastforge_auth.tokens import hash_token

if TYPE_CHECKING:
    from conftest import FakeAuthTokenRepository, FakeUserRepository
    from fastforge_auth.services.auth_service import AuthService


def _add_user(fake_users: FakeUserRepository, *, is_verified: bool = False) -> User:
    user = User(
        email="user@example.com",
        password_hash="hashed:old",
        is_active=True,
        is_verified=is_verified,
    )
    user.id = uuid4()
    fake_users.users_by_email[user.email] = user
    fake_users.users_by_id[user.id] = user
    return user


async def test_issue_and_verify_email_marks_user_verified(
    auth_service: AuthService, fake_users: FakeUserRepository
) -> None:
    user = _add_user(fake_users)

    raw_token = await auth_service.issue_email_verification_token(user)
    verified = await auth_service.verify_email(raw_token)

    assert verified.is_verified is True


async def test_verification_token_is_stored_only_as_a_hash(
    auth_service: AuthService, fake_users: FakeUserRepository, fake_tokens: FakeAuthTokenRepository
) -> None:
    user = _add_user(fake_users)

    raw_token = await auth_service.issue_email_verification_token(user)

    stored = fake_tokens.tokens[0].token_hash
    assert stored != raw_token
    assert stored == hash_token(raw_token)


async def test_verification_token_is_single_use(
    auth_service: AuthService, fake_users: FakeUserRepository
) -> None:
    user = _add_user(fake_users)

    raw_token = await auth_service.issue_email_verification_token(user)
    await auth_service.verify_email(raw_token)

    with pytest.raises(InvalidTokenError):
        await auth_service.verify_email(raw_token)


async def test_issuing_a_new_token_invalidates_the_previous_one(
    auth_service: AuthService, fake_users: FakeUserRepository
) -> None:
    user = _add_user(fake_users)

    first = await auth_service.issue_email_verification_token(user)
    await auth_service.issue_email_verification_token(user)

    with pytest.raises(InvalidTokenError):
        await auth_service.verify_email(first)


async def test_verify_email_rejects_unknown_token(auth_service: AuthService) -> None:
    with pytest.raises(InvalidTokenError):
        await auth_service.verify_email("not-a-real-token")


async def test_verify_email_rejects_expired_token(
    auth_service: AuthService, fake_users: FakeUserRepository, fake_tokens: FakeAuthTokenRepository
) -> None:
    user = _add_user(fake_users)

    raw_token = await auth_service.issue_email_verification_token(user)
    fake_tokens.tokens[0].expires_at = datetime.now(UTC) - timedelta(seconds=1)

    with pytest.raises(InvalidTokenError):
        await auth_service.verify_email(raw_token)


async def test_password_reset_updates_the_hash(
    auth_service: AuthService, fake_users: FakeUserRepository
) -> None:
    user = _add_user(fake_users)

    result = await auth_service.issue_password_reset_token(user.email)
    assert result is not None
    _, raw_token = result

    updated = await auth_service.reset_password(raw_token, "a-brand-new-pass")

    assert updated.password_hash == "hashed:a-brand-new-pass"


async def test_password_reset_token_is_single_use(
    auth_service: AuthService, fake_users: FakeUserRepository
) -> None:
    user = _add_user(fake_users)

    result = await auth_service.issue_password_reset_token(user.email)
    assert result is not None
    _, raw_token = result
    await auth_service.reset_password(raw_token, "a-brand-new-pass")

    with pytest.raises(InvalidTokenError):
        await auth_service.reset_password(raw_token, "another-new-pass")


async def test_issue_password_reset_returns_none_for_unknown_email(
    auth_service: AuthService,
) -> None:
    assert await auth_service.issue_password_reset_token("ghost@example.com") is None


async def test_issue_password_reset_returns_none_for_inactive_user(
    auth_service: AuthService, fake_users: FakeUserRepository
) -> None:
    user = _add_user(fake_users)
    user.is_active = False

    assert await auth_service.issue_password_reset_token(user.email) is None


def test_verify_current_password_accepts_correct_password(
    auth_service: AuthService, fake_users: FakeUserRepository
) -> None:
    user = _add_user(fake_users)  # password_hash="hashed:old"

    auth_service.verify_current_password(user, "old")  # does not raise


def test_verify_current_password_rejects_wrong_password(
    auth_service: AuthService, fake_users: FakeUserRepository
) -> None:
    user = _add_user(fake_users)

    with pytest.raises(InvalidCredentialsError):
        auth_service.verify_current_password(user, "wrong")


def test_verify_current_password_is_noop_without_a_password_hash(
    auth_service: AuthService,
) -> None:
    user = User(email="oauth@example.com", password_hash=None)

    auth_service.verify_current_password(user, "anything")  # does not raise


async def test_delete_account_removes_the_user(
    auth_service: AuthService, fake_users: FakeUserRepository
) -> None:
    user = _add_user(fake_users)

    await auth_service.delete_account(user.id)

    assert await fake_users.get_by_id(user.id) is None
    assert await fake_users.get_by_email(user.email) is None


async def test_delete_account_raises_for_unknown_user(auth_service: AuthService) -> None:
    with pytest.raises(UserNotFoundError):
        await auth_service.delete_account(uuid4())
