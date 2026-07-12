"""Tests for database model foundations."""

from fastforge_database.models.base import Base, NAMING_CONVENTION


def test_base_metadata_uses_platform_naming_convention() -> None:
    assert Base.metadata.naming_convention == NAMING_CONVENTION
