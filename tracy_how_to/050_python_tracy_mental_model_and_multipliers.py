# python 050_python_tracy_mental_model_and_multipliers.py

from collections import deque
from dataclasses import dataclass
import dis
import sys
import time


# Performance work starts with measurement because almost every Python program
# spends 90% or more of its runtime inside less than 5% of its code. Rewriting
# cold startup config loaders or output formatters makes clear Python harder to
# read for almost zero total speedup.
#
# Two profiler designs help locate that 5% hotspot:
# Sampling profilers (such as py-spy or perf) interrupt threads on a timer,
# say 1,000 times per second, to inspect the call stack. They need zero code
# edits, which makes them great for finding unexpected CPU hogs, yet they can
# miss single-frame hitches or exact call counts.
# Instrumentation profilers (such as Tracy and Spall) record explicit zone
# start and end timestamps into a fixed per-thread ring buffer. In native builds
# with TracyClient, a background thread drains that ring buffer over TCP port
# 8086 to the Tracy GUI. Allocating brand-new lists or objects on every zone
# boundary triggers allocator overhead and garbage collection pauses that distort
# the very timing you are measuring, so a bounded collections.deque(maxlen=N)
# models that fixed ring-buffer footprint cleanly in Python.


@dataclass(frozen=True, slots=True)
class ZoneEvent:

    name: str
    start_ns: int
    end_ns: int

    @property
    def elapsed_ns(self) -> int:

        return self.end_ns - self.start_ns


# Why do hot pure-Python loops run so much slower than native Odin or C loops?
# In Odin, total += x compiles to a single hardware add instruction on raw
# 8-byte numbers in CPU registers. In CPython, every pass through a loop must
# fetch and decode VM bytecode instructions, look up variables (LOAD_FAST for
# locals vs. slower LOAD_GLOBAL for module names), update Py_INCREF / Py_DECREF
# reference counts, and allocate heap-boxed PyLongObject or PyFloatObject
# structs. Even a Python list[float] is not contiguous floats in memory: it is
# an array of 8-byte pointers chasing scattered 24-byte PyFloatObject structs
# across 64-byte CPU cache lines.
#
# Notice the Five Multipliers lens behind every hotspot we profile here:
# Waste (bytecode dispatch and PyObject boxing), IPC (serial dependency chains
# stalling CPU ports), SIMD (1 scalar vs. vector lanes), Caching (pointer
# chasing vs. contiguous array("d") / memoryview), and Multithreading (CPython's
# GIL serializing pure-Python CPU threads unless released in native code).


def boxing_and_bytecode_waste() -> None:

    # sys.getsizeof(obj) reports the byte footprint of the CPython object itself
    # in memory (not counting the objects inside a container, only the container
    # header and pointer table). A raw C double is 8 bytes; compare that with a
    # boxed Python float or integer and a list holding references to floats.
    #
    # dis.Bytecode(fn) walks the compiled CPython VM instructions inside fn.
    # Suppose you run dis.Bytecode(lambda x: x + 1.5). It emits LOAD_FAST,
    # LOAD_CONST, and BINARY_OP instead of a single machine add.

    gil_enabled = getattr(sys, "_is_gil_enabled", lambda: True)()
    tiny_ops = len(list(dis.Bytecode(lambda x: x + 1.5)))
    print(
        f"Python {sys.version.split()[0]} | GIL enabled: {gil_enabled} | "
        f"PyFloatObject={sys.getsizeof(1.5)} B, PyLongObject={sys.getsizeof(1)} B | "
        f"lambda ops={tiny_ops}"
    )

    # Measure PyObject boxing and pointer-table overhead using sys.getsizeof:
    # Print sys.getsizeof(0), sys.getsizeof(1 << 40), sys.getsizeof(3.14), and
    # sys.getsizeof([3.14] * 1000). Compute the total bytes of a 1,000-element
    # list[float] (list pointer table + 1,000 separate PyFloatObject allocations
    # assuming distinct floats) and compare that against 1,000 * 8 = 8,000 bytes
    # for raw 8-byte IEEE-754 doubles (notice 4x+ bloat and pointer indirection).


    # Inspect CPython VM dispatch directly with dis.Bytecode:
    # Define a tiny local function def loop_add(n: int) -> float: that initializes
    # total = 0.0 and runs for i in range(n): total += (i * 0.25) + 1.5.
    # Print every instruction in dis.Bytecode(loop_add) and count how many VM
    # instructions sit inside the loop body versus outside it. Notice that every
    # iteration executes multiple opcodes plus float boxing.


