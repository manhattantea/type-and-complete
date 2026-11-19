// odin run 599_tracy_hotspot_profiler_lab

package main

import "base:intrinsics"
import "core:fmt"
import "core:mem"

/*
This Lab wires Odin's @(deferred_out) zone stack and context.allocator hooks
into a realistic four-stage pipeline so you can catch hidden per-item heap
allocations from a single ranked table and prove your fix with identical
checksums and zero frame allocations.

For the full five-system Five-Multipliers Hotspot Hunt capstone (covering
Waste, IPC, SIMD, Cache, and Multithreading), continue to
../tracy_how_to/900_hotspot_hunt_five_multipliers_lab/.
*/

run_smoke_baseline :: proc() {

	/*
	Before hooking up the full 1,024-record multi-frame profile, we smoke-test
	the four baseline pipeline procedures on 8 records wrapped in a standard
	mem.Tracking_Allocator so any baseline memory leak fails loudly right away.
	*/

	track: mem.Tracking_Allocator
	mem.tracking_allocator_init(&track, context.allocator)
	defer mem.tracking_allocator_destroy(&track)
	context.allocator = mem.tracking_allocator(&track)

	anchor_recs := make([]Record, 8)
	defer delete(anchor_recs)
	anchor_out := make([]f32, 8)
	defer delete(anchor_out)
	for i in 0 ..< 8 {
		anchor_recs[i] = Record{id = u32(i), x = f32(i), y = 1.5, vx = 2.0, vy = -1.0, weight = 0.5}
	}

	prof_reset(&g_prof)
	g_prof.backing = context.allocator
	anchor_data := Pipeline_Data{records = anchor_recs, scratch_out = anchor_out}
	c0 := intrinsics.read_cycle_counter()
	parse_header_cold(&anchor_data)
	build_lookup_cold(&anchor_data)
	transform_records_hotspot(&anchor_data)
	verify_checksum_cold(&anchor_data)
	c1 := intrinsics.read_cycle_counter()

	prof_summary_header(&g_prof)
	fmt.printfln("Lab 599 smoke check: magic=0x%08X, checksum=%.4f, cycles=%d, live_allocs=%d",
		anchor_data.header_magic, anchor_data.checksum, c1 - c0, len(track.allocation_map))

	// Allocate a 1,024-record Pipeline_Data dataset:
	// records := make([]Record, 1024) and scratch := make([]f32, 1024) with
	// defer delete on each. Populate records[i] deterministically for 0..<1024
	// (for example x = f32(i % 64) * 0.25, y = 1.5, vx = 2.0, vy = -1.0, weight = 0.5)
	// and verify prof_allocator(&g_prof) wraps context.allocator cleanly.


	// Profile 5 baseline frames under prof_allocator(&g_prof):
	// Call prof_reset(&g_prof), then open a { ... } block saving
	// orig := context.allocator with defer context.allocator = orig and setting
	// context.allocator = prof_allocator(&g_prof). In each of 5 frames, open
	// prof_zone("Frame"), call parse_header_cold, build_lookup_cold,
	// transform_records_hotspot, and verify_checksum_cold, then call
	// prof_frame_mark(&g_prof). Outside the frame loop, call prof_print_table(&g_prof)
	// and record baseline_cycles := g_prof.total_frame_cycles plus
	// baseline_checksum := data.checksum.


	// Re-profile 5 fixed frames replacing ONLY transform_records_hotspot with
	// transform_records_optimized:
	// Call prof_reset(&g_prof), run the same 5-frame loop calling
	// transform_records_optimized, call prof_print_table(&g_prof), assert
	// abs(data.checksum - baseline_checksum) < 1e-6 and
	// g_prof.total_alloc_count == 0, and print the cycle speedup factor!
	// Finally verify len(track.allocation_map) == 0 and len(track.bad_free_array) == 0.
}

main :: proc() {

	fmt.println("=== 1. Lab 599 Odin Tracy zone and allocator hotspot hunt ===")
	run_smoke_baseline()
}
