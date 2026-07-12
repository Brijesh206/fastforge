"""Tests for AuthService registration and authentication workflows."""

from uuid import UUID, uuid4

import pytest

from fastforge_auth.exceptions import (
    InactiveUserError,
    InvalidCredentialsError,
    UserAlreadyExistsError,
)
from fastforge_auth.interfaces.password_hasher import PasswordHasher
from fastforge_auth.interfaces.token_service import TokenService
from fastforge_auth.models.user import User
from fastforge_auth.schemas.auth import LoginRequest, TokenPair
from fastforge_auth.schemas.user import UserCreate
from fastforge_auth.services.auth_service import AuthService


class FakeUserRepository:
    """In-memory stand-in for UserRepository, used to unit test AuthService
    without a real database session."""

    def __init__(self) -> None:
        self.users_by_email: dict[str, User] = {}
        self.users_by_id: dict[UUID, User] = {}

    async def get_by_email(self, email: str, *, include_deleted: bool = False) -> User | None:
        return self.users_by_email.get(email)

    async def get_by_id(self, record_id: UUID, *, include_deleted: bool = False) -> User | None:
        return self.users_by_id.get(record_id)

    async def create(self, instance: User) -> User:
        instance.id = uuid4()
        self.users_by_email[instance.email] = instance
        self.users_by_id[instance.id] = instance
        return instance

    async def update(self, instance: User) -> User:
        self.users_by_email[instance.email] = instance
        self.users_by_id[instance.id] = instance
        return instance


class FakePasswordHasher(PasswordHasher):
    """Deterministic hasher for tests — never use outside tests."""

    def hash(self, password: str) -> str:
        return f"hashed:{password}"

    def verify(self, password: str, password_hash: str) -> bool:
        return password_hash == f"hashed:{password}"


class FakeTokenService(TokenService):
    """Deterministic token service for tests."""

    def issue_token_pair(self, user_id: UUID) -> TokenPair:
        return TokenPair(access_token=f"access:{user_id}", refresh_token=f"refresh:{user_id}")

    def decode_access_token(self, token: str) -> UUID:
        return UUID(token.removeprefix("access:"))

    def decode_refresh_token(self, token: str) -> UUID:
        return UUID(token.removeprefix("refresh:"))


def _service() -> tuple[AuthService, FakeUserRepository]:
    repository = FakeUserRepository()
    service = AuthService(repository, FakePasswordHasher(), FakeTokenService())
    return service, repository


async def test_register_user_creates_user_with_hashed_password() -> None:
    service, repository = _service()

    user = await service.register_user(UserCreate(email="new@example.com", password="a-strong-pass"))

    assert user.email == "new@example.com"
    assert user.password_hash == "hashed:a-strong-pass"
    assert repository.users_by_email["new@example.com"] is user


async def test_register_user_raises_when_email_already_exists() -> None:
    service, repository = _service()
    repository.users_by_email["taken@example.com"] = User(
        email="taken@example.com", password_hash="hashed:existing"
    )

    with pytest.raises(UserAlreadyExistsError):
        await service.register_user(UserCreate(email="taken@example.com", password="a-strong-pass"))


async def test_authenticate_user_returns_token_pair_for_valid_credentials() -> None:
    service, repository = _service()
    existing = User(email="user@example.com", password_hash="hashed:a-strong-pass", is_active=True)
    existing.id = uuid4()
    repository.users_by_email["user@example.com"] = existing

    tokens = await service.authenticate_user(
        LoginRequest(email="user@example.com", password="a-strong-pass")
    )

    assert tokens.access_token == f"access:{existing.id}"


async def test_authenticate_user_raises_for_unknown_email() -> None:
    service, _ = _service()

    with pytest.raises(InvalidCredentialsError):
        await service.authenticate_user(LoginRequest(email="ghost@example.com", password="whatever"))


async def test_authenticate_user_raises_for_wrong_password() -> None:
    service, repository = _service()
    existing = User(email="user@example.com", password_hash="hashed:a-strong-pass", is_active=True)
    existing.id = uuid4()
    repository.users_by_email["user@example.com"] = existing

    with pytest.raises(InvalidCredentialsError):
        await service.authenticate_user(LoginRequest(email="user@example.com", password="wrong"))


async def test_authenticate_user_raises_for_inactive_user() -> None:
    service, repository = _service()
    existing = User(email="user@example.com", password_hash="hashed:a-strong-pass", is_active=False)
    existing.id = uuid4()
    repository.users_by_email["user@example.com"] = existing

    with pytest.raises(InactiveUserError):
        await service.authenticate_user(LoginRequest(email="user@example.com", password="a-strong-pass"))


def _add_user(repository: FakeUserRepository, *, is_active: bool = True) -> User:
    user = User(email="user@example.com", password_hash="hashed:a-strong-pass", is_active=is_active)
    user.id = uuid4()
    repository.users_by_email[user.email] = user
    repository.users_by_id[user.id] = user
    return user


async def test_refresh_tokens_returns_new_pair_for_valid_token() -> None:
    service, repository = _service()
    user = _add_user(repository)

    pair = await service.refresh_tokens(f"refresh:{user.id}")

    assert pair.access_token == f"access:{user.id}"
    assert pair.refresh_token == f"refresh:{user.id}"


async def test_refresh_tokens_raises_when_user_missing() -> None:
    service, _ = _service()

    with pytest.raises(InvalidCredentialsError):
        await service.refresh_tokens(f"refresh:{uuid4()}")


async def test_refresh_tokens_raises_for_inactive_user() -> None:
    service, repository = _service()
    user = _add_user(repository, is_active=False)

    with pytest.raises(InactiveUserError):
        await service.refresh_tokens(f"refresh:{user.id}")
