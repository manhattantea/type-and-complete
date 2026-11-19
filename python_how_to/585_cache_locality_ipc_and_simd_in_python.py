# python 585_cache_locality_ipc_and_simd_in_python.py

from array import array
import sys
import time


def cache_lines_and_boxed_floats() -> None:

    # Modern CPUs never fetch single bytes from RAM; they pull memory into L1,
    # L2, and L3 caches in 64-byte chunks called cache lines. When data sits
    # back-to-back in memory, the CPU hardware prefetcher streams upcoming
    # cache lines ahead of your loop automatically.
    #
    # A Python list[float] defeats this completely because it does NOT store
    # floats contiguously! Instead, a list holds a flat array of 8-byte
    # PyObject* pointers, and each pointer aims at a separate 24-byte
    # PyFloatObject (ob_refcnt, ob_type, ob_fval) scattered across the heap.
    # Walking 8 floats in a list chases 8 pointers across up to 8 different
    # 64-byte cache lines.
    #
    # By contrast, stdlib array.array("d") packs raw 8-byte IEEE-754 doubles
    # contiguously in one C buffer with zero per-element PyObject headers:
    # - 8 doubles (array("d")) fit inside ONE 64-byte cache line.
    # - 16 32-bit floats (array("f")) fit inside ONE 64-byte cache line.
    #
    #     Suppose one_line = array("d", [float(i) for i in range(8)]).
    #     Calling one_line.buffer_info() returns (base_addr, 8), proving all 8
    #     values sit at base_addr + i * 8 within a single 64-byte cache line.

    one_cache_line = array("d", [float(i) for i in range(8)])
    base_addr, elem_count = one_cache_line.buffer_info()
    print(
        f"Contiguous array('d') of {elem_count} doubles at 0x{base_addr:x}: "
        f"{elem_count * one_cache_line.itemsize} bytes (1 cache line)"
    )

    # Build n = 4_096 floats in both layouts:
    # lst: list[float] = [float(i) * 0.5 + 0.125 for i in range(n)]
    # arr = array("d", lst)
    # Compute total list memory as sys.getsizeof(lst) + sum(sys.getsizeof(x) for x in lst)
    # (pointer table plus 4,096 separate 24-byte PyFloatObject allocations).


    # Compute contiguous buffer bytes for arr using buf_addr, buf_len = arr.buffer_info():
    # raw_bytes = buf_len * arr.itemsize and cache_lines = raw_bytes // 64.
    # Assert raw_bytes == 32_768 and cache_lines == 512, then print the memory
    # savings ratio (list_total_bytes / raw_bytes) alongside buf_addr.


def aos_vs_soa_and_c_backed_loops() -> None:

    # Data layout also determines how much of each 64-byte cache line is useful
    # work. An Array of Structures (AoS) such as list[tuple[float, float, float, float]]
    # interleaves (x, y, z, w) together. If a pass only needs x, 75%+ of the
    # fetched cache-line bytes are wasted on y, z, w and tuple headers.
    #
    # A Structure of Arrays (SoA) splits each field into its own contiguous
    # column: xs = array("d", ...), ys = array("d", ...), zs = array("d", ...),
    # ws = array("d", ...). Now every single byte pulled into L1 is an x value!
    #
    # Notice one subtle Python trap: even over a contiguous array("d"), writing
    # a pure-Python 'for x in xs:' loop still re-boxes each double into a
    # temporary PyFloatObject on every step, stalling instruction-level
    # parallelism (IPC) and blocking SIMD vector lanes. Passing the buffer to
    # a C-backed operation like sum(xs), memoryview, or a ctypes SIMD kernel
    # (covered in Primer 865) keeps values unboxed in C!
    #
    #     Suppose points holds 4,096 (x, y, z, w) tuples and xs holds 4,096 doubles.
    #     sum(p[0] for p in points) chases list -> tuple -> float pointers, while
    #     sum(xs) walks contiguous 8-byte doubles inside C.

    sample_xs = array("d", [1.0, 2.0, 3.0, 4.0])
    with memoryview(sample_xs) as mv:
        print("Starter memoryview nbytes:", mv.nbytes, "| sum:", sum(sample_xs))

    # Write two small helpers inside this function (or at module scope):
    # - def aos_sum_x(points: list[tuple[float, float, float, float]]) -> float:
    #   returning sum(p[0] for p in points)
    # - def soa_sum_x(xs: array) -> float:
    #   returning sum(xs)


    # Build n = 4_096 AoS points = [(float(i), 1.0, 2.0, 3.0) for i in range(n)]
    # and SoA columns xs = array("d", (float(i) for i in range(n))) plus ys, zs, ws.
    # Time both aos_sum_x(points) and soa_sum_x(xs) taking min(...) over 5
    # time.perf_counter_ns() runs, assert both sums equal 4_095 * 4_096 / 2,
    # and print the speedup ratio.


    # Wrap xs in with memoryview(xs) as mv: to inspect the contiguous buffer
    # without copying: assert mv.nbytes == 32_768 and mv[10] == 10.0, and check
    # mv.strides == (8,) confirming 8-byte stride between adjacent doubles.


def main() -> None:

    print("=== 1. Cache Lines and Boxed Floats ===")
    cache_lines_and_boxed_floats()
    print("=== 2. AoS vs SoA and C-Backed Loops ===")
    aos_vs_soa_and_c_backed_loops()


if __name__ == "__main__":
    main()
