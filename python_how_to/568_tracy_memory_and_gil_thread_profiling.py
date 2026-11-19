# python 568_tracy_memory_and_gil_thread_profiling.py

from array import array
import sys
import threading
import time
import tracemalloc


def per_zone_memory_tracking() -> None:

    # A slow region of code is not always CPU-bound math. Two other culprits
    # regularly masquerade as slow code: transient heap allocation churn (which
    # stresses CPython's allocator and garbage collector) and threads waiting on
    # a lock.
    #
    # Python's built-in tracemalloc module intercepts heap allocations inside
    # CPython and tracks live bytes and peak bytes. Calling
    # tracemalloc.get_traced_memory() returns a (current_bytes, peak_bytes) pair.
    # Here is a subtle measurement trap: if a function builds 2,000 temporary
    # dicts and discards them before returning, current_bytes goes right back down
    # near where it started, making net_delta look like 0 bytes!
    #
    # Calling tracemalloc.reset_peak() right as you enter a scoped memory zone
    # resets the high-water mark to current_bytes so that peak_after captures the
    # transient allocation spike that happened strictly inside that block:
    #
    #     Suppose curr_before = 10_000 bytes.
    #     Inside the zone, a temporary list allocates 90_000 bytes and is freed.
    #     On exit, curr_after = 10_000 and peak_after = 100_000.
    #     retained_bytes = curr_after - curr_before   -> 0 bytes (no leak)
    #     peak_spike_bytes = max(0, peak_after - curr_before) -> 90_000 bytes (churn!)

    starter_buf = array("d", [0.0, 1.0, 2.0, 3.0])
    print(
        f"Starter array('d') buffer: {len(starter_buf)} doubles "
        f"({len(starter_buf) * starter_buf.itemsize} raw bytes), "
        f"tracemalloc active={tracemalloc.is_tracing()}"
    )

    # Import contextmanager from contextlib and Iterator from collections.abc,
    # then define @contextmanager def mem_zone(name: str, report: list[tuple[str, int, int]]) -> Iterator[None]:
    # Assuming tracemalloc.start() is active:
    # - Read curr_before, _ = tracemalloc.get_traced_memory() and call tracemalloc.reset_peak().
    # - Yield inside try / finally.
    # - In finally, read curr_after, peak_after = tracemalloc.get_traced_memory(),
    #   compute retained_bytes = curr_after - curr_before and
    #   peak_spike_bytes = max(0, peak_after - curr_before), and append
    #   (name, retained_bytes, peak_spike_bytes) to report.


    # Enable tracemalloc.start(), create report: list[tuple[str, int, int]] = [],
    # and pre-allocate buf = array("d", [0.0] * 2_000) before entering any zone.
    # Compare three zones inside try / finally: tracemalloc.stop():
    # - "InPlaceArrayUpdate": loop for i in range(len(buf)): buf[i] = i * 0.5
    #   (minimal heap churn because the C double buffer already exists).
    # - "TransientDictChurn": build tmp = [{"id": i, "val": i * 0.5} for i in range(2_000)],
    #   sum row["val"] into total, and let tmp go out of scope (near-zero retained
    #   bytes, huge peak_spike_bytes!).
    # - "RetainedLeak": append 500 fresh dicts into a list declared outside the
    #   zone so retained_bytes stays clearly positive after exit.
    # Print each (name, retained_bytes, peak_spike_bytes) row and verify the
    # contrast between 0-churn, transient churn, and retained growth.


