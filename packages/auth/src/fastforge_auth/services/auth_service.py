"""Authentication service — registration and login workflows."""

from datetime import UTC, datetime

from fastforge_auth.exceptions import (
    InactiveUserError,
    InvalidCredentialsError,
    UserAlreadyExistsError,
)
from fastforge_auth.interfaces.password_hasher import PasswordHasher
from fastforge_auth.interfaces.token_service import TokenService
from fastforge_auth.models.user import User
from fastforge_auth.repositories.user import UserRepository
from fastforge_auth.schemas.auth import LoginRequest, TokenPair
from fastforge_auth.schemas.user import UserCreate


class AuthService:
    """Owns registration and authentication business logic.

    Depends on the password hasher and token service interfaces only,
    never on a concrete hashing library or provider SDK.
    """

    def __init__(
        self,
        user_repository: UserRepository,
        password_hasher: PasswordHasher,
        token_service: TokenService,
    ) -> None:
        self._user_repository = user_repository
        self._password_hasher = password_hasher
        self._token_service = token_service

    async def register_user(self, data: UserCreate) -> User:
        """Create a new user with a hashed password.

        Raises UserAlreadyExistsError if the email is already registered.
        """
        existing = await self._user_repository.get_by_email(data.email)
        if existing is not None:
            raise UserAlreadyExistsError()

        user = User(
            email=data.email,
            password_hash=self._password_hasher.hash(data.password),
            full_name=data.full_name,
        )
        return await self._user_repository.create(user)

    async def authenticate_user(self, data: LoginRequest) -> TokenPair:
        """Verify credentials and issue a token pair.

        Raises InvalidCredentialsError on unknown email or wrong password,
        and InactiveUserError if the account has been deactivated.
        """
        user = await self._user_repository.get_by_email(data.email)
        if user is None or user.password_hash is None:
            raise InvalidCredentialsError()

        if not self._password_hasher.verify(data.password, user.password_hash):
            raise InvalidCredentialsError()

        if not user.is_active:
            raise InactiveUserError()

        user.last_login_at = datetime.now(UTC)
        await self._user_repository.update(user)

        return self._token_service.issue_token_pair(user.id)

    async def refresh_tokens(self, refresh_token: str) -> TokenPair:
        """Issue a new token pair from a valid refresh token.

        Raises InvalidTokenError for an invalid or expired refresh token,
        InvalidCredentialsError if the subject no longer exists, and
        InactiveUserError if the account has been deactivated.
        """
        user_id = self._token_service.decode_refresh_token(refresh_token)

        user = await self._user_repository.get_by_id(user_id)
        if user is None:
            raise InvalidCredentialsError()

        if not user.is_active:
            raise InactiveUserError()

        return self._token_service.issue_token_pair(user.id)
