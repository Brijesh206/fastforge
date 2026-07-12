"""Password hashing interface."""

from abc import ABC, abstractmethod


class PasswordHasher(ABC):
    """Contract for password hashing implementations.

    This keeps the hashing algorithm swappable (e.g. Argon2id to bcrypt)
    without touching the services that depend on it.
    """

    @abstractmethod
    def hash(self, password: str) -> str:
        """Hash a plaintext password for storage."""

    @abstractmethod
    def verify(self, password: str, password_hash: str) -> bool:
        """Verify a plaintext password against a stored hash."""
