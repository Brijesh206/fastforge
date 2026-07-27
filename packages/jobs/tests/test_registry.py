"""Registry behaviour: the contract every adapter depends on."""

import pytest
from fastforge_jobs import (
    DuplicateTaskError,
    UnknownTaskError,
    clear_registry,
    get_handler,
    registered_tasks,
    run_task,
    task,
)


@pytest.fixture(autouse=True)
def _clean_registry():
    clear_registry()
    yield
    clear_registry()


async def test_registered_handler_runs_with_kwargs() -> None:
    seen: dict[str, str] = {}

    @task("demo.echo")
    async def echo(*, message: str) -> None:
        seen["message"] = message

    await run_task("demo.echo", message="hello")

    assert seen == {"message": "hello"}


def test_decorator_returns_handler_unchanged() -> None:
    """Handlers stay plain callables, so they're testable without a broker."""

    async def original(*, x: int) -> None: ...

    decorated = task("demo.plain")(original)

    assert decorated is original


def test_unknown_task_lists_what_is_registered() -> None:
    @task("demo.known")
    async def known() -> None: ...

    with pytest.raises(UnknownTaskError) as exc:
        get_handler("demo.typo")

    assert "demo.typo" in str(exc.value)
    assert "demo.known" in str(exc.value)


def test_duplicate_name_from_different_handler_is_rejected() -> None:
    @task("demo.dup")
    async def first() -> None: ...

    with pytest.raises(DuplicateTaskError):

        @task("demo.dup")
        async def second() -> None: ...


def test_reregistering_same_function_is_allowed() -> None:
    """Module re-import under pytest's importlib mode must not blow up."""

    async def handler() -> None: ...

    task("demo.same")(handler)
    task("demo.same")(handler)

    assert get_handler("demo.same") is handler


def test_registered_tasks_returns_a_copy() -> None:
    @task("demo.copy")
    async def handler() -> None: ...

    snapshot = registered_tasks()
    snapshot.clear()

    assert "demo.copy" in registered_tasks()
