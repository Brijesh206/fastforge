"""GitHub OAuth provider.

The only module in the platform that talks to GitHub's OAuth + REST APIs.
"""

from urllib.parse import urlencode

import httpx

from fastforge_auth.config import OAuthSettings
from fastforge_auth.exceptions import OAuthEmailNotVerifiedError, OAuthNotConfiguredError
from fastforge_auth.interfaces.oauth_provider import OAuthProvider, OAuthUserInfo

_AUTHORIZE_URL = "https://github.com/login/oauth/authorize"
_TOKEN_URL = "https://github.com/login/oauth/access_token"
_USER_URL = "https://api.github.com/user"
_EMAILS_URL = "https://api.github.com/user/emails"


class GitHubOAuthProvider(OAuthProvider):
    """Implements OAuthProvider against GitHub's OAuth + REST APIs.

    GitHub's primary /user profile doesn't reliably include a verified email
    (it's null unless the user made one public), so this always makes a
    second call to /user/emails and picks the verified primary address.
    """

    def __init__(self, settings: OAuthSettings) -> None:
        self._settings = settings

    def authorization_url(self, *, state: str, redirect_uri: str) -> str:
        if not self._settings.github_client_id:
            raise OAuthNotConfiguredError("GITHUB_CLIENT_ID is not set.")
        params = {
            "client_id": self._settings.github_client_id,
            "redirect_uri": redirect_uri,
            "scope": "read:user user:email",
            "state": state,
        }
        return f"{_AUTHORIZE_URL}?{urlencode(params)}"

    async def fetch_user_info(self, *, code: str, redirect_uri: str) -> OAuthUserInfo:
        client_secret = self._settings.github_client_secret.get_secret_value()
        if not self._settings.github_client_id or not client_secret:
            raise OAuthNotConfiguredError("GitHub OAuth credentials are not set.")

        async with httpx.AsyncClient(
            timeout=10.0, headers={"Accept": "application/json"}
        ) as client:
            token_response = await client.post(
                _TOKEN_URL,
                data={
                    "code": code,
                    "client_id": self._settings.github_client_id,
                    "client_secret": client_secret,
                    "redirect_uri": redirect_uri,
                },
            )
            token_response.raise_for_status()
            token_payload = token_response.json()
            if "access_token" not in token_payload:
                raise OAuthNotConfiguredError(
                    token_payload.get("error_description", "GitHub token exchange failed.")
                )
            access_token = token_payload["access_token"]

            auth_header = {"Authorization": f"Bearer {access_token}"}
            user_response = await client.get(_USER_URL, headers=auth_header)
            user_response.raise_for_status()
            profile = user_response.json()

            emails_response = await client.get(_EMAILS_URL, headers=auth_header)
            emails_response.raise_for_status()
            emails = emails_response.json()

        verified_primary = next(
            (e["email"] for e in emails if e.get("primary") and e.get("verified")), None
        )
        if verified_primary is None:
            raise OAuthEmailNotVerifiedError()

        return OAuthUserInfo(
            email=verified_primary,
            full_name=profile.get("name") or profile.get("login"),
            avatar_url=profile.get("avatar_url"),
        )
