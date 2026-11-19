// odin run 440_string_allocation_ownership.odin -file

package main

import "core:fmt"
import "core:mem"
import "core:strings"

/*
An Odin string is a 16-byte header: a raw byte pointer (data: [^]u8) and a
byte length (len: int). Because that header stores NO allocator pointer and NO
reference count, you cannot tell by looking at a string variable where its
bytes live. Every string in Odin belongs to one of four ownership categories:

  Zero-alloc views  (.rodata literals, s[a:b], strings.trim_space) -> NEVER delete
  Temp strings      (fmt.tprintf, strings.clone(s, context.temp_allocator)) -> free_all
  Heap strings      (fmt.aprintf, strings.clone, strings.concatenate, clone_to_cstring) -> delete
  strings.Builder   (strings.builder_make()) -> strings.builder_destroy(&b)

Mixing these up is the single most common source of leaks and bad-free crashes in
beginner Odin programs. This file pairs every ownership category with a
mem.Tracking_Allocator so you can prove zero leaks and zero bad frees.

This file is split into four sections called from main at the bottom so you can
read top to bottom and run the program at any point.
*/

verify_zero_leaks :: proc(track: ^mem.Tracking_Allocator, section: string) {

	if len(track.allocation_map) > 0 {
		fmt.printfln("[%s] LEAK DETECTED (%d):", section, len(track.allocation_map))
		for _, entry in track.allocation_map {
			fmt.printfln("  - %d bytes at %v", entry.size, entry.location)
		}
	}
	if len(track.bad_free_array) > 0 {
		fmt.printfln("[%s] BAD FREE DETECTED (%d):", section, len(track.bad_free_array))
		for bad in track.bad_free_array {
			fmt.printfln("  - %p at %v", bad.memory, bad.location)
		}
	}
	if len(track.allocation_map) == 0 && len(track.bad_free_array) == 0 {
		fmt.printfln("[%s] clean: 0 leaks, 0 bad frees", section)
	}
}

zero_alloc_views_and_slices :: proc() {

	/*
	String literals like "Hellope" live in the executable's read-only data
	segment (.rodata) for the entire life of the program. Slicing a string with
	s[a:b] or calling view helpers like strings.trim_space(s) simply computes a
	new {data, len} header pointing inside the existing bytes—zero heap memory
	is allocated, so you must NEVER pass those views to delete().

	Watch the lifetime rule when taking a view of a heap string: suppose
	src := fmt.aprintf("  data  ") and view := strings.trim_space(src). Calling
	delete(src) frees the underlying buffer, turning view into a dangling pointer!
	*/

	// Starter zero-alloc view verified with Tracking_Allocator:

	track: mem.Tracking_Allocator
	mem.tracking_allocator_init(&track, context.allocator)
	defer mem.tracking_allocator_destroy(&track)
	defer verify_zero_leaks(&track, "views")
	context.allocator = mem.tracking_allocator(&track)

	trimmed_view := strings.trim_space("  Hellope, String Ownership!  ")
	fmt.printfln("Zero-alloc view: %q (active allocs=%d)", trimmed_view, len(track.allocation_map))

	// Declare original := "Commander Shepard", take two zero-allocation slice
	// views title := original[:9] and surname := original[10:], print both,
	// and print len(track.allocation_map) to confirm 0 allocations occurred.


	// Test the view-aliasing lifetime rule: allocate dyn_src := fmt.aprintf("  payload-42  ")
	// paired with defer delete(dyn_src), take view := strings.trim_space(dyn_src),
	// print view while dyn_src is still alive, and note that delete(dyn_src)
	// runs only at scope exit (never call delete(view)!).
}

temp_vs_heap_strings :: proc() {

	/*
	Procedures ending in tprintf or taking context.temp_allocator allocate into
	the per-thread scratch buffer and are cleaned in bulk by
	free_all(context.temp_allocator). Procedures like fmt.aprintf,
	strings.clone, strings.concatenate, and strings.clone_to_cstring allocate
	from context.allocator by default and stay live until you call delete().
	Note that cstring values produced by strings.clone_to_cstring are also freed
	with delete(c_str).
	*/

	// Starter temp string showing Tracking_Allocator stays at 0 heap allocs:

	track: mem.Tracking_Allocator
	mem.tracking_allocator_init(&track, context.allocator)
	defer mem.tracking_allocator_destroy(&track)
	defer verify_zero_leaks(&track, "temp-vs-heap")
	context.allocator = mem.tracking_allocator(&track)

	temp_banner := fmt.tprintf("Temp ID-%d", 7)
	fmt.printfln("Temp string: %q (tracked heap allocs=%d)", temp_banner, len(track.allocation_map))
	free_all(context.temp_allocator)

	// Create temp_report := fmt.tprintf("Status for %s: OK", "Shepard") and
	// temp_copy := strings.clone("Commander", context.temp_allocator), print
	// both, and wipe them with free_all(context.temp_allocator).


	// Create heap_str := fmt.aprintf("ID-%d", 42) and cloned := strings.clone("owned"),
	// pair each immediately with defer delete(heap_str) and defer delete(cloned)
	// so verify_zero_leaks sees 0 leaks, and print both strings.


	// Build joined := strings.concatenate({"alpha", "-", "beta"}) and
	// c_str := strings.clone_to_cstring(joined), pair both with
	// defer delete(joined) and defer delete(c_str), and print both.
}

