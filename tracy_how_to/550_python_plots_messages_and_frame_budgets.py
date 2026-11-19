# python 550_python_plots_messages_and_frame_budgets.py

from dataclasses import dataclass
import gc
import json
import math
import time

# Scoped CPU zones tell you which function spent 24.0 ms when a frame blows its
# 16.67 ms (60 FPS) budget, yet they cannot show what state changed right before
# the stall. Adding numeric Plots, colored Messages, and percentile budgets turns
# your profiler into a full application flight recorder:
# - Plots ("ph": "C" in Chrome JSON, ___tracy_emit_plot in Tracy) graph live state
#   such as Gen0Objects (gc.get_count()[0]) and measured CacheHitPct over time.
# - Messages ("ph": "i" in Chrome JSON, ___tracy_emit_messageC in Tracy) pin a
#   vertical flag on the exact microsecond an event fired (such as "Cache_Invalidated").
# - Percentile budgets (P50, P95, P99) expose tail hitches that average frame
#   times hide.
#
# In Chrome Tracing / Perfetto JSON (ui.perfetto.dev), timestamps ("ts") and
# durations ("dur") use microseconds relative to origin_ns, while instant markers
# carry global scope "s": "g" so they span across all timeline tracks.


@dataclass(frozen=True, slots=True)
class PlotPoint:
    frame: int
    ts_ns: int
    series: str
    value: float


@dataclass(frozen=True, slots=True)
class MessageMarker:
    frame: int
    ts_ns: int
    text: str
    color: int


@dataclass(frozen=True, slots=True)
class FrameBudgetRecord:
    frame: int
    ts_ns: int
    elapsed_ns: int
    over_budget: bool


# Define class PythonFlightRecorder:
# - __init__(self, budget_ns: int = 16_666_667) -> None: store self.budget_ns,
#   self.origin_ns = time.perf_counter_ns(), self.frame_index = 0, and empty
#   lists self.plots: list[PlotPoint], self.messages: list[MessageMarker], and
#   self.frames: list[FrameBudgetRecord].
# - def plot(self, series: str, value: float) -> None: append PlotPoint using
#   self.frame_index and time.perf_counter_ns().
# - def message(self, text: str, color: int = 0xFFAA00) -> None: append
#   MessageMarker using self.frame_index and time.perf_counter_ns().
# - def end_frame(self, elapsed_ns: int) -> FrameBudgetRecord: build
#   FrameBudgetRecord with over_budget = elapsed_ns > self.budget_ns, append to
#   self.frames, increment self.frame_index += 1, and return the record.
# - def percentile_ns(self, pct: float) -> int: sort [f.elapsed_ns for f in self.frames]
#   and return the nearest-rank sample for 0.0 <= pct <= 100.0 (0 if empty).
# - def to_trace_events(self) -> list[dict[str, object]]: emit Chrome JSON dicts
#   for self.frames ("ph": "X"), self.plots ("ph": "C"), and self.messages ("ph": "i")
#   using ts = (ts_ns - self.origin_ns) / 1000.0.


def flight_recorder_plots_and_messages() -> None:

    # Suppose a service tick normally runs in 0.8 ms, then Tick #4 spikes to
    # 22.0 ms. Plotting measured CacheHitPct and Gen0Objects on every tick lets
    # you see whether a cache wipeout or a GC threshold crossing lined up with
    # the Timeline Message right when latency spiked.

    budget_ns = 16_666_667
    sample_counter = {
        "ph": "C",
        "name": "Gen0Objects",
        "ts": round((time.perf_counter_ns() % 1_000_000) / 1000.0, 2),
        "pid": 1,
        "args": {"Gen0Objects": gc.get_count()[0]},
    }
    print(
        f"Target budget: {budget_ns / 1_000_000:.2f} ms | "
        f"Sample Chrome counter JSON: {json.dumps(sample_counter)}"
    )

    # Implement PythonFlightRecorder above (methods plot, message, end_frame,
    # percentile_ns, and to_trace_events), instantiate rec = PythonFlightRecorder(),
    # emit one "Gen0Objects" plot and one "Recorder_Armed" message, close frame 0
    # with end_frame(...), and print rec.frames[0].


