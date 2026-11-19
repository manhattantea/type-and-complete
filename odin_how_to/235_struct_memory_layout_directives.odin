// odin run 235_struct_memory_layout_directives.odin -file

package main

import "core:fmt"

/*
By default, Odin lays out struct fields in the exact order you write them and
aligns every field to a byte boundary matching its size (1 byte for u8, 4 bytes
for u32, 8 bytes for u64). CPUs fetch aligned data in a single memory operation,
so Odin inserts invisible padding bytes between fields whenever a wider field
follows a narrower one.

When you talk to hardware registers, binary file headers, multi-threaded CPU
caches, or growing configuration structs, you need direct control over that
layout. Instead of compiler-specific pragmas or attributes from C, Odin builds
four layout directives right into 'struct':

    #packed       1-byte alignment with zero padding between fields
    #align(N)     forces alignment (and stride) up to N bytes
    #raw_union    places every field at byte offset 0 (untagged overlay)
    #all_or_none  rejects partial compound literals (all fields or {})
*/

Strict_Config :: struct #all_or_none {
	port:    u16,
	timeout: u32,
}

#assert(size_of(Strict_Config) == 8)

natural_alignment_and_reordering :: proc() {

	/*
	Three compile-time builtins let you inspect struct layout directly:
	'size_of(T)' returns total bytes including padding, 'align_of(T)' returns the
	required byte boundary, and 'offset_of(T, field)' returns the byte offset of
	one field from the start of T. Pairing them with '#assert(cond)' checks your
	layout assumptions at compile time before the program ever runs.

	Suppose you write:
	    Sample :: struct { a: u8, b: u32, c: u8 }
	Here 'a' takes offset 0, Odin inserts 3 padding bytes at offsets 1..=3 so
	'b' lands on 4-byte boundary 4..=7, 'c' sits at offset 8, and Odin appends 3
	tail padding bytes at offsets 9..=11 so an array [2]Sample keeps the second
	element's 'b' 4-byte aligned. Total size: 12 bytes for 6 bytes of data!

	Simply reordering fields from widest to narrowest (b: u32, a: u8, c: u8)
	packs 'a' and 'c' right after 'b' at offsets 4 and 5, leaving only 2 tail
	bytes and cutting the struct from 12 bytes down to 8 bytes with zero directives.
	*/

	// Starter layout check on Strict_Config (u16 at 0..=1, 2 pad bytes, u32 at 4..=7):
	fmt.printfln(
		"Strict_Config: size=%v, align=%v, offset(port)=%v, offset(timeout)=%v",
		size_of(Strict_Config),
		align_of(Strict_Config),
		offset_of(Strict_Config, port),
		offset_of(Strict_Config, timeout),
	)

	// Define Padded_Header :: struct { a: u8, b: u32, c: u8 } (at file scope or
	// right here inside this procedure) and verify at compile time with:
	// #assert(size_of(Padded_Header) == 12)
	// #assert(offset_of(Padded_Header, b) == 4)
	// Print size_of(Padded_Header), align_of(Padded_Header), and offset_of for a, b, c.


	// Now define Reordered_Header :: struct { b: u32, a: u8, c: u8 } putting the
	// widest field first. Add #assert(size_of(Reordered_Header) == 8) and print
	// size_of, align_of, and offset_of for b, a, c to observe the 4-byte drop
	// without using #packed.


	// Practice on a larger real-world record: define
	// Bloated_Record :: struct { flag: u8, id: u64, active: bool, score: u32, tag: u8 }
	// and a reordered Slim_Record with the same five fields ordered widest-first
	// (u64, u32, u8, bool, u8). Print size_of([1000]Bloated_Record) vs
	// size_of([1000]Slim_Record) to see how field order shrinks array footprints.
}