def ring_buffer_and_amdahl() -> None:

    # When a fixed ring buffer reaches capacity, the oldest event drops off the
    # front with zero heap growth. In Python, collections.deque(maxlen=capacity)
    # enforces that fixed cap automatically in C.
    #
    # Once your profiler shows which zone owns most of your runtime, Amdahl's
    # Law predicts total speedup when you speed up fraction hot_fraction (0.0 to
    # 1.0) by factor:
    #
    #     speedup = 1.0 / ((1.0 - hot_fraction) + (hot_fraction / factor))
    #
    # Suppose a script spends 92% (0.92) in a math loop and 8% in config parsing.
    # Making config parsing 1,000x faster yields 1.0 / (0.92 + 0.08/1000) = 1.09x.
    # Making the 92% loop 20x faster yields 1.0 / (0.08 + 0.92/20) = 7.94x.

    sample_ring: deque[ZoneEvent] = deque(maxlen=16)
    t0 = time.perf_counter_ns()
    warmup_sum = sum(range(100))
    t1 = time.perf_counter_ns()
    sample_ring.append(ZoneEvent("WarmupAnchor", t0, t1))
    print(f"Ring sample: {sample_ring[0].elapsed_ns} ns | warmup_sum={warmup_sum}")

    # Build class RingBufferProfiler directly above this section or inside it
    # (import contextmanager from contextlib and Iterator from collections.abc):
    # - __init__(self, capacity: int = 64) -> None storing self._events: deque[ZoneEvent] = deque(maxlen=capacity)
    # - record(self, name: str, start_ns: int, end_ns: int) -> None appending ZoneEvent(name=name, start_ns=start_ns, end_ns=end_ns)
    # - @contextmanager def zone(self, name: str) -> Iterator[None]: capturing start_ns = time.perf_counter_ns() before yield inside try: ... finally: and calling self.record(name, start_ns, time.perf_counter_ns()) in finally:
    # - summary(self) -> dict[str, int] summing elapsed_ns per event.name across self._events


    # Verify ring-buffer wraparound without unbounded memory growth:
    # Create rb = RingBufferProfiler(capacity=4), enter 6 zones named "z0".."z5"
    # using with rb.zone(f"z{i}"): with a small arithmetic loop inside each, and
    # print rb.summary() to confirm only "z2".."z5" remain while "z0" and "z1"
    # evicted cleanly.


    # Define amdahl_max_speedup(hot_fraction: float, factor: float) -> float:
    # Validate 0.0 <= hot_fraction <= 1.0 and factor > 0.0 (raising ValueError on
    # invalid inputs), then return 1.0 / ((1.0 - hot_fraction) + (hot_fraction / factor)).
    # Print amdahl_max_speedup(0.02, 1000.0) vs. amdahl_max_speedup(0.92, 20.0).


def baseline_vs_optimized_trace() -> None:

    # Profiling before editing gives you a falsifiable baseline; re-running the
    # same profiler after changing only the hotspot proves whether your fix
    # delivered the speedup Amdahl's Law predicted.
    #
    # Suppose sum_coordinates_hot runs 50,000 iterations of Python bytecode and
    # consumes 95% of your pipeline. Rewriting the cold settings loader buys you
    # nothing, whereas hoisting locals or moving the inner reduction into C
    # removes the bytecode dispatch and PyFloatObject boxing multiplier at once.

    cold_total = sum(range(100))
    print(f"Starter cold sum (0..<100): {cold_total}")

    # Define the 3-stage baseline pipeline helpers:
    # - load_settings_cold() -> dict[str, int] returning {"count": 50_000, "bias": 3}
    # - sum_coordinates_hot(count: int = 50_000) -> float accumulating total = 0.0 via for i in range(count): total += (i * 0.25) + 1.5
    # - format_output_cold(total: float) -> str returning f"checksum={total:.2f}"


    # Profile the baseline pipeline using RingBufferProfiler(capacity=32):
    # Wrap each of the 3 stages in with profiler.zone(...):, read totals = profiler.summary(),
    # print each zone's milliseconds and percentage share, assert sum_coordinates_hot
    # exceeds 85% of total pipeline time, and compute predicted speedup with
    # amdahl_max_speedup(hot_fraction, 20.0) using your measured hot_fraction.


    # Validate a post-fix trace:
    # Write sum_coordinates_fast(count: int = 50_000) -> float that eliminates
    # per-element Python bytecode dispatch and float boxing—for example, hoist
    # local math into C-backed sum(range(count)) via 0.25 * sum(range(count)) + 1.5 * count
    # (or compare a hoisted local generator sum against C-backed arithmetic),
    # verify abs(fast_total - hot_total) < 1e-6 so checksum parity holds, re-run
    # the 3-stage pipeline under a fresh RingBufferProfiler, and compare the
    # measured total pipeline speedup against amdahl_max_speedup(hot_fraction, hot_speedup).


def main() -> None:

    print("=== 1. CPython boxing and bytecode waste ===")
    boxing_and_bytecode_waste()

    print("\n=== 2. Ring buffer profiler and Amdahl's Law ===")
    ring_buffer_and_amdahl()

    print("\n=== 3. Baseline vs. optimized post-fix trace ===")
    baseline_vs_optimized_trace()


if __name__ == "__main__":
    main()