def real_cache_miss_and_percentiles() -> None:

    # Hardcoding fake numbers like 98.0 or 12.0 hides whether a real fix improved
    # behavior. Instead, count genuine cache hits and misses inside a lookup dict
    # so CacheHitPct = 100.0 * hits / (hits + misses) and real rebuild work drives
    # frame duration directly.
    #
    # To compute nearest-rank percentile P over N sorted durations:
    #     Suppose sorted_ns holds 20 durations [d0 .. d19].
    #     idx = math.ceil(0.95 * 20) - 1 = 19 - 1 = 18 -> sorted_ns[18] is P95!

    idx_95 = math.ceil(0.95 * 20) - 1
    print(f"Nearest-rank P95 index across 20 frames: {idx_95} (19th fastest sample)")

    # Write simulate_cache_workload(recorder: PythonFlightRecorder, tick_count: int = 10, clear_on_spike: bool = True) -> float
    # Pre-populate cache: dict[int, tuple[float, float]] = {k: (float(k), k * 0.25) for k in range(256)}.
    # For each tick in range(tick_count):
    # - Start t0 = time.perf_counter_ns() and reset per-tick hits = 0, misses = 0.
    # - If clear_on_spike and tick == 4: call cache.clear(), emit
    #   recorder.message("Cache_Invalidated", color=0xFF3333), and look up keys
    #   range(20_000) (missing the cleared cache and running a heavy rebuild pass
    #   computing and storing fresh tuples so both real misses and Gen-0 objects
    #   push frame time over 16.67 ms!).
    # - On normal ticks (or when clear_on_spike is False), loop 2_500 lookups over
    #   k = i % 256 so cache hits stay high and frame time stays near ~0.5 ms.
    # - Compute measured hit_pct = 100.0 * hits / max(1, hits + misses), call
    #   recorder.plot("CacheHitPct", hit_pct) and recorder.plot("Gen0Objects", float(gc.get_count()[0])),
    #   and call recorder.end_frame(time.perf_counter_ns() - t0).
    # Print a correlated table (Tick, Elapsed ms, OverBudget, CacheHitPct, Gen0,
    # Message) plus P50, P95, P99, and Max frame latencies.


def chrome_json_and_post_fix_budget() -> None:

    # Exporting Chrome Tracing JSON in memory lets you verify that every plot ("C"),
    # message ("i"), and frame duration ("X") serializes cleanly for Perfetto or
    # chrome://tracing without leaving stray temporary files on disk.
    #
    # Once your baseline trace proves Tick #4's cache wipeout broke P95/P99, rerun
    # with the invalidation storm fixed (clear_on_spike=False, keeping the lookup
    # cache warm and bounded) and assert P95 drops below budget_ns.

    sample_span = {"ph": "X", "name": "Frame_0", "ts": 0.0, "dur": 520.0, "pid": 1, "tid": 1}
    print(f"Sample Chrome duration JSON: {json.dumps(sample_span)}")

    # Serialize events = recorder.to_trace_events() with payload = json.dumps(events)
    # in memory (without writing stray files to disk), parse back with json.loads,
    # and assert that "X", "C", and "i" event phases are all present alongside
    # positive "dur" values on "X" frame spans.


    # Post-fix trace validation: instantiate fixed_rec = PythonFlightRecorder(budget_ns=16_666_667),
    # run simulate_cache_workload(fixed_rec, tick_count=10, clear_on_spike=False),
    # print the updated P50, P95, P99, and minimum measured CacheHitPct, and assert
    # fixed_rec.percentile_ns(95.0) < fixed_rec.budget_ns and min_hit_pct > 95.0!


def main() -> None:

    print("=== 1. Flight recorder plots, messages, and Chrome schema ===")
    flight_recorder_plots_and_messages()

    print("\n=== 2. Real cache-miss counters and P50/P95/P99 frame budgets ===")
    real_cache_miss_and_percentiles()

    print("\n=== 3. Chrome JSON verification and post-fix budget validation ===")
    chrome_json_and_post_fix_budget()


if __name__ == "__main__":
    main()
