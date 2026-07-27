"""In-memory adapter: the default path a fresh checkout actually runs."""

import asyncio

import pytest
from fastforge_jobs import InMemoryTaskQueue, UnknownTaskError, clear_registry, task


@pytest.fixture(autouse=True)
def _clean_registry():
    clear_registry()
    yield
    clear_registry()


async def test_enqueue_runs_the_handler() -> None:
    done = asyncio.Event()
    seen: dict[str, str] = {}

    @task("demo.work")
    async def work(*, value: str) -> None:
        seen["value"] = value
        done.set()

    queue = InMemoryTaskQueue()
    await queue.enqueue("demo.work", value="payload")
    await asyncio.wait_for(done.wait(), timeout=1)

    assert seen == {"value": "payload"}
    await queue.close()


async def test_enqueue_does_not_block_the_caller() -> None:
    """The whole point: the request returns before the job finishes."""
    release = asyncio.Event()
    finished = False

    @task("demo.slow")
    async def slow() -> None:
        nonlocal finished
        await release.wait()
        finished = True

    queue = InMemoryTaskQueue()
    await queue.enqueue("demo.slow")

    assert finished is False  # enqueue returned while the job is still waiting

    release.set()
    await queue.close()
    assert finished is True


async def test_unknown_task_raises_at_the_call_site() -> None:
    """A typo must fail where it was made, not vanish into a background task."""
    queue = InMemoryTaskQueue()

    with pytest.raises(UnknownTaskError):
        await queue.enqueue("demo.nope")

    await queue.close()


async def test_handler_failure_does_not_propagate_to_caller() -> None:
    failed = asyncio.Event()

    @task("demo.boom")
    async def boom() -> None:
        failed.set()
        raise RuntimeError("job exploded")

    queue = InMemoryTaskQueue()
    await queue.enqueue("demo.boom")  # must not raise
    await asyncio.wait_for(failed.wait(), timeout=1)
    await queue.close()  # must not raise either


async def test_close_drains_in_flight_jobs() -> None:
    """Shutdown must not silently drop work that was already accepted."""
    completed: list[int] = []

    @task("demo.drain")
    async def drain(*, n: int) -> None:
        await asyncio.sleep(0.01)
        completed.append(n)

    queue = InMemoryTaskQueue()
    for n in range(5):
        await queue.enqueue("demo.drain", n=n)

    await queue.close()

    assert sorted(completed) == [0, 1, 2, 3, 4]
