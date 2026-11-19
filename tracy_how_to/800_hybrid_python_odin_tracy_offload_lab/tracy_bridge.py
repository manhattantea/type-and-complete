# 800_hybrid_python_odin_tracy_offload_lab/tracy_bridge.py

# Run this lab from its entry script:
# python 800_hybrid_python_odin_tracy_offload_lab/main.py
#
# When you offload a hot inner loop from Python to a compiled Odin DLL via
# ctypes, keeping both layers in one timeline lets you verify two things:
# - Pure-Python orchestration zones (Stage1_Python_AoS, Stage2_Python_SoA)
#   capture bytecode dispatch and pointer-chasing costs on the Python layer.
# - The FFI boundary zone (Stage3_Odin_SIMD or Stage3_Fallback) wraps the
#   ctypes.from_buffer view setup plus native call so you measure true
#   end-to-end wall cost—including small-N FFI crossover overhead—and export
#   separate pid layers into Chrome Tracing / Perfetto JSON.

from dataclasses import dataclass
import threading
import time


LAYER_PIDS: dict[str, int] = {
    "Python": 1,
    "OdinSIMD": 2,
    "PyFallback": 3,
}


@dataclass(frozen=True, slots=True)
class ZoneRecord:

    name: str
    layer: str
    pid: int
    tid: int
    start_ns: int
    end_ns: int
    item_count: int = 0

    @property
    def elapsed_ns(self) -> int:

        return self.end_ns - self.start_ns


class TracyTimeline:

    def __init__(self) -> None:

        self.origin_ns: int = time.perf_counter_ns()
        self._last_frame_ns: int = self.origin_ns
        self.main_tid: int = threading.get_native_id()
        self.records: list[ZoneRecord] = []
        self.frame_durations_ns: list[int] = []

    def to_trace_us(self, ts_ns: int) -> float:

        return (ts_ns - self.origin_ns) / 1000.0

    # Import contextmanager from contextlib, Iterator from collections.abc,
    # defaultdict from collections, and json when implementing the methods below:
    #
    # Define @contextmanager def zone(self, name: str, item_count: int = 0, layer: str = "Python") -> Iterator[None]
    # Capture start_ns = time.perf_counter_ns(), yield inside try: ... finally:,
    # resolve pid = LAYER_PIDS.get(layer, 1) and tid = threading.get_native_id(),
    # and append ZoneRecord(name=name, layer=layer, pid=pid, tid=tid, start_ns=start_ns, end_ns=time.perf_counter_ns(), item_count=item_count)
    # to self.records.
    #
    # Define frame_mark(self) -> int
    # Compute elapsed = now - self._last_frame_ns using time.perf_counter_ns(),
    # update self._last_frame_ns = now, append elapsed to self.frame_durations_ns,
    # and return elapsed.
    #
    # Define format_comparison_report(self) -> str
    # Group self.records by (rec.layer, rec.name), compute call count,
    # minimum duration (min_ms), total duration (total_ms), and
    # ns_per_item = min_ns / max(1, rec.item_count), and return a formatted
    # multi-line comparison table across all recorded N sizes and layers.
    #
    # Define to_chrome_trace_events(self) -> list[dict[str, object]]
    # Emit Chrome Tracing / Perfetto metadata events ("ph": "M", "name": "process_name")
    # for each entry in LAYER_PIDS so Python (pid=1) and OdinSIMD (pid=2) appear
    # on separate timeline tracks, then emit one Complete duration event
    # ("ph": "X", "name": rec.name, "cat": rec.layer, "pid": rec.pid, "tid": rec.tid,
    # "ts": self.to_trace_us(rec.start_ns), "dur": max(0.001, rec.elapsed_ns / 1000.0),
    # "args": {"items": rec.item_count, "layer": rec.layer}) per ZoneRecord!
