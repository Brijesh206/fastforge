"""Token issuance and verification interface."""

from abc import ABC, abstractmethod
from uuid import UUID

from fastforge_auth.schemas.auth import TokenPair


class TokenService(ABC):
    """Contract for issuing and verifying authentication tokens.

    Kept independent of any specific JWT library or identity provider so
    the token strategy can evolve (e.g. opaque tokens, provider-issued
    JWTs) without changing service-layer code.
    """

    @abstractmethod
    def issue_token_pair(self, user_id: UUID) -> TokenPair:
        """Issue a new access/refresh token pair for a user."""

    @abstractmethod
    def decode_access_token(self, token: str) -> UUID:
        """Decode an access token and return the subject user id."""

    @abstractmethod
    def decode_refresh_token(self, token: str) -> UUID:
        """Decode a refresh token and return the subject user id."""
