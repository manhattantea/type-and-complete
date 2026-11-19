// odin run 790_five_multipliers_haversine_lab

package main

import "base:intrinsics"
import "core:fmt"
import "core:simd"

/*
Five Multipliers Haversine Lab — Standalone Repetition Harness ('main.odin'):

This lab applies five progressive hardware optimizations to a single hot
kernel (polynomial Haversine chord evaluation) with zero external profiler
dependencies. Measure baseline vs. each stage with 'intrinsics.read_cycle_counter()'
and keep 'min_cycles' across 16 repetitions so OS interrupts and scheduler
noise drop out, revealing the true CPU execution cost.

Once you verify the five hardware multipliers here, see 'tracy_how_to/' for
profiler-guided timeline forensics and multi-system hotspot isolation.

Compile and compare both debug and optimized builds once your drills run:
    odin run 790_five_multipliers_haversine_lab
    odin run 790_five_multipliers_haversine_lab -o:speed
*/

Coord_Pair :: struct {
	x0, y0: f32,
	x1, y1: f32,
}

Benchmark_Result :: struct {
	name:       string,
	sum:        f32,
	min_cycles: u64,
}

main :: proc() {

	// Starter anchor verifying Stage 0 baseline, scalar/SIMD kernel parity, and Worker_Slot alignment:
	#assert(align_of(Worker_Slot) == 64)
	anchor_coords := [4]Coord_Pair{
		{-10.0, 20.0, 15.0, -5.0},
		{1.0, 2.0, 3.0, 4.0},
		{-25.0, 12.0, 8.0, -14.0},
		{0.0, 0.0, 10.0, 10.0},
	}
	naive_anchor := build_naive_pairs(anchor_coords[:])
	defer destroy_naive_pairs(naive_anchor)

	c0 := intrinsics.read_cycle_counter()
	naive_sum := compute_naive_wasted(naive_anchor)
	v_anchor := haversine_chord_simd(
		#simd[4]f32{-10.0, 1.0, -25.0, 0.0},
		#simd[4]f32{20.0, 2.0, 12.0, 0.0},
		#simd[4]f32{15.0, 3.0, 8.0, 10.0},
		#simd[4]f32{-5.0, 4.0, -14.0, 10.0},
	)
	c1 := intrinsics.read_cycle_counter()
	anchor_res := Benchmark_Result{name = "Anchor", sum = naive_sum, min_cycles = u64(c1 - c0)}
	fmt.printfln("Lab 790 ready: Coord_Pair=%dB | Worker_Slot=%dB (align=%dB) | naive=%.6f | simd_sum=%.6f (%d cyc)",
		size_of(Coord_Pair), size_of(Worker_Slot), align_of(Worker_Slot),
		anchor_res.sum, simd.reduce_add_ordered(v_anchor), anchor_res.min_cycles)

	// Generate N :: 4096 deterministic Coord_Pair records across three layouts:
	// allocate aos_pairs := make([]Coord_Pair, N) (defer delete(aos_pairs))
	// and soa_pairs := make(#soa[]Coord_Pair, N) (defer delete_soa(soa_pairs)).
	// Fill both with identical coordinates in [-30.0, 30.0] such as:
	// p := Coord_Pair{x0 = f32(i % 41) - 20.0, y0 = f32(i % 29) - 14.0, x1 = f32((i * 7) % 41) - 20.0, y1 = f32((i * 5) % 29) - 14.0}
	// Then construct naive_pairs := build_naive_pairs(aos_pairs) paired with
	// defer destroy_naive_pairs(naive_pairs).


	// Repetition-test all 5 stages across 16 iterations using
	// intrinsics.read_cycle_counter() and store results in [5]Benchmark_Result:
	// Stage 0 ("0. Naive Clean (VTable+Heap)"): compute_naive_wasted(naive_pairs)
	// Stage 1 ("1. De-Wasted AoS"):             compute_dewasted_aos(aos_pairs)
	// Stage 2 ("2. 4x IPC Unrolled"):           compute_ipc_unrolled(aos_pairs)
	// Stage 3 ("3. #soa + #simd[4]f32"):        compute_simd_soa(soa_pairs)
	// Stage 4 ("4. 4-Thread #soa + #align(64)"): compute_multithreaded_soa(soa_pairs)
	// Track min_cycles across the 16 runs per stage and feed each returned sum
	// into a live sink variable printed at the end so -o:speed cannot remove work.


	// Assert abs(r.sum - results[0].sum) < 1e-2 for every stage r in results,
	// print each stage's name, sum, min_cycles, and speedup ratio
	// f64(results[0].min_cycles) / f64(max(r.min_cycles, 1)), then run both
	// debug and -o:speed builds to compare the multiplier gains.
}
