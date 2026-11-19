# python 830_asyncio_coroutines_and_event_loop.py

import asyncio
import time


async def coroutines_sequential_vs_concurrent() -> None:

    # An asyncio program runs thousands of concurrent I/O waits on ONE OS thread
    # driven by an event loop. Unlike preemptive threads that the OS can pause
    # mid-statement, an async def coroutine yields control to the event loop
    # ONLY when it hits an explicit await expression (such as awaiting a timer,
    # socket, or async queue). Between await points, no other coroutine runs, so
    # in-memory state updates cannot race!
    #
    # Calling an async def function does NOT run its body—it merely builds an
    # unstarted coroutine object. Dropping that object without await or
    # asyncio.create_task() leaves the body unexecuted and emits RuntimeWarning:
    # coroutine was never awaited.
    #
    # Just as important: writing two awaits back-to-back runs them SERIALLY!
    #
    #     Suppose fetch_sensor(id, 0.04) awaits asyncio.sleep(0.04):
    #         await fetch_sensor(1, 0.04)
    #         await fetch_sensor(2, 0.04)   # total = 0.04 + 0.04 = 0.08s
    #
    #         await asyncio.gather(
    #             fetch_sensor(1, 0.04),
    #             fetch_sensor(2, 0.04),
    #         )                             # total = max(0.04, 0.04) = 0.04s
    #
    # In the sequential version, the second coroutine is not even created until
    # the first finishes; asyncio.gather() schedules all coroutines onto the
    # event loop together so their waits overlap.

    started = time.perf_counter()
    await asyncio.sleep(0.005)
    print(f"Starter async sleep finished in {(time.perf_counter() - started) * 1000:.1f} ms")

    # Define async def fetch_sensor(sensor_id: int, delay: float) -> tuple[int, float]:
    # inside this function that awaits asyncio.sleep(delay) and returns
    # (sensor_id, delay).
    # Measure sequential timing first: await fetch_sensor(1, 0.04),
    # fetch_sensor(2, 0.04), and fetch_sensor(3, 0.04) one after another using
    # time.perf_counter() and store seq_s.
    # Measure concurrent timing next: run the same 3 calls together via
    # readings = await asyncio.gather(fetch_sensor(1, 0.04), fetch_sensor(2, 0.04), fetch_sensor(3, 0.04))
    # and store conc_s. Print readings, seq_s (~0.12s), and conc_s (~0.04s),
    # and assert conc_s < seq_s.


    # Observe asyncio.gather(..., return_exceptions=True) error isolation:
    # Define async def maybe_fail(idx: int) -> str: that awaits
    # asyncio.sleep(0.01), raises ValueError(f"sensor {idx} offline") when
    # idx == 2, and returns f"sensor-{idx}-ok" otherwise.
    # Run outcomes = await asyncio.gather(maybe_fail(1), maybe_fail(2), maybe_fail(3), return_exceptions=True)
    # and print outcomes to see the ValueError returned as data instead of
    # aborting the call.
    #
    # Try uncommenting below to observe RuntimeWarning on an unawaited coroutine:
    # fetch_sensor(99, 0.01)


