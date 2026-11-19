# python 250_python_frame_marks_and_scoped_zones.py

from dataclasses import dataclass
import json
import time


# Without FrameMark calls, a continuous server tick or simulation looks like
# one unbroken ribbon of calls in Tracy. Emitting frame_mark() at the end of
# every tick slices execution into discrete frames (such as 16.67 ms at 60 FPS)
# so Tracy's top histogram exposes single-frame hitches even when average FPS
# looks healthy.
#
# Inside each frame, a profiler must separate Inclusive Time (wall time from
# entry to exit) from Self Time (work done directly by that block, excluding
# child zones).
#
#     Suppose FrameTick runs 10.0 ms total and calls Broadphase (1.5 ms) and
#     Narrowphase (8.2 ms):
#         self_ns = elapsed_ns - child_ns  ->  10.0 - (1.5 + 8.2) = 0.3 ms
#
# An active stack computes this in O(1) per zone: push ActiveZone on entry,
# pop on exit, subtract popped.child_ns to get self_ns, and add elapsed_ns to
# the new stack top's child_ns if a parent exists.


@dataclass(slots=True)
class ActiveZone:

    name: str
    start_ns: int
    color: int
    child_ns: int = 0
    value: int = 0
    text: str = ""

    def set_value(self, value: int) -> None:

        self.value = value

    def set_text(self, text: str) -> None:

        self.text = text


@dataclass(frozen=True, slots=True)
class CompletedZone:

    frame_index: int
    name: str
    depth: int
    start_ns: int
    inclusive_ns: int
    self_ns: int
    value: int
    text: str


# Build class TracyFrameProfiler above or inside the first section (import
# defaultdict from collections, Iterator from collections.abc, and
# contextmanager from contextlib):
# - __init__(self, frame_budget_ns: int = 16_666_667) -> None storing
#   self.frame_budget_ns, self.frame_index = 0, self._active_stack: list[ActiveZone] = [],
#   self._name_depth: dict[str, int] = defaultdict(int),
#   self.completed: list[CompletedZone] = [], self.frame_durations_ns: list[int] = [],
#   self.trace_origin_ns = time.perf_counter_ns(), and self._last_frame_ns = self.trace_origin_ns.
# - @contextmanager def zone(self, name: str, color: int = 0x00AAFF, value: int = 0, text: str = "") -> Iterator[ActiveZone]:
#   On entry: increment self._name_depth[name] += 1, create ActiveZone with
#   start_ns = time.perf_counter_ns(), and append it to self._active_stack.
#   Inside try: yield active finally: pop zone, compute elapsed_ns = time.perf_counter_ns() - zone.start_ns,
#   compute self_ns = max(0, elapsed_ns - zone.child_ns), add elapsed_ns to
#   self._active_stack[-1].child_ns if self._active_stack is non-empty, record
#   CompletedZone(self.frame_index, name, len(self._active_stack) + 1, zone.start_ns, elapsed_ns, self_ns, zone.value, zone.text),
#   and keep track of whether this exit was at self._name_depth[name] == 1
#   before decrementing self._name_depth[name] -= 1.
# - frame_mark(self, name: str | None = None) -> int: measure now = time.perf_counter_ns(),
#   compute frame_ns = now - self._last_frame_ns, update self._last_frame_ns = now,
#   append frame_ns to self.frame_durations_ns, increment self.frame_index += 1,
#   and return frame_ns.
# - aggregated_stats(self) -> list[tuple[str, int, int, int]]: aggregate
#   (name, calls, total_self_ns, total_inclusive_ns) per zone name sorted
#   descending by total_self_ns—summing inclusive_ns ONLY for depth-1 entries so
#   recursive self-calls never double-count inclusive time!
# - to_chrome_trace(self) -> list[dict[str, object]]: convert each CompletedZone
#   into a Chrome Tracing "ph": "X" span dict (defined in Section 3 below).


def nested_self_time_and_recursion() -> None:

    # Recursive functions break naive inclusive-time summation. Suppose
    # walk_bvh(4) takes 8 ms wall time and calls walk_bvh(3) (4 ms),
    # walk_bvh(2) (2 ms), and walk_bvh(1) (1 ms). If a profiler adds elapsed_ns
    # to WalkBVH's aggregate inclusive total on every recursive return, WalkBVH
    # reports 15 ms—more than 100% of total runtime!
    #
    # Tracking self._name_depth[name] fixes this cleanly: always add self_ns on
    # every exit, and add inclusive_ns ONLY when recursion depth == 1 (when the
    # outermost call for that zone name exits).

    sample_zone = ActiveZone(name="FrameTick", start_ns=time.perf_counter_ns(), color=0x3399FF)
    sample_zone.set_value(256)
    sample_zone.set_text("entities=256")
    print(f"ActiveZone preview: {sample_zone.name} | {sample_zone.text} | value={sample_zone.value}")

    # Test nested Self Time subtraction with TracyFrameProfiler:
    # Open with profiler.zone("ParentZone"): containing two sequential child
    # zones ("FastChild" doing 1_000 iterations and "SlowChild" doing 50_000
    # iterations). Call profiler.aggregated_stats() and verify ParentZone has
    # high Inclusive ms and near-zero Self ms compared to SlowChild.


    # Test the recursive zone depth == 1 rule directly:
    # Define def walk_bvh(profiler: TracyFrameProfiler, depth: int) -> int:
    # wrapping its body in with profiler.zone("WalkBVH"):, doing a tiny loop over
    # 1_500 integers, and returning 1 + walk_bvh(depth - 1) if depth > 1 else 1.
    # Call walk_bvh(profiler, 5) inside with profiler.zone("BVHRoot"):, print
    # aggregated_stats(), and assert WalkBVH's total_inclusive_ns <= BVHRoot's
    # total_inclusive_ns (proving recursive calls did not inflate >100%).


