// odin run 710_simd_vectors.odin -file

package main

import "core:fmt"
import "core:simd"

/*
A scalar addition adds one number per instruction. Hardware SIMD (Single
Instruction, Multiple Data) registers — SSE/AVX on x86_64 and NEON on ARM64 —
pack 4 floats, 8 floats, or 16 bytes into a single vector register and apply the
same operation to every lane simultaneously.

Odin exposes hardware vectors directly in the type system as '#simd[N]T',
where N must be a power of 2 (such as 4, 8, or 16):

    #simd[4]f32       128-bit vector holding 4 single-precision floats
    #simd[16]u8       128-bit vector holding 16 bytes (great for text scans!)
    #simd[4]f32(5.0)  broadcasts 5.0 into all 4 lanes

Because '#simd[N]T' represents a CPU vector register rather than an addressable
slice in memory, arithmetic operators (+, -, *, /) work lane-wise, and Odin
provides 'core:simd' intrinsics for horizontal reductions, slice loads, and
branchless lane masking.

This file is split into three sections called from main at the bottom so you
can read top to bottom and run the program at any point.
*/

vector_registers_and_reductions :: proc() {

	/*
	Suppose a := #simd[4]f32{1, 2, 3, 4}, b := #simd[4]f32{10, 20, 30, 40}, and
	c := #simd[4]f32{0.5, 0.5, 0.5, 0.5}. Calling 'simd.fma(a, b, c)' computes
	(a * b) + c across all 4 lanes in a single fused multiply-add operation,
	producing {10.5, 20.5, 30.5, 40.5} without intermediate rounding.

	Notice you cannot write 'res[0]' on a '#simd[4]f32' because vector lanes live
	in a CPU register rather than memory; instead, use 'simd.extract(res, idx)'
	and 'simd.replace(res, idx, val)', or convert to/from a regular array with
	'simd.to_array(res)' and 'simd.from_array(arr)'.
	*/

	// Here is a starter 4-lane fused multiply-add:

	a := #simd[4]f32{1.0, 2.0, 3.0, 4.0}
	b := #simd[4]f32{10.0, 20.0, 30.0, 40.0}
	c := #simd[4]f32{0.5, 0.5, 0.5, 0.5}
	res := simd.fma(a, b, c)
	fmt.printfln("fma result=%v", res)

	// Reduce all lanes horizontally to scalars: compute total := simd.reduce_add_ordered(res)
	// and peak := simd.reduce_max(res), then print both values with fmt.printfln.


	// Convert res into a regular [4]f32 via arr := simd.to_array(res), read lane
	// 2 with simd.extract(res, 2), create modified := simd.replace(res, 0, 999.0),
	// and rebuild a vector from arr using simd.from_array(arr). Print all four.


	// Try uncommenting both experiments below to see compiler diagnostics:
	// bad_len: #simd[3]f32        // lane count N must be a power of 2
	// bad_idx := res[0]           // direct [i] indexing rejected on #simd
}

branchless_masks_and_select :: proc() {

	/*
	Inside a scalar loop, an 'if x > limit' branch can mispredict and flush the
	CPU pipeline, and inside a SIMD register different lanes might take different
	branches at the same time! Instead of branching, SIMD compares all lanes in
	parallel to build a bitmask vector, then blends results branchlessly:

	    Suppose v := #simd[4]f32{12, 65, 48, 80} and limit := #simd[4]f32{50.0, 50.0, 50.0, 50.0}:
	        mask := simd.lanes_gt(v, limit)           // {0, 0xFFFFFFFF, 0, 0xFFFFFFFF}
	        out  := simd.select(mask, limit, v)       // {12, 50, 48, 50}

	Wherever a lane of 'mask' is all-1s, 'simd.select' picks the corresponding
	lane from the first vector; wherever 'mask' is 0, it picks from the second.
	*/

	// Here is a starter broadcast threshold vector:

	limit := #simd[4]f32{50.0, 50.0, 50.0, 50.0}
	fmt.printfln("broadcast limit=%v", limit)

	// Clamp sample := #simd[4]f32{10.5, 72.0, 50.0, 99.5} down to limit using
	// mask := simd.lanes_gt(sample, limit) and clamped := simd.select(mask, limit, sample).
	// Print mask and clamped.


	// Write a branchless helper proc outside main:
	// relu_vec :: proc(v: #simd[4]f32) -> #simd[4]f32
	// Inside it, use zero := #simd[4]f32{0.0, 0.0, 0.0, 0.0}, simd.lanes_lt(v, zero), and
	// simd.select so negative lanes become 0.0 and non-negative lanes stay v.
	// Call relu_vec(#simd[4]f32{-3.5, 4.0, -0.1, 7.2}) and print the result.
}

