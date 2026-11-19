// odin run 715_ipc_dependency_chains_and_unrolling.odin -file

package main

import "base:intrinsics"
import "core:fmt"
import "core:simd"

/*
Multiplier #2 in Casey Muratori's Computer, Enhance! ("Instructions Per Clock"
and "Analyzing Dependency Chains") explains why a single-threaded loop can run
3x to 4x slower than hardware speed even when every byte sits in L1d cache
with zero function-call waste.

Modern x86_64 and ARM64 cores are superscalar out-of-order machines capable of
retiring 4 to 6+ instructions every clock cycle on a single thread. However,
every instruction has two distinct costs:

    Latency      how many cycles until one result is ready (e.g. 3-4 cycles for fadd)
    Throughput   how many independent adds can start per cycle (e.g. 2 per cycle)

Consider a naive loop summing an array:

    for x in data {
        total += x
    }

Because iteration i + 1 cannot add until iteration i finishes updating 'total',
the CPU is trapped in a single loop-carried dependency chain and stalls 3-4
cycles on every element! Splitting 'total' into four independent accumulators
(s0, s1, s2, s3) gives the scheduler four unrelated chains to run in parallel.

This file is split into four sections called from main at the bottom so you
can read top to bottom and run the program at any point.
*/

latency_throughput_and_dependency_chains :: proc() {

	/*
	Suppose your CPU's floating-point adder has a 3-cycle latency and can start
	2 additions per cycle. With one accumulator 'total', you retire at most 1
	addition every 3 cycles (0.33 adds/cycle). With four independent accumulators
	's0, s1, s2, s3' inside a '#no_bounds_check' loop (which tells Odin to skip
	per-index slice bounds branches inside the hot loop once you guarantee
	'i + 4 <= len(data)'):

	    s0 += data[i + 0]
	    s1 += data[i + 1]
	    s2 += data[i + 2]
	    s3 += data[i + 3]

	none of the four chains wait on each other, letting the out-of-order engine
	fill its execution ports before summing '(s0 + s1) + (s2 + s3)' at the end.
	*/

	// Here is a quick RDTSC anchor measuring one fused multiply-add and reduce:

	a := #simd[4]f32{1.0, 2.0, 3.0, 4.0}
	b := #simd[4]f32{2.0, 2.0, 2.0, 2.0}
	c := #simd[4]f32{0.5, 0.5, 0.5, 0.5}
	fma_res := simd.fma(a, b, c)
	t0 := intrinsics.read_cycle_counter()
	anchor_total := simd.reduce_add_ordered(fma_res)
	t1 := intrinsics.read_cycle_counter()
	fmt.printfln("fma_sum=%v (%d cycles)", anchor_total, t1 - t0)

	// Write two scalar summation procedures at file scope:
	// sum_serial :: proc(data: []f32) -> f32
	// Loop for x in data accumulating into a single total: f32.
	//
	// sum_interleaved_4x :: proc(data: []f32) -> f32
	// Declare s0, s1, s2, s3: f32 and i := 0. Inside a #no_bounds_check loop
	// for ; i + 4 <= len(data); i += 4, add data[i + 0]..data[i + 3] into
	// s0..s3, handle the remaining < 4 elements in a scalar tail loop into s0,
	// and return (s0 + s1) + (s2 + s3).
}

simd_multi_accumulators :: proc() {

	/*
	Watch out for a common trap: switching to '#simd[4]f32' without unrolling
	still leaves a 3-to-4 cycle loop-carried dependency chain on that single
	vector accumulator! Every iteration still waits for the previous vector add
	to complete before starting the next.

	When you pair SIMD with two independent vector accumulators 'v0, v1: #simd[4]f32'
	processing 8 floats per step (i += 8), you multiply 4-lane vector width by
	multiple independent execution ports.
	*/

	// Write a 1-accumulator SIMD baseline and a 2-accumulator SIMD version at file scope:
	// sum_simd_serial :: proc(data: []f32) -> f32
	// Keep one v0: #simd[4]f32 accumulator stepping i += 4 with simd.from_slice(#simd[4]f32, data[i : i + 4]),
	// finish any < 4 tail, and return simd.reduce_add_ordered(v0) + rem.
	//
	// sum_simd_interleaved :: proc(data: []f32) -> f32
	// Declare two independent accumulators v0, v1: #simd[4]f32. Under #no_bounds_check,
	// step i += 8 loading data[i : i + 4] into v0 and data[i + 4 : i + 8] into v1.
	// Handle the < 8 tail in a scalar variable rem: f32, and return
	// simd.reduce_add_ordered(v0 + v1) + rem.
}

