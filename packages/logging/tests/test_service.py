"""Tests for logging service setup."""

import logging

from fastforge_logging.config import LogFormat, LoggingSettings
from fastforge_logging.service import configure_logging, get_logger


def test_configure_logging_sets_root_handler() -> None:
    configure_logging(
        LoggingSettings(
            service_name="api",
            environment="testing",
            level="DEBUG",
            log_format=LogFormat.JSON,
        )
    )

    root_logger = logging.getLogger()

    assert root_logger.level == logging.DEBUG
    assert len(root_logger.handlers) == 1


def test_get_logger_returns_logging_service() -> None:
    logger = get_logger("app.test")

    assert logger.name == "app.test"


def test_logging_service_filters_reserved_extra_keys() -> None:
    configure_logging(
        LoggingSettings(
            service_name="api",
            environment="testing",
            level="INFO",
            log_format=LogFormat.JSON,
        )
    )
    logger = get_logger("app.test")

    logger.info("Event created", name="metadata collision", event="created")