async def strong_task_references_and_cancellation() -> None:

    # Two subtle runtime rules separate reliable asyncio services from flaky
    # ones:
    # - Strong references for background tasks: asyncio.create_task(coro) only
    #   registers a WEAK reference inside the event loop! If you call
    #   asyncio.create_task(coro) without storing the returned Task handle, the
    #   garbage collector can destroy that running task mid-flight before it
    #   finishes. The standard Python pattern is storing tasks in a set and
    #   detaching them on completion:
    #
    #       background_tasks: set[asyncio.Task[str]] = set()
    #       task = asyncio.create_task(work())
    #       background_tasks.add(task)
    #       task.add_done_callback(background_tasks.discard)
    #
    # - Cooperative cancellation with task.cancel(): calling task.cancel()
    #   injects asyncio.CancelledError at the coroutine's next await point.
    #   Notice CancelledError inherits from BaseException (NOT Exception!), so
    #   except Exception: will not accidentally swallow cancellation. Put
    #   cleanup in try ... finally: (or catch asyncio.CancelledError, clean up,
    #   and immediately re-raise it!).
    #
    #     Suppose a streaming loop awaits asyncio.sleep(1.0) inside try ... finally::
    #         Caller runs task.cancel() then awaits task.
    #         The sleeping await raises CancelledError, finally: flushes state,
    #         and the caller receives CancelledError confirming clean shutdown.

    starter_task = asyncio.create_task(asyncio.sleep(0.002, result="ready"))
    print("Starter task result:", await starter_task)

    # Practice the strong-reference Task set pattern:
    # Create bg_tasks: set[asyncio.Task[str]] = set().
    # Define async def background_ping(idx: int) -> str: awaiting
    # asyncio.sleep(0.01 * idx) and returning f"pong-{idx}".
    # Loop for idx in range(1, 4): create task = asyncio.create_task(background_ping(idx)),
    # call bg_tasks.add(task), and register task.add_done_callback(bg_tasks.discard).
    # Print len(bg_tasks) while tasks are active (expected: 3), await
    # results = await asyncio.gather(*list(bg_tasks)), print results, and
    # assert len(bg_tasks) == 0 afterward so no finished tasks leak in the set!


    # Practice task.cancel() and CancelledError cleanup:
    # Create cleanup_log: list[str] = [] and define async def long_listener() -> None:
    # wrapping while True: await asyncio.sleep(0.05) inside
    # try ... except asyncio.CancelledError: cleanup_log.append("cancelled"); raise
    # and finally: cleanup_log.append("closed").
    # Schedule listener = asyncio.create_task(long_listener()), pause briefly
    # with await asyncio.sleep(0.015), call listener.cancel(), and await
    # listener inside try ... except asyncio.CancelledError:.
    # Assert listener.cancelled() and cleanup_log == ["cancelled", "closed"],
    # then print cleanup_log.


async def offloading_blocking_calls_with_to_thread() -> None:

    # Because an asyncio event loop runs on a single OS thread, calling a
    # blocking synchronous function like time.sleep(0.05) or blocking file/C
    # I/O directly inside async def freezes the ENTIRE event loop—every other
    # coroutine stops making progress until the blocking call returns!
    #
    # When you must call synchronous blocking code from async def, wrap it with
    # await asyncio.to_thread(fn, arg1, arg2). Python runs fn on a background
    # worker thread from the default ThreadPoolExecutor and yields control back
    # to the event loop until the thread completes.
    #
    #     Suppose a heartbeat coroutine ticks every 0.01s while checksum() sleeps
    #     synchronously for 0.04s:
    #         Direct call: heartbeat freezes at 0 ticks until checksum() returns.
    #         asyncio.to_thread: heartbeat ticks ~3-4 times concurrently!

    quick_sum = await asyncio.to_thread(sum, b"abc")
    print("Starter asyncio.to_thread sum(b'abc'):", quick_sum)

    # Offload a blocking helper without stalling a concurrent heartbeat:
    # Define def blocking_checksum(payload: bytes) -> int: that calls
    # time.sleep(0.04) and returns sum(payload).
    # Define async def heartbeat(ticks: list[int]) -> None: that loops 4 times
    # awaiting asyncio.sleep(0.01) and appending len(ticks) + 1 to ticks.
    # Run ticks: list[int] = [] and checksum, _ = await asyncio.gather(
    # asyncio.to_thread(blocking_checksum, b"telemetry"), heartbeat(ticks)).
    # Print checksum and ticks (verify ticks grew concurrently during the 40 ms
    # blocking sleep!).
    #
    # Try experimenting afterward: replace asyncio.to_thread(blocking_checksum, ...)
    # with a coroutine calling blocking_checksum(b"telemetry") directly before
    # yielding, and watch how the heartbeat freezes until the sleep finishes.


async def async_main() -> None:

    print("=== 1. Coroutines: sequential vs concurrent timing ===")
    await coroutines_sequential_vs_concurrent()

    print("\n=== 2. Strong Task references and cooperative cancellation ===")
    await strong_task_references_and_cancellation()

    print("\n=== 3. Offloading blocking calls with asyncio.to_thread ===")
    await offloading_blocking_calls_with_to_thread()


def main() -> None:

    # asyncio.run() creates a fresh event loop, drives async_main() to
    # completion, cancels any leftover tasks, and closes the loop cleanly.
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
