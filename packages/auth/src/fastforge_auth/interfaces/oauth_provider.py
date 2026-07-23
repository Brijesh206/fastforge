"""OAuth identity provider interface."""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class OAuthUserInfo:
    """A user's identity as vouched for by an OAuth provider.

    ``email`` is guaranteed by the adapter to already be verified by the
    provider — callers may link it to an existing account (or create a new
    one) without re-checking ownership.
    """

    email: str
    full_name: str | None
    avatar_url: str | None


class OAuthProvider(ABC):
    """A "Sign in with X" identity provider (Google, GitHub today).

    The service depends on this interface only — no provider SDK/HTTP detail
    may leak past it; callers only ever see the normalized OAuthUserInfo.
    """

    @abstractmethod
    def authorization_url(self, *, state: str, redirect_uri: str) -> str:
        """Build the URL to send the user to for consent.

        Raises OAuthNotConfiguredError if the provider's credentials aren't set.
        """

    @abstractmethod
    async def fetch_user_info(self, *, code: str, redirect_uri: str) -> OAuthUserInfo:
        """Exchange an authorization code for the caller's verified identity.

        Raises OAuthNotConfiguredError if the provider's credentials aren't
        set, and OAuthEmailNotVerifiedError if the provider can't vouch that
        the associated email is verified.
        """
