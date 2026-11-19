# python 810_thread_safe_queues_and_worker_pools.py

from concurrent.futures import ThreadPoolExecutor
import queue
import threading
import time


def thread_pool_submit_map_and_exceptions() -> None:

    # When a raw threading.Thread(target=fn) raises an unhandled exception,
    # Python prints a traceback to stderr and lets the worker thread die
    # silently. Calling thread.join() on the main thread still returns None,
    # giving your caller zero programmatic signal that the job failed!
    #
    # concurrent.futures.ThreadPoolExecutor fixes both lifecycle and error
    # propagation:
    # - Entering with ThreadPoolExecutor(max_workers=N) as pool: guarantees
    #   exiting the with block calls pool.shutdown(wait=True), so no worker
    #   threads leak past the block.
    # - pool.submit(fn, *args) schedules one call and immediately returns a
    #   Future[T] handle representing the eventual outcome. Calling
    #   future.result() either returns the worker's value OR re-raises the exact
    #   exception raised on the worker thread!
    # - as_completed(futures) yields each Future the moment it finishes (fastest
    #   first), whereas pool.map(fn, iterable) yields results strictly in the
    #   original submission order.
    #
    #     Suppose 3 tasks take 0.03s, 0.01s, and 0.02s respectively:
    #         as_completed(futures) yields task 1, then task 2, then task 0.
    #         list(pool.map(fn, [0, 1, 2])) always yields [res0, res1, res2],
    #         waiting on slow task 0 before surfacing already-finished task 1!

    with ThreadPoolExecutor(max_workers=2) as pool:
        starter_fut = pool.submit(lambda value: value * 2, 21)
        print("Starter ThreadPoolExecutor result:", starter_fut.result())

    # Fan out 6 I/O jobs with pool.submit and as_completed:
    # Import Future and as_completed from concurrent.futures inside this
    # function. Define def simulate_io(task_id: int) -> str: that sleeps
    # time.sleep(0.01 * (4 - (task_id % 3))) so later IDs finish faster, then
    # returns f"task-{task_id}-ok".
    # Inside with ThreadPoolExecutor(max_workers=3) as pool:, build
    # futures: dict[Future[str], int] = {pool.submit(simulate_io, i): i for i in range(6)}.
    # Iterate for fut in as_completed(futures):, unpack task_id = futures[fut]
    # and result = fut.result(), record completion order, and print each line.


    # Contrast pool.map against as_completed on the exact same 6 task IDs:
    # Inside with ThreadPoolExecutor(max_workers=3) as pool:, compute
    # ordered = list(pool.map(simulate_io, range(6))) and print ordered.
    # Confirm ordered matches ["task-0-ok", ..., "task-5-ok"] in submission
    # order even though the underlying sleeps finished out of order.


    # Practice catching worker exceptions cleanly around future.result():
    # Define def flaky_io(task_id: int) -> str: that sleeps 0.01s, raises
    # ValueError(f"bad id {task_id}") when task_id == 2, and otherwise returns
    # f"ok-{task_id}".
    # Submit range(5) to a ThreadPoolExecutor(max_workers=3), collect succeeded: list[str] = []
    # and failed: list[int] = [], and wrap fut.result() inside
    # try ... except ValueError as err: as you iterate as_completed(futures).
    # Assert len(succeeded) == 4 and failed == [2], then print both lists.


    # Test Future timeouts without blocking forever:
    # Submit time.sleep(0.06) to a pool, call fut.result(timeout=0.01) inside
    # try ... except TimeoutError:, and print a confirmation when the short
    # timeout fires (note the pool context manager still waits for the worker
    # to finish on exit).


def bounded_queues_and_backpressure() -> None:

    # When tasks stream continuously into long-lived worker threads,
    # queue.Queue(maxsize=N) provides a thread-safe FIFO channel built on a
    # deque plus threading.Condition variables.
    #
    # Setting maxsize > 0 enforces backpressure: once N items sit in the queue,
    # q.put(item) blocks the producer until a consumer removes one with q.get().
    # That prevents a fast producer from piling millions of pending items into
    # RAM while slow consumers fall behind.
    #
    # Two rules keep queue pipelines from hanging at shutdown:
    # - Every q.get() MUST pair with q.task_done() inside a finally: block!
    #   Calling q.join() waits until the unfinished-task counter hits zero—not
    #   merely until the queue looks empty. Skipping task_done() on an error
    #   deadlocks q.join() forever.
    # - Put one None sentinel ("poison pill") per consumer thread after all real
    #   items so every worker breaks out of its while True: loop cleanly (note
    #   Python 3.13+ also added q.shutdown() / queue.ShutDown).
    #
    #     Suppose q = queue.Queue(maxsize=2) feeds 2 consumers:
    #         Producer puts 6 items, then puts None TWICE (one per consumer).
    #         Each consumer pulls an item, runs try ... finally: q.task_done(),
    #         and breaks when item is None. Then q.join() returns cleanly!

    starter_q: queue.Queue[str] = queue.Queue(maxsize=2)
    starter_q.put("ping")
    first = starter_q.get()
    starter_q.task_done()
    print(f"Starter queue round-trip: {first!r} (thread={threading.current_thread().name})")

    # Build a single-consumer bounded producer-consumer pipeline:
    # Create bounded_q: queue.Queue[str | None] = queue.Queue(maxsize=4) and
    # processed: list[str] = [].
    # Define def consumer() -> None: running while True:
    # - item = bounded_q.get()
    # - wrap handling in try ... finally: bounded_q.task_done()
    # - if item is None: break
    # - sleep time.sleep(0.005) and append item.upper() to processed.
    # Start worker = threading.Thread(target=consumer), enqueue "job-0" .. "job-7"
    # followed by None, call bounded_q.join() and worker.join(), assert
    # len(processed) == 8, and print processed.


    # Scale up to 2 concurrent consumers sharing one bounded queue:
    # Create multi_q: queue.Queue[int | None] = queue.Queue(maxsize=3),
    # results: list[tuple[str, int]] = [], and out_lock = threading.Lock().
    # Spawn 2 named consumer threads ("c1", "c2") that square each int, append
    # (threading.current_thread().name, item * item) under out_lock, and always
    # call multi_q.task_done() in finally:.
    # Enqueue range(10) followed by TWO None sentinels (one per consumer!), wait
    # on multi_q.join() and both threads, and assert len(results) == 10.


    # Practice non-blocking overload rejection with put_nowait and get_nowait:
    # Create tiny_q: queue.Queue[str] = queue.Queue(maxsize=1), put "first" with
    # tiny_q.put_nowait("first"), then attempt tiny_q.put_nowait("overflow")
    # inside try ... except queue.Full: to print an overload warning.
    # Drain "first" with tiny_q.get_nowait(), then call tiny_q.get_nowait()
    # again inside try ... except queue.Empty: to confirm empty detection.


def main() -> None:

    print("=== 1. ThreadPoolExecutor: submit, map, and worker exceptions ===")
    thread_pool_submit_map_and_exceptions()

    print("\n=== 2. Bounded queue.Queue and backpressure ===")
    bounded_queues_and_backpressure()


if __name__ == "__main__":
    main()
