// odin run 900_hotspot_hunt_five_multipliers_lab

package main

import "base:intrinsics"
import "core:fmt"
import "core:mem"

/*
Hotspot Hunt & Five Multipliers Capstone Driver (main.odin)

Why verify cold systems and full-state parity alongside speedup?
Speeding up code by deleting work or breaking edge elements produces fake
speedups. In this capstone Lab you run the full 5-system pipeline before and
after optimization, verify from the Self Cycles report that 3 of the 5 systems
are cold herrings (< 1% of cycles) that stay untouched, fix only the 2 true
hotspots across Multipliers #1 through #4, and prove identical full-buffer
results with zero steady-state heap allocations.

When we wrap context.allocator with mem.Tracking_Allocator in main, every
allocation passes through track before reaching the OS heap, so defer runs at
exit to confirm zero leaks or bad frees. Suppose step_entity_kinematics
allocates and frees 2,048 label strings inside a single frame: track reports 0
leaks at program exit because every string was freed, yet profiler_allocator
catches 2,048 alloc_calls_now of per-frame heap churn ruining frame time.
*/

FRAME_COUNT :: 8
FRAME_DT :: f32(0.016)

run_baseline_smoke_frame :: proc(w: ^Sim_World, dt: f32) -> f32 {

	load_world_config(w)
	build_spatial_tags(w)
	step_entity_kinematics(w, dt)
	sensor_sum := evaluate_sensor_polynomials(w)
	return audit_frame_checksum(w, false, sensor_sum)
}

main :: proc() {

	track: mem.Tracking_Allocator
	mem.tracking_allocator_init(&track, context.allocator)
	defer {
		if len(track.allocation_map) > 0 {
			for _, entry in track.allocation_map {
				fmt.eprintf("Leaked %d bytes at %v\n", entry.size, entry.location)
			}
		}
		if len(track.bad_free_array) > 0 {
			for entry in track.bad_free_array {
				fmt.eprintf("Bad free %p at %v\n", entry.memory, entry.location)
			}
		}
		mem.tracking_allocator_destroy(&track)
	}
	context.allocator = mem.tracking_allocator(&track)

	world: Sim_World
	init_sim_world(&world)
	defer destroy_sim_world(&world)

	anchor_prof: Profiler
	profiler_init(&anchor_prof, context.allocator)
	c0 := intrinsics.read_cycle_counter()
	anchor_checksum: f32
	{
		prev_alloc := context.allocator
		defer context.allocator = prev_alloc
		context.allocator = profiler_allocator(&anchor_prof)
		anchor_checksum = run_baseline_smoke_frame(&world, FRAME_DT)
		frame_mark(&anchor_prof)
	}
	c1 := intrinsics.read_cycle_counter()
	fmt.printfln(
		"Lab 900 smoke frame: checksum=%.4f | cycles=%d | frame_allocs=%d (%d B) | leaks=%d",
		anchor_checksum, c1 - c0, anchor_prof.alloc_calls_now, anchor_prof.alloc_bytes_now, len(track.allocation_map),
	)

	// After completing zone_enter, zone_exit, and print_hotspot_report in
	// profiler.odin, add a helper run_sim_frame :: proc(prof: ^Profiler, w: ^Sim_World, dt: f32, optimized: bool) -> f32
	// above main that opens zone_enter(prof, "SimFrame", ENTITY_COUNT + SENSOR_COUNT),
	// calls load_world_config, build_spatial_tags, either step_entity_kinematics_fast
	// or step_entity_kinematics, either evaluate_sensor_polynomials_fast or
	// evaluate_sensor_polynomials, and returns audit_frame_checksum(prof, w, optimized, sensor_sum).


	// Profile 8 baseline frames (optimized = false):
	// Call reset_sim_world(&world) and initialize base_prof: Profiler via
	// profiler_init(&base_prof, context.allocator). Inside a scoped block with
	// context.allocator = profiler_allocator(&base_prof), run a loop over
	// 0..<FRAME_COUNT calling base_checksum = run_sim_frame(&base_prof, &world, FRAME_DT, false)
	// and frame_mark(&base_prof), bracketing the loop with intrinsics.read_cycle_counter()
	// to record base_cycles := t1 - t0. Snapshot base_config_scale := world.config_scale
	// and base_tag_sum := world.tag_sum, then call print_hotspot_report(&base_prof, "BASELINE")
	// and verify that load_world_config, build_spatial_tags, and audit_frame_checksum
	// sit below 1% of Self Cycles while step_entity_kinematics and
	// evaluate_sensor_polynomials dominate frame cycles.


	// Implement step_entity_kinematics_fast and evaluate_sensor_polynomials_fast
	// in simulation.odin (leaving the three cold systems untouched), then profile
	// 8 optimized frames (optimized = true) into fast_prof: Profiler after
	// calling reset_sim_world(&world). Measure fast_cycles := t3 - t2, then
	// assert cold outputs stayed identical (assert(world.config_scale == base_config_scale)
	// and assert(world.tag_sum == base_tag_sum)), assert full-state checksum parity
	// (assert(abs(base_checksum - fast_checksum) < 1e-2)), and assert zero heap
	// allocations during optimized frames (assert(fast_prof.alloc_calls_now == 0 && fast_prof.alloc_bytes_now == 0)).
	// Finish by calling print_hotspot_report(&fast_prof, "OPTIMIZED") and printing
	// the total frame speedup f64(base_cycles) / f64(fast_cycles).
}
