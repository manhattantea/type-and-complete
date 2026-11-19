# python 800_hybrid_python_odin_tracy_offload_lab/main.py

# Hybrid Python <-> Odin SIMD Tracy Offload Lab:
# Keep 95% of your program—data setup, validation, reporting, and Chrome Trace
# export—in clean Python, pack hot coordinates into contiguous array("f") SoA
# buffers, and offload the 95% hotspot zero-copy across ctypes to Odin's
# #simd[4]f32 kernel (kernel_simd_sum_distances in odin_simd_kernel.odin).
#
# Notice the FFI crossover rule you will measure directly in this lab:
# Suppose you offload only N = 16 segments. Creating four ctypes.from_buffer
# array views and crossing the C ABI boundary takes hundreds of nanoseconds,
# dwarfing 16 float pairs of math! Once N reaches 50_000 segments, that one-time
# FFI boundary fee vanishes into < 0.01 ns/pair and Odin #simd wins > 50x.

from array import array
import ctypes
from dataclasses import dataclass
import math
from pathlib import Path

from tracy_bridge import TracyTimeline


@dataclass(slots=True)
class SegmentPairAoS:

    x0: float
    y0: float
    x1: float
    y1: float


SAMPLE_CORPUS: list[SegmentPairAoS] = [
    SegmentPairAoS(0.0, 0.0, 3.0, 4.0),
    SegmentPairAoS(1.0, 1.0, 5.0, 4.0),
    SegmentPairAoS(2.0, 2.0, 2.0, 2.0),
    SegmentPairAoS(3.0, 3.0, 6.0, 7.0),
]


def build_segment_inputs(
    count: int,
) -> tuple[list[SegmentPairAoS], array, array, array, array]:

    x0 = array("f", ((i % 97) * 0.01 for i in range(count)))
    y0 = array("f", ((i % 53) * 0.02 for i in range(count)))
    x1 = array("f", (((i + 13) % 89) * 0.015 for i in range(count)))
    y1 = array("f", (((i + 7) % 61) * 0.025 for i in range(count)))
    pairs = [SegmentPairAoS(x0[i], y0[i], x1[i], y1[i]) for i in range(count)]
    return pairs, x0, y0, x1, y1


def load_odin_simd_kernel() -> ctypes.CDLL | None:

    dll_path = Path(__file__).with_name("odin_simd_kernel.dll")
    if not dll_path.is_file():
        return None
    try:
        lib = ctypes.CDLL(str(dll_path))
        fn = lib.kernel_simd_sum_distances
        fn.argtypes = [
            ctypes.POINTER(ctypes.c_float),
            ctypes.POINTER(ctypes.c_float),
            ctypes.POINTER(ctypes.c_float),
            ctypes.POINTER(ctypes.c_float),
            ctypes.c_int64,
        ]
        fn.restype = ctypes.c_float
    except (OSError, AttributeError):
        return None
    return lib


def stage1_python_aos(pairs: list[SegmentPairAoS]) -> float:

    total = 0.0
    for p in pairs:
        dx = p.x1 - p.x0
        dy = p.y1 - p.y0
        total += dx * dx + dy * dy
    return total


# Define stage2_python_soa(x0: array, y0: array, x1: array, y1: array) -> float
# Hoist local references lx0 = x0, ly0 = y0, lx1 = x1, ly1 = y1, n = len(x0),
# loop for i in range(n): computing dx = lx1[i] - lx0[i] and dy = ly1[i] - ly0[i],
# accumulate dx * dx + dy * dy, and return the float total.


# Define stage3_odin_offload_or_fallback(x0: array, y0: array, x1: array, y1: array, odin_lib: ctypes.CDLL | None) -> float
# When odin_lib is not None:
# - Compute count = len(x0) and create four zero-copy ctypes buffer views via
#   (ctypes.c_float * count).from_buffer(arr) for x0, y0, x1, and y1 (keep the
#   source array objects alive for the duration of the C call!).
# - Call float(odin_lib.kernel_simd_sum_distances(cx0, cy0, cx1, cy1, count)).
# When odin_lib is None (DLL not compiled yet), fall back cleanly by calling
# stage2_python_soa(x0, y0, x1, y1) (or math.fsum over zip pairs) so the lab
# still verifies end-to-end with zero errors.


def main() -> None:

    dll_path = Path(__file__).with_name("odin_simd_kernel.dll")
    odin_lib = load_odin_simd_kernel()
    timeline = TracyTimeline()
    sample_total = stage1_python_aos(SAMPLE_CORPUS)
    assert math.isclose(sample_total, 75.0, rel_tol=1e-6)

    if odin_lib is not None:
        print(
            f"Loaded native Odin SIMD kernel: {dll_path.name} | "
            f"tid={timeline.main_tid} | sample_sum={sample_total:.1f}"
        )
    else:
        print(
            f"{dll_path.name} not found -- running graceful Python fallback "
            f"(tid={timeline.main_tid}, sample_sum={sample_total:.1f}).\n"
            "  Build native DLL with: odin build "
            "800_hybrid_python_odin_tracy_offload_lab/odin_simd_kernel.odin "
            "-file -build-mode:dll -out:800_hybrid_python_odin_tracy_offload_lab/"
            "odin_simd_kernel.dll -o:speed"
        )

    # Measure the N-size FFI crossover across N = 16 vs N = 50_000:
    # For each n in (16, 50_000), call pairs, x0, y0, x1, y1 = build_segment_inputs(n)
    # and run 3 warmup/timed iterations recording into timeline:
    # - with timeline.zone(f"Stage1_Python_AoS_N{n}", item_count=n, layer="Python"):
    #     r1 = stage1_python_aos(pairs)
    # - with timeline.zone(f"Stage2_Python_SoA_N{n}", item_count=n, layer="Python"):
    #     r2 = stage2_python_soa(x0, y0, x1, y1)
    # - layer = "OdinSIMD" if odin_lib is not None else "PyFallback"
    #   with timeline.zone(f"Stage3_Odin_SIMD_N{n}", item_count=n, layer=layer):
    #     r3 = stage3_odin_offload_or_fallback(x0, y0, x1, y1, odin_lib)
    # - timeline.frame_mark()
    # Assert abs(r1 - r2) / max(1.0, abs(r1)) < 1e-4 and
    # abs(r1 - r3) / max(1.0, abs(r1)) < 1e-3 at both N = 16 and N = 50_000.
    # Print timeline.format_comparison_report() to compare how ctypes call overhead
    # dominates at N = 16 while Odin #simd[4]f32 wins > 50x at N = 50_000, then
    # serialize events = timeline.to_chrome_trace_events() with json.dumps(events)
    # in memory and verify distinct pid layers exist for Python vs Odin/Fallback!


if __name__ == "__main__":
    main()
