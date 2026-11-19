// odin run 015_number_types_and_casting.odin -file

package main

import "core:fmt"

/*
Odin gives you explicit-width numeric types built for systems, graphics, and
network programming:
signed integers (i8, i16, i32, i64, i128, and register-sized int),
unsigned integers (u8 / byte, u16, u32, u64, u128, uint, uintptr),
IEEE floats (f16, f32, f64),
and endian-fixed integers and floats (i16le, u16be, i32be, u64le, f32be) whose
byte order is swapped automatically by the compiler on load and store.

This file is split into three small sections called from main at the bottom so
you can read top to bottom and run the program at any point.
*/

explicit_widths_endian_and_literals :: proc() {

	/*
	Numeric literals support hexadecimal (0x), binary (0b), octal (0o),
	scientific notation (1.5e-3), and visual underscore separators (5_000_000)
	that the compiler ignores when parsing the digits.

	Notice two system-level aliases: 'byte' is a direct alias for 'u8', and
	'uintptr' is an unsigned integer guaranteed to be wide enough to hold a
	memory address on the target architecture (8 bytes on 64-bit CPUs). Endian
	types like u16be store big-endian network bytes in memory while letting you
	read and write normal integer values in Odin code.
	*/

	// Hexadecimal u8 starter:

	small_byte: u8 = 0xFF
	fmt.printfln("small_byte = %v (hex: 0x%X, size: %vB)", small_byte, small_byte, size_of(small_byte))

	// Declare four explicitly typed variables:
	// hex_mask: u32 = 0xDEAD_BEEF
	// bin_flags: u16 = 0b1010_0101
	// oct_mode: u16 = 0o755
	// big_count: i64 = 5_000_000
	// Print all four values with fmt.printfln.


	// Declare net_port: u16be = 80 and sci_step: f32 = 1.5e-3, then print both
	// alongside size_of(u128), size_of(f16), and size_of(uintptr).


	// Declare raw_b: byte = 65 and print its value and %T type name to confirm
	// that byte is a direct alias for u8.
}

strict_typing_and_explicit_conversions :: proc() {

	/*
	Unlike C, Odin never performs implicit conversions between distinct typed
	numeric variables, not even for "safe" widening such as u8 to u32 or i32 to
	i64. Every conversion between typed variables must be written explicitly so
	width or signedness changes are always visible at the call site:

	    T(expr)         type conversion call (everyday choice)
	    cast(T)expr     explicit cast operator
	    auto_cast expr  infers T when the destination type is already explicit

	Suppose a: u8 = 200 and b: u32 = 10. Writing a + b fails to compile; you
	write u32(a) + b so the widening from u8 to u32 is unmistakable.
	*/

	// Explicit type-call conversion starter:

	base_byte: u8 = 0x7F
	fmt.printfln("base_byte = %v -> u32(base_byte) = %v", base_byte, u32(base_byte))

	// Convert base_byte to u32 into widened_call using u32(base_byte), and into
	// widened_cast using cast(u32)base_byte. Print both values and types.


	// Try uncommenting the widening mismatch below to see Odin reject implicit
	// numeric assignment even when u32 fits easily inside i64:
	// src_u32: u32 = 100
	// dst_i64: i64 = src_u32


	// Converting a floating-point value to an integer truncates toward zero.
	// Declare precise_val: f64 = 42.9, convert it to an int named truncated
	// using int(precise_val), and print both (expected: 42.9 and 42).


	// Explicit narrowing truncates upper bits at runtime: declare wide_val: u32 = 300
	// and narrow it with narrowed := u8(wide_val). Print narrowed (expected: 44,
	// because 300 & 0xFF == 44).


	// When a declaration already states its target type on the left, auto_cast
	// tells Odin to cast the right-hand expression to match that target type.
	// Declare my_i32: i32 = 123, then declare target_i64: i64 = auto_cast my_i32
	// and print target_i64.
}

transmute_raw_bits :: proc() {

	/*
	Whereas cast(T)x converts a numeric value mathematically (turning 1.0 into
	integer 1), transmute(T)x reinterprets the exact raw bits in memory as type
	T without changing a single bit. Because no conversion math runs, Odin
	requires size_of(T) == size_of(x) at compile time.

	Suppose val: f32 = 1.0. Calling cast(u32)val yields 1, whereas
	transmute(u32)val yields 0x3F800000 (the raw IEEE-754 bit pattern for 1.0).
	*/

	// Numeric cast of 1.0 to integer 1:

	one_f32: f32 = 1.0
	fmt.printfln("cast(u32)f32(1.0) = %v", cast(u32)one_f32)

	// Store transmute(u32)one_f32 in raw_bits and print it in hexadecimal with
	// "0x%08X" (expected: 0x3F800000).


	// Round-trip raw bits back into a float: use transmute(f32)u32(0x4000_0000)
	// into decoded_f32 and print it (expected: 2).
	// Also try uncommenting below to see Odin catch a transmute size mismatch:
	// bad_bits := transmute(u64)one_f32
}

main :: proc() {

	fmt.println("=== 1. Explicit widths, endian types, and literals ===")
	explicit_widths_endian_and_literals()

	fmt.println("\n=== 2. Strict typing and explicit conversions ===")
	strict_typing_and_explicit_conversions()

	fmt.println("\n=== 3. Transmute raw bits ===")
	transmute_raw_bits()
}
