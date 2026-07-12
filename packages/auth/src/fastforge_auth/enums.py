"""Authentication enums."""

from enum import StrEnum


class AuthProvider(StrEnum):
    """Supported identity providers."""

    EMAIL = "email"
    GOOGLE = "google"
    GITHUB = "github"


class TokenType(StrEnum):
    """JWT token purpose, embedded as a claim to prevent token misuse."""

    ACCESS = "access"
    REFRESH = "refresh"
