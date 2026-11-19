// Five Multipliers Lab — Progressive IPC, SIMD, #soa, and multi-thread stages

package main

import "core:simd"
import "core:thread"

/*
Once Stage 0 establishes the reference checksum and baseline cycle count,
each stage below removes one hardware bottleneck at a time:

Stage 1 strips heap indirection and vtable calls by iterating contiguous
'[]Coord_Pair' values directly. Stage 2 breaks the loop-carried float add
dependency chain with four independent accumulators under '#no_bounds_check'.
Stage 3 switches layout to '#soa[]Coord_Pair' so each coordinate field sits
in its own contiguous array, letting two '#simd[4]f32' accumulators compute
8 pairs per iteration via 'simd.fma'. Stage 4 partitions that '#soa' slice
across 4 OS threads writing into '#align(64)' 'Worker_Slot' structs so
adjacent threads never share a 64-byte cache line.
*/

splat_f32x4 :: #force_inline proc "contextless" (v: f32) -> #simd[4]f32 {

	return #simd[4]f32{v, v, v, v}
}

haversine_chord_simd :: proc(x0, y0, x1, y1: #simd[4]f32) -> #simd[4]f32 {

	half_deg := splat_f32x4(0.5 * DEG_TO_RAD)
	deg := splat_f32x4(DEG_TO_RAD)
	c_one := splat_f32x4(1.0)
	c_s1 := splat_f32x4(-0.16666667)
	c_s2 := splat_f32x4(0.008333333)
	c_c1 := splat_f32x4(-0.5)
	c_c2 := splat_f32x4(0.041666668)

	dlat_half := (y1 - y0) * half_deg
	dlon_half := (x1 - x0) * half_deg
	lat0 := y0 * deg
	lat1 := y1 * deg

	dl2 := dlat_half * dlat_half
	sin_dlat := dlat_half * simd.fma(dl2, simd.fma(dl2, c_s2, c_s1), c_one)

	dn2 := dlon_half * dlon_half
	sin_dlon := dlon_half * simd.fma(dn2, simd.fma(dn2, c_s2, c_s1), c_one)

	l0_2 := lat0 * lat0
	cos_lat0 := simd.fma(l0_2, simd.fma(l0_2, c_c2, c_c1), c_one)

	l1_2 := lat1 * lat1
	cos_lat1 := simd.fma(l1_2, simd.fma(l1_2, c_c2, c_c1), c_one)

	return simd.fma(cos_lat0 * cos_lat1, sin_dlon * sin_dlon, sin_dlat * sin_dlat)
}

// Cache-line-isolated output slot: #align(64) keeps adjacent worker threads
// on separate 64-byte cache lines so MESI coherence never ping-pongs.
Worker_Slot :: struct #align(64) {
	pairs:       #soa[]Coord_Pair,
	partial_sum: f32,
}

join_and_destroy_workers :: proc(workers: []^thread.Thread) {

	for t in workers {
		if t != nil {
			thread.join(t)
			thread.destroy(t)
		}
	}
}

// Write Stage 1 at file scope with exact signature:
// compute_dewasted_aos :: proc(pairs: []Coord_Pair) -> f32
// Iterate 'for p in pairs' directly over contiguous Coord_Pair values and
// accumulate haversine_chord_scalar(p.x0, p.y0, p.x1, p.y1) into total: f32.


// Write Stage 2 at file scope with exact signature:
// compute_ipc_unrolled :: proc(pairs: []Coord_Pair) -> f32
// Break the serial float addition dependency chain using four independent
// accumulators (s0, s1, s2, s3: f32) inside a #no_bounds_check loop stepping
// i += 4 while i + 4 <= len(pairs), handle any < 4 tail elements with a scalar
// loop, and return (s0 + s1) + (s2 + s3) + tail.


// Write Stage 3 at file scope with exact signature:
// compute_simd_soa :: proc(pairs: #soa[]Coord_Pair) -> f32
// Note that on an #soa[]Coord_Pair slice, pairs.x0, pairs.y0, pairs.x1, and
// pairs.y1 are [^]f32 multi-pointers, so pairs.x0[i : i + 4] yields a []f32
// slice for simd.from_slice(#simd[4]f32, ...). Process 8 pairs per step using
// two independent accumulators v0, v1: #simd[4]f32 under #no_bounds_check, sum
// any < 8 tail pairs with haversine_chord_scalar, and return
// simd.reduce_add_ordered(v0 + v1) + tail_sum.


// Write Stage 4 at file scope with exact signatures:
// simd_worker_proc :: proc(slot: ^Worker_Slot)
// compute_multithreaded_soa :: proc(pairs: #soa[]Coord_Pair) -> f32
// In simd_worker_proc, set slot.partial_sum = compute_simd_soa(slot.pairs).
// In compute_multithreaded_soa, slice pairs into 4 contiguous #soa sub-slices
// across slots: [4]Worker_Slot (pairs[start:end] slices #soa directly without
// copying), spawn 4 threads into workers: [4]^thread.Thread with
// thread.create_and_start_with_poly_data(&slots[w], simd_worker_proc), call
// join_and_destroy_workers(workers[:]), and return the sum of all 4
// slots[w].partial_sum.
