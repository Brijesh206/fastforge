"""Background jobs for FastForge — swappable queue backends.

Handlers are plain async functions registered by name (see registry), so the
backend is a configuration choice: JOBS_PROVIDER=memory|taskiq|celery.
"""

from fastforge_jobs.adapters.in_memory_queue import InMemoryTaskQueue
from fastforge_jobs.config import JobsProvider, JobsSettings
from fastforge_jobs.factory import MissingJobsDependencyError, create_task_queue
from fastforge_jobs.interfaces.task_queue import TaskQueue
from fastforge_jobs.registry import (
    DuplicateTaskError,
    TaskHandler,
    UnknownTaskError,
    clear_registry,
    get_handler,
    registered_tasks,
    run_task,
    task,
)

__all__ = [
    "DuplicateTaskError",
    "InMemoryTaskQueue",
    "JobsProvider",
    "JobsSettings",
    "MissingJobsDependencyError",
    "TaskHandler",
    "TaskQueue",
    "UnknownTaskError",
    "clear_registry",
    "create_task_queue",
    "get_handler",
    "registered_tasks",
    "run_task",
    "task",
]
