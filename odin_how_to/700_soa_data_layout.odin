// odin run 700_soa_data_layout.odin -file

package main

import "core:fmt"

/*
Suppose you store 10,000 game particles in a plain Array of Structures (AoS),
like [10000]Particle where each Particle holds x, y, vx, vy, and life. Every
time the CPU reads particles[i].x, it does not fetch 4 bytes from RAM; it pulls
a whole 64-byte cache line into L1 cache. When a physics pass only updates
x += vx * dt, the CPU still drags y, vy, and life along for the ride, wasting
most of your cache capacity and memory bandwidth on fields the loop never reads.

Structure of Arrays (SoA) flips that layout inside out: all x values sit
contiguously in one array, all vx values in another, and all life values in
another. Odin builds SoA straight into the type system with the '#soa' modifier:

    #soa[N]Particle          fixed-size SoA array on the stack or in a struct
    #soa[]Particle           heap-allocated SoA slice via make(#soa[]Particle, n)
    #soa[dynamic]Particle    growable SoA array via make(#soa[dynamic]Particle)

You still describe the data once in a normal struct, yet Odin stores separate
parallel arrays behind the scenes and lets you index either by column
(particles.x[i]) or virtually by row (particles[i].x).

This file is split into three sections called from main at the bottom so you
can read top to bottom and run the program at any point.
*/

Particle :: struct {
	x, y:   f32,
	vx, vy: f32,
	life:   f32,
}

fixed_soa_and_column_layout :: proc() {

	/*
	When we place '#soa' in front of a fixed array type like '#soa[4]Particle',
	Odin allocates four contiguous f32 arrays back-to-back instead of four
	interleaved structs. Accessing 'fixed_soa.x' gives you the entire [4]f32
	column directly, while 'fixed_soa[0]' behaves like a virtual row view whose
	fields point straight into those parallel columns:

	    Suppose fixed_soa: #soa[4]Particle:
	        fixed_soa[0] = Particle{x = 1, y = 2, vx = 0.5, vy = -0.5, life = 1}
	        &fixed_soa.x[0] == &fixed_soa[0].x   // true: same slot in memory!

	Notice also that taking '&fixed_soa[0]' produces a special #soa pointer, NOT
	a plain ^Particle, because the fields of particle 0 are spread across five
	separate arrays rather than sitting together in 20 consecutive bytes.
	*/

	// Here is a starter #soa[4]Particle proving column and row addresses match:

	fixed_soa: #soa[4]Particle
	fixed_soa[0] = Particle{x = 1.0, y = 2.0, vx = 0.5, vy = -0.5, life = 1.0}
	fmt.printfln("fixed_soa.x[0]=%v (same slot as fixed_soa[0].x: %v)", fixed_soa.x[0], &fixed_soa.x[0] == &fixed_soa[0].x)

	// Populate the remaining three slots fixed_soa[1], fixed_soa[2], and
	// fixed_soa[3] with Particle literals, copy the contiguous x column into
	// all_x: [4]f32 = fixed_soa.x, and print both all_x and fixed_soa.life.


	// Advance every particle horizontally by writing a loop for i in 0..<len(fixed_soa)
	// that updates fixed_soa.x[i] += fixed_soa.vx[i], then print fixed_soa.x
	// afterward to confirm only the x column changed.


	// Modify slot 0 through an #soa pointer: declare soa_ptr := &fixed_soa[0],
	// assign soa_ptr.life = 0.25, and print fixed_soa[0].life.
	//
	// Try uncommenting below to verify an #soa element address is not a ^Particle:
	// raw_ptr: ^Particle = &fixed_soa[0]
}

