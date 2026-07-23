"""Google OAuth provider.

The only module in the platform that talks to Google's OAuth endpoints.
"""

from urllib.parse import urlencode

import httpx

from fastforge_auth.config import OAuthSettings
from fastforge_auth.exceptions import OAuthEmailNotVerifiedError, OAuthNotConfiguredError
from fastforge_auth.interfaces.oauth_provider import OAuthProvider, OAuthUserInfo

_AUTHORIZE_URL = "https://accounts.google.com/o/oauth2/v2/auth"
_TOKEN_URL = "https://oauth2.googleapis.com/token"
_USERINFO_URL = "https://openidconnect.googleapis.com/v1/userinfo"


class GoogleOAuthProvider(OAuthProvider):
    """Implements OAuthProvider against Google's OpenID Connect endpoints."""

    def __init__(self, settings: OAuthSettings) -> None:
        self._settings = settings

    def authorization_url(self, *, state: str, redirect_uri: str) -> str:
        if not self._settings.google_client_id:
            raise OAuthNotConfiguredError("GOOGLE_CLIENT_ID is not set.")
        params = {
            "client_id": self._settings.google_client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": "openid email profile",
            "state": state,
        }
        return f"{_AUTHORIZE_URL}?{urlencode(params)}"

    async def fetch_user_info(self, *, code: str, redirect_uri: str) -> OAuthUserInfo:
        client_secret = self._settings.google_client_secret.get_secret_value()
        if not self._settings.google_client_id or not client_secret:
            raise OAuthNotConfiguredError("Google OAuth credentials are not set.")

        async with httpx.AsyncClient(timeout=10.0) as client:
            token_response = await client.post(
                _TOKEN_URL,
                data={
                    "code": code,
                    "client_id": self._settings.google_client_id,
                    "client_secret": client_secret,
                    "redirect_uri": redirect_uri,
                    "grant_type": "authorization_code",
                },
            )
            token_response.raise_for_status()
            access_token = token_response.json()["access_token"]

            userinfo_response = await client.get(
                _USERINFO_URL, headers={"Authorization": f"Bearer {access_token}"}
            )
            userinfo_response.raise_for_status()
            profile = userinfo_response.json()

        if not profile.get("email_verified"):
            raise OAuthEmailNotVerifiedError()

        return OAuthUserInfo(
            email=profile["email"],
            full_name=profile.get("name"),
            avatar_url=profile.get("picture"),
        )
