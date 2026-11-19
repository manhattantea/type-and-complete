# python 350_python_tracy_memory_and_object_churn.py

from array import array
from dataclasses import dataclass
import gc
import sys
import tracemalloc

# In C or Odin, looping over 1,000 floats uses CPU registers or one flat stack
# array and allocates zero heap bytes. In Python, almost every temporary value or
# container hits CPython's small-object allocator (pymalloc) and cyclic garbage
# collector (gc):
# - Every Python float beyond CPython's small internal freelist is a 24-byte
#   PyFloatObject on the heap.
# - Every dict starts at 64+ bytes, plus boxed keys and values, and registers
#   with the cyclic gc so Python can detect reference cycles.
# - Every time net Gen-0 container allocations minus deallocations reach
#   gc.get_threshold()[0] (700 by default), Python pauses execution mid-frame
#   to scan object graphs.
#
# In pure Python, the stdlib tracemalloc module hooks CPython's PyMem_* and
# PyObject_* allocators directly in C. Pairing tracemalloc.get_traced_memory()
# with gc.get_stats() inside each profiled zone lets us separate four distinct
# memory signatures:
# - Retained leak: net_delta_bytes > 0 across frames (objects stay alive).
# - Transient GC churn: net_delta_bytes == 0, but peak_delta_bytes >> 0 and
#   Gen-0 collections fire mid-frame.
# - __slots__ pool reuse: instances omit per-object __dict__ and update in place.
# - Pre-allocated array("d") reuse: steady-state frames achieve 0 B net growth,
#   0 B peak growth, and 0 GC collections.


@dataclass(frozen=True, slots=True)
class MemoryZoneReport:
    zone_name: str
    pool_name: str
    net_delta_bytes: int
    peak_delta_bytes: int
    gc_delta: tuple[int, int, int]


# Define class TracyMemoryProfiler:
# - __init__(self) -> None: store self.reports: list[MemoryZoneReport] = [].
# - @contextmanager def memory_zone(self, name: str, pool: str = "PythonHeap") -> Iterator[None]:
#   (import contextmanager from contextlib and Iterator from collections.abc).
#   Ensure tracemalloc.is_tracing() is active, call tracemalloc.reset_peak(),
#   capture start_current, _ = tracemalloc.get_traced_memory() and
#   gc_before = tuple(s["collections"] for s in gc.get_stats()).
#   Yield inside try: ... finally:. On exit, read
#   end_current, peak_bytes = tracemalloc.get_traced_memory() and
#   gc_after = tuple(s["collections"] for s in gc.get_stats()), compute
#   net_delta_bytes = end_current - start_current,
#   peak_delta_bytes = max(0, peak_bytes - start_current), and
#   gc_delta = (gc_after[0] - gc_before[0], gc_after[1] - gc_before[1], gc_after[2] - gc_before[2]),
#   then append MemoryZoneReport(...) to self.reports.


def memory_zone_tracker_and_gc_stats() -> None:

    # Calling tracemalloc.start() attaches CPython's allocation tracer globally
    # so every subsequent dict, list, or object allocation records its exact
    # byte size and peak high-water mark. Calling tracemalloc.reset_peak() right
    # before entering a zone guarantees peak_bytes measures only that zone's spike
    # rather than an earlier setup phase.
    #
    # Suppose gc.get_threshold()[0] is 700 and a single frame allocates 1,200
    # temporary dictionaries inside a list comprehension. Because more than 700
    # container objects become live before the comprehension finishes, Gen-0 GC
    # fires mid-frame and increments gc.get_stats()[0]["collections"] by at least 1.

    print(
        f"tracemalloc active={tracemalloc.is_tracing()} | "
        f"GC thresholds (gen0, gen1, gen2): {gc.get_threshold()} | "
        f"Current counts: {gc.get_count()} | "
        f"float={sys.getsizeof(1.5)} B, small_dict={sys.getsizeof({'x': 1.0, 'y': 2.0})} B"
    )

    # Implement TracyMemoryProfiler above, start tracemalloc inside a
    # try: ... finally: tracemalloc.stop() block, and verify memory_zone captures
    # a real Gen-0 GC sweep mid-frame: inside
    # with profiler.memory_zone("Gen0SweepBurst", pool="ContainerChurn"):
    # build pairs = [{"id": i, "vals": [i, i + 1]} for i in range(1200)] (each
    # iteration allocates both a dict and a list, easily crossing threshold 700),
    # compute len(pairs), and assert report.gc_delta[0] >= 1.


