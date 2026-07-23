"""High-entropy secret generation and hashing.

Shared by any package that issues a bearer credential (email verification and
password reset tokens in fastforge_auth, API keys in fastforge_api_keys). The
raw secret is high-entropy random, so a fast hash (SHA-256) is the right
choice — slow hashes like argon2 exist to slow down guessing of low-entropy
input, which does not apply here. Only the hash is ever stored; a database
leak never exposes a usable secret.
"""

import hashlib
import secrets

DEFAULT_SECRET_ENTROPY_BYTES = 32


def generate_secret(entropy_bytes: int = DEFAULT_SECRET_ENTROPY_BYTES) -> str:
    """Return a new URL-safe random secret."""
    return secrets.token_urlsafe(entropy_bytes)


def hash_secret(raw_secret: str) -> str:
    """Return the SHA-256 hex digest stored for a raw secret."""
    return hashlib.sha256(raw_secret.encode()).hexdigest()
