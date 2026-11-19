// odin run 740_atomics_and_lock_free.odin -file

package main

import "core:fmt"
import "core:sync"
import "core:thread"

/*
A mutex protects shared memory by putting contending threads to sleep in the
OS kernel, which costs thousands of cycles per transition. When you only need
to update a single counter, publish a flag, or claim a unique array slot,
hardware atomic operations in 'core:sync' compile straight to single CPU
instructions (such as LOCK XADD or CMPXCHG on x86_64) with no kernel switch.

Even a simple statement like 'counter += 1' is NOT atomic: the CPU loads
counter into a register, adds 1, and stores it back. If two threads execute
those three steps concurrently, one update silently overwrites the other.
Atomic operations force the hardware cache-coherency protocol to serialize
access to that one memory location cleanly.

This file is split into three sections called from main at the bottom so you
can read top to bottom and test each piece in isolation.
*/

Handshake_Packet :: struct {
	payload:  int,
	checksum: u32,
	ready:    bool,
}

atomic_loads_stores_and_counters :: proc() {

	/*
	The core building blocks in 'core:sync' operate on pointers to plain values:
	'sync.atomic_load(&x)' reads x atomically; 'sync.atomic_store(&x, v)' writes
	v atomically. For counters, 'sync.atomic_add(&x, delta)' and
	'sync.atomic_sub(&x, delta)' modify x in one indivisible hardware step.

	Watch the return value of 'sync.atomic_add(&x, delta)': it returns the
	PREVIOUS value held in x before adding delta, not the new total! Returning
	the old value is ideal for lock-free slot claiming.

	    Suppose next_slot := 0 and two threads both run:
	        slot := sync.atomic_add(&next_slot, 1)
	    Thread A receives 0 (and next_slot becomes 1), while Thread B receives 1
	    (and next_slot becomes 2). Neither thread can ever claim the same slot.

	Similarly, 'sync.atomic_exchange(&x, new_val)' atomically swaps new_val into
	x and returns whatever old value was sitting there before the swap.
	*/

	// Here is a quick starter check showing what sync.atomic_add returns:

	counter: int = 0
	prev := sync.atomic_add(&counter, 1)
	fmt.printfln("Starter atomic_add: prev=%d, now=%d (Thread=%dB)",
		prev, sync.atomic_load(&counter), size_of(thread.Thread))

	// Claim 3 unique slot indices from a shared counter: declare next_slot := 0,
	// call sync.atomic_add(&next_slot, 1) three times into s0, s1, and s2, and
	// print s0, s1, s2 (expected: 0, 1, 2) alongside sync.atomic_load(&next_slot)
	// (expected: 3).


	// Practice atomic_sub and atomic_exchange: declare remaining := 5 and
	// active_flag := 1, subtract 2 with sync.atomic_sub(&remaining, 2), swap
	// active_flag to 0 with sync.atomic_exchange(&active_flag, 0), and print both
	// returned previous values as well as the current atomic_load values.


	// Verify atomic increments across real OS threads: define a local or file
	// Counter_Work :: struct { total: int }, spawn 4 threads with
	// thread.create_and_start_with_poly_data where each worker runs 10_000 passes
	// of sync.atomic_add(&work.total, 1), join and destroy all 4 threads, and
	// confirm sync.atomic_load(&work.total) equals 40_000.


	/*
	One subtle data-race bug in Odin is accessing the same variable atomically
	in one place and with a plain read or write somewhere else. Passing the
	'-vet-atomic-access' flag to 'odin check' asks the compiler to warn whenever
	an atomic address is touched by a non-atomic expression.
	*/

	// Try uncommenting the plain read below and running:
	// odin check 740_atomics_and_lock_free.odin -file -vet-atomic-access
	// plain_read := counter
	// fmt.println("Non-atomic read:", plain_read)
}

cas_loops_and_lock_free_updates :: proc() {

	/*
	What if you want a conditional update such as "update high_score only when
	candidate > high_score"? Writing an atomic_load followed by an atomic_store
	creates a race window: another thread can slip in between your load and your
	store with an even bigger score, and your stale store overwrites it.

	Compare-And-Swap (CAS) closes that window in hardware. When we call
	'sync.atomic_compare_exchange_strong(&target, expected, desired)', the CPU
	checks whether target^ still equals expected; if so, it writes desired in
	one atomic instruction and returns (expected, true). If another thread
	changed target^ first, it leaves target^ untouched and returns
	(actual_val, false) so your loop can reload and try again.

	    Suppose high_score := 50 and two threads race with candidates 70 and 90:
	    Thread A loads curr := 50, sees 70 > 50, and prepares CAS(50 -> 70).
	    Thread B wins first, changing high_score to 90.
	    Thread A's CAS sees high_score is 90 (not 50), returns (90, false), loops
	    back, loads curr := 90, sees 70 <= 90, and exits without clobbering 90.
	*/

	// Write a lock-free maximum updater above or inside this section with exact
	// signature: atomic_update_max :: proc(max_val: ^int, candidate: int)
	// Inside a 'for' loop, load curr := sync.atomic_load(max_val), return early
	// if candidate <= curr, otherwise call:
	// _, ok := sync.atomic_compare_exchange_strong(max_val, curr, candidate)
	// and return as soon as ok is true.


	// Write a one-shot CAS state transition helper with exact signature:
	// atomic_try_claim :: proc(state: ^int, expected, desired: int) -> bool
	// Return true only if sync.atomic_compare_exchange_strong transitions
	// state^ from expected to desired on this attempt.


	// Test both CAS helpers: declare high_score := 50, call
	// atomic_update_max(&high_score, 40) (remains 50) and
	// atomic_update_max(&high_score, 85) (updates to 85), then spawn 4 threads
	// that each call atomic_update_max(&high_score, (id + 1) * 100) and verify
	// high_score finishes at 400. Also call atomic_try_claim twice on a zeroed
	// state flag (0 -> 1) and confirm only the first claim returns true.
}

