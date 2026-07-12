"""Context propagation for structured logs."""

from contextvars import ContextVar
from dataclasses import asdict, dataclass
from uuid import UUID


@dataclass(frozen=True)
class LogContext:
    """Request or job context included in each log record."""

    request_id: str | None = None
    correlation_id: str | None = None
    user_id: UUID | str | None = None
    organization_id: UUID | str | None = None
    api_key_id: UUID | str | None = None
    trace_id: str | None = None
    span_id: str | None = None

    def to_dict(self) -> dict[str, str]:
        """Return non-empty context fields as strings."""
        values = asdict(self)
        return {
            key: str(value)
            for key, value in values.items()
            if value is not None and str(value) != ""
        }


_log_context: ContextVar[LogContext | None] = ContextVar("log_context", default=None)


def get_log_context() -> LogContext:
    """Return the current log context, or an empty context if none is bound."""
    context = _log_context.get()
    return context if context is not None else LogContext()


def bind_log_context(**values: UUID | str | None) -> LogContext:
    """Merge values into the current log context."""
    current = get_log_context()
    next_context = LogContext(
        request_id=values.get("request_id", current.request_id),
        correlation_id=values.get("correlation_id", current.correlation_id),
        user_id=values.get("user_id", current.user_id),
        organization_id=values.get("organization_id", current.organization_id),
        api_key_id=values.get("api_key_id", current.api_key_id),
        trace_id=values.get("trace_id", current.trace_id),
        span_id=values.get("span_id", current.span_id),
    )
    _log_context.set(next_context)
    return next_context


def clear_log_context() -> None:
    """Clear context for the current execution flow."""
    _log_context.set(LogContext())
