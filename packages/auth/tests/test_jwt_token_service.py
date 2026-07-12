"""Tests for the JWT token service adapter."""

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import jwt
import pytest

from fastforge_auth.adapters.jwt_token_service import JwtTokenService
from fastforge_auth.config import AuthSettings
from fastforge_auth.exceptions import InvalidTokenError


def _service() -> JwtTokenService:
    settings = AuthSettings(jwt_secret_key="test-secret-key-1234567890-abcdef")
    return JwtTokenService(settings)


def test_issue_token_pair_round_trips_through_access_token() -> None:
    service = _service()
    user_id = uuid4()

    tokens = service.issue_token_pair(user_id)

    assert service.decode_access_token(tokens.access_token) == user_id


def test_issue_token_pair_round_trips_through_refresh_token() -> None:
    service = _service()
    user_id = uuid4()

    tokens = service.issue_token_pair(user_id)

    assert service.decode_refresh_token(tokens.refresh_token) == user_id


def test_decode_access_token_rejects_refresh_token() -> None:
    service = _service()
    tokens = service.issue_token_pair(uuid4())

    with pytest.raises(InvalidTokenError):
        service.decode_access_token(tokens.refresh_token)


def test_decode_access_token_rejects_garbage_token() -> None:
    service = _service()

    with pytest.raises(InvalidTokenError):
        service.decode_access_token("not-a-jwt")


def test_decode_access_token_rejects_expired_token() -> None:
    settings = AuthSettings(jwt_secret_key="test-secret-key-1234567890-abcdef")
    service = JwtTokenService(settings)

    now = datetime.now(UTC)
    expired_token = jwt.encode(
        {
            "sub": str(uuid4()),
            "type": "access",
            "iat": now - timedelta(minutes=30),
            "exp": now - timedelta(minutes=1),
        },
        settings.jwt_secret_key.get_secret_value(),
        algorithm=settings.jwt_algorithm,
    )

    with pytest.raises(InvalidTokenError):
        service.decode_access_token(expired_token)


def test_decode_access_token_rejects_token_signed_with_different_secret() -> None:
    service = _service()
    other_settings = AuthSettings(jwt_secret_key="a-completely-different-secret-value")
    other_service = JwtTokenService(other_settings)
    tokens = other_service.issue_token_pair(uuid4())

    with pytest.raises(InvalidTokenError):
        service.decode_access_token(tokens.access_token)
