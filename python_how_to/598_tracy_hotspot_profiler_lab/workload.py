# 598_tracy_hotspot_profiler_lab/workload.py

from array import array
import math

from tracy_prof import TracySession


# This 4-stage pipeline separates cold setup/reporting (<1% of runtime) from
# one proven inner-loop hotspot:
# - parse_header_cold and build_index_cold run once per batch (keep clean).
# - transform_records_hotspot walks list[dict[str, float]], allocates a
#   temporary dict per sample, and hits LOAD_GLOBAL for math.sqrt / math.sin.
# - transform_records_optimized fixes ONLY that hotspot using contiguous
#   array("d") columns, hoisted local math bindings (LOAD_FAST), and in-place
#   writes into a pre-allocated output array("d").
# - verify_checksum_cold sums outputs accurately via math.fsum (<1%).


def generate_sensor_batch(
    count: int = 8_000,
) -> tuple[list[dict[str, float]], tuple[array, array, array]]:

    records: list[dict[str, float]] = [
        {
            "x": 1.0 + (i % 100) * 0.1,
            "y": 2.0 + (i % 50) * 0.2,
            "w": 0.5 + (i % 7) * 0.25,
        }
        for i in range(count)
    ]
    xs = array("d", (r["x"] for r in records))
    ys = array("d", (r["y"] for r in records))
    weights = array("d", (r["w"] for r in records))
    return (records, (xs, ys, weights))


# Define def parse_header_cold(raw_header: str, prof: TracySession) -> dict[str, str]:
# Wrap inside with prof.zone("parse_header_cold"): and split raw_header
# (e.g. "version=2;site=north;unit=metric") on ";" and "=" into dict[str, str].


# Define def build_index_cold(header: dict[str, str], prof: TracySession) -> dict[str, int]:
# Wrap inside with prof.zone("build_index_cold"): and return a small lookup
# dict such as {k: idx for idx, k in enumerate(sorted(header))}.


# Define def transform_records_hotspot(records: list[dict[str, float]], prof: TracySession) -> list[float]:
# Wrap the ENTIRE loop (never a single iteration!) inside
# with prof.zone("transform_records_hotspot", value=len(records)):
# For each rec in records, build a temporary dict
# tmp = {"mag": math.sqrt(rec["x"] * rec["x"] + rec["y"] * rec["y"]), "bias": math.sin(rec["x"])}
# and append tmp["mag"] * rec["w"] + tmp["bias"] to results.


# Define def transform_records_optimized(xs: array, ys: array, weights: array, out: array, prof: TracySession) -> array:
# Wrap the loop inside with prof.zone("transform_records_optimized", value=len(xs)):
# Hoist sqrt = math.sqrt and sin = math.sin into local variables before the
# loop, iterate for i, (x, y, w) in enumerate(zip(xs, ys, weights)):, write
# sqrt(x * x + y * y) * w + sin(x) into out[i], and return out.


# Define def verify_checksum_cold(values: list[float] | array, prof: TracySession) -> float:
# Wrap inside with prof.zone("verify_checksum_cold"): and return math.fsum(values).


# Define def run_pipeline(records: list[dict[str, float]], xs: array, ys: array, weights: array, out: array | None, optimized: bool, prof: TracySession) -> float:
# Open with prof.zone("PipelineFrame", value=len(records)):, call
# parse_header_cold("version=2;site=north;unit=metric", prof), call
# build_index_cold(header, prof), dispatch to transform_records_optimized
# when optimized and out is not None else transform_records_hotspot, compute
# checksum = verify_checksum_cold(transformed, prof), call prof.frame_mark()
# at frame end, and return checksum.
