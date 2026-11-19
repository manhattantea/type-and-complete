# python 840_asyncio_taskgroups_queues_and_timeouts.py

import asyncio
import time


async def taskgroups_semaphores_and_exception_groups() -> None:

    # Legacy asyncio.gather(a(), b(), c()) has a dangerous cleanup gap: if a()
    # raises an exception, gather immediately raises to the caller while leaving
    # b() and c() running unattended as orphaned background tasks!
    #
    # Python 3.11+ introduced Structured Concurrency via
    # async with asyncio.TaskGroup() as tg::
    # - Every task spawned with tg.create_task(coro) belongs to the TaskGroup
    #   block and stays strongly referenced automatically.
    # - Exiting the async with block waits for every child task to finish.
    # - If ANY child task raises an exception (other than CancelledError), the
    #   TaskGroup immediately cancels all sibling tasks, waits for their
    #   finally: or async with cleanup blocks to run, and raises an
    #   ExceptionGroup containing every failure.
    #
    # To catch specific errors inside an ExceptionGroup, Python 3.11+ adds
    # except* SomeError as eg:. Unlike ordinary except, except* splits the
    # group by type and passes matching exceptions in eg.exceptions—so multiple
    # except* blocks can even run for the same ExceptionGroup!
    #
    # Pairing TaskGroup with asyncio.Semaphore(limit) caps concurrent in-flight
    # tasks: async with sem: allows at most limit coroutines inside the critical
    # section at once so fanning out 10_000 jobs never opens 10_000 sockets.
    #
    #     Suppose TaskGroup spawns sibling (sleeping 0.5s with a finally: log)
    #     and failing_job (raising RuntimeError after 0.01s):
    #         At t=0.01s, failing_job raises -> TaskGroup cancels sibling ->
    #         sibling's finally: logs "cancelled" -> except* RuntimeError catches
    #         the ExceptionGroup with zero leaked background tasks!

    async with asyncio.TaskGroup() as tg:
        starter = tg.create_task(asyncio.sleep(0.005, result="group-ok"))
    print("Starter TaskGroup result:", starter.result())

    # Fan out 5 rate-limited jobs with TaskGroup and Semaphore(2):
    # Create sem = asyncio.Semaphore(2), active = [0], peak = [0].
    # Define async def bounded_job(job_id: int) -> str: that enters
    # async with sem:, increments active[0] += 1, updates
    # peak[0] = max(peak[0], active[0]), awaits asyncio.sleep(0.02) inside
    # try ... finally: active[0] -= 1, and returns f"job-{job_id}".
    # Launch 5 tasks inside async with asyncio.TaskGroup() as tg:, collect
    # results = [t.result() for t in tasks] after the block, assert peak[0] <= 2,
    # and print results and peak[0].


    # Prove live sibling cancellation and ExceptionGroup handling with except*:
    # Create events: list[str] = [].
    # Define async def slow_sibling() -> None: that awaits asyncio.sleep(0.5)
    # inside try ... finally: events.append("sibling-cleaned-up").
    # Define async def crashing_job() -> None: that awaits asyncio.sleep(0.01)
    # and raises RuntimeError("boom").
    # Run both inside async with asyncio.TaskGroup() as tg: wrapped in
    # try ... except* RuntimeError as eg:. Print [str(e) for e in eg.exceptions],
    # and assert events == ["sibling-cleaned-up"] to verify no orphan remained!


    # Practice splitting two failure types with multiple except* clauses:
    # Inside a TaskGroup, launch one task raising ValueError("bad-payload") and
    # another raising KeyError("missing-id") after 0.005s. Catch them with both
    # except* ValueError as veg: and except* KeyError as keg: in the same try
    # block, and print both matched exception lists!


