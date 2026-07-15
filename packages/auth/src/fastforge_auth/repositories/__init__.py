"""Authentication repositories."""

from fastforge_auth.repositories.auth_token import AuthTokenRepository
from fastforge_auth.repositories.user import UserRepository

__all__ = ["AuthTokenRepository", "UserRepository"]
