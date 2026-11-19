# python 650_diagnosing_python_waste_cache_and_ipc.py

# Once Tracy's Statistics view (sorted descending by Self Time) points to your
# hottest Python zone, dividing minimum nanoseconds by the item count (ns/item)
# and inspecting the executed loop-body bytecode separates CPython bottlenecks:
#
# - Above ~100 ns/item with heap/attribute access: Multiplier #1 (attribute
#   lookups and PyObject boxing waste) plus Multiplier #4 (pointer chasing
#   across scattered heap objects instead of contiguous cache lines).
# - Roughly 15-80 ns/item over contiguous array("d") with hoisted LOAD_FAST
#   locals: cache lines are packed at 8 doubles per 64-byte line, yet CPython's
#   interpreter dispatch loop still pays bytecode overhead per item (Multiplier
#   #1 VM dispatch + Multiplier #2 serial accumulator dependency).
# - Below ~2-5 ns/item: C-backed bulk reduction (such as math.sumprod or sum)
#   or a native Odin/C DLL eliminates per-item Python bytecode completely.
#
# For raw Python VM, memoryview, and array("d") mechanics, see
# ../python_how_to/570_bytecode_disassembly_with_dis.py,
# ../python_how_to/580_buffer_protocol_and_mmap.py, and
# ../python_how_to/585_cache_locality_ipc_and_simd_in_python.py.

from array import array
from collections.abc import Callable
from dataclasses import dataclass
import dis
import math
import sys
import time


@dataclass(slots=True)
class ParticleAoS:

    x: float
    y: float
    vx: float
    vy: float
    tag: int
    mass: float


@dataclass(frozen=True, slots=True)
class ZoneDiagnostic:

    name: str
    items: int
    min_ns: int
    loop_opcodes: int
    bytes_per_item: float
    diagnosis: str

    @property
    def ns_per_item(self) -> float:

        return self.min_ns / max(1, self.items)

    @property
    def effective_mb_per_sec(self) -> float:

        total_bytes = self.items * self.bytes_per_item
        return (total_bytes / (1024.0 * 1024.0)) / (max(1, self.min_ns) / 1_000_000_000.0)


def benchmark_min_ns(fn: Callable[[], float], repeats: int = 5) -> int:

    best_ns = 1 << 62
    for _ in range(repeats):
        t0 = time.perf_counter_ns()
        _result = fn()
        elapsed = time.perf_counter_ns() - t0
        if elapsed < best_ns:
            best_ns = elapsed
    return best_ns


