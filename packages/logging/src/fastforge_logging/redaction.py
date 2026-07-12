"""Sensitive data redaction helpers."""

from collections.abc import Mapping, Sequence

REDACTED = "[REDACTED]"
SENSITIVE_KEYS = {
    "api_key",
    "apikey",
    "authorization",
    "client_secret",
    "cookie",
    "credit_card",
    "jwt",
    "password",
    "private_key",
    "refresh_token",
    "secret",
    "session",
    "token",
}


def is_sensitive_key(key: str) -> bool:
    """Return True when a key name should be redacted."""
    normalized = key.lower().replace("-", "_")
    return any(sensitive_key in normalized for sensitive_key in SENSITIVE_KEYS)


def redact_value(value: object) -> object:
    """Recursively redact sensitive mapping values."""
    if isinstance(value, Mapping):
        return {
            str(key): REDACTED if is_sensitive_key(str(key)) else redact_value(item)
            for key, item in value.items()
        }

    if isinstance(value, str | bytes):
        return value

    if isinstance(value, Sequence):
        return [redact_value(item) for item in value]

    return value