async def async_queues_and_backpressure() -> None:

    # asyncio.Queue(maxsize=N) is the async twin of queue.Queue (Primer 810):
    # it coordinates producer and consumer coroutines on one event loop with
    # automatic backpressure.
    # - When N items are already buffered, await q.put(item) suspends only the
    #   producer coroutine until a consumer calls await q.get().
    # - Every await q.get() MUST pair with q.task_done() inside finally: so
    #   await q.join() resolves once all items finish processing.
    # - Notice q.task_done() is synchronous (no await), whereas q.put(),
    #   q.get(), and q.join() are coroutines (require await)!
    #
    #     Suppose q = asyncio.Queue(maxsize=2) connects 1 producer and 2 workers:
    #         Producer puts 6 integers plus two None shutdown sentinels.
    #         Each worker pulls until None, calling q.task_done() in finally:.
    #         When await q.join() returns, all 6 items and both sentinels are done.

    starter_q: asyncio.Queue[str] = asyncio.Queue(maxsize=2)
    await starter_q.put("seed")
    got = await starter_q.get()
    starter_q.task_done()
    print("Starter asyncio.Queue item:", got)

    # Build a bounded producer-consumer asyncio.Queue(maxsize=2) pipeline:
    # Create q: asyncio.Queue[int | None] = asyncio.Queue(maxsize=2),
    # processed: list[tuple[int, int]] = [], and backpressure_hits = [0].
    # Define async def producer() -> None: that loops for n in range(6):
    # checking if q.full(): backpressure_hits[0] += 1 before await q.put(n),
    # then puts None twice (once for each of 2 workers).
    # Define async def worker(wid: int) -> None: looping while True:, awaiting
    # item = await q.get(), wrapping handling in try ... finally: q.task_done(),
    # breaking on item is None, awaiting asyncio.sleep(0.01), and appending
    # (wid, item * 10) to processed.
    # Run producer() and worker(0), worker(1) inside async with asyncio.TaskGroup() as tg:,
    # await q.join(), assert len(processed) == 6, and print backpressure_hits[0]
    # and sorted(processed).


    # Practice non-blocking queue probes with put_nowait and get_nowait:
    # Create tiny_q: asyncio.Queue[str] = asyncio.Queue(maxsize=1), push "a" via
    # tiny_q.put_nowait("a"), catch asyncio.QueueFull on tiny_q.put_nowait("b"),
    # pop "a" with tiny_q.get_nowait(), and catch asyncio.QueueEmpty on a second
    # get_nowait().


async def timeouts_async_generators_and_context_managers() -> None:

    # Three more async building blocks show up in almost every real service:
    # - async with asyncio.timeout(seconds): (Python 3.11+) enforces a deadline
    #   across an entire block of awaits, cancelling whatever is still pending
    #   when time runs out and raising standard TimeoutError.
    # - Async generators (async def containing yield) implement __aiter__ and
    #   __anext__ automatically so you can stream asynchronous values using
    #   async for x in gen: (or an async comprehension [x async for x in gen]).
    # - Async context managers implement async def __aenter__(self) and
    #   async def __aexit__(self, exc_type, exc, tb) so resource setup and
    #   teardown (such as opening a DB session or flushing a network stream)
    #   can themselves await I/O via async with resource as handle:.
    #
    #     Suppose class AsyncSession logs "open" in __aenter__ and "close" in
    #     __aexit__ (returning False so exceptions are not suppressed):
    #         Even if the body inside async with raises RuntimeError, Python
    #         still awaits __aexit__ so "close" is guaranteed to run!

    async with asyncio.timeout(0.1):
        await asyncio.sleep(0.005)
    print(f"Starter asyncio.timeout passed cleanly (clock={time.monotonic():.2f})")

    # Enforce a tight deadline with asyncio.timeout:
    # Record started = time.perf_counter(), run await asyncio.sleep(0.2) inside
    # async with asyncio.timeout(0.02): wrapped in try ... except TimeoutError:,
    # compute elapsed = time.perf_counter() - started, assert elapsed < 0.1,
    # and print a timeout confirmation with elapsed ms.


    # Stream values with an async generator and async for:
    # Import AsyncIterator from collections.abc inside this function and define
    # async def ticker(n: int) -> AsyncIterator[int]: looping for i in range(n):,
    # awaiting asyncio.sleep(0.01), and yielding i.
    # Consume ticker(4) first with an async for tick in ticker(4): loop, then
    # again with an async comprehension ticks = [t async for t in ticker(4)],
    # and assert ticks == [0, 1, 2, 3].


    # Implement a custom async context manager using __aenter__ and __aexit__:
    # Define class AsyncConnection: storing self.name: str and
    # self.lifecycle: list[str] = [].
    # Implement async def __aenter__(self) -> AsyncConnection: awaiting
    # asyncio.sleep(0.005), appending f"open:{self.name}", and returning self.
    # Implement async def __aexit__(self, exc_type: object, exc: object, tb: object) -> bool:
    # awaiting asyncio.sleep(0.005), appending f"close:{self.name}", and
    # returning False.
    # Test it twice: once normally inside async with AsyncConnection("db") as conn:,
    # and once raising ValueError("abort") inside try ... except ValueError:,
    # asserting conn.lifecycle == ["open:db", "close:db"] in both cases!


async def async_main() -> None:

    print("=== 1. TaskGroup, Semaphore, and except* ExceptionGroup ===")
    await taskgroups_semaphores_and_exception_groups()

    print("\n=== 2. Bounded asyncio.Queue and backpressure ===")
    await async_queues_and_backpressure()

    print("\n=== 3. asyncio.timeout, async for, and async with ===")
    await timeouts_async_generators_and_context_managers()


def main() -> None:

    asyncio.run(async_main())


if __name__ == "__main__":
    main()