def adaptive_bytecode_and_bandwidth_metrics() -> None:

    # Two measurement traps distort Python zone diagnostics if you skip them:
    # - Calling len(list(dis.Bytecode(fn))) counts one-time function setup
    #   instructions alongside the loop body and misses PEP 659 specialization.
    #   When we pass adaptive=True to dis.Bytecode(fn, adaptive=True), CPython
    #   shows the runtime-specialized opcodes (such as BINARY_OP_MULTIPLY_FLOAT)
    #   after ~16 warmup passes, and counting only instructions between
    #   FOR_ITER and JUMP_BACKWARD isolates what actually runs N times!
    # - Hardcoding bytes_per_item=16 hides layout changes if you switch from
    #   array("d") (8-byte doubles) to array("f") (4-byte floats). Wrapping each
    #   buffer in memoryview(buf) lets you read mv.nbytes / len(mv) directly
    #   with zero copies.
    #
    # Suppose xs and vxs are array("d") buffers of length 1,000.
    # memoryview(xs).nbytes is 8,000 and (mv_x.nbytes + mv_v.nbytes) / len(mv_x)
    # evaluates to 16.0 bytes/item; switching to array("f") drops it to 8.0.

    def sample_dot_loop(xs: array, vxs: array) -> float:

        total = 0.0
        for i in range(len(xs)):
            total += xs[i] * vxs[i]
        return total

    preview_x = array("d", [1.0, 2.0, 3.0, 4.0])
    preview_v = array("d", [0.5, 1.0, 1.5, 2.0])
    for _ in range(20):
        sample_dot_loop(preview_x, preview_v)

    adaptive_ops = [instr.opname for instr in dis.Bytecode(sample_dot_loop, adaptive=True)]
    with memoryview(preview_x) as mv_x, memoryview(preview_v) as mv_v:
        bytes_per_pair = (mv_x.nbytes + mv_v.nbytes) / len(mv_x)

    min_ns = benchmark_min_ns(lambda: sample_dot_loop(preview_x, preview_v), repeats=3)
    print(
        f"Warm adaptive ops={len(adaptive_ops)} ({adaptive_ops[:6]}...) | "
        f"memoryview bytes/pair={bytes_per_pair:.1f} B | min_ns={min_ns} ns"
    )

    # Define count_loop_body_opcodes(fn: Callable[..., object]) -> int
    # Inspect list(dis.Bytecode(fn, adaptive=True)). Walk the instruction list:
    # start counting when instr.opname == "FOR_ITER" and stop right after the
    # matching backward jump (instr.opname.startswith("JUMP_BACKWARD")). If the
    # callable has no Python FOR_ITER loop (such as C-backed math.sumprod),
    # return the total instruction count (or 0 for built-in C functions without
    # __code__).


    # Define classify_bottleneck(ns_per_item: float, loop_opcodes: int) -> str
    # Map measured cost to the Five Multipliers:
    # - ns_per_item >= 80.0 or loop_opcodes >= 12 -> "Multiplier #1 (Attr/Box Waste) + #4 (AoS Cache)"
    # - ns_per_item >= 10.0                       -> "Multiplier #1 (VM Dispatch) + #2 (Serial Chain)"
    # - otherwise                                 -> "C/Native Speed (<10 ns/item: VM Dispatch Gone)"


    # Define diagnose_python_zone(name: str, fn: Callable[[], float], items: int, bytes_per_item: float, loop_fn: Callable[..., object] | None = None, repeats: int = 5) -> ZoneDiagnostic
    # Warm fn() once before timing so PEP 659 adaptive specialization kicks in,
    # measure min_ns = benchmark_min_ns(fn, repeats=repeats), compute
    # loop_opcodes = count_loop_body_opcodes(loop_fn) if loop_fn is not None else 0,
    # classify with classify_bottleneck(min_ns / max(1, items), loop_opcodes),
    # and return ZoneDiagnostic(name, items, min_ns, loop_opcodes, bytes_per_item, diagnosis).


def aos_to_soa_to_c_reduction() -> None:

    # Why does moving from Stage 1 to Stage 2 to Stage 3 shrink frame time by
    # more than an order of magnitude?
    # - Stage 1 (list[ParticleAoS]) chases two heap pointers per element: first
    #   from the list pointer table to each ParticleAoS, then to boxed
    #   24-byte PyFloatObject values for p.x and p.vx, running LOAD_ATTR on
    #   every iteration.
    # - Stage 2 (array("d") + hoisted LOAD_FAST locals) removes scattered object
    #   headers so 8 doubles pack into each 64-byte cache line, and binding
    #   local_xs = xs avoids global lookups, though Python's for loop still
    #   boxes temporary floats and pays VM dispatch every pass.
    # - Stage 3 (math.sumprod(xs, vxs) or sum(xs)) pushes the entire loop into
    #   compiled C over raw unboxed doubles, eliminating loop bytecode.

    sample_p = ParticleAoS(1.0, 2.0, 0.5, -0.5, 7, 3.0)
    sample_arr = array("d", [1.0, 2.0])
    with memoryview(sample_arr) as mv_s:
        soa_item_bytes = mv_s.nbytes / len(mv_s)
    print(
        f"AoS ParticleAoS={sys.getsizeof(sample_p)} B (+ boxed floats {sys.getsizeof(1.0)} B each) | "
        f"SoA array('d')={soa_item_bytes:.1f} B/scalar"
    )

    # Define stage1_aos_object_loop(particles: list[ParticleAoS]) -> float
    # Loop for p in particles: accumulating total += p.x * p.vx and return total.


    # Define stage2_soa_array_hoisted(xs: array, vxs: array) -> float
    # Hoist local_xs = xs, local_vxs = vxs, n = len(xs), loop for i in range(n):
    # accumulating total += local_xs[i] * local_vxs[i], and return total.


    # Define stage3_c_bulk_reduction(xs: array, vxs: array) -> float
    # Return math.sumprod(xs, vxs) (also try comparing sum(xs) for a single-array
    # C reduction vs math.sumprod across two contiguous buffers!).


    # Build count = 10_000 particles in both particles: list[ParticleAoS] and
    # SoA buffers xs = array("d", ...), vxs = array("d", ...) using matching values
    # x = (i % 97) * 0.125 and vx = ((i % 31) - 15) * 0.0625.
    # Compute true AoS bytes per item (sys.getsizeof(particles[0]) + 2 * sys.getsizeof(1.0))
    # and true SoA bytes per item via memoryview(xs) and memoryview(vxs)
    # ((mv_x.nbytes + mv_v.nbytes) / len(mv_x)).
    # Run diagnose_python_zone on all three stages, assert all three sums agree
    # within 1e-6, and print a table showing Stage, Min ms, ns/item, LoopOps,
    # MB/s, and Diagnosis!


