"""Celery task queue adapter — the familiar option, with retries and Beat.

Celery is sync on both sides, and this codebase is async throughout. That
mismatch is contained here so handlers never see it:

  - producing: ``send_task`` does blocking I/O, so it runs in a worker thread
    rather than stalling the API's event loop
  - consuming: the Celery task is a sync function that drives the coroutine
    with ``asyncio.run``

celery is an optional dependency, imported inside this module. The factory
only loads it when JOBS_PROVIDER=celery.
"""

import asyncio
from typing import Any

from celery import Celery

from fastforge_jobs.interfaces.task_queue import TaskQueue
from fastforge_jobs.registry import get_handler, run_task

# One Celery task dispatches every job by name — same approach as the Taskiq
# adapter, so adding a handler never means touching broker configuration.
DISPATCH_TASK_NAME = "fastforge.dispatch"


def build_app(broker_url: str, result_backend_url: str | None = None) -> Celery:
    """Create the Celery app and register the registry dispatcher on it."""
    app = Celery("fastforge", broker=broker_url, backend=result_backend_url)
    app.conf.update(
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        timezone="UTC",
        enable_utc=True,
        # Redelivers a job if the worker dies mid-task. Costs at-least-once
        # semantics, so handlers should tolerate being run twice.
        task_acks_late=True,
        worker_prefetch_multiplier=1,
    )

    # celery has no py.typed, so its decorator is untyped to mypy.
    @app.task(name=DISPATCH_TASK_NAME, bind=True, max_retries=3)  # type: ignore[untyped-decorator]
    def _dispatch(self: Any, task_name: str, kwargs: dict[str, Any]) -> None:
        try:
            # Each task gets a fresh loop. Celery's prefork worker forks after
            # start, so a loop created at import time would be unusable here.
            asyncio.run(run_task(task_name, **kwargs))
        except Exception as exc:
            # Exponential backoff: 2s, 4s, 8s. After max_retries the job lands
            # in the failed state rather than looping forever.
            raise self.retry(exc=exc, countdown=2 ** (self.request.retries + 1)) from exc

    return app


class CeleryTaskQueue(TaskQueue):
    """Enqueues onto a Celery broker."""

    def __init__(self, app: Celery) -> None:
        self._app = app

    async def enqueue(self, task_name: str, /, **kwargs: Any) -> None:
        get_handler(task_name)  # fail fast on a typo, before it hits the broker
        # send_task opens a socket to the broker — off the event loop it goes.
        await asyncio.to_thread(
            self._app.send_task,
            DISPATCH_TASK_NAME,
            kwargs={"task_name": task_name, "kwargs": kwargs},
        )

    async def close(self) -> None:
        # Celery's producer pool is process-global and closing it would break
        # any other producer in this process; Celery cleans up at exit.
        return
