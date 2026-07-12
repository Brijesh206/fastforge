"""Argon2id password hashing adapter."""

from argon2 import PasswordHasher as Argon2Hasher
from argon2.exceptions import InvalidHash, VerificationError, VerifyMismatchError

from fastforge_auth.interfaces.password_hasher import PasswordHasher


class Argon2PasswordHasher(PasswordHasher):
    """Argon2id-based password hasher, the platform default."""

    def __init__(self) -> None:
        self._hasher = Argon2Hasher()

    def hash(self, password: str) -> str:
        """Hash a plaintext password for storage."""
        return self._hasher.hash(password)

    def verify(self, password: str, password_hash: str) -> bool:
        """Verify a plaintext password against a stored hash."""
        try:
            return self._hasher.verify(password_hash, password)
        except (VerifyMismatchError, VerificationError, InvalidHash):
            return False
