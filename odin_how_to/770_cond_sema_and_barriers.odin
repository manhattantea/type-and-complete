// odin run 770_cond_sema_and_barriers.odin -file

package main

import "core:fmt"
import "core:sync"
import "core:thread"

/*
A mutex protects data, and atomics update single words, but concurrent
programs also need ways for threads to WAIT for conditions, synchronize at
phase boundaries, throttle scarce permits, and run one-time setup safely.

In 'core:sync', all four primitives ('sync.Cond', 'sync.Barrier', 'sync.Sema',
and 'sync.Once') are zero-initialized value structs: declaring them on the
stack or inside another struct leaves them ready to use (only 'sync.Barrier'
takes a thread count via 'sync.barrier_init').

This file is split into four sections called from main at the bottom covering
condition variables, barriers, counting semaphores, and one-time init.
*/

Cond_State :: struct {
	mu:      sync.Mutex,
	cond:    sync.Cond,
	ready:   bool,
	payload: int,
}

Barrier_Context :: struct {
	barrier:   ^sync.Barrier,
	thread_id: int,
}

condition_variables_and_predicates :: proc() {

	/*
	Suppose a consumer thread needs to wait until a producer thread populates
	shared state. Spinning in a tight 'for !state.ready {}' loop burns 100% of
	a CPU core doing nothing. A condition variable ('sync.Cond') lets the
	waiting thread sleep in the OS kernel until another thread wakes it.

	'sync.Cond' always works alongside a 'sync.Mutex' protecting your state:
	first lock the mutex (for example with 'sync.guard(&state.mu)'), then loop
	while the predicate is false:
	       for !state.ready {
	           sync.cond_wait(&state.cond, &state.mu)
	       }
	'sync.cond_wait' atomically unlocks '&state.mu' and puts the thread to
	sleep; when woken, it re-locks '&state.mu' before returning! Always use a
	'for' loop (never 'if'), because OS condition variables can wake spuriously
	or another thread might consume the item first.

	On the producer side, lock '&state.mu', set 'state.ready = true', and call
	'sync.cond_signal(&state.cond)' to wake one waiter, or
	'sync.cond_broadcast(&state.cond)' to wake all waiting threads at once.
	*/

	// Starter anchor printing sync primitive sizes:

	once_anchor: sync.Once
	fmt.printfln("Starter sync sizes: Cond=%dB, Barrier=%dB, Sema=%dB, Once=%dB, Thread=%dB",
		size_of(sync.Cond), size_of(sync.Barrier), size_of(sync.Sema),
		size_of(once_anchor), size_of(thread.Thread))

	// Write a consumer procedure at file scope with exact signature:
	// cond_consumer :: proc(state: ^Cond_State)
	// Acquire sync.guard(&state.mu), wait inside a loop:
	// for !state.ready { sync.cond_wait(&state.cond, &state.mu) }
	// and print state.payload once woken.


	// Write a producer procedure at file scope with exact signature:
	// cond_producer :: proc(state: ^Cond_State)
	// Acquire sync.guard(&state.mu), set state.payload = 777 and
	// state.ready = true, and call sync.cond_signal(&state.cond).


	// Declare state: Cond_State, spawn cond_consumer and cond_producer threads
	// via thread.create_and_start_with_poly_data(&state, ...), and join/destroy
	// both threads. Then test sync.cond_broadcast(&state.cond) waking 2
	// waiting consumer threads simultaneously from one producer update.
}

phase_barriers_lockstep :: proc() {

	/*
	In multi-phase simulations (such as updating all particle velocities in
	Phase 1 before reading neighbor positions in Phase 2), all worker threads
	must finish Phase 1 before any thread begins Phase 2.

	When we call 'sync.barrier_init(&b, thread_count)' and each worker calls
	'sync.barrier_wait(&b)', the first N - 1 arriving threads block at the
	barrier. As soon as the N-th thread arrives, all N threads release together
	into Phase 2.
	*/

	// Write a two-phase worker procedure at file scope with exact signature:
	// barrier_worker :: proc(ctx: ^Barrier_Context)
	// Print a Phase 1 message with ctx.thread_id, call
	// sync.barrier_wait(ctx.barrier), and then print a Phase 2 message.


	// Initialize b: sync.Barrier with sync.barrier_init(&b, 3), build
	// contexts: [3]Barrier_Context for thread_ids 0, 1, and 2, spawn 3 threads
	// running barrier_worker, and join/destroy all 3 threads. Notice in the
	// output that every Phase 1 line prints before any Phase 2 line appears!
}

counting_semaphores_permits :: proc() {

	/*
	While a mutex permits only 1 holder at a time, a counting semaphore
	('sync.Sema') tracks an arbitrary non-negative permit count.
	'sync.sema_post(&sema, count)' adds 'count' permits and wakes waiting
	threads; 'sync.sema_wait(&sema)' consumes 1 permit (or sleeps until a
	permit is posted).

	    Suppose a pool has 2 database connections and 4 worker threads:
	    Calling sync.sema_post(&sema, 2) seeds 2 permits. Workers 0 and 1 call
	    sync.sema_wait(&sema) and enter immediately (permits drop to 0), while
	    Workers 2 and 3 sleep until someone calls sync.sema_post(&sema, 1).
	*/

	// Practice single-thread permit accounting: declare sema: sync.Sema, post
	// 2 permits with sync.sema_post(&sema, 2), consume one permit with
	// sync.sema_wait(&sema), and return it with sync.sema_post(&sema, 1).


	// Throttle 4 concurrent worker threads down to at most 2 active at once:
	// define a Sema_Work :: struct { sema: ^sync.Sema, active: int, max_seen: int },
	// pre-post 2 permits, have each worker call sync.sema_wait(w.sema) with
	// defer sync.sema_post(w.sema, 1), track concurrent active count via
	// sync.atomic_add / sync.atomic_sub, and verify max_seen <= 2 after join.
}

one_time_init_with_once :: proc() {

	/*
	Checking a plain boolean flag 'if !initialized' across multiple threads is
	a race condition: two threads can both observe 'false' and run setup twice,
	or a second thread can see 'initialized == true' before setup finishes.
	'sync.Once' solves both hazards: 'sync.once_do(&once, init_proc)' guarantees
	'init_proc' runs at most once and blocks concurrent callers until it completes.
	*/

	// Write a parameterless initializer at file scope with exact signature:
	// init_global_table :: proc()
	// Print a message confirming the lookup table initialized once.


	// Declare once: sync.Once and invoke sync.once_do(&once, init_global_table)
	// twice sequentially, then spawn 4 threads that all call
	// sync.once_do(&once_mt, init_global_table) concurrently on a fresh
	// sync.Once and verify the print fires exactly once.
}

main :: proc() {

	fmt.println("=== 1. Condition variables and predicate wait loops ===")
	condition_variables_and_predicates()

	fmt.println("\n=== 2. Lockstep phase barriers ===")
	phase_barriers_lockstep()

	fmt.println("\n=== 3. Counting semaphores and permit throttling ===")
	counting_semaphores_permits()

	fmt.println("\n=== 4. Thread-safe lazy initialization with sync.Once ===")
	one_time_init_with_once()
}
