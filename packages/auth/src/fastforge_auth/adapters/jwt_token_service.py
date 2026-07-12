"""JWT-based token service adapter."""

from datetime import UTC, datetime, timedelta
from uuid import UUID

import jwt

from fastforge_auth.config import AuthSettings
from fastforge_auth.enums import TokenType
from fastforge_auth.exceptions import InvalidTokenError
from fastforge_auth.interfaces.token_service import TokenService
from fastforge_auth.schemas.auth import TokenPair


class JwtTokenService(TokenService):
    """Issues and verifies signed JWT access and refresh tokens."""

    def __init__(self, settings: AuthSettings) -> None:
        self._settings = settings

    def issue_token_pair(self, user_id: UUID) -> TokenPair:
        """Issue a new access/refresh token pair for a user."""
        return TokenPair(
            access_token=self._encode(
                user_id,
                TokenType.ACCESS,
                timedelta(minutes=self._settings.access_token_expire_minutes),
            ),
            refresh_token=self._encode(
                user_id,
                TokenType.REFRESH,
                timedelta(days=self._settings.refresh_token_expire_days),
            ),
        )

    def decode_access_token(self, token: str) -> UUID:
        """Decode an access token and return the subject user id."""
        return self._decode(token, TokenType.ACCESS)

    def decode_refresh_token(self, token: str) -> UUID:
        """Decode a refresh token and return the subject user id."""
        return self._decode(token, TokenType.REFRESH)

    def _encode(self, user_id: UUID, token_type: TokenType, lifetime: timedelta) -> str:
        now = datetime.now(UTC)
        payload = {
            "sub": str(user_id),
            "type": token_type.value,
            "iat": now,
            "exp": now + lifetime,
        }
        return jwt.encode(
            payload,
            self._settings.jwt_secret_key.get_secret_value(),
            algorithm=self._settings.jwt_algorithm,
        )

    def _decode(self, token: str, expected_type: TokenType) -> UUID:
        try:
            payload = jwt.decode(
                token,
                self._settings.jwt_secret_key.get_secret_value(),
                algorithms=[self._settings.jwt_algorithm],
            )
        except jwt.PyJWTError as exc:
            raise InvalidTokenError() from exc

        if payload.get("type") != expected_type.value:
            raise InvalidTokenError()

        subject = payload.get("sub")
        if not isinstance(subject, str):
            raise InvalidTokenError()

        try:
            return UUID(subject)
        except ValueError as exc:
            raise InvalidTokenError() from exc
