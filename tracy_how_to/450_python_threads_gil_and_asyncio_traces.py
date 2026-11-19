# python 450_python_threads_gil_and_asyncio_traces.py

import asyncio
from dataclasses import dataclass
import json
import sys
import threading
import time

# Spawning Python threads does not automatically parallelize CPU work. On a
# timeline trace, concurrency bottlenecks appear in three distinct shapes:
# - GIL-serialized CPU threads: on standard CPython (sys._is_gil_enabled() == True),
#   only one thread can execute Python bytecode at a time. Four CPU-bound threads
#   form a sequential staircase across their OS thread rows while paying context-
#   switch and GIL handoff overhead. By contrast, time.sleep and native C/Odin
#   calls that release the GIL overlap concurrently across OS thread IDs.
# - Explicit threading.Lock contention: even when work releases the GIL (or runs
#   under free-threaded Python), a shared mutex forces workers to wait in line.
# - Blocked asyncio event loops: asyncio runs all coroutines on one OS thread by
#   yielding at every await. Calling a synchronous blocking function such as
#   time.sleep inside a coroutine freezes the entire event-loop thread!
#
# To separate active CPU execution from waiting in pure Python, compare two clocks:
# - time.perf_counter_ns() measures wall-clock time (wall_ns).
# - time.thread_time_ns() measures only OS-scheduled CPU time on that thread (cpu_ns).
# Subtracting them (max(0, wall_ns - cpu_ns)) exposes off-CPU wait time spent
# sleeping, blocked on a Lock, or stalled waiting for the GIL.


@dataclass(frozen=True, slots=True)
class ThreadZoneEvent:
    name: str
    thread_name: str
    native_tid: int
    start_ns: int
    wall_ns: int
    cpu_ns: int

    @property
    def off_cpu_wait_ns(self) -> int:

        return max(0, self.wall_ns - self.cpu_ns)


# Define class ConcurrencyTraceRecorder:
# - __init__(self) -> None: store self._lock = threading.Lock() and
#   self.events: list[ThreadZoneEvent] = [].
# - @contextmanager def thread_zone(self, name: str) -> Iterator[None]:
#   (import contextmanager from contextlib and Iterator from collections.abc).
#   Capture start_wall = time.perf_counter_ns() and start_cpu = time.thread_time_ns(),
#   yield inside try: ... finally:, then append ThreadZoneEvent(name,
#   threading.current_thread().name, threading.get_native_id(), start_wall,
#   time.perf_counter_ns() - start_wall, time.thread_time_ns() - start_cpu)
#   to self.events while holding self._lock.
# - @asynccontextmanager async def async_zone(self, name: str) -> AsyncIterator[None]:
#   (import asynccontextmanager from contextlib and AsyncIterator from collections.abc).
#   Record the coroutine span labeled f"async:{name}" using perf_counter_ns()
#   and thread_time_ns() around yield inside try: ... finally: under self._lock.
# - def export_chrome_json(self) -> str: compute origin_ns = min(e.start_ns for e in self.events),
#   emit Chrome Tracing "ph": "X" dicts with "name": e.name, "ts": (e.start_ns - origin_ns) / 1000.0,
#   "dur": e.wall_ns / 1000.0, "pid": 1, "tid": e.native_tid, and return json.dumps(spans).


def gil_cpu_vs_io_threads() -> None:

    # Notice why mixing time.sleep inside a lock hides the GIL story: sleeping
    # releases the GIL intentionally, whereas pure-Python arithmetic holds the
    # GIL for up to sys.getswitchinterval() (5 ms by default) before handing off
    # to another thread. Comparing pure-Python CPU workers (no locks, no sleep)
    # against pure time.sleep I/O workers isolates the GIL cleanly.
    #
    # Suppose 3 threads each run 40 ms of pure-Python hashing. On GIL-enabled
    # CPython, total wall time is ~120 ms (or more) even though all 3 threads ran
    # "in parallel". Run 3 threads calling time.sleep(0.05) instead and total wall
    # time is ~50 ms because sleep drops the GIL immediately.

    gil_enabled = getattr(sys, "_is_gil_enabled", lambda: True)()
    t0_wall = time.perf_counter_ns()
    t0_cpu = time.thread_time_ns()
    print(
        f"Main thread={threading.current_thread().name!r} | "
        f"native_tid={threading.get_native_id()} | GIL enabled={gil_enabled} | "
        f"clock_sample=({t0_wall % 1000}, {t0_cpu % 1000})"
    )

    # Implement ConcurrencyTraceRecorder above and write two isolated workers:
    # - cpu_bound_worker(recorder: ConcurrencyTraceRecorder, n: int = 350_000) -> int
    #   running pure-Python integer mixing inside with recorder.thread_zone("GIL_CPU"):
    #   with zero locks and zero sleep calls. Measure 1 single-threaded baseline vs
    #   3 threads ("CPU-0", "CPU-1", "CPU-2") and compare total_wall_ms against
    #   sum(e.cpu_ns) / 1e6 and off_cpu_wait_ns.
    # - io_sleep_worker(recorder: ConcurrencyTraceRecorder, delay_s: float = 0.05) -> None
    #   calling time.sleep(delay_s) inside with recorder.thread_zone("GIL_Released_IO"):.
    #   Run 3 threads ("IO-0", "IO-1", "IO-2"), print each event's wall_ms, cpu_ms,
    #   and off_cpu_wait_ms, and assert total_wall_ms < sum(e.wall_ns for e in io_events) / 1e6.


