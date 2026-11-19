// odin run 730_mutex_and_wait_group.odin -file

package main

import "core:fmt"
import "core:sync"
import "core:thread"

/*
When two threads increment a plain shared integer ('total += 1'), each thread
loads the old value into a register, adds 1, and stores it back. If both load
10 at the same instant, both write back 11 — silently losing an update!

Odin's 'core:sync' package prevents data races with zero-initialized primitives
that need no constructor or destructor calls:

    sync.Mutex        exclusive lock protecting shared mutations
    sync.RW_Mutex     multiple concurrent readers OR one exclusive writer
    sync.Wait_Group   counter waiting until N background tasks finish

Declaring 'mu: sync.Mutex' leaves it immediately ready to lock. Better yet,
'sync.guard(&mu)' uses Odin's '@(deferred_in=unlock)' attribute to acquire the
lock on entry and guarantee an automatic unlock at the end of the enclosing
scope, even if you return early or hit an error branch.

This file is split into three sections called from main at the bottom so you
can read top to bottom and run the program at any point.
*/

Shared_State :: struct {
	mu:    sync.Mutex,
	wg:    sync.Wait_Group,
	total: int,
}

Config_Table :: struct {
	rw:         sync.RW_Mutex,
	version:    int,
	thresholds: [4]int,
	torn_reads: int,
}

mutex_guards_and_races :: proc() {

	/*
	You can always pair 'sync.lock(&mu)' with 'defer sync.unlock(&mu)' by hand,
	or wrap a short critical section with 'if sync.guard(&state.mu) { ... }'.
	Inside an 'if sync.guard(&state.mu)' block, the mutex stays locked only
	until the closing brace of the 'if' statement; outside an 'if', calling
	'sync.guard(&state.mu)' as a standalone statement keeps it locked until the
	surrounding procedure or block exits.
	*/

	// Here is a starter zero-initialized Shared_State using if sync.guard:

	state: Shared_State
	if sync.guard(&state.mu) {
		state.total = 1
	}
	fmt.printfln("guarded total=%d | size_of(thread.Thread)=%dB", state.total, size_of(thread.Thread))

	// Practice explicit lock/unlock vs scoped guard on a local mutex:
	// Declare local_mu: sync.Mutex and count := 0. First call sync.lock(&local_mu),
	// increment count += 10, and call sync.unlock(&local_mu). Then open an inner
	// { ... } block, call sync.guard(&local_mu), increment count += 5, and print
	// count after the block closes.


	// Verify early-return lock safety: write safe_deposit :: proc(state: ^Shared_State, amount: int) -> bool
	// at file scope. Put sync.guard(&state.mu) as the first statement, return
	// false immediately if amount <= 0, otherwise add amount to state.total and
	// return true. Call safe_deposit(&state, -5) then safe_deposit(&state, 20)
	// here to confirm the mutex never stays locked after the early return.
}

wait_group_coordination :: proc() {

	/*
	Suppose a coordinator spawns 4 worker threads and needs to read the final
	total once every worker finishes. With 'sync.Wait_Group', always call
	'sync.wait_group_add(&state.wg, 4)' on the coordinator BEFORE launching any
	thread! If you instead called wait_group_add inside each worker, the
	coordinator could reach 'sync.wait_group_wait(&state.wg)' while the count is
	still 0 and continue before the workers even started.

	Inside each worker, put 'defer sync.wait_group_done(&state.wg)' on the very
	first line so even an early return decrements the Wait_Group cleanly and
	never deadlocks the coordinator.
	*/

	// Write a worker procedure at file scope:
	// increment_worker :: proc(state: ^Shared_State)
	// Put defer sync.wait_group_done(&state.wg) at the top, acquire
	// sync.guard(&state.mu) (inside a loop or per batch), and add 1_000 to
	// state.total. If state == nil, return safely before acquiring the lock.


	// In this section, declare work_state: Shared_State, call
	// sync.wait_group_add(&work_state.wg, 4) BEFORE spawning 4 threads with
	// thread.create_and_start_with_poly_data(&work_state, increment_worker),
	// wait with sync.wait_group_wait(&work_state.wg), join and destroy all 4
	// thread handles, and print work_state.total (expected: 4000).


	// Reuse a Wait_Group across two consecutive phases: run a second batch of
	// 2 threads after calling sync.wait_group_add(&work_state.wg, 2) and
	// sync.wait_group_wait(&work_state.wg) again, then print the new total
	// (expected: 6000).
}

rw_mutex_read_sharing :: proc() {

	/*
	A plain 'sync.Mutex' forces readers to line up single-file even when nobody
	is modifying the data. When reads far outnumber writes, 'sync.RW_Mutex' lets
	multiple reader threads hold 'sync.shared_guard(&tbl.rw)' simultaneously,
	while blocking until any active writer holding 'sync.guard(&tbl.rw)' drops
	its exclusive lock.

	    Suppose writer updates version = 5 and thresholds = {5, 10, 15, 20}:
	        Without a lock, a reader could see version == 5 alongside stale
	        thresholds[3] == 16 from version 4 (a torn read!).
	        With shared_guard on readers and guard on the writer, every snapshot
	        satisfies thresholds[k] == version * (k + 1).
	*/

	// Here is a starter Config_Table snapshot check:

	anchor_tbl: Config_Table
	if sync.shared_guard(&anchor_tbl.rw) {
		fmt.printfln("size_of(sync.RW_Mutex)=%dB | initial version=%d", size_of(sync.RW_Mutex), anchor_tbl.version)
	}

	// Write two concurrent worker procedures at file scope:
	// writer_worker :: proc(tbl: ^Config_Table)
	// Loop 500 times; in each step acquire if sync.guard(&tbl.rw), increment
	// tbl.version += 1, and update all four slots tbl.thresholds[k] = tbl.version * (k + 1).
	//
	// reader_worker :: proc(tbl: ^Config_Table)
	// Loop 10_000 times; in each step acquire if sync.shared_guard(&tbl.rw),
	// read v := tbl.version, and verify every tbl.thresholds[k] == v * (k + 1)
	// (incrementing torn_reads safely if a mismatch ever occurred — expect 0!).


	// In this section, declare live_tbl: Config_Table, spawn 3 reader_worker
	// threads and 1 writer_worker thread concurrently via
	// thread.create_and_start_with_poly_data(&live_tbl, ...), join and destroy
	// all 4 handles, and print live_tbl.version and live_tbl.torn_reads (expect
	// version=500, torn_reads=0).
	//
	// Experiment: swap sync.shared_guard(&tbl.rw) to exclusive sync.guard(&tbl.rw)
	// inside reader_worker to compare contention when readers block each other,
	// and remember never to call sync.guard(&tbl.rw) while already holding
	// sync.shared_guard(&tbl.rw) on the same thread (self-deadlock!).
}

main :: proc() {

	fmt.println("=== 1. Mutex guards and data-race protection ===")
	mutex_guards_and_races()

	fmt.println("\n=== 2. Wait_Group coordination ===")
	wait_group_coordination()

	fmt.println("\n=== 3. Live multi-thread RW_Mutex read sharing ===")
	rw_mutex_read_sharing()
}