soa_slices_and_dynamic_arrays :: proc() {

	/*
	Real workloads rarely know their particle count at compile time. Odin pairs
	'#soa[]Particle' and '#soa[dynamic]Particle' with dedicated built-ins:
	'make(#soa[]Particle, n)' allocates a fixed-length SoA slice backed by one
	contiguous buffer split into N-element columns, 'make(#soa[dynamic]Particle, 0, cap)'
	allocates a growable SoA container, 'append_soa(&s, item)' pushes a new
	element across all columns at once, and 'delete_soa(s)' frees the backing
	storage cleanly.

	    Suppose buf := make(#soa[]Particle, 6) with defer delete_soa(buf):
	        buf[0].x = 10.0   // writes into the x column
	        sub := buf[1:4]   // zero-copy #soa[]Particle slice of length 3
	*/

	// Here is the byte size of one Particle compared with #soa[4]Particle:

	fmt.printfln("size_of(Particle)=%dB | size_of(#soa[4]Particle)=%dB", size_of(Particle), size_of(#soa[4]Particle))

	// Allocate a fixed-count SoA slice using buf := make(#soa[]Particle, 6)
	// with defer delete_soa(buf). Loop for i in 0..<len(buf) to initialize
	// buf[i] = Particle{x = f32(i), vx = 0.5, life = 1.0 - f32(i) * 0.1}, then
	// sum the contiguous buf.life column across 0..<len(buf) and print the total.


	// Take a zero-copy sub-slice: declare mid := buf[1:4], verify len(mid) is 3,
	// and print mid[0].x (expected: 1.0) plus &mid.x[0] == &buf.x[1] to confirm
	// no elements were copied.


	// Create a dynamic SoA array: dyn_soa := make(#soa[dynamic]Particle, 0, 8)
	// with defer delete_soa(dyn_soa). Append four Particle values using
	// append_soa(&dyn_soa, Particle{...}), integrate positions in a loop with
	// dyn_soa.x[i] += dyn_soa.vx[i] and dyn_soa.y[i] += dyn_soa.vy[i], and
	// print len(dyn_soa) and dyn_soa.x[:len(dyn_soa)].
}

soa_zip_and_soa_unzip :: proc() {

	/*
	Sometimes you already hold separate []f32 slices (from an arena, a file, or
	an external library) and want to iterate or pass them together as a single
	SoA table without allocating or copying a single byte.

	When we call 'soa_zip(x = xs, y = ys)', Odin builds a lightweight '#soa'
	slice view whose fields alias your original slices directly. Calling
	'soa_unzip(zipped)' unpacks those column pointers right back into separate
	'[]T' slices.

	    Suppose xs := []f32{1, 2} and ys := []f32{3, 4}:
	        zipped := soa_zip(x = xs, y = ys)
	        zipped[1].y = 40   // mutates ys[1] directly in place!
	        out_x, out_y := soa_unzip(zipped)
	*/

	// Here is a quick starter zip over two small coordinate slices:

	anchor_xs := []f32{1.0, 2.0}
	anchor_ys := []f32{3.0, 4.0}
	anchor_zip := soa_zip(x = anchor_xs, y = anchor_ys)
	fmt.printfln("zipped len=%d | anchor_zip[0].x=%v", len(anchor_zip), anchor_zip[0].x)

	// Declare three []f32 slices: pos_x := []f32{2.0, 4.0, 6.0},
	// pos_y := []f32{1.0, 3.0, 5.0}, and weights := []f32{0.5, 1.0, 2.0}.
	// Combine them with zipped := soa_zip(x = pos_x, y = pos_y, w = weights)
	// and iterate with for item, idx in zipped to compute and print the
	// weighted sum of item.x * item.w.


	// Unpack zipped back into separate slices using:
	// out_x, out_y, out_w := soa_unzip(zipped)
	// Print raw_data(out_x) == raw_data(pos_x) and len(out_y) == len(out_w) to
	// prove soa_zip and soa_unzip never copy underlying memory.


	// Synthesize #soa slices with a reusable procedure:
	// Define integrate_particles :: proc(particles: #soa[]Particle, dt: f32)
	// that updates particles.x[i] += particles.vx[i] * dt and
	// particles.y[i] += particles.vy[i] * dt while decaying particles.life[i] -= dt.
	// Call integrate_particles on a make(#soa[]Particle, 4) buffer (with
	// defer delete_soa) and print the resulting x and life columns.
}

main :: proc() {

	fmt.println("=== 1. Fixed #soa arrays and column layout ===")
	fixed_soa_and_column_layout()

	fmt.println("\n=== 2. #soa slices and dynamic arrays ===")
	soa_slices_and_dynamic_arrays()

	fmt.println("\n=== 3. Zero-copy soa_zip, soa_unzip, and #soa procedures ===")
	soa_zip_and_soa_unzip()
}
