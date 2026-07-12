"""Log formatters."""

import json
import logging
from datetime import UTC, datetime
from traceback import format_exception

from fastforge_logging.context import get_log_context
from fastforge_logging.redaction import redact_value

RESERVED_RECORD_KEYS = {
    "args",
    "asctime",
    "created",
    "exc_info",
    "exc_text",
    "filename",
    "funcName",
    "levelname",
    "levelno",
    "lineno",
    "module",
    "msecs",
    "message",
    "msg",
    "name",
    "pathname",
    "process",
    "processName",
    "relativeCreated",
    "stack_info",
    "thread",
    "threadName",
}


class JsonLogFormatter(logging.Formatter):
    """Format log records as structured JSON."""

    def __init__(self, *, service_name: str, environment: str) -> None:
        super().__init__()
        self._service_name = service_name
        self._environment = environment

    def format(self, record: logging.LogRecord) -> str:
        """Format a log record as JSON."""
        payload: dict[str, object] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "service": self._service_name,
            "environment": self._environment,
            "message": record.getMessage(),
        }
        payload.update(get_log_context().to_dict())
        payload.update(self._extra_fields(record))

        if record.exc_info is not None:
            exc_type, exc_value, traceback = record.exc_info
            payload["exception"] = {
                "type": exc_type.__name__ if exc_type is not None else None,
                "message": str(exc_value),
                "stacktrace": "".join(format_exception(exc_type, exc_value, traceback)),
            }

        return json.dumps(redact_value(payload), default=str, separators=(",", ":"))

    def _extra_fields(self, record: logging.LogRecord) -> dict[str, object]:
        """Return non-standard fields attached through logger extra."""
        return {
            key: value
            for key, value in record.__dict__.items()
            if key not in RESERVED_RECORD_KEYS and not key.startswith("_")
        }


class TextLogFormatter(logging.Formatter):
    """Format log records for local development."""

    def __init__(self, *, service_name: str, environment: str) -> None:
        super().__init__("%(asctime)s %(levelname)s [%(name)s] %(message)s")
        self._service_name = service_name
        self._environment = environment

    def format(self, record: logging.LogRecord) -> str:
        """Format a human-readable log record with context appended."""
        message = super().format(record)
        context = get_log_context().to_dict()
        extra = {
            key: value
            for key, value in record.__dict__.items()
            if key not in RESERVED_RECORD_KEYS and not key.startswith("_")
        }
        metadata = {
            "service": self._service_name,
            "environment": self._environment,
            **context,
            **extra,
        }
        redacted = redact_value(metadata)
        if not redacted:
            return message
        return f"{message} {json.dumps(redacted, default=str, sort_keys=True)}"
