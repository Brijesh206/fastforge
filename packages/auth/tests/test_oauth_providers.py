"""Tests for GoogleOAuthProvider and GitHubOAuthProvider.

Network calls are intercepted via httpx.MockTransport (built into httpx
already, no extra test dependency) by monkeypatching AsyncClient to always
route through it.
"""

from collections.abc import Callable

import httpx
import pytest
from fastforge_auth.adapters.github_oauth_provider import GitHubOAuthProvider
from fastforge_auth.adapters.google_oauth_provider import GoogleOAuthProvider
from fastforge_auth.config import OAuthSettings
from fastforge_auth.exceptions import OAuthEmailNotVerifiedError, OAuthNotConfiguredError


def _mock_transport(
    monkeypatch: pytest.MonkeyPatch, handler: Callable[[httpx.Request], httpx.Response]
) -> None:
    """Route every httpx.AsyncClient created during the test through handler."""
    original_init = httpx.AsyncClient.__init__

    def patched_init(self: httpx.AsyncClient, *args: object, **kwargs: object) -> None:
        kwargs["transport"] = httpx.MockTransport(handler)
        original_init(self, *args, **kwargs)  # type: ignore[arg-type]

    monkeypatch.setattr(httpx.AsyncClient, "__init__", patched_init)


@pytest.fixture
def oauth_settings() -> OAuthSettings:
    return OAuthSettings(
        GOOGLE_CLIENT_ID="google-id",
        GOOGLE_CLIENT_SECRET="google-secret",
        GITHUB_CLIENT_ID="github-id",
        GITHUB_CLIENT_SECRET="github-secret",
        _env_file=None,
    )


class TestGoogleOAuthProvider:
    def test_authorization_url_includes_client_id_state_and_redirect(
        self, oauth_settings: OAuthSettings
    ) -> None:
        provider = GoogleOAuthProvider(oauth_settings)

        url = provider.authorization_url(state="xyz", redirect_uri="https://api.example.com/cb")

        assert "accounts.google.com" in url
        assert "client_id=google-id" in url
        assert "state=xyz" in url

    def test_authorization_url_raises_when_not_configured(self) -> None:
        provider = GoogleOAuthProvider(OAuthSettings(_env_file=None))

        with pytest.raises(OAuthNotConfiguredError):
            provider.authorization_url(state="xyz", redirect_uri="https://api.example.com/cb")

    async def test_fetch_user_info_returns_the_verified_profile(
        self, oauth_settings: OAuthSettings, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            if request.url.path == "/token":
                return httpx.Response(200, json={"access_token": "at"})
            return httpx.Response(
                200,
                json={
                    "email": "ada@example.com",
                    "email_verified": True,
                    "name": "Ada",
                    "picture": "https://img",
                },
            )

        _mock_transport(monkeypatch, handler)
        provider = GoogleOAuthProvider(oauth_settings)

        info = await provider.fetch_user_info(
            code="abc", redirect_uri="https://api.example.com/cb"
        )

        assert info.email == "ada@example.com"
        assert info.full_name == "Ada"
        assert info.avatar_url == "https://img"

    async def test_fetch_user_info_rejects_an_unverified_email(
        self, oauth_settings: OAuthSettings, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            if request.url.path == "/token":
                return httpx.Response(200, json={"access_token": "at"})
            return httpx.Response(200, json={"email": "ada@example.com", "email_verified": False})

        _mock_transport(monkeypatch, handler)
        provider = GoogleOAuthProvider(oauth_settings)

        with pytest.raises(OAuthEmailNotVerifiedError):
            await provider.fetch_user_info(code="abc", redirect_uri="https://api.example.com/cb")

    async def test_fetch_user_info_raises_when_not_configured(self) -> None:
        provider = GoogleOAuthProvider(OAuthSettings(_env_file=None))

        with pytest.raises(OAuthNotConfiguredError):
            await provider.fetch_user_info(code="abc", redirect_uri="https://api.example.com/cb")


class TestGitHubOAuthProvider:
    def test_authorization_url_includes_client_id_state_and_redirect(
        self, oauth_settings: OAuthSettings
    ) -> None:
        provider = GitHubOAuthProvider(oauth_settings)

        url = provider.authorization_url(state="xyz", redirect_uri="https://api.example.com/cb")

        assert "github.com" in url
        assert "client_id=github-id" in url
        assert "state=xyz" in url

    async def test_fetch_user_info_picks_the_verified_primary_email(
        self, oauth_settings: OAuthSettings, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            if "access_token" in request.url.path:
                return httpx.Response(200, json={"access_token": "at"})
            if request.url.path == "/user":
                return httpx.Response(
                    200,
                    json={"login": "ada", "name": "Ada Lovelace", "avatar_url": "https://img"},
                )
            return httpx.Response(
                200,
                json=[
                    {"email": "secondary@example.com", "primary": False, "verified": True},
                    {"email": "ada@example.com", "primary": True, "verified": True},
                ],
            )

        _mock_transport(monkeypatch, handler)
        provider = GitHubOAuthProvider(oauth_settings)

        info = await provider.fetch_user_info(
            code="abc", redirect_uri="https://api.example.com/cb"
        )

        assert info.email == "ada@example.com"
        assert info.full_name == "Ada Lovelace"
        assert info.avatar_url == "https://img"

    async def test_fetch_user_info_falls_back_to_login_without_a_display_name(
        self, oauth_settings: OAuthSettings, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            if "access_token" in request.url.path:
                return httpx.Response(200, json={"access_token": "at"})
            if request.url.path == "/user":
                return httpx.Response(200, json={"login": "ada", "avatar_url": None})
            return httpx.Response(
                200, json=[{"email": "ada@example.com", "primary": True, "verified": True}]
            )

        _mock_transport(monkeypatch, handler)
        provider = GitHubOAuthProvider(oauth_settings)

        info = await provider.fetch_user_info(
            code="abc", redirect_uri="https://api.example.com/cb"
        )

        assert info.full_name == "ada"

    async def test_fetch_user_info_rejects_when_no_verified_primary_email(
        self, oauth_settings: OAuthSettings, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            if "access_token" in request.url.path:
                return httpx.Response(200, json={"access_token": "at"})
            if request.url.path == "/user":
                return httpx.Response(200, json={"login": "ada"})
            return httpx.Response(
                200, json=[{"email": "ada@example.com", "primary": True, "verified": False}]
            )

        _mock_transport(monkeypatch, handler)
        provider = GitHubOAuthProvider(oauth_settings)

        with pytest.raises(OAuthEmailNotVerifiedError):
            await provider.fetch_user_info(code="abc", redirect_uri="https://api.example.com/cb")