def lock_wait_vs_hold_contention() -> None:

    # Even when threads do not fight over the GIL, acquiring a shared
    # threading.Lock around slow work serializes every worker behind the lock
    # holder. Measuring wait_ns = t_acquired - t_before_acquire separately from
    # hold_ns = t_release - t_acquired tells you immediately whether threads are
    # stalling outside a critical section.

    probe_lock = threading.Lock()
    with probe_lock:
        locked_inside = probe_lock.locked()
    print(f"Lock probe: locked_inside={locked_inside}, locked_after={probe_lock.locked()}")

    # Write a contended lock helper or timed_lock context manager measuring wait_ns
    # around shared_lock.acquire() and hold_ns until shared_lock.release(). Run 3
    # worker threads ("Lock-0".."Lock-2") each holding shared_lock while running
    # time.sleep(0.02) and updating shared_total[0] += 1; print per-thread wait_ms
    # and hold_ms (notice 2 threads wait ~20 ms and ~40 ms while one runs!).


    # Remediate the lock bottleneck: move the 0.02 s work outside shared_lock so
    # each worker only acquires shared_lock briefly at the end to merge its local
    # result into shared_total[0]. Re-run all 3 threads and verify total wall time
    # drops ~3x while wait_ms approaches 0 ms.


def asyncio_freeze_and_to_thread_fix() -> None:

    # Asyncio multiplexes thousands of I/O tasks on a single OS thread by pausing
    # each coroutine at await and running ready siblings on the event loop. If one
    # coroutine executes synchronous time.sleep(0.05) instead of await asyncio.sleep
    # or await asyncio.to_thread(...), it never returns control to the event loop
    # and freezes every sibling coroutine on that tid!

    asyncio.run(asyncio.sleep(0.0))
    sample_span = {"ph": "X", "name": "async:Probe", "ts": 0.0, "dur": 10.0, "pid": 1, "tid": 1}
    print(f"Asyncio runtime ready | Sample multi-tid Chrome span: {json.dumps(sample_span)}")

    # Demonstrate the event-loop freeze: write
    # blocking_sync_task(recorder: ConcurrencyTraceRecorder, name: str, delay_s: float = 0.05) -> str
    # calling synchronous time.sleep(delay_s) inside async with recorder.async_zone(name):.
    # Run 3 copies concurrently via asyncio.gather inside asyncio.run(...) and print
    # total_wall_ms vs sum_task_ms (both ~150 ms—completely serialized on 1 tid!).


    # Fix the freeze with asyncio.to_thread: write
    # nonblocking_offload_task(recorder: ConcurrencyTraceRecorder, name: str, delay_s: float = 0.05) -> str
    # calling await asyncio.to_thread(time.sleep, delay_s) inside
    # async with recorder.async_zone(name): (plus an await asyncio.sleep(delay_s)
    # sibling). Run 3 tasks via asyncio.gather, assert total_wall_ms < sum_task_ms
    # (~50 ms wall vs ~150 ms summed task spans), then call recorder.export_chrome_json(),
    # parse it in memory with json.loads, and assert at least 2 distinct "tid"
    # values exist across your worker-thread and event-loop events!


def main() -> None:

    print("=== 1. GIL-serialized CPU threads vs. GIL-releasing I/O threads ===")
    gil_cpu_vs_io_threads()

    print("\n=== 2. Explicit threading.Lock wait vs. hold contention ===")
    lock_wait_vs_hold_contention()

    print("\n=== 3. Asyncio blocking-sleep freeze, to_thread fix, and multi-tid JSON ===")
    asyncio_freeze_and_to_thread_fix()


if __name__ == "__main__":
    main()
