"""Tests for UUID utilities."""

from fastforge_database.utils.uuid import generate_uuid7


def test_generate_uuid7_returns_uuidv7() -> None:
    generated = generate_uuid7()

    assert generated.version == 7
    assert generated.variant == "specified in RFC 4122"


def test_generate_uuid7_generates_unique_values() -> None:
    generated = {generate_uuid7() for _ in range(100)}

    assert len(generated) == 100