def frame_marks_and_spike_tags() -> None:

    # Suppose Frame #4 spikes from 0.5 ms to 25 ms while Frames #1, #2, #3, and
    # #5 stay under 1 ms. Knowing Narrowphase spiked is only half the puzzle—you
    # also need to know which input payload blew up! Attaching
    # z.set_value(entity_count) and z.set_text(f"entities={entity_count}") lets
    # you inspect the outlier span directly and see entity_count = 2000 instead
    # of 200.

    budget_ns = 16_666_667
    print(f"60 FPS frame budget: {budget_ns / 1_000_000:.2f} ms ({budget_ns} ns)")

    # Define simulate_frame(profiler: TracyFrameProfiler, entity_count: int) -> float:
    # Wrap the body in with profiler.zone("FrameTick", color=0x3399FF):.
    # Inside it, run with profiler.zone("Broadphase", value=entity_count): doing
    # an O(N) pass over entity_count * 10, then run
    # with profiler.zone("Narrowphase", color=0xFF5500) as z: calling
    # z.set_value(entity_count) and z.set_text(f"entities={entity_count}") while
    # running an O(N^2) pair scan over range(entity_count) and inner
    # range(i, min(entity_count, i + entity_count // 2)) so entity_count=2000
    # noticeably spikes above 16.67 ms! Return the accumulated float checksum.


    # Simulate 5 frames with counts = [200, 200, 200, 2000, 200]:
    # Call simulate_frame(profiler, count) and profiler.frame_mark() per frame.
    # Print every frame's duration in milliseconds and flag any frame whose
    # Narrowphase zone exceeds 3x the median frame duration alongside its
    # attached value and text tag (confirming Frame #4 reports value=2000).
    # Print profiler.aggregated_stats() to verify FrameTick Self ms stays tiny.


def post_fix_trace_and_json_export() -> None:

    # Chrome Tracing / Perfetto JSON reads a list of complete-event spans using
    # "ph": "X", where "ts" is start time in microseconds relative to trace
    # origin and "dur" is duration in microseconds.
    #
    #     Suppose CompletedZone starts 1_500_000 ns after trace_origin_ns and
    #     runs for 420_000 ns:
    #         "ts" becomes 1500.0 us, "dur" becomes 420.0 us, and "args" carries
    #         frame_index, self_ns, value, and text for timeline inspection!
    #
    # Exporting those spans lets you inspect nested Self Time and spike tags
    # visually in ui.perfetto.dev without needing TracyClient.dll installed.

    sample_span = {
        "name": "Narrowphase",
        "cat": "zone",
        "ph": "X",
        "ts": 1500.0,
        "dur": 420.0,
        "pid": 1,
        "tid": 1,
        "args": {"frame": 0, "self_ns": 420_000, "value": 200, "text": "entities=200"},
    }
    print("Sample Chrome X span:", json.dumps(sample_span))

    # Remediate the Narrowphase spike and validate the post-fix trace:
    # Define simulate_frame_fast(profiler: TracyFrameProfiler, entity_count: int) -> float
    # keeping FrameTick and Broadphase identical, while replacing the O(N^2)
    # Narrowphase pair scan with a linear O(N) spatial-cell / sliding-window
    # check over entity_count items (still tagging z.set_value and z.set_text).
    # Re-run counts = [200, 200, 200, 2000, 200] on a fresh TracyFrameProfiler,
    # print the new frame histogram, and assert every frame duration falls below
    # 16.67 ms (16_666_667 ns)!


    # Implement and inspect to_chrome_trace(self) -> list[dict[str, object]]:
    # Emit one "ph": "X" dict per CompletedZone with "ts" = (z.start_ns - self.trace_origin_ns) / 1000.0,
    # "dur" = z.inclusive_ns / 1000.0, "pid": 1, "tid": 1, and "args" holding
    # frame, depth, self_ns, value, and text. Serialize the post-fix trace with
    # json.dumps(profiler.to_chrome_trace(), indent=2), verify every span has
    # "ph": "X" and dur >= 0.0, and print total exported spans plus Frame #4's
    # Narrowphase span from the JSON payload.


def main() -> None:

    print("=== 1. Nested Self Time and recursive depth == 1 rule ===")
    nested_self_time_and_recursion()

    print("\n=== 2. Frame marks and data-driven spike tags ===")
    frame_marks_and_spike_tags()

    print("\n=== 3. Post-fix frame budget trace and Chrome JSON export ===")
    post_fix_trace_and_json_export()


if __name__ == "__main__":
    main()
