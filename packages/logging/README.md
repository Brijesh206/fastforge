# Logging Package

Structured logging foundation for FastForge.

## Responsibilities

- Structured JSON logs
- Local text logs
- Request and correlation context
- Safe metadata redaction
- Reusable logger service
- Framework-agnostic logging setup for API and workers

## Usage

```python
from fastforge_logging import bind_log_context, configure_logging, get_logger
from fastforge_logging.config import LogFormat, LoggingSettings

configure_logging(
    LoggingSettings(
        service_name="api",
        environment="development",
        log_format=LogFormat.JSON,
    )
)

bind_log_context(request_id="req_123")

logger = get_logger("app.auth")
logger.info("User logged in", user_id="user_123")
```

## Rules

- Applications should use `LoggingService`, not raw `print()`.
- Do not log passwords, tokens, API keys, cookies, or secrets.
- Keep this package independent from FastAPI and worker frameworks.
- Audit log persistence belongs in a future audit module or feature package.
