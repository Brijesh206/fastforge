"""Background worker entry point.

Serves whichever backend JOBS_PROVIDER names. The worker never defines tasks —
it imports the modules that register them and hands execution to the registry,
so API and worker always agree on what a task name means.

Run it with the CLI of the backend you selected:

    # JOBS_PROVIDER=taskiq
    taskiq worker worker_app.main:broker

    # JOBS_PROVIDER=celery
    celery -A worker_app.main:celery_app worker --loglevel=info

Or just `python -m worker_app.main`, which picks the right one for you.

There is no worker for JOBS_PROVIDER=memory — those jobs run inside the API
process, so starting one would do nothing.
"""

import os
import sys

# Importing these registers their handlers. Add a line here when a new module
# defines tasks — this import list is the worker's contract with the registry.
import fastforge_mail.tasks  # noqa: F401  (import for side effect: task registration)
from fastforge_jobs import JobsSettings, registered_tasks
from fastforge_logging import LoggingSettings, configure_logging, get_logger

configure_logging(LoggingSettings(service_name="worker"))
logger = get_logger("app.worker")

settings = JobsSettings()

# Module-level names so the taskiq/celery CLIs can find them. Only the one
# matching the selected provider is built; the other stays None.
broker = None
celery_app = None

if settings.provider == "taskiq":
    from fastforge_jobs.adapters.taskiq_queue import build_broker

    broker = build_broker(settings.broker_url)
elif settings.provider == "celery":
    from fastforge_jobs.adapters.celery_queue import build_app

    celery_app = build_app(settings.broker_url, settings.result_backend_url)


def main() -> int:
    """Exec the CLI for the configured backend, replacing this process."""
    tasks = sorted(registered_tasks())
    logger.info("Worker starting", provider=settings.provider, task_count=len(tasks), tasks=tasks)

    if settings.provider == "memory":
        logger.error(
            "JOBS_PROVIDER=memory runs jobs inside the API process - there is "
            "nothing for a worker to do. Set JOBS_PROVIDER=taskiq or celery."
        )
        return 1

    target = "worker_app.main"
    if settings.provider == "taskiq":
        argv = ["taskiq", "worker", f"{target}:broker"]
    else:
        argv = ["celery", "-A", f"{target}:celery_app", "worker", "--loglevel=info"]
        if sys.platform == "win32":
            # Celery's default prefork pool needs fork(), which Windows lacks —
            # the worker starts and then never executes a task. Production runs
            # in Linux containers and keeps prefork.
            argv += ["--pool=solo"]
            logger.info("Windows detected, using --pool=solo (prefork needs fork())")

    # execvp replaces this process so the CLI owns signal handling - important
    # for graceful shutdown when Docker sends SIGTERM.
    os.execvp(argv[0], argv)


if __name__ == "__main__":
    sys.exit(main())
