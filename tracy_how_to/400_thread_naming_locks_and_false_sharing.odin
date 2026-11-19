// odin run 400_thread_naming_locks_and_false_sharing.odin -file

package main

import "base:intrinsics"
import "core:fmt"
import "core:sync"
import "core:thread"

/*
Spawning four worker threads does not automatically give you a 4x speedup. On a
multi-core CPU, two hardware and OS bottlenecks routinely turn parallel code into
a serialized crawl: lock contention and false sharing across 64-byte cache lines.

Before measuring either bottleneck on a timeline, you need readable thread tracks.
Tracy displays raw OS thread IDs unless each worker calls ___tracy_set_thread_name
at startup. Notice a critical pointer lifetime rule: Tracy reads the passed
cstring asynchronously after the worker moves on, so passing a temporary string
built with fmt.ctprintf (which lives in context.temp_allocator) creates a
use-after-free hazard the moment temp memory resets or the thread exits. Always
pass compile-time string literals or static table entries such as WORKER_NAMES
pinned for the lifetime of the process.
*/

TRACY_ENABLE :: #config(TRACY_ENABLE, false)
CACHE_LINE_BYTES :: 64

when TRACY_ENABLE {
	when ODIN_OS == .Windows {
		foreign import tracy "TracyClient.lib"
	} else {
		foreign import tracy "system:TracyClient"
	}

	foreign tracy {
		___tracy_set_thread_name :: proc "c" (name: cstring) ---
	}
}

WORKER_NAMES := [4]cstring{"Worker_0", "Worker_1", "Worker_2", "Worker_3"}

Padded_Slot :: struct #align(64) {
	value: i64,
}

Lock_Metrics :: struct {
	wait_cycles: u64,
	hold_cycles: u64,
}

Timed_Mutex_Guard :: struct {
	mu:          ^sync.Mutex,
	metrics:     ^Lock_Metrics,
	acquired_at: u64,
}

Thread_Span :: struct {
	worker_name: cstring,
	start_cycle: u64,
	end_cycle:   u64,
}

False_Share_Mode :: enum {
	Unaligned_Shared_Line,
	Padded_64B_Slots,
	Thread_Local_Register,
}

False_Share_Worker_Ctx :: struct {
	worker_id:  int,
	iterations: int,
	mode:       False_Share_Mode,
	bad_slots:  ^[4]i64,
	good_slots: ^[4]Padded_Slot,
	spans:      ^[4]Thread_Span,
	wg:         ^sync.Wait_Group,
}

// Define tracy_set_thread_name :: proc(name: cstring)
// Inside when TRACY_ENABLE, call ___tracy_set_thread_name(name). In the else
// branch, validate len(name) > 0 (or store it in a standalone trace table)
// without leaving an unused parameter or dummy silencer.


// Define tracy_mutex_release :: proc(g: Timed_Mutex_Guard)
// Measure t2 := intrinsics.read_cycle_counter(), add (t2 - g.acquired_at) to
// g.metrics.hold_cycles BEFORE calling sync.unlock(g.mu) so the update to
// g.metrics stays protected inside the critical section with zero data races!


// Define @(deferred_out = tracy_mutex_release) tracy_mutex_acquire :: proc(mu: ^sync.Mutex, metrics: ^Lock_Metrics) -> Timed_Mutex_Guard
// When we attach @(deferred_out = tracy_mutex_release) to a procedure, Odin runs
// tracy_mutex_release(returned_guard) automatically at the end of the caller's
// scope, just like RAII in C++. Read t0 := intrinsics.read_cycle_counter(), call
// sync.lock(mu), read t1 := intrinsics.read_cycle_counter(), add (t1 - t0) to
// metrics.wait_cycles (now safely under mu), and return
// Timed_Mutex_Guard{mu = mu, metrics = metrics, acquired_at = t1}.


// Define false_share_worker :: proc(ctx: ^False_Share_Worker_Ctx)
// Register defer sync.wait_group_done(ctx.wg), set the thread name using the
// persistent WORKER_NAMES[ctx.worker_id] literal (never fmt.ctprintf), record
// start := intrinsics.read_cycle_counter(), and run ctx.iterations passes:
// - .Unaligned_Shared_Line: update ctx.bad_slots[ctx.worker_id] directly every pass.
// - .Padded_64B_Slots: update ctx.good_slots[ctx.worker_id].value directly every pass.
// - .Thread_Local_Register: accumulate into local_count: i64 in a CPU register
//   and write ctx.good_slots[ctx.worker_id].value = local_count once after the loop.
// Record end := intrinsics.read_cycle_counter() and store
// Thread_Span{worker_name = WORKER_NAMES[ctx.worker_id], start_cycle = start, end_cycle = end}
// into ctx.spans[ctx.worker_id].
// Note: under -o:speed, the compiler may hoist repeated writes to a plain field
// into a register; using intrinsics.volatile_load / intrinsics.volatile_store on
// the shared slot forces real cache-line traffic even when optimizing.


