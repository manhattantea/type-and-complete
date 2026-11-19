// odin run 420_tracking_allocator_leak_detection.odin -file

package main

import "core:fmt"
import "core:mem"

/*
Because Odin passes allocators through context.allocator, you get leak and
invalid-free detection built into the standard library with zero external tools.
Wrapping context.allocator in a mem.Tracking_Allocator intercepts every
allocation and free, recording the pointer, byte size, and #caller_location
(file_path, line, procedure) inside two diagnostic containers:

  track.allocation_map    map[rawptr]mem.Tracking_Allocator_Entry of live blocks
  track.bad_free_array    [dynamic]mem.Tracking_Allocator_Bad_Free_Entry of bad frees

If an allocation is never freed, it stays in track.allocation_map at shutdown.
If you double-free a pointer or pass a stack/sub-slice address to free/delete,
Tracking_Allocator catches the mismatch before it corrupts heap metadata and
records it in track.bad_free_array instead.

This file is split into four sections called from main at the bottom so you can
read top to bottom and run the program at any point.
*/

report_tracking_results :: proc(track: ^mem.Tracking_Allocator, label: string) {

	fmt.printfln("[%s] total allocs: %d, peak bytes: %d", label, track.total_allocation_count, track.peak_memory_allocated)
	if len(track.allocation_map) > 0 {
		fmt.printfln("[%s] %d leaked allocation(s):", label, len(track.allocation_map))
		for _, entry in track.allocation_map {
			fmt.printfln("  - %d bytes leaked at %v", entry.size, entry.location)
		}
	}
	if len(track.bad_free_array) > 0 {
		fmt.printfln("[%s] %d bad free(s):", label, len(track.bad_free_array))
		for bad in track.bad_free_array {
			fmt.printfln("  - bad free on %p at %v", bad.memory, bad.location)
		}
	}
}

tracker_wiring_and_lifo_order :: proc() {

	/*
	Watch the order of defer statements when wiring a Tracking_Allocator.
	Because defers execute in LIFO (last-in, first-out) order at block exit,
	suppose you write:
	    defer mem.tracking_allocator_destroy(&track)   // registered 1st -> runs 3rd
	    defer report_tracking_results(&track, "run")   // registered 2nd -> runs 2nd
	    numbers := make([]int, 64)
	    defer delete(numbers)                          // registered 3rd -> runs 1st

	Every defer delete or defer free for tracked data MUST appear after the
	report defer so the resources are freed before the report inspects
	track.allocation_map!
	*/

	// Starter wiring with proper LIFO defer ordering:

	track: mem.Tracking_Allocator
	mem.tracking_allocator_init(&track, context.allocator)
	defer mem.tracking_allocator_destroy(&track)
	defer report_tracking_results(&track, "wiring")
	context.allocator = mem.tracking_allocator(&track)

	// Allocate numbers := make([]int, 64) right here, pair it with
	// defer delete(numbers), set numbers[0] = 42, and print numbers[0].
	// Run the program to confirm report_tracking_results prints zero leaks.


	// Also allocate pair := new([2]int) with defer free(pair), assign
	// pair^ = {7, 8}, and print pair^. Notice what would happen if the
	// report defer sat below defer free(pair): it would report a false leak!
}

leak_sweep_and_diagnostics :: proc() {

	/*
	You do not have to rely on a helper function to sweep leaks. Looping over
	track.allocation_map directly gives you access to entry.size, entry.memory,
	and entry.location.file_path / entry.location.line / entry.location.procedure
	so you can assert len(track.allocation_map) == 0 in tests or tools.

	Also notice track.total_allocation_count when using dynamic arrays: each
	time append outgrows capacity, [dynamic]T allocates a larger buffer and
	frees the old one, bumping total_allocation_count and peak_memory_allocated
	even though current_memory_allocated drops cleanly back to 0 at exit.
	*/

	// Baseline tracked slice cleanly freed before manual inspection:

	track: mem.Tracking_Allocator
	mem.tracking_allocator_init(&track, context.allocator)
	defer mem.tracking_allocator_destroy(&track)
	context.allocator = mem.tracking_allocator(&track)

	ok_slice := make([]u32, 4)
	ok_slice[0] = 0xCAFE
	fmt.printfln("Clean slice[0]=0x%X (live=%d)", ok_slice[0], len(track.allocation_map))
	delete(ok_slice)

	// Write a manual leak sweep right here before the function exits:
	// check if len(track.allocation_map) > 0, loop for _, entry in track.allocation_map
	// and print entry.size, entry.location.file_path, and entry.location.line.


	// Try uncommenting the deliberate leak below to watch your manual sweep
	// pinpoint the exact byte count and line number:
	// leaked := make([]u8, 1024)
	// fmt.printfln("Deliberate leak length: %d", len(leaked))


	// Allocate growing := make([dynamic]int, 0, 2) with defer delete(growing)
	// (be sure to free it before the manual sweep above if you run the sweep
	// at the bottom!). Append 1..=20 in a loop and print
	// track.total_allocation_count and track.peak_memory_allocated to observe
	// how dynamic growth shows up in tracker stats.
}

