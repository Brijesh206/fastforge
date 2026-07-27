"""Framework-agnostic registry of background task handlers.

This is what makes the backend swappable. A task is a plain ``async def``
registered under a name — it carries no Celery or Taskiq decorator, so the
same handler runs unchanged on every adapter:

    from fastforge_jobs import task

    @task("mail.send_verification")
    async def send_verification(*, to: str, url: str) -> None:
        ...

The API enqueues by name (``await queue.enqueue("mail.send_verification",
to=..., url=...)``) and never imports the handler. The worker imports the
modules that define handlers, which is what registers them.
"""

from collections.abc import Awaitable, Callable
from typing import Any

TaskHandler = Callable[..., Awaitable[None]]

_registry: dict[str, TaskHandler] = {}


class UnknownTaskError(LookupError):
    """Raised when a task name has no registered handler."""


class DuplicateTaskError(ValueError):
    """Raised when two handlers claim the same task name."""


def task(name: str) -> Callable[[TaskHandler], TaskHandler]:
    """Register an async function as the handler for ``name``.

    The handler is returned unchanged, so it stays directly callable and
    unit-testable without a broker.
    """

    def decorator(handler: TaskHandler) -> TaskHandler:
        existing = _registry.get(name)
        # Re-registering the identical function is fine: module re-import under
        # pytest's importlib mode would otherwise fail the whole suite.
        if existing is not None and existing is not handler:
            raise DuplicateTaskError(
                f"Task {name!r} is already registered to {existing.__module__}."
                f"{existing.__qualname__}"
            )
        _registry[name] = handler
        return handler

    return decorator


def get_handler(name: str) -> TaskHandler:
    """Return the handler registered under name, or raise UnknownTaskError."""
    try:
        return _registry[name]
    except KeyError:
        known = ", ".join(sorted(_registry)) or "none"
        raise UnknownTaskError(f"No task registered as {name!r}. Registered: {known}") from None


def registered_tasks() -> dict[str, TaskHandler]:
    """Return a copy of the registry — used by workers to bind every handler."""
    return dict(_registry)


def clear_registry() -> None:
    """Drop every registration. For tests only."""
    _registry.clear()


async def run_task(name: str, /, **kwargs: Any) -> None:
    """Look up and execute a task in the current process.

    Every adapter's worker side funnels through this, so behaviour on a
    missing handler is identical no matter which broker delivered the job.
    """
    await get_handler(name)(**kwargs)