def when_builtins_arent_enough() -> None:

    # math.sumprod solves dot products cleanly in C, but real simulations quickly
    # outgrow single stdlib reducers—for example, computing squared distance
    # sum((x1[i] - x0[i]) ** 2 + (y1[i] - y0[i]) ** 2) or clamping velocities.
    # Writing sum((b - a) * (b - a) for a, b in zip(xs, vxs)) looks C-backed at
    # first glance, yet Python still executes a generator frame's bytecode for
    # every single element!
    #
    # When no built-in C reducer fits your hot loop and Tracy shows that one
    # zone owns >90% of frame time, you keep 95% of your program in Python and
    # pass zero-copy ctypes.from_buffer views straight into an Odin #simd DLL
    # (covered hands-on in 800_hybrid_python_odin_tracy_offload_lab/).

    a_buf = array("d", [float(i % 17) for i in range(500)])
    b_buf = array("d", [float((i + 3) % 19) for i in range(500)])
    gen_ns = benchmark_min_ns(
        lambda: sum((b - a) * (b - a) for a, b in zip(a_buf, b_buf)),
        repeats=3,
    )
    sumprod_ns = benchmark_min_ns(lambda: math.sumprod(a_buf, b_buf), repeats=3)
    print(
        f"500-item preview: generator-in-sum={gen_ns / 500:.1f} ns/item vs "
        f"math.sumprod={sumprod_ns / 500:.1f} ns/item"
    )

    # Compare a generator expression inside sum(...) against math.sumprod at
    # count = 10_000 using diagnose_python_zone:
    # - Wrap gen = ((b - a) * (b - a) for a, b in zip(xs, vxs)) and pass
    #   gen.gi_code to dis.Bytecode(gen.gi_code, adaptive=True) to inspect why
    #   generator expressions inside sum() still pay FOR_ITER + BINARY_OP per item.
    # - Note the crossover threshold: once your custom non-builtin kernel
    #   exceeds ~1,000 elements per frame, offloading the array("f") buffers via
    #   (ctypes.c_float * count).from_buffer(arr) in Lab 800 eliminates Python
    #   VM dispatch entirely.


def main() -> None:

    print("=== 1. Adaptive loop-body bytecode and memoryview bandwidth ===")
    adaptive_bytecode_and_bandwidth_metrics()

    print("\n=== 2. AoS -> hoisted SoA -> C-backed bulk reduction ===")
    aos_to_soa_to_c_reduction()

    print("\n=== 3. When built-in C reducers aren't enough (FFI preview) ===")
    when_builtins_arent_enough()


if __name__ == "__main__":
    main()
