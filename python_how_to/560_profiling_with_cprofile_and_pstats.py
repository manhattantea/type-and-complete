# python 560_profiling_with_cprofile_and_pstats.py

import cProfile
import io
import pstats


def profiling_tottime_vs_cumtime() -> None:

    # Never optimize blind: intuition routinely picks the wrong function and
    # wastes effort speeding up 1% of runtime. Python's deterministic profiler
    # cProfile (a fast C extension, far lower overhead than pure-Python profile)
    # intercepts every function call and records exact counts and timings.
    #
    # Using with cProfile.Profile() as pr: enables profiling on entry and stops
    # it cleanly on exit even if an exception occurs. Wrapping pr in
    # pstats.Stats(pr, stream=buf) lets you sort and print reports into an
    # in-memory io.StringIO buffer. Key columns to read:
    # - ncalls: invocation count (recursive calls print as total/primitive, like
    #   42/1, separating total calls from top-level root calls).
    # - tottime: seconds spent STRICTLY inside that function's own body,
    #   excluding callees. Sort by pstats.SortKey.TIME to find tight hot loops.
    # - cumtime: inclusive seconds from entry to return, INCLUDING callees. Sort
    #   by pstats.SortKey.CUMULATIVE to find which pipeline stage owns latency.
    #
    #     Suppose workload() calls slow_step() and fast_step().
    #     Under SortKey.CUMULATIVE, workload ranks #1 because it encloses both.
    #     Under SortKey.TIME, slow_step moves to #1 because its loop burns CPU.

    stream = io.StringIO()
    with cProfile.Profile() as starter_pr:
        starter_sum = sum(range(1_000))
    print("Starter profiled sum:", starter_sum, "stream ready:", stream.getvalue() == "")

    # Define three helpers inside this function (keeping total runtime under
    # ~40 ms):
    # - def slow_step(n: int) -> int: sums [i * i for i in range(n)] across 40
    #   iterations so its tottime stands out clearly.
    # - def fast_step(n: int) -> int: returns sum(range(n)).
    # - def workload() -> int: calls slow_step(400) and fast_step(400) and
    #   returns their sum.
    # Profile result = workload() inside with cProfile.Profile() as pr:.


    # Wrap pr in stats = pstats.Stats(pr, stream=stream), call
    # stats.strip_dirs().sort_stats(pstats.SortKey.TIME).print_stats(5), and
    # print result and stream.getvalue(). Then create a second io.StringIO()
    # buffer, sort by pstats.SortKey.CUMULATIVE with print_stats(5), and compare
    # which function rises to row 1 in each table.


def inspecting_callers_and_callees() -> None:

    # Knowing WHICH function is hot in print_stats() is only half the puzzle.
    # Often a leaf helper is slow because one unexpected caller invokes it
    # thousands of times, or a top-level coordinator is slow because of one
    # expensive child call. pstats exposes both directions of the call graph:
    # - stats.print_callers("func_name") lists every upstream caller that
    #   invoked func_name, along with call counts and contributed time.
    # - stats.print_callees("func_name") lists every downstream function invoked
    #   by func_name and how much time each child consumed.
    #
    #     Suppose both pipeline_a() and pipeline_b() call parse_record().
    #     stats.print_callers("parse_record") shows immediately whether
    #     pipeline_a or pipeline_b drove 95% of the calls!

    with cProfile.Profile() as probe_pr:
        probe_sum = sum(range(200))
    probe_stats = pstats.Stats(probe_pr, stream=io.StringIO())
    print("Starter probe total calls:", probe_stats.total_calls, "sum:", probe_sum)

    # Build a tiny call graph with shared_work(n: int) -> int (computing
    # sum(i * i for i in range(n))), caller_light() calling shared_work(200)
    # twice, caller_heavy() calling shared_work(200) 40 times, and run_all()
    # invoking both callers. Profile run_all() inside with cProfile.Profile() as pr:.


    # Create callers_buf = io.StringIO(), wrap pr in
    # rel = pstats.Stats(pr, stream=callers_buf).strip_dirs(), and call
    # rel.print_callers("shared_work") to see caller_light (2 calls) vs
    # caller_heavy (40 calls). Then create callees_buf = io.StringIO() and run
    # pstats.Stats(pr, stream=callees_buf).strip_dirs().print_callees("run_all")
    # to inspect how run_all splits its time across both callers.


def recursion_and_profiler_overhead() -> None:

    # Because cProfile hooks every Python call/return edge, tiny functions
    # called thousands of times appear slightly more expensive than equivalent
    # C loops. Use cProfile to locate algorithmic bottlenecks and hot call
    # paths, then verify small micro-optimizations with timeit (Primer 550).

    print("Tip: pair cProfile call graphs with timeit microbenchmarks.")

    # Define recursive def fib(n: int) -> int: (returning n if n < 2 else
    # fib(n - 1) + fib(n - 2)), profile fib(18) inside cProfile.Profile(), and
    # print stats.strip_dirs().print_stats("fib") to observe the total/primitive
    # ncalls format (such as 8361/1) for recursive calls.


    # Verify a real optimization with before/after profiling: replace the
    # repeated list allocation inside slow_step (or memoize fib) and re-run
    # cProfile sorted by pstats.SortKey.TIME to confirm total calls and tottime
    # collapse dramatically.


def main() -> None:

    print("=== 1. Profiling tottime vs cumtime with cProfile and pstats ===")
    profiling_tottime_vs_cumtime()

    print("\n=== 2. Tracing call graphs with print_callers and print_callees ===")
    inspecting_callers_and_callees()

    print("\n=== 3. Recursion counts and profiler overhead ===")
    recursion_and_profiler_overhead()


if __name__ == "__main__":
    main()
