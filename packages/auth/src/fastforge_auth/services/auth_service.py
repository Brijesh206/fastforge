"""Authentication service — registration, login, and account lifecycle."""

from datetime import UTC, datetime, timedelta

from fastforge_auth.constants import (
    DEFAULT_EMAIL_VERIFICATION_EXPIRE_HOURS,
    DEFAULT_PASSWORD_RESET_EXPIRE_MINUTES,
)
from fastforge_auth.enums import AuthTokenPurpose
from fastforge_auth.exceptions import (
    InactiveUserError,
    InvalidCredentialsError,
    InvalidTokenError,
    UserAlreadyExistsError,
)
from fastforge_auth.interfaces.password_hasher import PasswordHasher
from fastforge_auth.interfaces.token_service import TokenService
from fastforge_auth.models.auth_token import AuthToken
from fastforge_auth.models.user import User
from fastforge_auth.repositories.auth_token import AuthTokenRepository
from fastforge_auth.repositories.user import UserRepository
from fastforge_auth.schemas.auth import LoginRequest, TokenPair
from fastforge_auth.schemas.user import UserCreate
from fastforge_auth.tokens import generate_token, hash_token


class AuthService:
    """Owns registration, authentication, and account-lifecycle business logic.

    Depends on the password hasher and token service interfaces only, never on
    a concrete hashing library or provider SDK. Email delivery is the
    application's responsibility: the token-issuing methods return a raw token
    for the caller to put in a link, and the service never imports the mail
    package.
    """

    def __init__(
        self,
        user_repository: UserRepository,
        password_hasher: PasswordHasher,
        token_service: TokenService,
        auth_token_repository: AuthTokenRepository | None = None,
        *,
        email_verification_expire_hours: int = DEFAULT_EMAIL_VERIFICATION_EXPIRE_HOURS,
        password_reset_expire_minutes: int = DEFAULT_PASSWORD_RESET_EXPIRE_MINUTES,
    ) -> None:
        self._user_repository = user_repository
        self._password_hasher = password_hasher
        self._token_service = token_service
        self._auth_token_repository = auth_token_repository
        self._email_verification_expire_hours = email_verification_expire_hours
        self._password_reset_expire_minutes = password_reset_expire_minutes

    @property
    def _auth_tokens(self) -> AuthTokenRepository:
        if self._auth_token_repository is None:
            raise RuntimeError("AuthService was constructed without an AuthTokenRepository.")
        return self._auth_token_repository

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

    async def issue_email_verification_token(self, user: User) -> str:
        """Create a verification token for the user and return the raw value.

        The caller emails a link containing the raw token; only its hash is
        stored. Any earlier unused verification token is invalidated first.
        """
        return await self._issue_token(
            user,
            AuthTokenPurpose.EMAIL_VERIFICATION,
            timedelta(hours=self._email_verification_expire_hours),
        )

    async def verify_email(self, raw_token: str) -> User:
        """Consume a verification token and mark the user verified.

        Raises InvalidTokenError if the token is unknown, already used, or
        expired.
        """
        token = await self._consume_token(raw_token, AuthTokenPurpose.EMAIL_VERIFICATION)
        user = await self._user_repository.get_by_id(token.user_id)
        if user is None:
            raise InvalidTokenError()

        user.is_verified = True
        return await self._user_repository.update(user)

    async def issue_password_reset_token(self, email: str) -> tuple[User, str] | None:
        """Create a reset token for the email, or None if no account matches.

        Returns None rather than raising so the endpoint can respond
        identically whether or not the address exists, avoiding account
        enumeration.
        """
        user = await self._user_repository.get_by_email(email)
        if user is None or not user.is_active:
            return None

        raw_token = await self._issue_token(
            user,
            AuthTokenPurpose.PASSWORD_RESET,
            timedelta(minutes=self._password_reset_expire_minutes),
        )
        return user, raw_token

    async def reset_password(self, raw_token: str, new_password: str) -> User:
        """Consume a reset token and set a new password.

        Raises InvalidTokenError if the token is unknown, already used, or
        expired.
        """
        token = await self._consume_token(raw_token, AuthTokenPurpose.PASSWORD_RESET)
        user = await self._user_repository.get_by_id(token.user_id)
        if user is None:
            raise InvalidTokenError()

        user.password_hash = self._password_hasher.hash(new_password)
        return await self._user_repository.update(user)

    async def _issue_token(
        self, user: User, purpose: AuthTokenPurpose, ttl: timedelta
    ) -> str:
        now = datetime.now(UTC)
        await self._auth_tokens.invalidate_unused(user.id, purpose, now=now)

        raw_token = generate_token()
        await self._auth_tokens.create(
            AuthToken(
                user_id=user.id,
                token_hash=hash_token(raw_token),
                purpose=purpose.value,
                expires_at=now + ttl,
            )
        )
        return raw_token

    async def _consume_token(self, raw_token: str, purpose: AuthTokenPurpose) -> AuthToken:
        token = await self._auth_tokens.get_by_hash(hash_token(raw_token), purpose)
        if token is None or token.used_at is not None:
            raise InvalidTokenError()
        if token.expires_at <= datetime.now(UTC):
            raise InvalidTokenError()

        token.used_at = datetime.now(UTC)
        await self._auth_tokens.update(token)
        return token