thread_naming_and_timeline_spans :: proc() {

	/*
	On a Tracy timeline, parallel work looks like stacked overlapping horizontal
	bars across Worker_0..Worker_3, whereas serialized work looks like a staircase
	where only one bar is active at any cycle. Recording each thread's start_cycle
	and end_cycle relative to origin_cycle lets us compute the overlap ratio
	(sum of worker durations divided by total wall span): an ideal 4-thread
	parallel batch approaches 4.0x, while a serialized batch stays near 1.0x.
	*/

	span_bytes := size_of(Thread_Span)
	fmt.printfln("Persistent thread name[0]=%s | Thread_Span=%v B | thread.Thread=%v B",
		WORKER_NAMES[0], span_bytes, size_of(thread.Thread))

	// Spawn 4 worker threads with thread.create_and_start_with_poly_data (or
	// thread.create_and_start_with_data), passing each worker its index 0..=3, a
	// shared ^sync.Wait_Group, and a ^[4]Thread_Span array. Have each worker call
	// tracy_set_thread_name(WORKER_NAMES[id]), run a pure local arithmetic loop of
	// 5_000_000 iterations, and stamp its [start_cycle, end_cycle] span.
	// Wait via sync.wait_group_wait(&wg), clean up threads with thread.destroy,
	// print each worker's [start - origin, end - origin] cycle range, and verify
	// overlap_ratio := f64(sum_worker_cycles) / f64(max_end - min_start) > 1.5.
}

mutex_contention_and_local_merge :: proc() {

	/*
	When multiple cores acquire one sync.Mutex inside a tight loop, every thread
	stalls waiting for ownership while the OS parks and wakes threads. Splitting
	every lock acquisition into wait_cycles (time blocked inside sync.lock) and
	hold_cycles (time inside the critical section) exposes whether contention is
	starving your workers.

	    Suppose 4 workers each run 25,000 updates.
	    Lock-in-loop: 100,000 lock acquisitions -> huge wait_cycles and serialized cores.
	    Thread-local merge: each worker accumulates local_sum in a register and
	    acquires the mutex once at the end -> 4 lock acquisitions total, wait_cycles -> 0!
	*/

	mu: sync.Mutex
	c0 := intrinsics.read_cycle_counter()
	sync.lock(&mu)
	sync.unlock(&mu)
	c1 := intrinsics.read_cycle_counter()
	fmt.printfln("Uncontended mutex probe: %v cycles", c1 - c0)

	// Measure lock-in-loop contention: spawn 4 workers sharing one sync.Mutex,
	// shared_counter: i64, and metrics: Lock_Metrics. Inside each worker loop of
	// 25_000 iterations, open a scoped block { guard := tracy_mutex_acquire(&mu, &metrics); shared_counter += 1 }
	// (using @(deferred_out = tracy_mutex_release) so the lock releases at the
	// brace). Wait for all 4 workers, assert shared_counter == 100_000, and print
	// metrics.wait_cycles vs metrics.hold_cycles.


	// Remediate with thread-local reduction + single merge: run 4 workers on the
	// same 25_000-iteration count, accumulating local_sum: i64 += 1 in a local
	// variable and calling tracy_mutex_acquire(&mu, &fixed_metrics) ONCE after the
	// loop to add local_sum to shared_counter. Assert shared_counter == 100_000
	// and print fixed_metrics.wait_cycles alongside the speedup over lock-in-loop.
}

three_way_false_sharing_lab :: proc() {

	/*
	Even with zero locks, four threads writing to adjacent memory addresses can
	still fight each other in hardware. CPUs enforce cache coherency in 64-byte
	cache lines using the MESI protocol (Modified, Exclusive, Shared, Invalid).

	    Suppose bad_slots is [4]i64 (32 bytes total). Slots 0, 1, 2, and 3 sit on
	    the exact same 64-byte cache line. When Worker_0 writes bad_slots[0], its
	    core marks that line Modified and broadcasts Invalidate to Cores 1, 2, and 3.
	    The moment Worker_1 writes bad_slots[1], its L1 cache misses and stalls to
	    fetch the updated line from Core 0, invalidating Core 0 right back!

	Adding #align(64) on Padded_Slot :: struct #align(64) { value: i64 } tells Odin
	to align every element to a 64-byte boundary (padding each slot to 64 bytes),
	giving each worker its own isolated cache line. Even better, keeping the loop
	counter in a CPU register (.Thread_Local_Register) eliminates shared-memory
	writes inside the hot loop altogether.
	*/

	fmt.printfln(
		"Cache-line layout (%v B line): [4]i64=%v B (1 line) vs [4]Padded_Slot=%v B (align=%v)",
		CACHE_LINE_BYTES,
		size_of([4]i64),
		size_of([4]Padded_Slot),
		align_of(Padded_Slot),
	)

	// Run the 3-way false-sharing comparison across 4 workers with iterations = 2_000_000:
	// - Run 1 (.Unaligned_Shared_Line): all 4 workers write to bad_slots: [4]i64.
	// - Run 2 (.Padded_64B_Slots): all 4 workers write to good_slots: [4]Padded_Slot.
	// - Run 3 (.Thread_Local_Register): all 4 workers accumulate in a register and
	//   store once into good_slots[id].value at exit.
	// Assert all three runs sum to 4 * 2_000_000, print wall cycles and per-worker
	// Thread_Span bounds for each mode, and compare the Unaligned -> Padded -> Register
	// cycle speedups!
}

main :: proc() {

	fmt.println("=== 1. Persistent thread naming and timeline spans ===")
	thread_naming_and_timeline_spans()

	fmt.println("\n=== 2. Mutex wait/hold contention vs. thread-local merge ===")
	mutex_contention_and_local_merge()

	fmt.println("\n=== 3. Three-way false sharing (unaligned vs. #align(64) vs. register) ===")
	three_way_false_sharing_lab()
}
