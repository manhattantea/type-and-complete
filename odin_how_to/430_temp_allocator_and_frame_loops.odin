// odin run 430_temp_allocator_and_frame_loops.odin -file

package main

import "core:fmt"
import "core:strings"
import "base:runtime"

/*
Every thread in Odin starts with a built-in scratch arena wired into
context.temp_allocator. Instead of calling malloc and free hundreds of times per
frame for temporary UI labels, path strings, or scratch arrays, you allocate
into context.temp_allocator and wipe all of those allocations at once in O(1)
time with free_all(context.temp_allocator).

Two rules govern temporary memory:
  Never call free() or delete() on an item allocated from temp_allocator.
  Never keep a slice or string allocated from temp_allocator across a reset!

This file is split into four sections called from main at the bottom so you can
read top to bottom and run the program at any point.
*/

temp_allocator_basics :: proc() {

	/*
	Under the hood, context.temp_allocator is backed by Odin's thread-local
	Default_Temp_Allocator: a bump-pointer ring buffer that grows by chaining
	4 MB backing blocks if a single frame overflows. Calling fmt.tprintf or
	passing context.temp_allocator to make advances the bump pointer in a few
	CPU instructions, and free_all(context.temp_allocator) resets that bump
	pointer back to zero without walking individual allocations.
	*/

	// Starter temp allocation and O(1) reset:

	temp_alloc: runtime.Allocator = context.temp_allocator
	banner := fmt.tprintf("Temp allocator ready (proc=%v)", temp_alloc.procedure)
	fmt.printfln("%s", banner)
	free_all(context.temp_allocator)

	// Allocate a temporary slice scratch := make([]int, 8, context.temp_allocator),
	// fill each slot with i * i in a loop, print scratch, and wipe it cleanly
	// with free_all(context.temp_allocator) (no delete(scratch)!).


	// Format three temp strings in a row using fmt.tprintf (for example,
	// tag_a, tag_b, tag_c), print all three without deleting any of them, and
	// release all three together with a single free_all(context.temp_allocator).
}

frame_loop_reset_pattern :: proc() {

	/*
	Game engines, web servers, and simulations share a natural lifetime boundary:
	one frame or one request. Putting free_all(context.temp_allocator) at the
	end of each loop pass lets every subsystem format HUD strings and build
	scratch lists freely without worrying about cleanup, while keeping total
	memory flat across millions of iterations.

	Suppose a loop processes 5 frames. Placing defer free_all(context.temp_allocator)
	right at the top of the loop body guarantees the reset still runs even if
	an early continue skips the bottom of the loop.
	*/

	// Baseline single-tick scratch formatting:

	tick := 0
	tick_label := fmt.tprintf("Baseline tick %d", tick)
	fmt.println(tick_label)
	free_all(context.temp_allocator)

	// Write a for frame in 0..<5 loop that formats a status string
	// msg := fmt.tprintf("Frame %d: %d entities", frame, frame * 10)
	// and allocates a temporary slice scratch := make([]int, 32, context.temp_allocator).
	// Set scratch[0] = frame * 100, print msg and scratch[0], and end the loop
	// body with free_all(context.temp_allocator).


	// Write a second loop for step in 0..<6 where the very first line inside
	// the loop body is defer free_all(context.temp_allocator). Format a temp
	// label, skip even steps with if step % 2 == 0 do continue, and print odd
	// steps to verify defer free_all still fires on continue.
}

temp_guard_in_helpers :: proc() {

	/*
	Library and helper procedures should NEVER call free_all(context.temp_allocator)
	directly. Suppose a caller formats caller_note := fmt.tprintf("Header") and
	then calls your helper. If your helper runs free_all(context.temp_allocator),
	it wipes caller_note out from under the caller!

	Instead, call runtime.DEFAULT_TEMP_ALLOCATOR_TEMP_GUARD() on the first line
	of the helper. It uses @(deferred_out) to save the current temp offset on
	entry and automatically rewind only back to that saved checkpoint on return,
	leaving everything the caller allocated earlier untouched.
	*/

	// Starter outer allocation showing caller-owned temp lifetime:

	caller_note := fmt.tprintf("Caller note stays alive")
	defer free_all(context.temp_allocator)
	fmt.println(caller_note)

	// Define sum_scratch_squares :: proc(n: int) -> int above main. Put
	// runtime.DEFAULT_TEMP_ALLOCATOR_TEMP_GUARD() on its very first line, then
	// allocate scratch := make([]int, n, context.temp_allocator), fill
	// scratch[i] = i * i, and return the sum of all elements.


	// Test that the temp guard protects outer allocations: allocate
	// outer_msg := fmt.tprintf("Alive before helper %d", 77) right here, call
	// total := sum_scratch_squares(16), print total, and print outer_msg
	// afterward to confirm sum_scratch_squares rewound only its own scratch
	// bytes and left outer_msg intact.
}

cross_frame_dangling_trap :: proc() {

	/*
	Because fmt.tprintf returns a plain 16-byte string header pointing into
	context.temp_allocator's bump buffer, storing that string in a struct or
	variable that survives past free_all(context.temp_allocator) creates a
	dangling view!

	Suppose frame 0 runs saved = fmt.tprintf("Wave %d", 1) and keeps saved
	around. Then free_all(context.temp_allocator) rewinds the temp offset back
	to 0. On frame 1, the very next fmt.tprintf("OVERWRITTEN") writes new bytes
	straight onto offset 0 of that exact same buffer—silently overwriting the
	bytes that saved still points to! Any temp string that must outlive a reset
	must be promoted onto context.allocator with strings.clone or allocated
	directly with fmt.aprintf.
	*/

	// Safe promotion onto context.allocator before resetting temp_allocator:

	persisted := strings.clone(fmt.tprintf("Safe header %d", 1))
	defer delete(persisted)
	free_all(context.temp_allocator)
	fmt.printfln("Promoted string after temp reset: %s", persisted)

	// Reproduce the cross-frame fmt.tprintf dangling trap directly:
	// declare stale_msg: string outside a loop for frame in 0..<2.
	// On frame == 0, assign stale_msg = fmt.tprintf("FrameZero-Token-%d", 42)
	// and print stale_msg, then call free_all(context.temp_allocator).
	// On frame == 1, allocate overwrite := fmt.tprintf("OVERWRITTEN-BY-FRAME-1"),
	// print overwrite, and then print stale_msg again to watch stale_msg's
	// bytes get clobbered by frame 1!


	// Fix the dangling trap: repeat the same 2-frame pattern with kept_msg: string,
	// except on frame == 0 promote the formatted string using
	// kept_msg = strings.clone(fmt.tprintf("FrameZero-Token-%d", 42))
	// paired with defer delete(kept_msg). After frame 1's fmt.tprintf and
	// free_all, print kept_msg to confirm it stays uncorrupted.


	// Compare strings.clone(fmt.tprintf("Direct-%d", 99)) with formatting
	// directly onto context.allocator via direct_msg := fmt.aprintf("Direct-%d", 99)
	// paired with defer delete(direct_msg), which skips the temp buffer completely.
}

main :: proc() {

	fmt.println("=== 1. Temp allocator basics and O(1) reset ===")
	temp_allocator_basics()

	fmt.println("\n=== 2. Frame loop reset pattern ===")
	frame_loop_reset_pattern()

	fmt.println("\n=== 3. Protecting callers with DEFAULT_TEMP_ALLOCATOR_TEMP_GUARD ===")
	temp_guard_in_helpers()

	fmt.println("\n=== 4. Cross-frame fmt.tprintf dangling trap and heap promotion ===")
	cross_frame_dangling_trap()
}
