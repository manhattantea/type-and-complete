// odin run 070_complex_and_quaternions.odin -file

package main

import "core:fmt"

/*
Because Odin targets graphics, audio, simulation, and scientific computing,
complex numbers and Hamilton quaternions are built-in primitive types rather
than third-party templates.

Complex types store two floats (complex32 uses f16, complex64 uses f32, and
complex128 uses f64) and use the imaginary suffix 'i' (such as 3 + 4i).
Quaternion types store four floats (quaternion64, quaternion128, quaternion256)
using suffixes 'i', 'j', 'k' (such as 1 + 0i + 0j + 0k), exposing components
via .w, .x, .y, .z (or .real, .imag, .jmag, .kmag).

This file is split into two small sections called from main at the bottom so
you can read top to bottom and run the program at any point.
*/

complex_numbers :: proc() {

	/*
	When we write real(c), imag(c), conj(c), or abs(c) on a complex number:
	    real(c)   extracts the real part
	    imag(c)   extracts the imaginary part
	    conj(c)   returns the complex conjugate (flips the sign of imag)
	    abs(c)    returns Euclidean magnitude sqrt(r*r + i*i)

	    Suppose c := complex64(3 + 4i):
	        abs(c) equals 5 (the 3-4-5 right triangle) and conj(c) is 3 - 4i.
	*/

	// Here is a complex64 literal and its magnitude:

	c1: complex64 = 3 + 4i
	fmt.printfln("c1 = %v | magnitude abs(c1) = %v", c1, abs(c1))

	// Declare c2: complex64 = 1 - 2i.
	// Compute sum := c1 + c2 and prod := c1 * c2, extract real(c1), imag(c1),
	// and conj(c1), and print all five values.


	// Practice double-precision complex128:
	// declare quarter_turn: complex128 = 0 + 1i and print quarter_turn * quarter_turn
	// (expected: -1 + 0i, two 90-degree rotations in the complex plane).


	// Print size_of(complex32), size_of(complex64), and size_of(complex128)
	// to verify they occupy 4, 8, and 16 bytes respectively.
}

quaternions_for_3d_rotation :: proc() {

	/*
	Quaternions encode 3D orientations compactly in four numbers without the
	gimbal-lock singularities of Euler angles. Multiplying two unit quaternions
	composes their rotations, and conj(q) inverts a unit rotation.

	    Suppose q := quaternion128(1 + 0i + 0j + 0k):
	        q.w (or q.real) is the scalar part 1, while q.x, q.y, q.z (or
	        q.imag, q.jmag, q.kmag) hold the 3D vector axis (0, 0, 0).

	Watch out for multiplication order: quaternion multiplication composes 3D
	rotations, so unlike regular numbers, a * b is not equal to b * a!
	*/

	// Here is an identity quaternion128 (zero rotation):

	identity_q: quaternion128 = 1 + 0i + 0j + 0k
	fmt.printfln("identity_q = %v (w=%v)", identity_q, identity_q.w)

	// Declare rot_q: quaternion128 = 0.7071 + 0i + 0.7071j + 0k (about 90 deg around Y).
	// Print its .w, .x, .y, .z fields (and .real, .jmag aliases), plus abs(rot_q)
	// and its inverse rotation conj(rot_q).


	// Verify Hamilton's non-commutative multiplication rule:
	// declare qi: quaternion128 = 0 + 1i + 0j + 0k and qj: quaternion128 = 0 + 0i + 1j + 0k
	// Print qi * qj (expected: 0 + 0i + 0j + 1k) and qj * qi (expected: 0 + 0i + 0j - 1k).
}

main :: proc() {

	fmt.println("=== 1. Complex numbers ===")
	complex_numbers()

	fmt.println("\n=== 2. Quaternions for 3D orientation ===")
	quaternions_for_3d_rotation()
}