slicing_simd_loops_and_byte_scan :: proc() {

	/*
	Real slices rarely have lengths that are exact multiples of 4 or 16. The
	standard SIMD loop pattern processes full N-element chunks via
	'simd.from_slice(#simd[4]f32, data[i : i + 4])' while 'i + 4 <= len(data)',
	and then handles the remaining 0..=3 trailing elements in a scalar tail loop.

	The exact same pattern on '#simd[16]u8' turns text and byte scanning into a
	16-bytes-per-step operation: load 16 bytes, compare against '#simd[16]u8(needle)'
	with 'simd.lanes_eq', turn each matching 0xFF lane into 1 with 'simd.select',
	and sum the lane counts with 'simd.reduce_add_ordered'.
	*/

	// Here is a starter simd.from_slice load over a 4-float slice:

	seed_vals := []f32{1.0, 2.0, 3.0, 4.0}
	seed_vec := simd.from_slice(#simd[4]f32, seed_vals)
	fmt.printfln("loaded slice vec=%v", seed_vec)

	// Write a slice-processing proc outside main:
	// scale_and_bias_slice :: proc(data: []f32, scale, bias: f32)
	// Broadcast s := #simd[4]f32(scale) and b := #simd[4]f32(bias). Loop
	// i := 0; i + 4 <= len(data); i += 4 loading v := simd.from_slice(#simd[4]f32, data[i : i + 4]),
	// computing out := simd.to_array(simd.fma(v, s, b)), and copying out[:] back
	// into data[i : i + 4]. Finish any trailing < 4 elements with a scalar loop
	// (data[i] = data[i] * scale + bias), and test it here on an 11-element slice.


	// Write a 16-byte SIMD byte scanner outside main:
	// count_byte_simd :: proc(haystack: []u8, needle: u8) -> int
	// Broadcast target := #simd[16]u8(needle), ones := #simd[16]u8(1), and
	// zeros := #simd[16]u8(0). Step i += 16 while i + 16 <= len(haystack): load
	// chunk := simd.from_slice(#simd[16]u8, haystack[i : i + 16]), build
	// eq_mask := simd.lanes_eq(chunk, target), convert matches to 1s with
	// hits := simd.select(eq_mask, ones, zeros), and add int(simd.reduce_add_ordered(hits))
	// to total. Finish the remaining < 16 bytes in a scalar loop, then test
	// scanning transmute([]u8)string("alpha,beta,gamma,delta,epsilon,zeta,eta")
	// for ',' (expected: 6).


	// Add a fast-skip search helper outside main:
	// contains_byte_simd :: proc(haystack: []u8, needle: u8) -> bool
	// Load 16-byte chunks with #simd[16]u8, compute eq_mask := simd.lanes_eq(chunk, target),
	// and check simd.reduce_max(eq_mask) != 0 to return true immediately when any
	// of the 16 lanes matched, falling back to a scalar loop for < 16 tail bytes.
}

main :: proc() {

	fmt.println("=== 1. Vector registers, reductions, and lane access ===")
	vector_registers_and_reductions()

	fmt.println("\n=== 2. Branchless lane masks and simd.select ===")
	branchless_masks_and_select()

	fmt.println("\n=== 3. Slicing #simd loops and #simd[16]u8 byte scan ===")
	slicing_simd_loops_and_byte_scan()
}
