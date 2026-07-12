"""Tests for log formatters."""

import json
import logging

from fastforge_logging.context import bind_log_context, clear_log_context
from fastforge_logging.formatters import JsonLogFormatter


def test_json_formatter_includes_context_and_redacts_sensitive_values() -> None:
    clear_log_context()
    bind_log_context(request_id="req_123")
    formatter = JsonLogFormatter(service_name="api", environment="testing")
    record = logging.LogRecord(
        name="app.auth",
        level=logging.INFO,
        pathname=__file__,
        lineno=10,
        msg="User logged in",
        args=(),
        exc_info=None,
    )
    record.password = "secret-password"

    payload = json.loads(formatter.format(record))

    assert payload["service"] == "api"
    assert payload["environment"] == "testing"
    assert payload["request_id"] == "req_123"
    assert payload["password"] == "[REDACTED]"
