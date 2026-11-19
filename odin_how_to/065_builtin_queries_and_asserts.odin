// odin run 065_builtin_queries_and_asserts.odin -file

package main

import "core:fmt"

/*
Odin builds memory-layout introspection, math helpers, and assertions directly
into the compiler so you can inspect struct padding and guard invariants without
external headers or macros.

Knowing exact field offsets matters in systems code: CPUs fetch 4-byte or
8-byte values fastest when their address is a multiple of 4 or 8 (align_of). To
satisfy alignment, the compiler inserts invisible padding bytes between fields
and at the end of a struct, meaning field declaration order directly changes
how much memory your structs consume.

This file is split into three small sections called from main at the bottom so
you can read top to bottom and run the program at any point.
*/

Packet_Header :: struct {
	magic:   u16, // 2 bytes at offset 0
	version: u8,  // 1 byte at offset 2 (+ 1 byte padding so length aligns to 4)
	length:  u32, // 4 bytes at offset 4
}

#assert(size_of(Packet_Header) == 8)

layout_queries_and_padding :: proc() {

	/*
	Odin gives you five core layout and type queries:
	    size_of(T)                total size in bytes including padding
	    align_of(T)               required byte alignment
	    offset_of(T, field)       byte offset of a field inside struct T
	    offset_of_by_string(T, s) same offset lookup using a field name string
	    offset_of(val.field)      field offset queried from an existing value

	When we write type_of(expr), it yields the compile-time type of expr, while
	typeid_of(T) returns a runtime typeid handle representing type T.

	    Suppose Bad :: struct { a: u8, b: u64, c: u8 }:
	        'a' sits at offset 0 (1 byte), followed by 7 padding bytes so 'b'
	        lands at offset 8 (8 bytes), then 'c' at offset 16 (1 byte), plus
	        7 trailing padding bytes -> size_of(Bad) is 24 bytes!
	    Suppose Good :: struct { b: u64, a: u8, c: u8 }:
	        'b' sits at 0..7, 'a' at 8, 'c' at 9, plus 6 trailing bytes ->
	        size_of(Good) drops to 16 bytes for the exact same fields!
	*/

	// Here we print Packet_Header's total size and alignment:

	fmt.printfln("Packet_Header: size=%vB, align=%vB", size_of(Packet_Header), align_of(Packet_Header))

	// Query field offsets inside Packet_Header:
	// print offset_of(Packet_Header, magic), offset_of(Packet_Header, version),
	// and offset_of(Packet_Header, length) to confirm length starts at byte 4
	// instead of 3. Also declare hdr: Packet_Header and test offset_of(hdr.length)
	// and offset_of_by_string(Packet_Header, "version").


	// Check how reordering struct fields drops padding:
	// define two structs above main (or locally):
	// Unpacked_Record :: struct { flag: u8, timestamp: u64, tag: u8 }
	// Packed_Record   :: struct { timestamp: u64, flag: u8, tag: u8 }
	// Print size_of and align_of for both, print offset_of for each field, and
	// add #assert(size_of(Unpacked_Record) == 24) and #assert(size_of(Packed_Record) == 16)
	// to prove at compile time that reordering saved 8 bytes per record.


	// Practice type_of, typeid_of, len, and cap:
	// declare hdr2: Packet_Header and declare count: type_of(hdr2.length) = 5
	// Print typeid_of(Packet_Header) and typeid_of(type_of(count)).
	// Then declare fixed := [4]int{1, 2, 3, 4} and dyn := make([dynamic]int, 2, 8)
	// with defer delete(dyn), and print len and cap for both.
}

builtin_math_helpers :: proc() {

	/*
	Basic bounds helpers—min, max, abs, and clamp—are compiler built-ins that
	work across both integer and floating-point types without importing math.
	min and max even accept more than two arguments (such as min(a, b, c)).
	*/

	// Here is a quick clamp example keeping -5 inside 0..100:

	fmt.printfln("Example clamp(-5, 0, 100) = %v", clamp(-5, 0, 100))

	// Compute and print all four integer math built-ins with fmt.printfln:
	// - lowest  := min(15, 42)
	// - highest := max(15, 42, 9)
	// - pos_val := abs(-99)
	// - clamped := clamp(125, 0, 100)


	// Practice the same helpers on floats:
	// declare delta := abs(f32(-3.5)) and ratio := clamp(f32(1.4), f32(0.0), f32(1.0))
	// and print both values.
}

assertions_and_compile_time_checks :: proc() {

	/*
	Odin separates invariant checks into three levels depending on when they run:
	    #assert(const_cond)  checked by the compiler; fails build immediately
	    assert(cond, msg)    runtime debug check (disabled by -disable-assert)
	    ensure(cond, msg)    runtime check that stays active even with -disable-assert
	    panic(msg)           unconditionally aborts the program with a message

	Use #assert for struct sizes and constant math, assert for internal debug
	invariants, and ensure for critical runtime checks you never want stripped.
	*/

	// Here is a runtime debug assert guarding Packet_Header size:

	ok_header := size_of(Packet_Header) == 8
	assert(ok_header, "Packet_Header layout mismatch")

	// Verify clamp(125, 0, 100) == 100 using assert(cond, "message"), and verify
	// min(15, 42) == 15 using ensure(cond, "message").


	// Practice guarding an impossible branch with panic:
	// declare state := 1 and write an if / else block where state == 1 prints
	// "Valid state" and the untaken else branch calls panic("unreachable state").


	// Compile-time #assert experiment:
	// try uncommenting the line below and checking the file to watch the build
	// fail before any binary is produced:
	// #assert(size_of(Packet_Header) == 7)
}

main :: proc() {

	fmt.println("=== 1. Layout queries and struct padding ===")
	layout_queries_and_padding()

	fmt.println("\n=== 2. Built-in math helpers ===")
	builtin_math_helpers()

	fmt.println("\n=== 3. Assertions and compile-time #assert ===")
	assertions_and_compile_time_checks()
}
