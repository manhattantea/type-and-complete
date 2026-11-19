# python 565_profiling_with_tracy_zones_and_frames.py

from dataclasses import dataclass
import time


@dataclass(slots=True)
class ZoneSummary:

    name: str
    calls: int = 0
    total_ns: int = 0
    max_ns: int = 0


def frame_timing_and_clock_basics() -> None:

    # In Primer 560, cProfile aggregated total time per function across an entire
    # run. Aggregation is great for finding overall CPU sinks, but it averages
    # away when latency happened. Suppose three frames take 2 ms each and Frame 3
    # stalls for 35 ms because a single batch grew 10x larger: an aggregated table
    # shows a calm 10 ms average and hides the single-frame hitch completely.
    #
    # A Tracy-style zone and frame wrapper slices execution along time using
    # time.perf_counter_ns(). Calling time.perf_counter_ns() reads the highest
    # resolution monotonic clock the OS exposes and returns an integer count of
    # nanoseconds, avoiding floating-point precision loss over long runs.
    #
    # Notice @dataclass(slots=True) on ZoneSummary above: slots=True replaces each
    # instance's dynamic __dict__ hash table with fixed struct slots so recording
    # summaries stays lightweight.
    #
    #     Suppose frame_start = time.perf_counter_ns(), work runs for 1_500_000 ns,
    #     and frame_end = time.perf_counter_ns().
    #     Then frame_dur_ns = frame_end - frame_start is 1_500_000 ns (1.50 ms),
    #     and storing each frame's duration in a list exposes spikes immediately.

    t0 = time.perf_counter_ns()
    t1 = time.perf_counter_ns()
    print(f"Back-to-back perf_counter_ns delta: {t1 - t0} ns")

    # Measure a tiny timing helper to feel clock resolution on this machine:
    # record start = time.perf_counter_ns(), sum range(5_000) into total,
    # compute elapsed_ns = time.perf_counter_ns() - start, and print both total
    # and elapsed_ns / 1_000_000.0 formatted to 3 decimal places in ms.


    # Create a starter ZoneSummary instance directly:
    # bind summary = ZoneSummary(name="Warmup"), increment summary.calls += 1,
    # add elapsed_ns to summary.total_ns, update summary.max_ns = max(summary.max_ns, elapsed_ns),
    # and print summary to verify its fields update cleanly.


def stdlib_zone_contextmanager_and_decorator() -> None:

    # Python's contextlib.contextmanager decorator lets you write a scoped timer
    # as a generator function with a single yield. Code before yield runs on
    # entering the 'with' block; code inside 'finally:' after yield is guaranteed
    # to run on exit even if an exception unwinds the block.
    #
    # When you also want to instrument whole functions cleanly, a decorator using
    # functools.wraps(fn) copies fn.__name__ and fn.__qualname__ onto the wrapper
    # so stack traces and zone labels keep the real function name.
    #
    #     Suppose prof = FrameZoneRecorder() wraps a helper:
    #         with prof.zone("ParseBatch"):
    #             items = [i * 2 for i in range(1_000)]
    #     On exit, prof.summaries["ParseBatch"] records calls=1 and the elapsed
    #     nanoseconds, while prof.events appends (name, start_ns, dur_ns, value).
    #
    # Always place a zone wrapper OUTSIDE a tight loop rather than inside it:
    #
    #     Good:
    #         with prof.zone("ParseBatch", value=len(items)):
    #             for item in items:
    #                 total += item
    #     Bad:
    #         for item in items:
    #             with prof.zone("OneItem"):
    #                 total += item
    #
    # Entering a Python context manager and reading the OS clock inside a 10,000-
    # iteration loop measures your profiler wrapper instead of your algorithm.

    sample_summary = ZoneSummary(name="ParseBatch", calls=1, total_ns=250_000, max_ns=250_000)
    print(f"Starter zone preview: {sample_summary.name} ({sample_summary.total_ns / 1e6:.3f} ms)")

    # Import contextmanager from contextlib, Iterator and Callable from
    # collections.abc, and functools inside this function (or at module top), then
    # define class FrameZoneRecorder with:
    # - __init__(self) -> None storing self._origin_ns = time.perf_counter_ns(),
    #   self._last_frame_ns = self._origin_ns, self.summaries: dict[str, ZoneSummary] = {},
    #   self.frame_durations_ns: list[int] = [], and
    #   self.plots: dict[str, list[tuple[int, float]]] = {}.
    # - @contextmanager def zone(self, name: str, value: int = 0) -> Iterator[None]:
    #   capturing start_ns = time.perf_counter_ns(), yielding inside try / finally,
    #   and in finally computing elapsed_ns = time.perf_counter_ns() - start_ns
    #   and updating self.summaries.setdefault(name, ZoneSummary(name))
    #   (calls += 1, total_ns += elapsed_ns, max_ns = max(max_ns, elapsed_ns)).
    # - def frame_mark(self) -> int: capturing now = time.perf_counter_ns(),
    #   computing dur_ns = now - self._last_frame_ns, setting self._last_frame_ns = now,
    #   appending dur_ns to self.frame_durations_ns, and returning dur_ns.
    # - def plot(self, series: str, val: float) -> None: appending
    #   (time.perf_counter_ns() - self._origin_ns, float(val)) to
    #   self.plots.setdefault(series, []).


    # Add a decorator factory method def instrument(self, name: str | None = None)
    # on FrameZoneRecorder that wraps a function using @functools.wraps(fn) and
    # runs its body inside with self.zone(name or fn.__qualname__):.
    # Test it on a tiny helper def sum_squares(n: int) -> int: returning
    # sum(i * i for i in range(n)) and verify the wrapped function preserves
    # __name__ == "sum_squares" while recording a call in prof.summaries.


    # Verify exception safety of your zone context manager:
    # open with prof.zone("FailingStep"): and raise ValueError("boom") inside a
    # try / except ValueError: block. Print prof.summaries["FailingStep"] afterward
    # to confirm the finally block still recorded the zone duration cleanly.