def leak_vs_churn_vs_slots_pool() -> None:

    # Not every memory problem is a leak. If a frame builds 1,000 temporary dicts
    # and drops them at return, net_delta_bytes is near zero—yet peak_delta_bytes
    # jumps by tens of kilobytes and triggers Gen-0 GC pauses. By contrast, a
    # retained leak appends objects to a long-lived cache or list that never
    # shrinks, pushing net_delta_bytes upward every single frame.
    #
    # Defining __slots__ = ("x", "y") on a class tells Python to store those two
    # fields in fixed C-level pointer slots on the instance instead of allocating
    # a per-instance __dict__. Pre-allocating a pool of slotted instances before
    # the frame loop eliminates per-frame container allocations completely.

    sample_dict = {"x": 1.0, "y": 2.0}
    sample_tuple = (1.0, 2.0)
    print(f"Boxed dict={sys.getsizeof(sample_dict)} B vs tuple={sys.getsizeof(sample_tuple)} B")

    # Write step_retained_leak(leak_sink: list[dict[str, float]], count: int = 400) -> int
    # appending {"x": float(i), "y": float(i) * 0.5} for i in range(count) into
    # leak_sink and returning len(leak_sink). Profile 3 frames under a
    # "RetainedLeak" zone and verify net_delta_bytes > 0 on every frame.


    # Write step_boxed_dicts_churn(count: int = 1000) -> float allocating a fresh
    # local list [{"x": float(i), "y": float(i) * 0.5} for i in range(count)],
    # summing p["x"] + p["y"], and returning the float total. Profile 3 frames
    # under "BoxedDictsChurn" and note how peak_delta_bytes stays high even when
    # net_delta_bytes drops back near zero after frame 0.


    # Define class SlottedParticle with __slots__ = ("x", "y") and __init__,
    # pre-allocate pool = [SlottedParticle(0.0, 0.0) for _ in range(1000)] before
    # the loop, and write step_slots_pool(pool: list[SlottedParticle]) -> float
    # updating p.x and p.y in place. Compare sys.getsizeof(pool[0]) against a
    # regular dict-backed instance and profile 3 frames under "SlotsPoolReuse".


def zero_alloc_array_post_fix() -> None:

    # Python's array("d", ...) stores unboxed C double values contiguously inside
    # one compact buffer object instead of N separate 24-byte PyFloatObject boxes.
    # Pre-allocating scratch_x and scratch_y once before the loop lets steady-state
    # frames mutate raw slots in place with zero container churn—though notice that
    # reading scratch_x[i] back into Python still boxes a float unless the update
    # stays minimal or is offloaded (covered in Primer 650 and Lab 800). Running one
    # untimed warmup pass first settles CPython's internal float freelists and
    # adaptive interpreter caches before measurement starts.

    probe = array("d", [0.0]) * 8
    print(f"Contiguous array('d', 8): len={len(probe)}, size={sys.getsizeof(probe)} B")

    # Write step_preallocated_array_zero_alloc(scratch_x: array, scratch_y: array) -> float
    # looping i in range(len(scratch_x)), updating scratch_x[i] and scratch_y[i]
    # in place without allocating dicts or lists, and returning sum(scratch_x).


    # Post-fix trace validation: inside try: ... finally: tracemalloc.stop() with
    # tracemalloc.start(), pre-allocate scratch_x = array("d", [0.0]) * 1000 and
    # scratch_y = array("d", [0.0]) * 1000 and run 1 untimed warmup call of
    # step_preallocated_array_zero_alloc(scratch_x, scratch_y). Then instantiate
    # profiler = TracyMemoryProfiler() and run 4 frames each of BoxedDictsChurn
    # vs. PreallocArrayZeroAlloc, print a formatted table (Zone, Pool, Net B,
    # Peak B, Gen0 GC), and assert every PreallocArrayZeroAlloc frame reports
    # net_delta_bytes == 0 and gc_delta == (0, 0, 0).


def main() -> None:

    print("=== 1. Memory zone tracker and Gen-0 GC sweeps ===")
    memory_zone_tracker_and_gc_stats()

    print("\n=== 2. Retained leak vs. transient churn vs. __slots__ pool ===")
    leak_vs_churn_vs_slots_pool()

    print("\n=== 3. Zero-alloc array('d') post-fix trace validation ===")
    zero_alloc_array_post_fix()


if __name__ == "__main__":
    main()
