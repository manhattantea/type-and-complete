// odin run 598_tracy_memory_and_lock_profiling.odin -file

package main

import "base:runtime"
import "core:fmt"
import "core:mem"
import "core:sync"

/*
Many performance bugs hide inside invisible allocations or lock scopes rather
than arithmetic loops. Odin's implicit context.allocator and @(deferred_in)
procedure attributes let you attach Tracy memory and mutex hooks at one
wrapper boundary without modifying downstream call sites.

This Primer keeps focus strictly on Odin's runtime.Allocator and sync.Mutex
integration hooks under when TRACY_ENABLE. For named memory-pool leak hunts
against mem.Arena, multi-thread false-sharing timelines, and lock-contention
remediation, continue to ../tracy_how_to/300_tracy_memory_allocator_and_arena_tracking.odin
and ../tracy_how_to/400_thread_naming_locks_and_false_sharing.odin.
*/

TRACY_ENABLE :: #config(TRACY_ENABLE, false)

when TRACY_ENABLE {
	foreign import tracy "TracyClient.lib"

	foreign tracy {
		___tracy_emit_memory_alloc_named :: proc "c" (ptr: rawptr, size: uint, secure: i32, name: cstring) ---
		___tracy_emit_memory_free_named  :: proc "c" (ptr: rawptr, secure: i32, name: cstring) ---
		___tracy_set_thread_name         :: proc "c" (name: cstring) ---
	}
}

Tracy_Memory_Tracker :: struct {
	backing:      runtime.Allocator,
	pool_name:    cstring,
	active_sizes: map[rawptr]int,
	active_bytes: int,
	peak_bytes:   int,
	total_allocs: int,
	total_frees:  int,
}

Lock_Stats :: struct {
	name:     string,
	acquires: u64,
	releases: u64,
}

context_allocator_hook :: proc() {

	/*
	Every Odin allocation—make, new, append, fmt.aprintf—calls the function
	pointer stored in context.allocator. That makes a custom runtime.Allocator
	wrapper trivial to plug into any scope: delegate the real memory request
	to tracker.backing, update byte counters, and under when TRACY_ENABLE
	forward the pointer and size to Tracy's named memory track.

	Watch out for one classic trap when building tracking allocators: the
	tracker's own internal book-keeping map (active_sizes: map[rawptr]int)
	must allocate from tracker.backing—never from context.allocator! If
	active_sizes used the wrapped context.allocator, inserting a pointer into
	the map would trigger another allocation, recursing until the stack blows.
	*/

	nil_alloc: runtime.Allocator = mem.nil_allocator()
	fmt.printfln("Allocator hook ready (TRACY_ENABLE=%v, Tracker=%d B, nil_ok=%v)",
		TRACY_ENABLE, size_of(Tracy_Memory_Tracker), nil_alloc.procedure != nil)

	// Implement tracy_tracking_allocator_proc at file scope with the exact
	// runtime.Allocator_Proc signature:
	// proc(allocator_data: rawptr, mode: runtime.Allocator_Mode, size, alignment: int, old_memory: rawptr, old_size: int, location := #caller_location) -> ([]byte, runtime.Allocator_Error)
	// Cast tracker := (^Tracy_Memory_Tracker)(allocator_data) and delegate to
	// res, err := tracker.backing.procedure(tracker.backing.data, mode, size, alignment, old_memory, old_size, location).
	// Handle .Alloc / .Alloc_Non_Zeroed (record tracker.active_sizes[raw_data(res)] = size,
	// update active_bytes/peak_bytes/total_allocs, emit ___tracy_emit_memory_alloc_named
	// when TRACY_ENABLE), .Free (look up old_memory in active_sizes, subtract
	// from active_bytes, delete_key, increment total_frees, emit free_named),
	// .Resize, and .Free_All (clear(&tracker.active_sizes), active_bytes = 0).


	// Implement tracy_tracking_allocator :: proc(tracker: ^Tracy_Memory_Tracker) -> runtime.Allocator
	// returning runtime.Allocator{procedure = tracy_tracking_allocator_proc, data = tracker}.
}

mutex_deferred_in_hook :: proc() {

	/*
	Just like sync.guard(&mu) in core:sync, you can wrap sync.Mutex with
	Odin's @(deferred_in = tracy_lock_unlock) attribute. When we attach
	@(deferred_in = exit_proc) to an entry procedure, Odin passes the exact
	same arguments given to the entry call into exit_proc at scope exit:

	    Suppose you call:
	        tracy_lock_guard(&cache_mu, &lock_stats)
	    Odin inserts at the enclosing block exit:
	        defer tracy_lock_unlock(&cache_mu, &lock_stats)

	Unlike @(deferred_out), @(deferred_in) needs zero return-value token structs
	when the exit procedure only needs the original pointer arguments!
	*/

	anchor_mu: sync.Mutex
	sync.lock(&anchor_mu)
	sync.unlock(&anchor_mu)
	fmt.printfln("Mutex hook ready (Mutex=%d B, Lock_Stats=%d B)",
		size_of(sync.Mutex), size_of(Lock_Stats))

	// Implement tracy_lock_unlock :: proc(mu: ^sync.Mutex, stats: ^Lock_Stats)
	// at file scope: increment stats.releases += 1 and call sync.unlock(mu).
	// Then implement @(deferred_in = tracy_lock_unlock) on:
	// tracy_lock_guard :: proc(mu: ^sync.Mutex, stats: ^Lock_Stats)
	// calling sync.lock(mu) and incrementing stats.acquires += 1.


	// Also implement tracy_set_thread_name :: proc(name: cstring) calling
	// ___tracy_set_thread_name(name) inside when TRACY_ENABLE.
}

single_scope_verification :: proc() {

	/*
	Once both hooks are written, verify them together in one bounded scope:
	save and restore context.allocator via defer, initialize active_sizes on
	tracker.backing, allocate and free a slice under the lock guard, and confirm
	active_bytes returns cleanly to 0 with acquires == releases.

	For multi-thread contention timelines and false-sharing cache-line padding,
	continue to ../tracy_how_to/400_thread_naming_locks_and_false_sharing.odin.
	*/

	fmt.println("Single-scope hook verification ready.")

	// Call tracy_set_thread_name("MainThread"), then initialize:
	// tracker := Tracy_Memory_Tracker{backing = context.allocator, pool_name = "AssetCache"}
	// Allocate tracker.active_sizes = make(map[rawptr]int, allocator = tracker.backing)
	// with defer delete(tracker.active_sizes).


	// Open a { ... } block saving orig_alloc := context.allocator with
	// defer context.allocator = orig_alloc, then install:
	// context.allocator = tracy_tracking_allocator(&tracker)
	// Create cache_mu: sync.Mutex and lock_stats := Lock_Stats{name = "AssetCacheLock"}.
	// Inside the scope, acquire tracy_lock_guard(&cache_mu, &lock_stats),
	// allocate scratch := make([]u64, 256), fill a few slots, and free it
	// with delete(scratch).


	// Outside the { ... } block, print tracker.active_bytes (must be 0!),
	// tracker.peak_bytes, tracker.total_allocs, tracker.total_frees, and
	// lock_stats (acquires == 1, releases == 1).
}

main :: proc() {

	fmt.println("=== 1. Wrapping context.allocator via runtime.Allocator ===")
	context_allocator_hook()

	fmt.println("\n=== 2. Wrapping sync.Mutex via @(deferred_in) ===")
	mutex_deferred_in_hook()

	fmt.println("\n=== 3. Single-scope verification ===")
	single_scope_verification()
}
