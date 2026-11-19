# 950_python_hotspot_hunt_five_multipliers_lab/profiler.py
# Nested Self-Time, tracemalloc attribution, Chrome Trace JSON export, and optional TracyClient.dll hooks.
# Run this Lab from the workspace folder via: python 950_python_hotspot_hunt_five_multipliers_lab/main.py

import ctypes
from dataclasses import dataclass
from pathlib import Path
import sys
import time


# Why measure nested Self Time and tracemalloc deltas together inside one zone stack?
# Suppose SimFrame calls step_entity_kinematics. SimFrame's inclusive duration
# includes all time spent inside step_entity_kinematics, so ranking by inclusive
# time always puts SimFrame at the top and hides the actual leaf bottleneck.
#
# Keeping an _ActiveFrame stack solves both CPU and heap attribution cleanly:
#
#     Suppose SimFrame runs from 100 ns to 1,100 ns (elapsed = 1,000 ns) and its
#     child step_entity_kinematics runs for 850 ns:
#         parent.child_ns += 850
#         SimFrame self_ns = max(0, 1000 - 850) = 150 ns
#
# The exact same subtraction isolates heap churn: recording child_net_bytes on
# the parent frame credits transient dict/object allocations to the child zone
# where they occurred, while propagating tracemalloc's peak watermark upward
# before calling tracemalloc.reset_peak() keeps parent peak spikes accurate.
#
# When TracyClient.dll (or libTracyClient.so) is available next to this file
# or on PATH, ctypes lets CPython emit live C telemetry without a C extension.
# Tracy's background C thread reads _TracySourceLocationData pointers after a
# zone opens, so caching (name_bytes, func_bytes, file_bytes, struct) inside
# self._srclocs keeps Python's garbage collector from freeing those byte buffers.


class _TracySourceLocationData(ctypes.Structure):

    _fields_ = [
        ("name", ctypes.c_char_p),
        ("function", ctypes.c_char_p),
        ("file", ctypes.c_char_p),
        ("line", ctypes.c_uint32),
        ("color", ctypes.c_uint32),
    ]


class _TracyCZoneCtx(ctypes.Structure):

    _fields_ = [
        ("id", ctypes.c_uint32),
        ("active", ctypes.c_int32),
    ]


def try_load_tracy_client() -> ctypes.CDLL | None:

    if sys.platform == "win32":
        candidates = ["TracyClient.dll"]
    elif sys.platform == "darwin":
        candidates = ["libTracyClient.dylib"]
    else:
        candidates = ["libTracyClient.so"]

    module_dir = Path(__file__).resolve().parent
    search_paths = [str(module_dir / name) for name in candidates] + candidates

    for target in search_paths:
        try:
            lib = ctypes.CDLL(target)
        except OSError:
            continue

        lib.___tracy_emit_zone_begin.argtypes = [
            ctypes.POINTER(_TracySourceLocationData),
            ctypes.c_int32,
        ]
        lib.___tracy_emit_zone_begin.restype = _TracyCZoneCtx
        lib.___tracy_emit_zone_end.argtypes = [_TracyCZoneCtx]
        lib.___tracy_emit_zone_end.restype = None
        lib.___tracy_emit_frame_mark.argtypes = [ctypes.c_char_p]
        lib.___tracy_emit_frame_mark.restype = None
        lib.___tracy_emit_plot.argtypes = [ctypes.c_char_p, ctypes.c_double]
        lib.___tracy_emit_plot.restype = None
        return lib

    return None


@dataclass(slots=True)
class ZoneMetric:

    name: str
    calls: int = 0
    inclusive_ns: int = 0
    self_ns: int = 0
    net_bytes: int = 0
    max_peak_delta_bytes: int = 0
    items: int = 0


@dataclass(slots=True)
class _ActiveFrame:

    name: str
    start_ns: int
    start_bytes: int
    peak_bytes: int
    items: int = 0
    child_ns: int = 0
    child_net_bytes: int = 0
    c_ctx: _TracyCZoneCtx | None = None


