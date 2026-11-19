// odin run 010_constants_and_untyped_literals.odin -file

package main

import "core:fmt"

/*
While ':' declares runtime variables stored in stack or heap memory, '::' binds
an identifier at compile time to a constant, type, or procedure.

Odin distinguishes two kinds of constants:
Untyped constants (NAME :: value) are evaluated in exact arbitrary-precision
arithmetic inside the compiler and carry no fixed bit-width yet.
Typed constants (NAME : Type : value) lock the constant to one exact Odin type
right at declaration time.

Because constants live only during compilation, they occupy no runtime memory
address and cannot be mutated or pointed to with '&'.

This file is split into three small sections called from main at the bottom so
you can read top to bottom and run the program at any point.
*/

// File-scope untyped constant evaluated at compile time:
UNTYPED_PI :: 3.14159265358979323846

untyped_constants_and_adaptation :: proc() {

	/*
	An untyped constant acts just like a literal number written directly in code:
	it adapts automatically to any compatible target type without a cast, as long
	as the value fits inside that type's valid range. Even intermediate math
	stays exact: (1000000000000000000000 + 1) - 1000000000000000000000 evaluates
	to 1 at compile time with zero 64-bit integer overflow!

	Suppose MAX_ITEMS :: 100. Assigning small: u8 = MAX_ITEMS and ratio: f32 = MAX_ITEMS
	both compile without casts because MAX_ITEMS is untyped and 100 fits in both
	u8 (0..=255) and f32.
	*/

	// Assigning one untyped constant to both f32 and f64:

	pi_single: f32 = UNTYPED_PI
	pi_double: f64 = UNTYPED_PI
	fmt.printfln("pi_single (%T) = %v | pi_double (%T) = %v", pi_single, pi_single, pi_double, pi_double)

	// Declare an untyped constant GRAVITY :: 9.81 using '::'.
	// Assign GRAVITY to gravity_f32: f32 and gravity_f64: f64 with no casts,
	// and print both values with their types.


	// Declare an untyped integer constant TILE_SIZE :: 32 and assign it to
	// tile_u8: u8, tile_i32: i32, and tile_f32: f32 without casts. Print all three.


	// Declare an untyped constant TWO :: 2.0 and notice what type Odin picks if
	// you assign it with ':=' (whole_or_float := TWO) vs explicit int/f32. Print
	// whole_or_float with %T to confirm '.0' makes it an untyped float defaulting to f64.
}

typed_constants_and_compile_time_math :: proc() {

	/*
	Placing a type between the two colons (NAME : Type : value) locks the constant
	to that exact type. Typed constants are useful for network ports, bitmasks,
	or protocol versions where silent adaptation to another width would hide a
	mismatch.

	Compile-time arithmetic in constant declarations uses standard operators
	('*', '+', '-', '/', '<<') and produces exact compile-time results with zero
	runtime cost.
	*/

	// Compile-time constant expression:

	KB :: 1024
	fmt.printfln("1 KB = %v bytes", KB)

	// Declare a typed constant DEFAULT_PORT : u16 : 8080 and print its value
	// and type using fmt.printfln("%v (%T)", DEFAULT_PORT, DEFAULT_PORT).


	// Declare untyped constant PACKET_BYTES :: 16 * KB and constant PAGE_BYTES :: 4 << 10
	// using compile-time arithmetic, and print both.


	// Declare a typed string constant APP_NAME : string : "OdinLab" and an
	// untyped boolean constant FEATURE_ENABLED :: true, and print both.


	// Compute a compile-time constant expression combining earlier constants,
	// such as MAX_PACKETS :: (64 * KB) / PACKET_BYTES, and print it with %v (%T).
}

addressability_and_overflow_checks :: proc() {

	/*
	Because the compiler substitutes constants directly into instructions rather
	than allocating a stack slot, constants have no memory address at runtime.
	Odin also validates untyped constants against the destination type's range
	during compilation instead of silently wrapping bits like C.
	*/

	// Validating the upper bound of u8 at compile time:

	SAFE_BYTE : u8 : 255
	fmt.printfln("Max u8 constant = %v", SAFE_BYTE)

	// Error experiment 1: constants have no runtime memory address.
	// Try uncommenting the line below and running odin check:
	// ptr := &UNTYPED_PI


	// Error experiment 2: compile-time range check rejects out-of-range literals.
	// Try uncommenting below (300 exceeds u8's 0..=255 range):
	// overflow_byte: u8 = 300


	// Error experiment 3: typed constants obey strict type matching.
	// Suppose PORT_U16 : u16 : 8080; try uncommenting below to see that a typed
	// constant cannot implicitly widen to u32 without u32(PORT_U16):
	// PORT_U16 : u16 : 8080
	// wide_port: u32 = PORT_U16
}

main :: proc() {

	fmt.println("=== 1. Untyped constants and adaptation ===")
	untyped_constants_and_adaptation()

	fmt.println("\n=== 2. Typed constants and compile-time math ===")
	typed_constants_and_compile_time_math()

	fmt.println("\n=== 3. Addressability and overflow checks ===")
	addressability_and_overflow_checks()
}
