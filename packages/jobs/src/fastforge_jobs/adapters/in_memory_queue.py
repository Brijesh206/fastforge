"""In-memory task queue — the default so a fresh checkout needs no broker.

Runs handlers as asyncio tasks inside the calling process. Good for local dev
and tests; wrong for production, because a job lives only as long as the
process does:

  - a restart or crash loses everything still in flight, with no redelivery
  - failures are logged, never retried
  - jobs compete with request handling for the same event loop

Set JOBS_PROVIDER=taskiq or celery for durability. This adapter deliberately
mirrors InMemoryCache: the zero-config default that tells you when it isn't
enough rather than pretending to be a broker.
"""

import asyncio
from typing import Any

from fastforge_logging import get_logger

from fastforge_jobs.interfaces.task_queue import TaskQueue
from fastforge_jobs.registry import get_handler, run_task

logger = get_logger("fastforge.jobs.memory")


class InMemoryTaskQueue(TaskQueue):
    """Runs tasks in the background of the current process."""

    def __init__(self) -> None:
        # Strong references to pending tasks. Without this the event loop only
        # holds a weak reference and a job can be garbage-collected mid-flight.
        self._pending: set[asyncio.Task[None]] = set()

    async def enqueue(self, task_name: str, /, **kwargs: Any) -> None:
        # Resolve now so an unknown name raises at the call site, matching the
        # broker-backed adapters instead of failing later in a worker.
        get_handler(task_name)
        task = asyncio.create_task(self._run(task_name, **kwargs))
        self._pending.add(task)
        task.add_done_callback(self._pending.discard)

    async def _run(self, task_name: str, /, **kwargs: Any) -> None:
        try:
            await run_task(task_name, **kwargs)
        except Exception:
            # A background failure must never take down the caller, but it must
            # not disappear either. No retry here by design — that's what the
            # durable backends are for.
            logger.exception("Background task failed", task_name=task_name)

    async def close(self) -> None:
        """Wait for in-flight jobs so shutdown doesn't silently drop them."""
        if not self._pending:
            return
        logger.info("Draining background tasks", count=len(self._pending))
        await asyncio.gather(*tuple(self._pending), return_exceptions=True)
