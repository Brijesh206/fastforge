"""Tests for the Argon2 password hasher adapter."""

from fastforge_auth.adapters.argon2_password_hasher import Argon2PasswordHasher


def test_hash_and_verify_round_trip() -> None:
    hasher = Argon2PasswordHasher()

    password_hash = hasher.hash("correct-horse-battery-staple")

    assert hasher.verify("correct-horse-battery-staple", password_hash) is True


def test_verify_rejects_wrong_password() -> None:
    hasher = Argon2PasswordHasher()

    password_hash = hasher.hash("correct-horse-battery-staple")

    assert hasher.verify("wrong-password", password_hash) is False


def test_verify_rejects_malformed_hash() -> None:
    hasher = Argon2PasswordHasher()

    assert hasher.verify("any-password", "not-a-real-hash") is False


def test_hash_produces_different_output_each_time() -> None:
    hasher = Argon2PasswordHasher()

    first = hasher.hash("same-password")
    second = hasher.hash("same-password")

    assert first != second
