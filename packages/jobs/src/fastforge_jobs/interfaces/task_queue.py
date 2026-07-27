"""Task queue interface."""

from abc import ABC, abstractmethod
from typing import Any


class TaskQueue(ABC):
    """Hands work off to be run outside the request that created it.

    Callers depend on this interface only. They enqueue by *name* and never
    import a handler, a broker, or a framework decorator — which is what lets
    the backend be swapped in configuration alone.
    """

    @abstractmethod
    async def enqueue(self, task_name: str, /, **kwargs: Any) -> None:
        """Schedule the registered task named task_name to run with kwargs.

        Returns as soon as the job is accepted, not when it completes. kwargs
        must be JSON-serializable: they cross a process boundary for every
        backend except the in-memory one.

        Raises UnknownTaskError if no task is registered under task_name, so a
        typo fails at the call site instead of vanishing into a broker.
        """

    @abstractmethod
    async def close(self) -> None:
        """Release any held resources (connections, pools). Call at shutdown."""