def lock_wait_and_hold_instrumentation() -> None:

    # When multiple threads share a threading.Lock, wall-clock duration inside a
    # worker mixes two very different intervals:
    # - wait_ns: time spent blocked waiting for another thread to release the lock.
    # - hold_ns: time spent owning the lock while running the critical section.
    #
    # Calling self._lock.acquire(blocking=False) tests immediately whether the
    # lock is free without sleeping. If it returns False, the acquisition is
    # contended: record t_wait = time.perf_counter_ns(), call blocking
    # self._lock.acquire(), and measure wait_ns = time.perf_counter_ns() - t_wait.
    #
    # Notice threading.get_native_id(): unlike Python's internal thread identity,
    # get_native_id() returns the real OS kernel thread ID (TID) that native tools
    # like Tracy or OS task monitors display alongside threading.current_thread().name.
    #
    #     Suppose Worker-1 holds TelemetryMutex for 2 ms while Worker-2 arrives.
    #     Worker-2 sees acquire(blocking=False) == False, records wait_ns ~ 2 ms,
    #     enters the critical section, holds it for 2 ms, and records hold_ns ~ 2 ms.
    #     Separating wait_ns from hold_ns tells you immediately whether a slow lock
    #     zone is doing too much work inside the lock or simply queuing behind peers.

    gil_enabled: bool = getattr(sys, "_is_gil_enabled", lambda: True)()
    print(
        f"Main thread {threading.current_thread().name!r} "
        f"(native_id={threading.get_native_id()}, GIL={gil_enabled})"
    )

    # Define class MonitoredLock wrapping a threading.Lock with wait/hold metrics:
    # - __init__(self, name: str = "SharedLock") -> None storing self.name = name,
    #   self._lock = threading.Lock(), self._acquire_ns: int = 0, and
    #   self.per_thread: dict[int, dict[str, int | str]] = {}.
    # - def acquire(self) -> None: try contended = not self._lock.acquire(blocking=False).
    #   If contended, measure wait_ns around blocking self._lock.acquire(); else wait_ns = 0.
    #   Once self._lock is held, record self._acquire_ns = time.perf_counter_ns(),
    #   look up tid = threading.get_native_id(), and update self.per_thread[tid]
    #   with name, wait_ns += wait_ns, acquires += 1, and contentions += int(contended).
    # - def release(self) -> None: compute hold_ns = time.perf_counter_ns() - self._acquire_ns
    #   BEFORE calling self._lock.release(), add hold_ns to
    #   self.per_thread[threading.get_native_id()]["hold_ns"], then release self._lock.
    # - Implement __enter__ and __exit__ so MonitoredLock works in a 'with' block.


    # Create monitored = MonitoredLock("TelemetryMutex") and shared: list[int] = [].
    # Spawn 3 named threading.Thread workers (name=f"Worker-{idx}") that each
    # loop 4 times: enter with monitored:, sleep 0.002 s to simulate critical-section
    # work, and append idx to shared.
    # Join all 3 threads, assert len(shared) == 12, and print each thread's name,
    # native_id, acquires, contentions, wait_ms, and hold_ms.


    # Verify why shrinking the critical section slashes wait_ns:
    # run a second test with a fresh MonitoredLock("TrimmedMutex") where each
    # worker performs the 0.002 s sleep OUTSIDE with monitored: and holds the lock
    # ONLY for shared.append(idx). Print total wait_ms across all threads for both
    # runs and compare the contention drop.


def tracy_cross_repo_next_steps() -> None:

    # This Primer focuses strictly on Python stdlib wrappers (tracemalloc zones
    # and MonitoredLock) so you can inspect heap churn and lock contention in any
    # Python 3.12+ script with zero native dependencies.
    #
    # When you are ready for deeper timeline forensics—Gen-0 garbage-collector
    # sweep triggers, GIL-bound vs GIL-releasing native thread isolation, asyncio
    # event-loop blocking freezes fixed via asyncio.to_thread, and multi-tid Chrome
    # Trace JSON tracks—continue into ../tracy_how_to/:
    # - ../tracy_how_to/350_python_tracy_memory_and_object_churn.py
    # - ../tracy_how_to/450_python_threads_gil_and_asyncio_traces.py

    start_ns = time.perf_counter_ns()
    time.sleep(0.001)
    slept_ms = (time.perf_counter_ns() - start_ns) / 1_000_000.0
    print(f"Clock sanity check (1 ms sleep measured as {slept_ms:.2f} ms)")

    # Write a quick thread-safe summary helper
    # def format_lock_report(lock: MonitoredLock) -> str:
    # that sorts lock.per_thread.items() by wait_ns descending and formats one
    # aligned line per thread (name, native_id, contentions/acquires, wait_ms, hold_ms).
    # Call it on both TelemetryMutex and TrimmedMutex to confirm the bottleneck moved.


def main() -> None:

    print("=== 1. Per-zone memory tracking with tracemalloc ===")
    per_zone_memory_tracking()

    print("\n=== 2. Lock wait vs hold instrumentation ===")
    lock_wait_and_hold_instrumentation()

    print("\n=== 3. Reporting and Tracy cross-repo boundary ===")
    tracy_cross_repo_next_steps()


if __name__ == "__main__":
    main()
