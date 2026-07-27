"""Taskiq task queue adapter — async-native, Redis-backed.

Taskiq handlers are coroutines, so registry handlers bind to the broker with
no bridging: the worker awaits them directly on its own event loop.

taskiq is an optional dependency. It's imported inside this module, which the
factory only loads when JOBS_PROVIDER=taskiq, so installs that don't use it
never need it present.
"""

from typing import Any

from taskiq import AsyncBroker
from taskiq_redis import ListQueueBroker

from fastforge_jobs.interfaces.task_queue import TaskQueue
from fastforge_jobs.registry import get_handler, registered_tasks, run_task

# One shared task on the broker dispatches every job by name, rather than
# registering each handler as its own taskiq task. Keeps the registry the
# single source of truth and means a new task needs no broker wiring.
_DISPATCH_TASK_NAME = "fastforge.dispatch"


def build_broker(broker_url: str) -> AsyncBroker:
    """Create the Taskiq broker and bind the registry dispatcher to it."""
    broker = ListQueueBroker(url=broker_url)
    broker.register_task(_dispatch, task_name=_DISPATCH_TASK_NAME)
    return broker


async def _dispatch(task_name: str, kwargs: dict[str, Any]) -> None:
    """Worker-side entry point: resolve the name and run the handler."""
    await run_task(task_name, **kwargs)


class TaskiqTaskQueue(TaskQueue):
    """Enqueues onto a Taskiq broker."""

    def __init__(self, broker: AsyncBroker) -> None:
        self._broker = broker
        self._started = False

    async def _ensure_started(self) -> None:
        # The producer side needs the broker's connection pool up before the
        # first kiq(). Starting lazily keeps construction synchronous so the
        # factory stays a plain function.
        if not self._started:
            await self._broker.startup()
            self._started = True

    async def enqueue(self, task_name: str, /, **kwargs: Any) -> None:
        get_handler(task_name)  # fail fast on a typo, before it hits the broker
        await self._ensure_started()
        await self._broker.find_task(_DISPATCH_TASK_NAME).kiq(  # type: ignore[union-attr]
            task_name=task_name, kwargs=kwargs
        )

    async def close(self) -> None:
        if self._started:
            await self._broker.shutdown()
            self._started = False


def registered_task_names() -> list[str]:
    """Names the worker will serve — logged at worker startup."""
    return sorted(registered_tasks())
