# python 950_python_hotspot_hunt_five_multipliers_lab/main.py

from profiler import TracySimProfiler
from simulation import (
    audit_frame_checksum,
    build_tag_lookup,
    compute_signal_energy,
    create_sim_world,
    load_world_config,
    step_entity_kinematics,
)


# Hotspot Hunt and Five Multipliers Python Capstone (main.py)
#
# Why compare both CPU Self Time and net heap bytes on every frame?
# In CPython, allocating 4,000 objects and 4,000 temporary dicts per frame does
# two separate kinds of damage: it burns bytecode cycles constructing objects,
# and it fills Generation-0 GC buckets so sweeps fire mid-frame and spike P95
# latency. Measuring Self Time alongside tracemalloc net bytes exposes both
# costs at once, while keeping cold functions untouched preserves readability.
#
# Suppose your baseline 5-frame trace spends 98% of self_ns in
# step_entity_kinematics and compute_signal_energy, while load_world_config,
# build_tag_lookup, and audit_frame_checksum together stay under 1%. Speeding
# up those two hotspots 10x to 40x lifts total frame throughput dramatically,
# whereas rewriting cold startup helpers buys almost nothing.


def main() -> None:

    preview = create_sim_world(entity_count=16)
    cfg = load_world_config()
    tags = build_tag_lookup(preview.count)
    step_entity_kinematics(preview, cfg["dt"])
    preview_energy = compute_signal_energy(preview)
    preview_chk = audit_frame_checksum(preview_energy, 0)
    prof = TracySimProfiler()
    print(
        f"Capstone 950 ready | backend={prof.backend_name} | "
        f"entities={preview.count} | dt={cfg['dt']} | "
        f"cold_tags={len(tags)} | chk={preview_chk:.6f}"
    )

    # First finish TracySimProfiler in profiler.py and the two optimized hotspot
    # functions in simulation.py, then import SimWorld, step_entity_kinematics_fast,
    # compute_signal_energy_fast, json, time, and tracemalloc into this file.

    # Define def run_baseline_frames(profiler: TracySimProfiler, world: SimWorld, frames: int = 5) -> float:
    # above main. Inside it, run cfg = load_world_config() inside
    # with profiler.zone("load_world_config", 1): and tags = build_tag_lookup(world.count)
    # inside with profiler.zone("build_tag_lookup", len(tags)): once before the
    # frame loop. Then for frame_idx in range(frames): record t0 = time.perf_counter_ns(),
    # wrap the tick in with profiler.zone("SimFrame", items=world.count): calling
    # step_entity_kinematics(world, cfg["dt"]), energy = compute_signal_energy(world),
    # and chk = audit_frame_checksum(energy, frame_idx) inside their own named
    # profiler.zone(...) scopes, call profiler.frame_mark(time.perf_counter_ns() - t0),
    # emit profiler.plot("Energy", chk) and profiler.message(f"Frame_{frame_idx}_Done"),
    # and return the final chk value after the loop.

    # Define def run_optimized_frames(profiler: TracySimProfiler, world: SimWorld, frames: int = 5) -> float:
    # above main mirroring run_baseline_frames exactly for all three cold
    # functions (load_world_config, build_tag_lookup, audit_frame_checksum) while
    # swapping ONLY the two measured hotspots to step_entity_kinematics_fast and
    # compute_signal_energy_fast.

    # Inside main, wrap the full comparison in tracemalloc.start() and
    # try: ... finally: tracemalloc.stop():
    # - Run a small warmup pass on create_sim_world(64) so CPython float/int
    #   freelists settle before measurements begin.
    # - Profile 5 baseline frames with base_prof = TracySimProfiler() on
    #   base_world = create_sim_world(4_000) into base_energy = run_baseline_frames(base_prof, base_world, 5).
    # - Profile 5 optimized frames with fast_prof = TracySimProfiler() on
    #   fast_world = create_sim_world(4_000) into fast_energy = run_optimized_frames(fast_prof, fast_world, 5).

    # Verify correctness, cold preservation, zero steady-state allocations, and speedup:
    # - Assert cold functions stayed unmodified: load_world_config() == cfg,
    #   build_tag_lookup(preview.count) == tags, and check that load_world_config,
    #   build_tag_lookup, and audit_frame_checksum each account for < 1% of
    #   base_prof total self_ns.
    # - Assert numerical checksum parity within 1e-9: assert abs(base_energy - fast_energy) < 1e-9
    #   and assert all(abs(e.x - x) < 1e-9 and abs(e.y - y) < 1e-9 for e, x, y in zip(base_world.entities, fast_world.xs, fast_world.ys)).
    # - Assert zero net heap growth in both optimized hotspots:
    #   assert fast_prof.metrics["step_entity_kinematics_fast"].net_bytes == 0
    #   assert fast_prof.metrics["compute_signal_energy_fast"].net_bytes == 0.
    # - Print base_prof.format_report("Baseline Run") and fast_prof.format_report("Optimized Run"),
    #   print the P95 speedup (base_prof.percentile_ns(95) / fast_prof.percentile_ns(95))
    #   alongside total frame speedup (sum(base_prof.frame_times_ns) / sum(fast_prof.frame_times_ns)),
    #   and verify json.loads(fast_prof.to_chrome_trace_json())["traceEvents"]
    #   contains "X", "C", and "i" phases.


if __name__ == "__main__":
    main()
