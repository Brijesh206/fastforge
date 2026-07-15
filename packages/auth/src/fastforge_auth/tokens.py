"""Single-use token generation and hashing.

The raw token is high-entropy random, so a fast hash (SHA-256) is the right
choice — argon2 exists to slow down guessing of low-entropy passwords, which
does not apply here. Only the hash is stored; a database leak never exposes a
usable token.
"""

import hashlib
import secrets

from fastforge_auth.constants import TOKEN_ENTROPY_BYTES


def generate_token() -> str:
    """Return a new URL-safe random token to embed in an email link."""
    return secrets.token_urlsafe(TOKEN_ENTROPY_BYTES)


def hash_token(raw_token: str) -> str:
    """Return the SHA-256 hex digest stored for a raw token."""
    return hashlib.sha256(raw_token.encode()).hexdigest()
