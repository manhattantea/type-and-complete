// odin run 595_profiling_with_spall.odin -file

package main

import "core:fmt"
import "core:os"
import "core:prof/spall"

/*
Before optimizing any procedure, follow the Hotspot-First Rule: measure with a
real profiler trace first so you fix the 5% of code burning 95% of your time
rather than polishing cold setup code.

Odin ships with first-party support for Spall (core:prof/spall), an offline
binary tracing profiler that records function timelines with sub-10-nanosecond
overhead per event. Instead of hitting the OS filesystem on every scope entry,
Spall writes timestamps into a caller-owned byte buffer (spall.Buffer) and
flushes large blocks to a .spall file via spall.Context. You can open the
resulting file in Spall or move up to live client-server timeline streaming,
memory pools, and lock forensics in 596, 598, 599, and ../tracy_how_to/.
*/

// Define instrumented helper procedures right here at file scope once you
// reach the first section:
// heavy_step :: proc(ctx: ^spall.Context, buf: ^spall.Buffer) -> u64
// Place spall.SCOPED_EVENT(ctx, buf, #procedure) as its first statement, then
// sum 0..<100_000 into an accumulator and return it so -o:speed keeps the loop.
// outer_step :: proc(ctx: ^spall.Context, buf: ^spall.Buffer) -> u64
// Place spall.SCOPED_EVENT(ctx, buf, #procedure) at the top and call heavy_step
// inside it.

hotspot_first_and_spall_architecture :: proc() {

	/*
	How does spall.SCOPED_EVENT(&spall_ctx, &spall_buf, #procedure) work with
	so little overhead? Under the hood, Spall marks its begin procedure with
	Odin's @(deferred_in_out) attribute. That tells the compiler to insert a
	hidden defer calling the matching end procedure at every exit of the
	enclosing block—automatically recording both entry and exit hardware
	timestamps on normal fallthrough and early returns alike.

	Passing #procedure as the name hands Spall a compile-time constant string
	naming the enclosing procedure (zero runtime formatting or allocation).
	*/

	fmt.printfln("Spall ready (ctx=%d B, buf=%d B, trace_exists=%v)",
		size_of(spall.Context), size_of(spall.Buffer), os.exists("trace.spall"))

	// After defining heavy_step and outer_step at file scope above, confirm why
	// returning the accumulated u64 prevents LLVM's dead-code elimination from
	// deleting the benchmark loop when compiling with -o:speed.
}

recording_nested_spall_events :: proc() {

	/*
	Pay close attention to LIFO defer order when setting up a Spall trace.
	A spall.Buffer holds unflushed events destined for spall.Context, and
	spall.Context holds the open output file handle. That means teardown must
	run in exact reverse order:
	flush and destroy buffer -> close and destroy context -> remove temp file.

	    Suppose you register defers in top-to-bottom order:
	        defer os.remove(trace_path)                     // runs 3rd (last!)
	        defer spall.context_destroy(&spall_ctx)         // runs 2nd
	        defer spall.buffer_destroy(&spall_ctx, &spall_buf) // runs 1st

	Because Odin executes defers in reverse declaration order (LIFO), the
	buffer flushes cleanly before the file closes, and os.remove runs only
	after the file handle is released (critical on Windows!).

	When outer_step calls heavy_step while both use spall.SCOPED_EVENT, Spall
	nests heavy_step cleanly inside outer_step's timeline bar so you can see
	inclusive time vs child time at a glance.
	*/

	trace_path := "trace.spall"
	fmt.printfln("Target Spall trace path: %s", trace_path)

	// Create the Spall context and check its boolean result:
	// spall_ctx, ctx_ok := spall.context_create(trace_path)
	// If !ctx_ok, print an error and return. Immediately register
	// defer os.remove(trace_path) and then defer spall.context_destroy(&spall_ctx).


	// Allocate a 64 KB stack backing buffer: backing: [64 * 1024]u8
	// Create the Spall buffer with:
	// spall_buf, buf_ok := spall.buffer_create(backing[:], 0)
	// Check !buf_ok and register defer spall.buffer_destroy(&spall_ctx, &spall_buf).


	// Open a nested { ... } scope, record spall.SCOPED_EVENT(&spall_ctx, &spall_buf, #procedure),
	// call outer_step(&spall_ctx, &spall_buf) twice, accumulate the returned
	// sums into a printed total, and call spall.buffer_flush(&spall_ctx, &spall_buf).
}

trace_hygiene_and_next_steps :: proc() {

	/*
	One instrumentation trap catches almost everyone on their first trace:
	putting spall.SCOPED_EVENT inside a tight inner loop that runs 100,000
	times. Even at ~5 ns per event, 100,000 inner events add ~1 MB of trace
	traffic and distort a fast arithmetic loop so it looks slower than it is.
	Wrap coarse pipeline stages, never per-element inner loops.

	Offline .spall files excel at single-run flame graphs. When you need live
	TCP streaming, named memory pools, thread lock contention timelines, or
	multi-frame budgets, step onward to 596, 598, 599, and ../tracy_how_to/.
	*/

	fmt.printfln("Leftover trace.spall after cleanup: %v", os.exists("trace.spall"))

	// Add a second helper cold_step :: proc(ctx: ^spall.Context, buf: ^spall.Buffer) -> u64
	// with only 100 iterations, call both cold_step and heavy_step inside a
	// fresh trace block, and verify cold_step's span is negligible compared to
	// heavy_step—illustrating why the Hotspot-First Rule ignores cold code.
}

main :: proc() {

	fmt.println("=== 1. Hotspot-first rule and Spall architecture ===")
	hotspot_first_and_spall_architecture()

	fmt.println("\n=== 2. Recording nested Spall events ===")
	recording_nested_spall_events()

	fmt.println("\n=== 3. Trace hygiene and next steps ===")
	trace_hygiene_and_next_steps()
}
