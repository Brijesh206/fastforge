"""Tests for shared settings."""

import pytest
from pydantic import ValidationError

from fastforge_common.config import BaseAppSettings
from fastforge_common.enums import AppEnvironment


def test_base_app_settings_loads_by_field_name() -> None:
    settings = BaseAppSettings(
        app_name="Example App",
        app_env=AppEnvironment.TESTING,
        app_debug=True,
        app_secret_key="super-secret-value",
    )

    assert settings.app_name == "Example App"
    assert settings.is_testing is True
    assert settings.is_development is False
    assert settings.is_production is False


def test_base_app_settings_rejects_empty_app_name() -> None:
    with pytest.raises(ValidationError):
        BaseAppSettings(app_name=" ", app_secret_key="super-secret-value")


def test_base_app_settings_requires_reasonable_secret_length() -> None:
    with pytest.raises(ValidationError):
        BaseAppSettings(app_secret_key="short")