class TracySimProfiler:

    def __init__(self) -> None:

        self._stack: list[_ActiveFrame] = []
        self.metrics: dict[str, ZoneMetric] = {}
        self.plots: list[tuple[int, int, str, float]] = []
        self.frame_times_ns: list[int] = []
        self._trace_events: list[dict[str, object]] = []
        self._origin_ns: int = time.perf_counter_ns()
        self._tracy_lib: ctypes.CDLL | None = try_load_tracy_client()
        self.backend_name: str = (
            "TracyClient" if self._tracy_lib is not None else "StandalonePerfCounter"
        )
        self._srclocs: dict[
            tuple[str, str, int],
            tuple[bytes, bytes, bytes, _TracySourceLocationData],
        ] = {}

    # Add imports at the top of profiler.py when implementing the methods below:
    # from collections.abc import Iterator
    # from contextlib import contextmanager
    # import inspect
    # import json
    # import threading
    # import tracemalloc

    # Implement @contextmanager def zone(self, name: str, items: int = 0) -> Iterator[None]:
    # Keep profiler allocations outside the [start_bytes, end_bytes] measurement
    # window so _ActiveFrame never inflates net_bytes:
    # - If tracemalloc.is_tracing(), read (_, peak) = tracemalloc.get_traced_memory()
    #   and propagate f.peak_bytes = max(f.peak_bytes, peak) across self._stack.
    # - Push frame = _ActiveFrame(name=name, start_ns=0, start_bytes=0, peak_bytes=0, items=items)
    #   onto self._stack before reading start_bytes.
    # - If self._tracy_lib is not None, resolve caller info via inspect.currentframe()
    #   (or name/file/line key), pin a _TracySourceLocationData and its UTF-8 bytes
    #   inside self._srclocs, and store frame.c_ctx = self._tracy_lib.___tracy_emit_zone_begin(ctypes.byref(srcloc), 1).
    # - Right before yield, if tracing, call tracemalloc.reset_peak(), read
    #   start_bytes, _ = tracemalloc.get_traced_memory(), set
    #   frame.start_bytes = frame.peak_bytes = start_bytes, and set frame.start_ns = time.perf_counter_ns().
    # - Inside finally:, capture end_ns = time.perf_counter_ns() first. If frame.c_ctx is not None
    #   and self._tracy_lib is not None, call self._tracy_lib.___tracy_emit_zone_end(frame.c_ctx).
    # - If tracing, read end_bytes, peak_bytes = tracemalloc.get_traced_memory(),
    #   propagate peak_bytes across self._stack, and call tracemalloc.reset_peak() (else end_bytes = 0).
    # - Pop frame = self._stack.pop(), compute elapsed_ns = end_ns - frame.start_ns,
    #   self_ns = max(0, elapsed_ns - frame.child_ns), net_bytes = end_bytes - frame.start_bytes,
    #   self_net_bytes = net_bytes - frame.child_net_bytes, and
    #   peak_delta = max(0, frame.peak_bytes - frame.start_bytes).
    # - When self._stack is non-empty, add elapsed_ns to self._stack[-1].child_ns and
    #   net_bytes to self._stack[-1].child_net_bytes. Update self.metrics[name] and
    #   append a Chrome Trace "X" event to self._trace_events with
    #   ts = (frame.start_ns - self._origin_ns) / 1000.0, dur = elapsed_ns / 1000.0,
    #   pid = 1, tid = threading.get_ident(), and args = {"self_ns": self_ns, "net_bytes": self_net_bytes}.

    # Implement def frame_mark(self, elapsed_ns: int) -> None:
    # Append elapsed_ns to self.frame_times_ns, and if self._tracy_lib is not None
    # call self._tracy_lib.___tracy_emit_frame_mark(None).

    # Implement def plot(self, series: str, value: float) -> None:
    # Capture now_ns = time.perf_counter_ns(), append (len(self.frame_times_ns), now_ns, series, value)
    # to self.plots, append a Chrome Trace "C" counter dict
    # {"ph": "C", "name": series, "ts": (now_ns - self._origin_ns) / 1000.0, "pid": 1, "args": {series: value}}
    # to self._trace_events, and if self._tracy_lib is not None emit
    # self._tracy_lib.___tracy_emit_plot(series.encode("utf-8"), value).

    # Implement def message(self, text: str, color: int = 0x33CC66) -> None:
    # Capture now_ns = time.perf_counter_ns() and append a Chrome Trace "i" instant
    # marker {"ph": "i", "name": text, "s": "g", "ts": (now_ns - self._origin_ns) / 1000.0, "pid": 1, "args": {"color": f"0x{color:06X}"}}
    # to self._trace_events.

    # Implement def percentile_ns(self, pct: float) -> int:
    # Return 0 if self.frame_times_ns is empty; otherwise sort a copy of
    # self.frame_times_ns and return the nearest-rank percentile for 0.0 <= pct <= 100.0.

    # Implement def to_chrome_trace_json(self) -> str:
    # Return json.dumps({"traceEvents": self._trace_events}, indent=2) so the
    # captured "X", "C", and "i" events can be inspected in Perfetto or chrome://tracing.

    # Implement def format_report(self, title: str) -> str:
    # Sort self.metrics.values() descending by m.self_ns, compute
    # total_self_ns = max(1, sum(m.self_ns for m in self.metrics.values())),
    # format a ranked table with columns Zone, Calls, Self ms, % Self, Total ms,
    # ns/item, Net B, Peak B, and append P50, P95, and Max frame latency rows
    # using self.percentile_ns.
