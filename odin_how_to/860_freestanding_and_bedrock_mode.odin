// odin run 860_freestanding_and_bedrock_mode.odin -file

package main

import "core:fmt"
import "core:mem"
import "core:strings"

/*
OS kernels, bootloaders, microcontrollers, and real-time audio DSP callbacks
often cannot depend on a system heap allocator or dynamic runtime tables. Odin
supports zero-heap programming directly through compiler flags and stack-backed
data structures:

- '-default-to-panic-allocator' replaces context.allocator with
  mem.panic_allocator(), so any accidental heap allocation via make, new,
  append, or strings.clone panics immediately with the exact offending line.
- '-default-to-nil-allocator' sets the default allocator to nil.
- '-bedrock' enables Odin's minimal freestanding mode without OS runtime
  assumptions.
- '-no-rtti' strips runtime type information tables to shrink binary size.
- '-disable-non-constant-globals' forbids mutable package-level globals.

At the declaration level, '@(rodata)' forces a lookup table into read-only
memory (ROM/Flash), and '@(link_section = ".boot")' places a symbol into a
custom linker section.
*/

@(rodata)
CONFIG_ROM_TABLE := [4]u32{0x0001, 0x0002, 0x0004, 0x0008}

panic_allocator_and_stack_containers :: proc() {

	/*
	Even with context.allocator set to mem.panic_allocator() in main, you can
	still build dynamic lists and format strings using stack memory:

	First, '[dynamic; N]T' is a fixed-capacity stack-backed dynamic array whose
	N-element buffer lives right inside the local stack frame (zero heap).
	Second, 'strings.builder_from_bytes(buf[:])' wraps a stack byte array in a
	strings.Builder backed by a non-allocating buffer, so strings.write_string
	and fmt.sbprintf append text up to len(buf) with zero heap touches.

	Suppose text_buf: [64]byte and sb := strings.builder_from_bytes(text_buf[:]).
	Writing "zero-heap" into &sb fills text_buf[0:9] and strings.to_string(sb)
	returns a slice directly into text_buf without allocating.
	*/

	text_buf: [64]byte
	sb := strings.builder_from_bytes(text_buf[:])
	strings.write_string(&sb, "zero-heap")
	fmt.printfln("ROM[0]=%#04x, stack builder='%s' (%d/%d bytes)", CONFIG_ROM_TABLE[0], strings.to_string(sb), strings.builder_len(sb), len(text_buf))

	// Use fmt.sbprintf(&sb, " v%d", 2) to append onto the same stack-backed
	// strings.Builder under mem.panic_allocator(), then print strings.to_string(sb).
	// Also test what happens when you exceed len(text_buf) with a long string
	// (builder_from_bytes refuses to grow onto the heap and truncates safely).


	// Declare stack_items: [dynamic; 8]int, append 10, 20, 30, 40 into
	// &stack_items (no defer delete needed because it lives on the stack!), and
	// print len(stack_items), cap(stack_items), and stack_items[:] with fmt.printfln.


	// Check what happens if you append a 9th element to stack_items: because
	// [dynamic; 8]int falls back to context.allocator once capacity 8 overflows,
	// mem.panic_allocator() catches the accidental heap spill immediately.
}

stack_backed_arena_and_flags :: proc() {

	/*
	When an API expects a runtime.Allocator (like make([]int, 10, allocator)),
	you can still stay 100% off the OS heap by initializing a mem.Arena over a
	fixed stack byte array:
	    stack_scratch: [512]byte
	    arena: mem.Arena
	    mem.arena_init(&arena, stack_scratch[:])
	    arena_alloc := mem.arena_allocator(&arena)

	Every allocation from arena_alloc simply bumps arena.offset forward inside
	stack_scratch, and mem.arena_free_all(&arena) rewinds offset back to 0 in
	one instruction.
	*/

	// Declare stack_scratch: [512]byte and arena: mem.Arena, initialize with
	// mem.arena_init(&arena, stack_scratch[:]), and bind
	// arena_alloc := mem.arena_allocator(&arena).


	// Allocate numbers := make([]int, 10, arena_alloc), fill each slot
	// numbers[i] = (i + 1) * 10, and print numbers and arena.offset with
	// fmt.printfln.


	// Call mem.arena_free_all(&arena) and print arena.offset (expected: 0) to
	// verify O(1) reclamation of the entire stack scratch buffer.


	// Practice explicit allocator injection while context.allocator stays
	// locked to mem.panic_allocator(): write a helper outside this procedure:
	// format_tag :: proc(label: string, id: int, allocator := context.allocator) -> string
	// calling fmt.aprintf("[%s:%d]", label, id, allocator = allocator).
	// Pass arena_alloc explicitly and print the resulting string!


	// Compare mem.panic_allocator() vs mem.nil_allocator(): inside a narrow
	// inner scope, temporarily assign context.allocator = mem.nil_allocator(),
	// call buf, alloc_err := make([]u8, 16), and verify alloc_err != nil
	// instead of panicking. Remember to restore or keep panic_allocator outside.


	// Add a @(rodata) lookup table of 4 u16 values at file scope and test
	// checking this file with:
	// odin check 860_freestanding_and_bedrock_mode.odin -file -default-to-panic-allocator


	// Try uncommenting the line below to watch mem.panic_allocator() catch an
	// unconfigured heap allocation at runtime with exact file and line info:
	// heap_leaker := make([]int, 100)
}

main :: proc() {

	context.allocator = mem.panic_allocator()

	fmt.println("=== 1. Panic allocator and stack containers ===")
	panic_allocator_and_stack_containers()

	fmt.println("\n=== 2. Stack-backed arena and freestanding checks ===")
	stack_backed_arena_and_flags()
}