string_builder_lifecycle :: proc() {

	/*
	Concatenating inside a loop with strings.concatenate allocates a new string
	every pass. Instead, strings.Builder wraps a growable [dynamic]u8 buffer:
	you append with strings.write_string(&b, "abc") or fmt.sbprintf(&b, "n=%d", 1),
	borrow a zero-allocation view of the built bytes via strings.to_string(b),
	reuse the buffer across batches with strings.builder_reset(&b), and free
	the backing buffer at the end with strings.builder_destroy(&b).

	Because strings.to_string(b) borrows b's internal byte slice, that string
	becomes invalid the moment you call builder_reset(&b) or builder_destroy(&b).
	*/

	// Starter strings.Builder lifecycle with Tracking_Allocator:

	track: mem.Tracking_Allocator
	mem.tracking_allocator_init(&track, context.allocator)
	defer mem.tracking_allocator_destroy(&track)
	defer verify_zero_leaks(&track, "builder")
	context.allocator = mem.tracking_allocator(&track)

	b := strings.builder_make()
	defer strings.builder_destroy(&b)
	strings.write_string(&b, "Header: ")
	fmt.printfln("Builder view: %q", strings.to_string(b))

	// Append formatted items inside a loop using fmt.sbprintf(&b, "item=%d ", i)
	// for i in 0..<3, print strings.to_string(b), then call
	// strings.builder_reset(&b) and append "reused" to observe buffer reuse
	// without leaking.


	// Before exiting, promote the builder output into an independent heap
	// string: final_msg := strings.clone(strings.to_string(b)) paired with
	// defer delete(final_msg), reset b afterward, and print final_msg to prove
	// final_msg owns its own bytes separately from b.
}

map_owned_key_value_tracking :: proc() {

	/*
	Storing strings inside a map[string]string introduces a classic ownership
	trap: calling delete(env_map) frees ONLY the map's internal hash-table
	bucket array—it does NOT free any heap-allocated key or value strings
	inside the map!

	Suppose env_map holds keys and values created with strings.clone or
	fmt.aprintf. Before calling delete(env_map), you must loop over every entry
	and free the owned strings:
	    for k, v in env_map { delete(k); delete(v) }
	    delete(env_map)

	Watch out for mixed ownership too: if your keys are .rodata literals like
	"host" while only values are cloned, calling delete(k) triggers a bad free!
	Pick one uniform ownership convention per map and enforce it consistently.
	*/

	// Starter owned map[string]string cleanup verified by Tracking_Allocator:

	track: mem.Tracking_Allocator
	mem.tracking_allocator_init(&track, context.allocator)
	defer mem.tracking_allocator_destroy(&track)
	defer verify_zero_leaks(&track, "map-ownership")
	context.allocator = mem.tracking_allocator(&track)

	env := make(map[string]string)
	seed_key := strings.clone("MODE")
	seed_val := strings.clone("debug")
	env[seed_key] = seed_val
	fmt.printfln("Seeded map entry: %s=%s", seed_key, env[seed_key])
	for k, v in env {
		delete(k)
		delete(v)
	}
	delete(env)

	// Create labels := make(map[string]string) where BOTH keys and values are
	// heap-allocated via fmt.aprintf("k_%d", i) and fmt.aprintf("val_%d", i)
	// for i in 0..<3. Register a defer block that loops
	// for k, v in labels { delete(k); delete(v) } before calling delete(labels),
	// and confirm verify_zero_leaks reports 0 leaks and 0 bad frees.


	// Test mixed ownership safely: create settings := make(map[string]string)
	// with .rodata literal keys ("host", "port") and cloned heap values
	// (strings.clone("localhost"), strings.clone("8080")). Free ONLY the values
	// in a defer loop (for _, v in settings { delete(v) }) before
	// delete(settings). Note what happens if you accidentally call delete(k) on
	// the literal key "host": Tracking_Allocator flags a bad free!


	// Practice updating an existing key in an owned map without leaking the
	// old value: before overwriting labels["k_0"] = strings.clone("updated"),
	// look up old_val, ok := labels["k_0"] and if ok { delete(old_val) }, and
	// avoid cloning a duplicate key when the key is already stored in the map.
}

main :: proc() {

	fmt.println("=== 1. Zero-alloc views and slice lifetimes ===")
	zero_alloc_views_and_slices()

	fmt.println("\n=== 2. Temp vs. heap string allocations ===")
	temp_vs_heap_strings()

	fmt.println("\n=== 3. strings.Builder lifecycle and promotion ===")
	string_builder_lifecycle()

	fmt.println("\n=== 4. Owned key/value tracking in map[string]string ===")
	map_owned_key_value_tracking()
}
