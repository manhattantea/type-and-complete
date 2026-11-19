# python 550_timing_and_benchmarking_timeit.py

import time
import timeit


def choosing_the_right_clock() -> None:

    # Python's time module exposes four clocks with very different guarantees.
    # Picking the wrong one creates subtle bugs in timeouts and benchmarks:
    # - time.time() / time.time_ns(): wall-clock Unix epoch. NEVER use this for
    #   elapsed durations—NTP clock sync or OS adjustments can make end - start
    #   jump forward wildly or even turn negative! Use it only for timestamps.
    # - time.monotonic() / time.monotonic_ns(): steady non-decreasing clock
    #   including sleep/wait time. Ideal for timeouts, retry backoff, and TTLs.
    # - time.perf_counter() / time.perf_counter_ns(): highest-resolution
    #   monotonic timer available on the OS (includes sleep). Prefer _ns integer
    #   math to avoid floating-point precision loss on short intervals.
    # - time.process_time() / time.process_time_ns(): counts only CPU seconds
    #   burned by the current process (user + kernel), pausing completely during
    #   time.sleep() and blocking I/O.
    #
    #     Suppose you call time.sleep(0.01) between two readings:
    #     perf_counter() advances by ~0.010s while process_time() advances by
    #     ~0.000s because the thread slept instead of executing CPU instructions.

    t0_ns = time.perf_counter_ns()
    t1_ns = time.perf_counter_ns()
    print(f"Starter perf_counter_ns resolution sample: {t1_ns - t0_ns} ns")

    # Time total = sum(range(10_000)) using start_ns = time.perf_counter_ns(),
    # print elapsed_ns = time.perf_counter_ns() - start_ns alongside total, and
    # confirm time.monotonic_ns() is non-decreasing across two calls.


    # Contrast wall-time vs CPU-only time across sleep: capture
    # p0 = time.perf_counter() and c0 = time.process_time(), call
    # time.sleep(0.01), and print time.perf_counter() - p0 (~0.01s) next to
    # time.process_time() - c0 (~0.00s).


def microbenchmarking_with_timeit() -> None:

    # timeit runs your snippet number times inside a tight loop with cyclic gc
    # temporarily disabled so random GC sweeps do not skew measurements, and
    # timeit.repeat runs that whole trial repeat times.
    #
    # Always report min(results) rather than the mean! On a shared OS, hardware
    # interrupts, scheduler preemptions, and background tasks can only ADD
    # positive delay to deterministic CPU work—they never make code run faster
    # than the CPU allows. Therefore min(results) best estimates true speed,
    # whereas an average bakes OS jitter straight into your number.
    #
    # Always build test containers in setup= (or outside a callable) so
    # allocation time does not contaminate a lookup benchmark.
    #
    #     Suppose setup="data = set(range(100))" and stmt="99 in data".
    #     timeit builds data once per repeat and times only the 1,000 lookups.

    baseline_s = timeit.timeit("1 + 1", number=100)
    print(f"Starter 100-add baseline: {baseline_s * 1e6:.2f} us")

    # Compare list vs set membership: call timeit.repeat with number=1000 and
    # repeat=3 for "99 in data" using setup="data = list(range(100))" vs
    # setup="data = set(range(100))". Take min(...) of each result list, print
    # both minimums in microseconds, and print the speedup ratio.


    # Benchmark Python callables without string snippets: create
    # nums = list(range(500)) and use timeit.Timer(lambda: sum(nums)).repeat(repeat=3, number=200)
    # compared against a manual for-loop helper def sum_loop(xs: list[int]) -> int:,
    # printing both minimum timings in microseconds.


def benchmark_hygiene_and_pitfalls() -> None:

    # Two easy microbenchmark mistakes invalidate results silently:
    # - Mutating setup data in place across iterations: timing data.sort() with
    #   number=500 sorts an unsorted list ONLY on iteration 1; iterations 2..500
    #   cheat by sorting an already-sorted list in O(N) Timsort fast-path!
    # - Treating mean as representative: one OS preemption spike can double the
    #   mean even when four of five runs were fast and clean.

    sample = [3, 1, 2]
    print("Starter non-mutating sorted copy:", sorted(sample), "original:", sample)

    # Compare timeit.repeat("sorted(data)", setup="data = list(range(200, 0, -1))", number=500, repeat=3)
    # against "data.sort()" with the exact same setup, and note why data.sort()
    # looks artificially faster once iteration 1 leaves data pre-sorted.


    # Run runs = timeit.repeat("[i * i for i in range(200)]", number=500, repeat=5)
    # and print min(runs) alongside sum(runs) / len(runs) in microseconds to
    # observe how OS jitter shifts the average above the hardware minimum.


def main() -> None:

    print("=== 1. Choosing the right clock ===")
    choosing_the_right_clock()

    print("\n=== 2. Microbenchmarking with timeit and min() ===")
    microbenchmarking_with_timeit()

    print("\n=== 3. Benchmark hygiene and common pitfalls ===")
    benchmark_hygiene_and_pitfalls()


if __name__ == "__main__":
    main()
