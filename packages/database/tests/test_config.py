"""Tests for database settings."""

import ssl

import pytest
from fastforge_database.config import DatabaseSettings
from pydantic import ValidationError


def _assert_require_ssl(connect_args: dict[str, object]) -> None:
    """Assert connect_args carry an encrypt-without-verify SSL context."""
    context = connect_args["ssl"]
    assert isinstance(context, ssl.SSLContext)
    assert context.verify_mode == ssl.CERT_NONE
    assert context.check_hostname is False


def test_database_settings_converts_sync_postgres_url() -> None:
    settings = DatabaseSettings(
        database_url="postgresql://postgres:postgres@localhost:5432/fastforge_platform"
    )

    assert (
        settings.async_url
        == "postgresql+asyncpg://postgres:postgres@localhost:5432/fastforge_platform"
    )


def test_database_settings_accepts_async_postgres_url() -> None:
    url = "postgresql+asyncpg://postgres:postgres@localhost:5432/fastforge_platform"
    settings = DatabaseSettings(database_url=url)

    assert settings.async_url == url
    assert settings.connect_args == {}


def test_database_settings_rejects_non_postgres_url() -> None:
    with pytest.raises(ValidationError):
        DatabaseSettings(database_url="sqlite+aiosqlite:///local.db")


def test_database_settings_rejects_invalid_pool_values() -> None:
    with pytest.raises(ValidationError):
        DatabaseSettings(
            database_url="postgresql+asyncpg://postgres:postgres@localhost:5432/db",
            pool_size=0,
        )


def test_database_settings_supports_supabase_direct_url() -> None:
    settings = DatabaseSettings(
        database_url=(
            "postgresql://postgres:secret@db.example-ref.supabase.co:5432/postgres"
            "?sslmode=require"
        )
    )

    assert settings.async_url == (
        "postgresql+asyncpg://postgres:secret@db.example-ref.supabase.co:5432/postgres"
    )
    assert settings.is_supabase_url is True
    _assert_require_ssl(settings.connect_args)


def test_database_settings_supports_supabase_pooler_url_without_ssl_query() -> None:
    settings = DatabaseSettings(
        database_url=(
            "postgresql://postgres.example-ref:secret@aws-0-us-east-1.pooler.supabase.com"
            ":6543/postgres"
        )
    )

    assert settings.is_supabase_url is True
    _assert_require_ssl(settings.connect_args)


def test_database_settings_can_force_ssl_for_custom_postgres_host() -> None:
    settings = DatabaseSettings(
        database_url="postgresql://postgres:secret@database.example.com:5432/postgres",
        ssl_mode="require",
    )

    _assert_require_ssl(settings.connect_args)


def test_database_settings_verify_full_uses_verifying_ssl_context() -> None:
    settings = DatabaseSettings(
        database_url="postgresql://postgres:secret@database.example.com:5432/postgres",
        ssl_mode="verify-full",
    )

    context = settings.connect_args["ssl"]
    assert isinstance(context, ssl.SSLContext)
    assert context.verify_mode == ssl.CERT_REQUIRED
    assert context.check_hostname is True
