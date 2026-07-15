"""Shared in-memory fakes for AuthService unit tests.

Placed in conftest so every test module can import them without depending on
another test module's import name (which is unstable under importlib mode).
"""

from datetime import datetime
from uuid import UUID, uuid4

import pytest
from fastforge_auth.enums import AuthTokenPurpose
from fastforge_auth.interfaces.password_hasher import PasswordHasher
from fastforge_auth.interfaces.token_service import TokenService
from fastforge_auth.models.auth_token import AuthToken
from fastforge_auth.models.user import User
from fastforge_auth.schemas.auth import TokenPair
from fastforge_auth.services.auth_service import AuthService


class FakeUserRepository:
    """In-memory stand-in for UserRepository."""

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


class FakeAuthTokenRepository:
    """In-memory stand-in for AuthTokenRepository."""

    def __init__(self) -> None:
        self.tokens: list[AuthToken] = []

    async def create(self, instance: AuthToken) -> AuthToken:
        instance.id = uuid4()
        self.tokens.append(instance)
        return instance

    async def update(self, instance: AuthToken) -> AuthToken:
        return instance

    async def get_by_hash(self, token_hash: str, purpose: AuthTokenPurpose) -> AuthToken | None:
        for token in self.tokens:
            if token.token_hash == token_hash and token.purpose == purpose.value:
                return token
        return None

    async def invalidate_unused(
        self, user_id: UUID, purpose: AuthTokenPurpose, *, now: datetime
    ) -> None:
        for token in self.tokens:
            if (
                token.user_id == user_id
                and token.purpose == purpose.value
                and token.used_at is None
            ):
                token.used_at = now


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


@pytest.fixture
def fake_users() -> FakeUserRepository:
    """A fresh in-memory user repository."""
    return FakeUserRepository()


@pytest.fixture
def fake_tokens() -> FakeAuthTokenRepository:
    """A fresh in-memory auth-token repository."""
    return FakeAuthTokenRepository()


@pytest.fixture
def auth_service(
    fake_users: FakeUserRepository, fake_tokens: FakeAuthTokenRepository
) -> AuthService:
    """AuthService wired to the in-memory fakes."""
    return AuthService(fake_users, FakePasswordHasher(), FakeTokenService(), fake_tokens)