memory_orderings_and_handshake :: proc() {

	/*
	Modern CPUs buffer stores and reorder independent instructions, and the
	compiler can also reorder non-atomic reads and writes. If Thread A writes
	'pkt.payload = 9001' and then sets 'pkt.ready = true', another core could
	observe 'pkt.ready == true' BEFORE seeing 'pkt.payload == 9001' unless
	memory ordering constraints tie them together!

	Odin exposes 'sync.Atomic_Memory_Order' (.Relaxed, .Acquire, .Release,
	.Acq_Rel, .Seq_Cst) through explicit variants such as
	'sync.atomic_store_explicit' and 'sync.atomic_load_explicit'.

	When we write 'sync.atomic_store_explicit(&pkt.ready, true, .Release)', it
	means "all memory writes performed before this store must become visible
	before pkt.ready flips to true". When the consumer reads
	'sync.atomic_load_explicit(&pkt.ready, .Acquire)', it means "do not execute
	any memory reads after this load until pkt.ready is observed as true".
	Pairing .Release on the writer with .Acquire on the reader safely publishes
	entire structs across threads without taking a mutex.

	    Suppose pkt: Handshake_Packet starts zero-initialized:
	        // Producer thread:
	        pkt.payload = 9001
	        pkt.checksum = 0xCAFE_BABE
	        sync.atomic_store_explicit(&pkt.ready, true, .Release)

	        // Consumer thread:
	        for !sync.atomic_load_explicit(&pkt.ready, .Acquire) {
	            thread.yield()
	        }
	        // Guaranteed to see payload == 9001 and checksum == 0xCAFE_BABE!
	*/

	// Starter anchor confirming Handshake_Packet layout and thread.yield wiring:

	anchor_pkt := Handshake_Packet{payload = 1, checksum = 2}
	sync.atomic_store_explicit(&anchor_pkt.ready, true, .Release)
	if !sync.atomic_load_explicit(&anchor_pkt.ready, .Acquire) {
		thread.yield()
	}
	fmt.printfln("Starter packet (%dB): payload=%d, checksum=0x%x",
		size_of(Handshake_Packet), anchor_pkt.payload, anchor_pkt.checksum)

	// Practice single-thread .Release / .Acquire calls first: declare
	// local_pkt: Handshake_Packet, set local_pkt.payload = 4242, publish with
	// sync.atomic_store_explicit(&local_pkt.ready, true, .Release), and assert
	// sync.atomic_load_explicit(&local_pkt.ready, .Acquire) returns true.


	// Write a producer procedure above or at file scope with exact signature:
	// handshake_producer :: proc(pkt: ^Handshake_Packet)
	// Have it write pkt.payload = 9001 and pkt.checksum = 0xCAFE_BABE, then
	// publish pkt.ready with sync.atomic_store_explicit(&pkt.ready, true, .Release).


	// Run the real 2-thread .Release/.Acquire handshake: declare
	// shared_pkt: Handshake_Packet, launch handshake_producer(&shared_pkt) with
	// thread.create_and_start_with_poly_data(&shared_pkt, handshake_producer),
	// spin here with for !sync.atomic_load_explicit(&shared_pkt.ready, .Acquire)
	// calling thread.yield(), assert shared_pkt.payload == 9001 and
	// shared_pkt.checksum == 0xCAFE_BABE, then thread.join and thread.destroy
	// the producer thread. Finally run:
	// odin check 740_atomics_and_lock_free.odin -file -vet-atomic-access
}

main :: proc() {

	fmt.println("=== 1. Atomic loads, stores, and counters ===")
	atomic_loads_stores_and_counters()

	fmt.println("\n=== 2. Compare-and-swap loops and lock-free updates ===")
	cas_loops_and_lock_free_updates()

	fmt.println("\n=== 3. Explicit memory orderings and .Release/.Acquire handshake ===")
	memory_orderings_and_handshake()
}