packed_and_cache_line_alignment :: proc() {

	/*
	When we write 'struct #packed', it tells Odin to drop alignment to 1 byte and
	strip every internal and tail padding byte. Use #packed for on-disk file
	headers or network wire packets whose exact byte offsets are fixed by a spec.
	Just remember the trade-off: accessing an unaligned multi-byte integer inside
	a #packed struct can force extra CPU load instructions, so unpack into a
	normal aligned struct when processing millions of items in a hot loop.

	Going the opposite direction, 'struct #align(64)' forces a struct's alignment
	and size multiple up to 64 bytes. On modern x86_64 and Apple Silicon CPUs,
	memory moves into L1 cache in 64-byte cache lines. Suppose two threads increment
	adjacent counters:
	    counts: [2]u64   // both sit inside the same 64-byte cache line
	Each core invalidates the other core's cache line on every write (false
	sharing). Giving each counter #align(64) spaces elements 64 bytes apart so
	each counter gets its own cache line.
	*/

	// Define Packed_Header :: struct #packed { a: u8, b: u32, c: u8 } and verify:
	// #assert(size_of(Packed_Header) == 6)
	// #assert(align_of(Packed_Header) == 1)
	// Print size_of(Packed_Header), align_of(Packed_Header), and
	// offset_of(Packed_Header, b) (expected: 1, zero padding before b).


	// Compare array footprints: print size_of([4]Padded_Header) (48 bytes) vs
	// size_of([4]Packed_Header) (24 bytes).


	// Define Cache_Line_Counter :: struct #align(64) { count: u64 }
	// Add #assert(align_of(Cache_Line_Counter) == 64) and
	// #assert(size_of(Cache_Line_Counter) == 64).
	// Declare counters: [2]Cache_Line_Counter, set counters[0].count = 10 and
	// counters[1].count = 20, and print size_of([2]Cache_Line_Counter) (128 bytes)
	// along with both counts.


	// Practice GPU/SIMD padding with #align(16): define
	// Vec3_Aligned :: struct #align(16) { x, y, z: f32 }
	// Add #assert(size_of(Vec3_Aligned) == 16) and print its size and alignment.
}

raw_unions_and_all_or_none :: proc() {

	/*
	Odin's normal 'union { A, B }' is type-safe and carries a hidden tag byte. By
	contrast, 'struct #raw_union { ... }' behaves like a C union: every field
	begins at byte offset 0 with zero hidden tag, and size_of is the largest
	field (rounded up to max alignment). Writing one field and reading another
	reinterprets the raw underlying bits directly.

	    Suppose Register32 :: struct #raw_union { full: u32, bytes: [4]u8 }:
	        reg := Register32{full = 0x01020304}
	    On a little-endian machine, reg.bytes reads {4, 3, 2, 1} because the
	    least-significant byte 0x04 sits at offset 0.

	Finally, 'struct #all_or_none' protects configuration structs as code evolves.
	Suppose you add a new field 'tls: bool' to a config struct next month: without
	#all_or_none, existing literals silently leave 'tls' as false; with
	#all_or_none, Odin forces every caller to write either '{}' (explicit defaults)
	or supply every single field by name.
	*/

	// Starter #all_or_none literal: every field of Strict_Config is supplied.
	cfg := Strict_Config{port = 8080, timeout = 5000}
	fmt.printfln("Starter Strict_Config: port=%v, timeout=%v", cfg.port, cfg.timeout)

	// Try uncommenting below to see #all_or_none reject partial initialization:
	// bad_cfg := Strict_Config{port = 8080}


	// Define Register32 :: struct #raw_union { full: u32, words: [2]u16, bytes: [4]u8 }
	// Add #assert(size_of(Register32) == 4) and #assert(offset_of(Register32, bytes) == 0).
	// Instantiate reg := Register32{full = 0x01020304}, print reg.bytes and
	// reg.words, then overwrite reg.bytes[0] = 0xFF and print reg.full with %#08x.


	// Define Window_Config :: struct #all_or_none { title: string, width: i32, height: i32, vsync: bool }
	// Construct both defaults := Window_Config{} (zero literal allowed!) and a full
	// custom := Window_Config{title = "Odin", width = 1280, height = 720, vsync = true},
	// printing both values.
}

main :: proc() {

	fmt.println("=== 1. Natural alignment and field reordering ===")
	natural_alignment_and_reordering()

	fmt.println("\n=== 2. Packed structs and cache-line alignment ===")
	packed_and_cache_line_alignment()

	fmt.println("\n=== 3. Raw unions and #all_or_none ===")
	raw_unions_and_all_or_none()
}
