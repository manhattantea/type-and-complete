// odin run 500_fmt_and_string_builders.odin -file

package main

import "core:fmt"
import "core:strings"

/*
Many languages allocate a new heap string every time you format or interpolate
text. If that happens inside a game frame or tight parser loop, your allocator
spends half its time churning tiny throwaway buffers.

In Odin, 'core:fmt' and 'core:strings' make memory ownership explicit so you pick
the exact backing storage for each job:
- 'fmt.bprintf' writes into a caller-owned byte slice (usually a fixed stack
  array) with zero heap allocations.
- 'fmt.tprintf' writes into 'context.temp_allocator', ideal for short-lived
  per-frame strings freed in bulk when the scratch arena resets.
- 'fmt.sbprintf' appends into a reusable 'strings.Builder' buffer that you can
  reset between iterations with 'strings.builder_reset(&b)' instead of freeing
  and re-allocating on every pass.
- 'fmt.aprintf' allocates on 'context.allocator', transferring ownership to you
  so you must free it with 'defer delete(s)'.
*/

stack_and_scratch_formatting :: proc() {

	/*
	When we call 'fmt.bprintf(buf[:], fmt_str, ..args)', the 'b' stands for
	buffer: Odin formats bytes straight into your slice and returns a 'string'
	header pointing into that exact same memory. Nothing touches the heap.

	    Suppose scratch: [16]u8 sits on the stack:
	        msg := fmt.bprintf(scratch[:], "HP:%d", 95)
	        // msg points at scratch[0:5] holding "HP:95" (zero heap allocations)

	Because 'msg' borrows 'scratch', never return 'msg' from a procedure whose
	local 'scratch' array is about to disappear when the stack frame pops!
	*/

	tag_buf: [32]u8
	tag := fmt.bprintf(tag_buf[:], "  [v%d.%d]  ", 1, 4)
	fmt.printfln("Starter stack tag: %q", strings.trim_space(tag))

	// Declare stack_buf: [64]u8 and format "Player %d: HP=%04d (0x%02x)" with
	// arguments 1, 75, 75 using: res := fmt.bprintf(stack_buf[:], ...)
	// Print res with fmt.println(res). Then test what happens when the buffer
	// is too small: declare tiny_buf: [8]u8, format the same string into
	// tiny_buf[:], and print the truncated result to see fmt.bprintf stay safe.


	// Scratch-format a transient message using context.temp_allocator:
	// declare pos_msg := fmt.tprintf("Entity %d at (%.2f, %.2f)", 42, 10.5, -20.25)
	// Print pos_msg, then contrast with heap-owned formatting:
	// heap_msg := fmt.aprintf("Saved profile: %s", "slot_1")
	// Register defer delete(heap_msg) immediately after and print heap_msg.
}

reusable_string_builders :: proc() {

	/*
	A 'strings.Builder' is a thin wrapper around a '[dynamic]u8' byte buffer.
	Creating one with 'strings.builder_make()' allocates a growable buffer on
	'context.allocator' (paired with 'defer strings.builder_destroy(&b)').

	The performance trick in loops is 'strings.builder_reset(&b)'. When we call
	'strings.builder_reset(&b)', it sets the active byte length back to zero
	while keeping the already-allocated heap capacity intact.

	    Suppose 'b' grew to capacity 128 on iteration 0:
	        strings.builder_reset(&b)   // len(b.buf) becomes 0, cap(b.buf) stays 128
	        fmt.sbprintf(&b, "Row %d", 1)
	        // writes straight into the existing 128-byte block with 0 new allocs!

	If you cannot touch the heap at all, 'strings.builder_from_bytes(buf[:])'
	wraps a fixed stack array as a non-growing builder instead.
	*/

	fixed_buf: [128]u8
	fb := strings.builder_from_bytes(fixed_buf[:])
	strings.write_string(&fb, "Stack builder ready")
	fmt.printfln("Starter stack builder: %s", strings.to_string(fb))

	// Create a heap-backed builder: b := strings.builder_make()
	// Register defer strings.builder_destroy(&b) right below it.
	// Append three inventory lines into &b using fmt.sbprintf(&b, "Item %d: %s\n", ...),
	// then convert b to a string view via strings.to_string(b) and print it.


	// Practice zero-reallocation loop reuse with strings.builder_reset:
	// declare reuse_b := strings.builder_make() and defer strings.builder_destroy(&reuse_b)
	// Write a loop: for item_id in 1..=4
	// Reset at the top of each pass with: strings.builder_reset(&reuse_b)
	// Append two formatted fragments with fmt.sbprintf(&reuse_b, ...) and
	// strings.write_string(&reuse_b, ...), then print strings.to_string(reuse_b)
	// alongside cap(reuse_b.buf) to confirm capacity stops growing after pass 1.


	// Extend the fixed-capacity stack builder pattern:
	// declare log_buf: [64]u8 and sb := strings.builder_from_bytes(log_buf[:])
	// Append chunks with strings.write_string(&sb, "[OK] ") and fmt.sbprintf(&sb, "port=%d", 8080)
	// Print strings.to_string(sb) and try overflowing 64 bytes to see it clamp cleanly.
}

format_verbs_and_inspection :: proc() {

	/*
	Odin's 'fmt' verbs always require a letter after '%' (never a bare '%').
	Because Odin carries runtime type information, '%v' prints any struct,
	enum, slice, or primitive automatically, while '%#v' prints full Odin
	literal syntax and '%T' prints the exact type name.
	*/

	sample_val := 42
	fmt.printfln("Starter inspect: val=%v | type=%T | addr=%p", sample_val, sample_val, &sample_val)

	// Declare flags := 255 and pi := 3.14159265
	// Use fmt.printfln to print flags in decimal (%d), 8-digit zero-padded hex (%08x),
	// binary (%b), type name (%T), and Odin syntax (%#v), plus pi rounded with %.3f.


	// Compare %v, %#v, and %q on a struct or slice:
	// declare coords := [3]int{10, 20, 30} and label := "tab\tstop"
	// Print coords with both %v and %#v, and print label with %s vs %q so you see
	// how %q escapes special characters inside quotes.
}

main :: proc() {

	fmt.println("=== 1. Stack and scratch formatting ===")
	stack_and_scratch_formatting()

	fmt.println("\n=== 2. Reusable string builders ===")
	reusable_string_builders()

	fmt.println("\n=== 3. Format verbs and inspection ===")
	format_verbs_and_inspection()
}