bad_free_detection :: proc() {

	/*
	Double-frees, freeing stack memory, and deleting an offset sub-slice are
	normally silent heap corruption bugs in systems languages. Because
	mem.Tracking_Allocator checks whether the pointer exists in
	track.allocation_map before forwarding a free to the backing allocator,
	any unrecognized pointer is safely intercepted and logged into
	track.bad_free_array with its exact #caller_location.
	*/

	// Starter tracker waiting for bad-free experiments:

	track: mem.Tracking_Allocator
	mem.tracking_allocator_init(&track, context.allocator)
	defer mem.tracking_allocator_destroy(&track)
	defer report_tracking_results(&track, "bad-free")
	context.allocator = mem.tracking_allocator(&track)

	clean_buf := make([]u8, 16)
	clean_buf[0] = 1
	delete(clean_buf)
	fmt.printfln("Clean free recorded bad_free count: %d", len(track.bad_free_array))

	// Trigger a stack-pointer bad free inside a controlled test: declare
	// stack_val := 99 and call free(&stack_val). Loop for bad in track.bad_free_array
	// to print bad.memory and bad.location.


	// Trigger a double-free: allocate node := new(int), set node^ = 123, call
	// free(node) once (valid), then call free(node) a second time and observe
	// track.bad_free_array record the second free's exact line number.


	// Trigger a sub-slice delete trap: allocate full := make([]int, 8), call
	// delete(full[1:]) (an offset pointer not at the base of the allocation!),
	// then call delete(full) so the real base allocation still cleans up with
	// zero leaks while bad_free_array flags the invalid sub-slice delete.
}

sub_allocator_and_reset_pattern :: proc() {

	/*
	Tracking_Allocator wraps whatever backing allocator you hand to
	mem.tracking_allocator_init. That means you can wrap a mem.Arena just as
	easily as the heap! Setting arena_track.clear_on_free_all = true tells the
	tracker to empty allocation_map whenever free_all resets the arena.

	Also remember that context.temp_allocator is a separate field from
	context.allocator: wrapping context.allocator does NOT intercept fmt.tprintf
	or other context.temp_allocator calls.
	*/

	// Wrapping a stack-backed mem.Arena inside a Tracking_Allocator:

	backing_buf: [256]byte
	arena: mem.Arena
	mem.arena_init(&arena, backing_buf[:])

	arena_track: mem.Tracking_Allocator
	mem.tracking_allocator_init(&arena_track, mem.arena_allocator(&arena))
	defer mem.tracking_allocator_destroy(&arena_track)
	fmt.printfln("Arena tracker initialized (current bytes=%d)", arena_track.current_memory_allocated)

	// Set arena_track.clear_on_free_all = true and store
	// tracked_arena := mem.tracking_allocator(&arena_track).
	// Allocate two slices from tracked_arena, print len(arena_track.allocation_map),
	// call free_all(tracked_arena), and print len(arena_track.allocation_map)
	// again to confirm it cleared to 0.


	// Wrap context.allocator with a tracker (or reuse a fresh scope), call
	// tmp := fmt.tprintf("temp-%d", 5), print tmp, and verify that
	// track.allocation_map stays at 0 because fmt.tprintf uses
	// context.temp_allocator instead of context.allocator. Call
	// free_all(context.temp_allocator) afterward.
}

main :: proc() {

	fmt.println("=== 1. Tracker wiring and LIFO defer ordering ===")
	tracker_wiring_and_lifo_order()

	fmt.println("\n=== 2. Leak sweep and allocation stats ===")
	leak_sweep_and_diagnostics()

	fmt.println("\n=== 3. Catching bad frees with track.bad_free_array ===")
	bad_free_detection()

	fmt.println("\n=== 4. Wrapping arenas and temp_allocator separation ===")
	sub_allocator_and_reset_pattern()
}
