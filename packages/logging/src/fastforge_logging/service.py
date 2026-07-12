"""Logging service and setup helpers."""

import logging

from fastforge_logging.config import LogFormat, LoggingSettings
from fastforge_logging.formatters import RESERVED_RECORD_KEYS, JsonLogFormatter, TextLogFormatter
from fastforge_logging.redaction import redact_value


class LoggingService:
    """Small wrapper around stdlib logging with platform conventions."""

    def __init__(self, logger: logging.Logger) -> None:
        self._logger = logger

    @property
    def name(self) -> str:
        """Return logger name."""
        return self._logger.name

    def debug(self, message: str, **metadata: object) -> None:
        """Log a debug message."""
        self._logger.debug(message, extra=_safe_extra(metadata))

    def info(self, message: str, **metadata: object) -> None:
        """Log an info message."""
        self._logger.info(message, extra=_safe_extra(metadata))

    def warning(self, message: str, **metadata: object) -> None:
        """Log a warning message."""
        self._logger.warning(message, extra=_safe_extra(metadata))

    def error(self, message: str, **metadata: object) -> None:
        """Log an error message."""
        self._logger.error(message, extra=_safe_extra(metadata))

    def critical(self, message: str, **metadata: object) -> None:
        """Log a critical message."""
        self._logger.critical(message, extra=_safe_extra(metadata))

    def exception(
        self,
        message: str,
        *,
        exc_info: bool = True,
        **metadata: object,
    ) -> None:
        """Log an exception with traceback information."""
        self._logger.exception(message, exc_info=exc_info, extra=_safe_extra(metadata))


def configure_logging(settings: LoggingSettings | None = None) -> None:
    """Configure root logging for an application or worker."""
    resolved_settings = settings or LoggingSettings()
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.setLevel(resolved_settings.level_number)

    if not resolved_settings.enable_console:
        return

    handler = logging.StreamHandler()
    handler.setLevel(resolved_settings.level_number)
    if resolved_settings.log_format == LogFormat.JSON:
        handler.setFormatter(
            JsonLogFormatter(
                service_name=resolved_settings.service_name,
                environment=resolved_settings.environment,
            )
        )
    else:
        handler.setFormatter(
            TextLogFormatter(
                service_name=resolved_settings.service_name,
                environment=resolved_settings.environment,
            )
        )
    root_logger.addHandler(handler)


def get_logger(name: str) -> LoggingService:
    """Return a platform logging service."""
    return LoggingService(logging.getLogger(name))


def _safe_extra(metadata: dict[str, object]) -> dict[str, object]:
    """Return redacted metadata safe for logging extra fields."""
    filtered = {
        key: value
        for key, value in metadata.items()
        if key not in RESERVED_RECORD_KEYS and not key.startswith("_")
    }
    redacted = redact_value(filtered)
    if not isinstance(redacted, dict):
        return {}
    return redacted