def frame_spike_simulation_and_tracy_bridge() -> None:

    # Once you capture per-frame durations and scalar plots side by side, a sudden
    # spike becomes self-explanatory: the frame bar jumps at the exact frame index
    # where the plotted batch_size jumped 10x.
    #
    # This Primer intentionally keeps the wrapper 100% Python stdlib so you learn
    # the core contextmanager, decorator, frame-mark, and outer-loop instrumentation
    # mechanics first. When you want native TracyClient.dll ctypes Srcloc pinning,
    # nested Self Time with recursive zone accounting, or Chrome Trace JSON flight
    # recorders with P95/P99 budgets, continue into ../tracy_how_to/:
    # - ../tracy_how_to/150_python_tracy_ctypes_api_and_zero_cost_gates.py
    # - ../tracy_how_to/250_python_frame_marks_and_scoped_zones.py
    # - ../tracy_how_to/550_python_plots_messages_and_frame_budgets.py

    batch_sizes = [1_000, 1_000, 10_000, 1_000]
    print("Planned 4-frame batch sizes (Frame 2 spikes 10x):", batch_sizes)

    # Instantiate prof = FrameZoneRecorder() and simulate 4 frames using
    # batch_sizes = [1_000, 1_000, 10_000, 1_000].
    # Write two helper functions:
    # - def parse_batch(size: int) -> list[int]: building [i * 3 + 1 for i in range(size)]
    # - def score_batch(items: list[int]) -> int: summing x * x for x in items
    # Decorate one with @prof.instrument("ParseBatch") and wrap the other inside
    # with prof.zone("ScoreBatch", value=len(items)): (always outside the loop!).
    # Inside each frame, call prof.plot("batch_size", batch_size), run both stages,
    # and call prof.frame_mark() at the end of the frame.


    # Print a clean per-frame report showing Frame 0..3 duration in ms alongside
    # its matching batch_size sample from prof.plots["batch_size"], and flag which
    # frame index exceeded 2x the minimum frame duration.


    # Print the aggregated zone summary table sorted by total_ns descending
    # (Zone, Calls, Total ms, Max ms) and compare the max_ns vs total_ns / calls
    # ratio to see why max_ns catches single-frame spikes that averages hide.


    # Demonstrate the outer-loop vs inner-loop instrumentation rule directly:
    # time 5_000 iterations of a tiny addition wrapped once outside with
    # with prof.zone("CoarseLoop"): versus entering with prof.zone("InnerItem"):
    # on every iteration, and print the overhead ratio between the two runs.


def main() -> None:

    print("=== 1. Frame timing and clock basics ===")
    frame_timing_and_clock_basics()

    print("\n=== 2. Stdlib zone contextmanager and decorator ===")
    stdlib_zone_contextmanager_and_decorator()

    print("\n=== 3. Frame spike simulation and Tracy bridge ===")
    frame_spike_simulation_and_tracy_bridge()


if __name__ == "__main__":
    main()
