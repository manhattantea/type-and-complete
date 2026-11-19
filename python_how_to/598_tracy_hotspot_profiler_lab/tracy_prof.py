# 598_tracy_hotspot_profiler_lab/tracy_prof.py

from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
import json
import time
import tracemalloc


# This module builds a zero-dependency Python stdlib zone and tracemalloc
# wrapper using time.perf_counter_ns() and Chrome / Perfetto JSON export.
# For full native Tracy C-ABI capture, multi-system cold-herring triage, and
# cross-language FFI timelines, see tracy_how_to/950_hotspot_hunt_capstone_lab/.
#
# When a parent zone like PipelineFrame wraps child zones (parse_header_cold,
# transform_records_hotspot), summing every zone's total_ns would count child
# work twice. Keeping an active-frame stack (self._stack) lets each exiting
# zone subtract its children's elapsed time from its own total:
#
#     self_ns = max(0, elapsed_ns - frame.child_ns)
#
#     Suppose PipelineFrame runs for 10 ms total, and its child
#     transform_records_hotspot takes 9.5 ms.
#     PipelineFrame records total_ns = 10 ms, child_ns = 9.5 ms, and
#     self_ns = 0.5 ms, isolating the exact function burning CPU cycles!
#
# Note on tracemalloc overhead: calling tracemalloc.get_traced_memory() inside
# zones requires tracemalloc.start(), which hooks Python's allocator and slows
# pure-Python loops slightly. Keep track_memory=False for pure CPU timing and
# track_memory=True when diagnosing per-zone heap churn.


@dataclass(slots=True)
class ZoneStats:

    name: str
    calls: int = 0
    total_ns: int = 0
    self_ns: int = 0
    alloc_bytes: int = 0


@dataclass(slots=True)
class _ActiveFrame:

    name: str
    start_ns: int
    child_ns: int = 0
    mem_start: int = 0
    value: int = 0


class TracySession:

    def __init__(self, track_memory: bool = False) -> None:

        self.track_memory = track_memory
        self._origin_ns: int = time.perf_counter_ns()
        self._last_frame_ns: int = self._origin_ns
        self._stack: list[_ActiveFrame] = []
        self.zones: dict[str, ZoneStats] = {}
        self.frames: list[int] = []
        self.trace_events: list[dict[str, object]] = []

    # Add @contextmanager def zone(self, name: str, value: int = 0) -> Iterator[_ActiveFrame]:
    # on TracySession:
    # - Read mem_start = tracemalloc.get_traced_memory()[0] if
    #   self.track_memory and tracemalloc.is_tracing() else 0.
    # - Push frame = _ActiveFrame(name=name, start_ns=time.perf_counter_ns(), mem_start=mem_start, value=value)
    #   onto self._stack and yield frame inside try: ... finally:.
    # - In finally:, pop done = self._stack.pop(), compute
    #   elapsed_ns = time.perf_counter_ns() - done.start_ns and
    #   self_ns = max(0, elapsed_ns - done.child_ns). If self._stack is
    #   non-empty, add elapsed_ns to self._stack[-1].child_ns.
    # - If self.track_memory and tracemalloc.is_tracing(), compute
    #   alloc_delta = tracemalloc.get_traced_memory()[0] - done.mem_start
    #   (else 0).
    # - Accumulate calls, total_ns, self_ns, and alloc_bytes into
    #   self.zones.setdefault(done.name, ZoneStats(done.name)).
    # - Append a Chrome Trace "X" event dict to self.trace_events:
    #   {"ph": "X", "name": done.name, "ts": (done.start_ns - self._origin_ns) / 1000.0, "dur": elapsed_ns / 1000.0, "pid": 1, "tid": 1, "args": {"value": done.value, "alloc_bytes": alloc_delta}}.


    # Add def frame_mark(self) -> int: on TracySession: read
    # now = time.perf_counter_ns(), compute dur_ns = now - self._last_frame_ns,
    # update self._last_frame_ns = now, append dur_ns to self.frames, and
    # return dur_ns.


    # Add def format_hotspot_table(self) -> str: on TracySession: compute
    # total_self = sum(z.self_ns for z in self.zones.values()), sort
    # self.zones.values() descending by self_ns, and format a readable table
    # showing Zone, Calls, Total (ms), Self (ms), % Self, and Alloc (KB).


    # Add def export_chrome_trace(self) -> str: on TracySession returning
    # json.dumps({"traceEvents": self.trace_events}, indent=2).
