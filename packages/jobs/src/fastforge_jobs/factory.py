"""Task queue provider selection."""

from fastforge_jobs.adapters.in_memory_queue import InMemoryTaskQueue
from fastforge_jobs.config import JobsSettings
from fastforge_jobs.interfaces.task_queue import TaskQueue


class MissingJobsDependencyError(RuntimeError):
    """Raised when the selected provider's optional dependency isn't installed."""


def create_task_queue(settings: JobsSettings) -> TaskQueue:
    """Build the task queue backend named by configuration.

    taskiq and celery are optional extras, imported only when selected, so an
    install that uses neither doesn't carry them.
    """
    if settings.provider == "taskiq":
        try:
            from fastforge_jobs.adapters.taskiq_queue import TaskiqTaskQueue, build_broker
        except ImportError as exc:  # pragma: no cover - depends on install extras
            raise MissingJobsDependencyError(
                "JOBS_PROVIDER=taskiq needs the taskiq extra: uv add 'fastforge-jobs[taskiq]'"
            ) from exc
        return TaskiqTaskQueue(build_broker(settings.broker_url))

    if settings.provider == "celery":
        try:
            from fastforge_jobs.adapters.celery_queue import CeleryTaskQueue, build_app
        except ImportError as exc:  # pragma: no cover - depends on install extras
            raise MissingJobsDependencyError(
                "JOBS_PROVIDER=celery needs the celery extra: uv add 'fastforge-jobs[celery]'"
            ) from exc
        return CeleryTaskQueue(build_app(settings.broker_url, settings.result_backend_url))

    return InMemoryTaskQueue()
