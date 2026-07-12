"""Tests for sensitive data redaction."""

from fastforge_logging.redaction import REDACTED, redact_value


def test_redact_value_redacts_nested_sensitive_keys() -> None:
    value = {
        "email": "user@example.com",
        "password": "secret",
        "metadata": {
            "api_key": "sk_test_123",
            "safe": "value",
        },
    }

    assert redact_value(value) == {
        "email": "user@example.com",
        "password": REDACTED,
        "metadata": {
            "api_key": REDACTED,
            "safe": "value",
        },
    }
