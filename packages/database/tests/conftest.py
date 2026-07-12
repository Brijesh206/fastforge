"""Test configuration for the database package.

``DatabaseSettings`` loads from a ``.env`` file and environment variables by
design. Unit tests must construct settings from explicit arguments only, so
this fixture isolates them from any developer ``.env`` file or ambient
environment variables that would otherwise leak in and make results depend on
the local machine's configuration.
"""

import os

import pytest


@pytest.fixture(autouse=True)
def isolate_settings_environment(
    tmp_path: "os.PathLike[str]", monkeypatch: pytest.MonkeyPatch
) -> None:
    """Prevent settings from reading the repository .env or ambient env vars."""
    # Run from an empty directory so pydantic-settings cannot discover a .env.
    monkeypatch.chdir(tmp_path)
    # Drop any ambient platform settings that could leak into constructed
    # settings objects during the test run.
    for key in list(os.environ):
        if key.startswith(("DATABASE_", "APP_", "LOG_", "JWT_")):
            monkeypatch.delenv(key, raising=False)
