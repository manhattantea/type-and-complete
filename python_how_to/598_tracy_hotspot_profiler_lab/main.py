# python 598_tracy_hotspot_profiler_lab/main.py

from array import array
import json
import tracemalloc

from tracy_prof import TracySession
from workload import generate_sensor_batch


# This lab pairs a pure-Python stdlib zone/tracemalloc wrapper (tracy_prof.py)
# with a 4-stage pipeline (workload.py) to measure self_ns, isolate a >90%
# hotspot, optimize only that hotspot, and verify Chrome Trace JSON output.
# For the full native Tracy C-ABI capstone, see tracy_how_to/950_hotspot_hunt_capstone_lab/.


def main() -> None:

    print("=== Tracy Hotspot Profiler Lab ===")
    sample_records, (sample_xs, _, _) = generate_sensor_batch(8)
    starter_prof = TracySession(track_memory=False)
    print(
        "Starter check -> sample records:",
        len(sample_records),
        "| array('d') len:",
        len(sample_xs),
        "| zones recorded:",
        len(starter_prof.zones),
        "| tracemalloc active:",
        tracemalloc.is_tracing(),
    )

    # Once TracySession methods in tracy_prof.py and pipeline functions in
    # workload.py are implemented, import run_pipeline from workload and run
    # the baseline profiling pass:
    # - Generate deterministic inputs: records, (xs, ys, weights) = generate_sensor_batch(8_000).
    # - Instantiate baseline_prof = TracySession(track_memory=True).
    # - Inside tracemalloc.start() / try: ... finally: tracemalloc.stop(), call
    #   base_checksum = run_pipeline(records, xs, ys, weights, None, optimized=False, prof=baseline_prof).
    # - Print baseline_prof.format_hotspot_table(), compute
    #   total_self = sum(z.self_ns for z in baseline_prof.zones.values()), and
    #   verify baseline_prof.zones["transform_records_hotspot"].self_ns / total_self > 0.90.


    # Run the hotspot-only optimized pass:
    # - Pre-allocate out = array("d", [0.0] * len(xs)) outside the profiled run.
    # - Instantiate opt_prof = TracySession(track_memory=True) and run
    #   opt_checksum = run_pipeline(records, xs, ys, weights, out, optimized=True, prof=opt_prof)
    #   with tracemalloc active.
    # - Assert abs(opt_checksum - base_checksum) < 1e-9, print
    #   opt_prof.format_hotspot_table(), and print the frame speedup
    #   (baseline_prof.frames[0] / opt_prof.frames[0]) plus memory savings.


    # Verify the Chrome / Perfetto JSON trace schema in memory (no temp files):
    # parse payload = json.loads(opt_prof.export_chrome_trace()), assert
    # "traceEvents" in payload and len(payload["traceEvents"]) == 5, and print
    # the first 2 trace event dicts.


if __name__ == "__main__":
    main()
