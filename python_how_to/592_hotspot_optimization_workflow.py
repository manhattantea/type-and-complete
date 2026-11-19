# python 592_hotspot_optimization_workflow.py

from array import array
from collections.abc import Iterator
from contextlib import contextmanager
import math
import time


def amdahl_speedup(hotspot_fraction: float, local_speedup: float) -> float:

    return 1.0 / ((1.0 - hotspot_fraction) + (hotspot_fraction / local_speedup))


def load_config_cold() -> dict[str, float]:

    return {"earth_radius_km": 6371.0, "scale": 1.0}


def format_summary_cold(total_km: float) -> str:

    return f"Total distance: {total_km:,.3f} km"


def amdahl_and_zone_timing() -> None:

    # Never optimize blindly, and never optimize cold code. In most Python
    # services, 90%+ of execution time lives in a tiny fraction of the code,
    # while startup config parsing and final formatting take <1%.
    #
    # Amdahl's Law quantifies why profiling comes first:
    # total_speedup = 1 / ((1 - p) + p / s), where p is the fraction of runtime
    # owned by the target block and s is how much faster you make that block.
    #
    #     Suppose a Haversine loop takes p = 0.95 (95%) of runtime and config
    #     loading takes p = 0.01 (1%).
    #     Speeding up the 95% hotspot by s = 10x yields 6.90x total speedup.
    #     Speeding up the 1% cold config loader by s = 100x yields only 1.01x!
    #
    # To prove which stage owns runtime before changing any algorithm, wrap
    # each pipeline stage in a lightweight contextlib.contextmanager zone timer
    # using time.perf_counter_ns().

    print(
        f"Amdahl check -> 95% @ 10x = {amdahl_speedup(0.95, 10.0):.2f}x total | "
        f"1% @ 100x = {amdahl_speedup(0.01, 100.0):.2f}x total"
    )

    # Define @contextmanager def profile_zone(label: str, timings: dict[str, int]) -> Iterator[None]:
    # inside this function (or at module scope): capture start_ns = time.perf_counter_ns(),
    # yield inside try: ... finally:, and in finally: add
    # time.perf_counter_ns() - start_ns into timings[label] = timings.get(label, 0) + elapsed_ns.


    # Test profile_zone on a tiny timings: dict[str, int] = {} dictionary wrapping
    # load_config_cold() and format_summary_cold(1234.5) to verify both labels
    # record positive nanosecond counts.


def haversine_hotspot_vs_optimized() -> None:

    # Once profiling proves a single inner loop owns >90% of runtime, optimize
    # ONLY that hotspot while leaving cold setup and formatting clean and
    # readable. Always keep a numerical checksum assertion so speed never
    # breaks correctness, and take min(...) across repeated trials to filter OS
    # scheduling jitter.
    #
    # Two focused Python changes speed up a math hotspot without hurting the
    # rest of the codebase:
    # 1. Hoist module attributes (sin = math.sin, cos = math.cos, sqrt = math.sqrt,
    #    asin = math.asin, radians = math.radians) into local variables before the
    #    loop so CPython emits fast LOAD_FAST instead of LOAD_GLOBAL every step.
    # 2. Replace list[dict[str, float]] string-keyed lookups with parallel
    #    Structure-of-Arrays array("d") columns iterated via zip(...).
    #
    #     Suppose n = 4_000 coordinate pairs sit in dicts vs 4 array("d") columns.
    #     The dict path pays 4 hash lookups + 5 global lookups per pair; the
    #     optimized hotspot reads unboxed doubles with local math bindings and
    #     produces the exact same total_km within 1e-9.

    cfg = load_config_cold()
    print("Starter cold config:", cfg, "|", format_summary_cold(0.0))

    # Define def compute_haversine_hotspot(records: list[dict[str, float]], radius_km: float) -> float:
    # summing great-circle distances over records with keys "lat1", "lon1",
    # "lat2", "lon2" in degrees: convert with math.radians(...), compute
    # dlat = r_lat2 - r_lat1, dlon = r_lon2 - r_lon1,
    # a = math.sin(dlat / 2.0) ** 2 + math.cos(r_lat1) * math.cos(r_lat2) * math.sin(dlon / 2.0) ** 2,
    # and accumulate 2.0 * radius_km * math.asin(math.sqrt(a)).


    # Define def compute_haversine_optimized(lat1: array, lon1: array, lat2: array, lon2: array, radius_km: float) -> float:
    # hoisting sin, cos, sqrt, asin, and radians into local variables before
    # iterating for la1, lo1, la2, lo2 in zip(lat1, lon1, lat2, lon2): with the
    # identical Haversine formula.


    # Build n = 4_000 deterministic coordinate pairs in both formats:
    # records = [{"lat1": 37.0 + (i % 90) * 0.05, "lon1": -122.0 + i * 0.001, "lat2": 40.0 + (i % 50) * 0.04, "lon2": -74.0 + i * 0.001} for i in range(n)]
    # and parallel array("d") columns lat1_arr, lon1_arr, lat2_arr, lon2_arr.
    # Profile load_config_cold -> compute_haversine_hotspot -> format_summary_cold
    # with profile_zone into baseline_timings, and print each zone's ms and %
    # share to verify compute_haversine_hotspot exceeds 90% of runtime.


    # Now run the same 3-stage pipeline swapping ONLY compute_haversine_hotspot
    # for compute_haversine_optimized across 5 trials, keeping the minimum
    # elapsed time per zone. Assert abs(opt_km - naive_km) < 1e-9 and print the
    # before/after comparison and total speedup.


def main() -> None:

    print("=== 1. Amdahl's Law and Zone Timing ===")
    amdahl_and_zone_timing()
    print("=== 2. Haversine Hotspot vs Optimized ===")
    haversine_hotspot_vs_optimized()


if __name__ == "__main__":
    main()