horners_rule_and_fma :: proc() {

	/*
	Suppose you need to evaluate the cubic polynomial 2.0 * x^3 - 3.0 * x^2 + 0.5 * x + 1.0
	across millions of coordinates. Computing x*x and x*x*x separately creates
	extra multiplications and longer dependency chains.

	Horner's rule rewrites the polynomial as nested multiply-adds:

	    ((2.0 * x - 3.0) * x + 0.5) * x + 1.0

	Each step has the exact shape (acc * x) + coeff, which maps straight to a
	single 'simd.fma(acc, x, coeff)' instruction across 4 lanes at once:

	    r := simd.fma(c3, x, c2)
	    r = simd.fma(r, x, c1)
	    r = simd.fma(r, x, c0)
	*/

	// Write two Horner's rule procedures at file scope:
	// eval_poly_horner_scalar :: proc(x: f32) -> f32
	// eval_poly_horner_simd :: proc(x: #simd[4]f32) -> #simd[4]f32
	// Evaluate 2.0 * x^3 - 3.0 * x^2 + 0.5 * x + 1.0 using c3 = 2.0, c2 = -3.0,
	// c1 = 0.5, c0 = 1.0 (broadcast as #simd[4]f32 in the SIMD version).


	// Write eval_poly_slice :: proc(xs: []f32, out: []f32) that evaluates the
	// cubic across xs in 4-float SIMD chunks (plus scalar tail) using
	// eval_poly_horner_simd and stores results into out.
}

repetition_benchmark_and_verification :: proc() {

	/*
	Because floating-point addition is not strictly associative for arbitrary
	decimals, changing accumulation order from 1 chain to 4 or 8 chains can
	change rounding in the lowest mantissa bits. Filling test buffers with
	exact binary-representable values like 'f32(i % 4) * 0.25 + 0.25' keeps
	every intermediate sum exact so you can assert bit-exact parity across all
	implementations before trusting the timing table.
	*/

	// Allocate data := make([]f32, 8192) with defer delete(data) (32 KB, L1d-resident)
	// and fill data[i] = f32(i % 4) * 0.25 + 0.25.


	// Benchmark sum_serial, sum_interleaved_4x, sum_simd_serial, and
	// sum_simd_interleaved over 64 repetitions using intrinsics.read_cycle_counter().
	// Record min_cycles for each variant, print all four sums (so -o:speed
	// cannot eliminate any call), assert s_serial == s_4x && s_4x == s_simd_serial && s_simd_serial == s_simd,
	// and print min_cycles plus cycles_per_element for each variant.


	// Verify eval_poly_horner_simd(#simd[4]f32{0.0, 1.0, 2.0, -1.0}) matches
	// eval_poly_horner_scalar on all 4 inputs (expected: 1.0, 0.5, 6.0, -4.5).
	// Run with -o:speed to see superscalar IPC and SIMD speedups clearly!
}

main :: proc() {

	fmt.println("=== 1. Latency, throughput, and dependency chains ===")
	latency_throughput_and_dependency_chains()

	fmt.println("\n=== 2. Multi-accumulator SIMD ===")
	simd_multi_accumulators()

	fmt.println("\n=== 3. Horner's rule and simd.fma ===")
	horners_rule_and_fma()

	fmt.println("\n=== 4. Repetition benchmark and verification ===")
	repetition_benchmark_and_verification()
}
