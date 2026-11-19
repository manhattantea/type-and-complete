// odin run 000_tracy_mental_model_and_five_multipliers.odin -file

package main

import "base:intrinsics"
import "core:fmt"
import "core:time"

/*
Why start with a profiler instead of rewriting code right away? Because almost
every real program spends roughly 95% of its CPU time inside 5% of its code.
If a cold config loader takes 1% of your runtime, speeding it up 1,000x shrinks
total runtime by less than 1%. Measuring first keeps 95% of your program clean
and readable while aiming every optimization at code that actually matters.

Two kinds of profilers help you find that 5% hotspot:
Sampling profilers pause your threads on a timer (say 1,000 times per second)
to inspect call stacks. They need zero code edits, which makes them handy for
spotting surprise CPU hogs, yet they can miss rare single-frame hitches or
exact call counts.
Instrumentation profilers (such as Tracy and Spall) record explicit begin and
end timestamps around scopes you mark. In full Tracy builds (covered in 100),
your program acts as a Client reading the hardware timestamp counter in a few
nanoseconds, pushing events into a fixed per-thread ring buffer, and streaming
them over localhost TCP port 8086 to the Tracy profiler GUI.

In this first Primer we build that core clock and fixed ring buffer directly
in standalone Odin with zero external libraries.
*/

Zone_Event :: struct {
	name:        string,
	start_cycle: u64,
	end_cycle:   u64,
}

Zone_Ring_Buffer :: struct {
	events: [16]Zone_Event,
	count:  int,
}

/*
Why store Zone_Event records in a fixed-size [16]Zone_Event ring buffer instead
of appending to a [dynamic]Zone_Event? Because calling append inside a timed
zone can trigger a heap allocation or buffer resize right inside the measurement,
polluting your timing numbers.

When we compute slot := rb.count %% len(rb.events), Odin's floored modulo %%
wraps any count cleanly into 0..=15 without ever returning a negative index:

    Suppose rb.count is 16 and len(rb.events) is 16.
    16 %% 16 yields 0, so the 17th zone overwrites slot 0 with zero allocations.
*/

// Define begin_zone :: proc(rb: ^Zone_Ring_Buffer, name: string) -> int
// Inside it, compute slot := rb.count %% len(rb.events), increment
// rb.count += 1, store a Zone_Event with name and
// start_cycle = intrinsics.read_cycle_counter(), and return slot.


// Define end_zone :: proc(rb: ^Zone_Ring_Buffer, slot: int)
// Inside it, stamp rb.events[slot].end_cycle = intrinsics.read_cycle_counter().


timers_and_overhead :: proc() {

	/*
	Odin gives you two ways to measure elapsed time:
	- intrinsics.read_cycle_counter() emits a single CPU instruction (RDTSC on
	  x86_64, CNTVCT_EL0 on ARM64) that reads the hardware cycle counter in a few
	  cycles without leaving user space.
	- time.tick_now() calls the OS clock API (QueryPerformanceCounter on Windows
	  or clock_gettime on Linux), which is portable wall time in nanoseconds at a
	  higher per-call cost.

	Every timing probe still costs non-zero cycles. Suppose a tight loop body
	costs 5 cycles per pass and your begin_zone/end_zone pair costs 40 cycles.
	If you place zones inside every iteration, roughly 89% of the recorded time
	is the profiler measuring itself! Always wrap coarse stages outside tight
	inner loops.
	*/

	// Measure one back-to-back RDTSC read and one OS tick_now read, plus buffer size:

	c0 := intrinsics.read_cycle_counter()
	c1 := intrinsics.read_cycle_counter()

	t0 := time.tick_now()
	t1 := time.tick_now()
	tick_ns := time.duration_nanoseconds(time.tick_diff(t0, t1))

	rb_sample: Zone_Ring_Buffer
	fmt.printfln("RDTSC back-to-back: %v cycles | tick_now: %v ns | Ring: %v B (%v slots)",
		c1 - c0, tick_ns, size_of(rb_sample), len(rb_sample.events))

	// Compare average read cost across 1,000 back-to-back calls:
	// First read start := intrinsics.read_cycle_counter(), loop 0..<1000 calling
	// tmp := intrinsics.read_cycle_counter(), accumulate into a sink so the
	// optimizer cannot erase the loop, then compute average cycles per call.
	// Repeat with time.tick_now() across 1,000 iterations and print average ns.


	// See instrumentation distortion firsthand over 50,000 iterations:
	// First wrap ONE coarse zone around a loop summing i in 0..<50_000 into
	// clean_sum: u64 (measuring cycles with read_cycle_counter around the whole
	// loop). Next run the same 50,000-iteration sum while calling begin_zone and
	// end_zone inside every iteration on a local Zone_Ring_Buffer. Print both
	// cycle totals and both sums so the compiler keeps both loops alive.
}

ring_buffer_and_wraparound :: proc() {

	/*
	In live Tracy, a background thread drains the ring buffer over TCP before it
	fills up. In our standalone ring buffer, old slots stay in place until
	count exceeds len(rb.events) and wraps back around slot 0.

	    Suppose you record 20 zones named "z0" through "z19" into [16]Zone_Event.
	    Zones "z0".."z15" fill slots 0..=15. Zone "z16" wraps (16 %% 16 == 0)
	    and overwrites slot 0, "z17" overwrites slot 1, and so on—leaving
	    test_rb.count at 20 while slots 0..=3 hold the newest 4 zones and zero
	    heap memory was allocated.
	*/

	test_rb: Zone_Ring_Buffer
	fmt.printfln("Empty ring buffer: count=%v, slot_cap=%v", test_rb.count, len(test_rb.events))

	// Record 20 tiny zones into test_rb in a for i in 0..<20 loop using
	// begin_zone(&test_rb, fmt.tprintf("z%v", i)) and end_zone(&test_rb, slot)
	// (fmt.tprintf allocates the short label in Odin's temporary scratch
	// allocator; put a small arithmetic loop inside each zone so every cycle
	// delta is > 0). Print test_rb.count (expected: 20), then loop over
	// 0..<len(test_rb.events) and print each slot's name and cycle delta to
	// verify slots 0..=3 hold z16..z19 while slots 4..=15 hold z4..z15.
}

amdahl_pipeline_and_multipliers :: proc() {

	/*
	Once a profiler shows which zone owns most of your runtime, Amdahl's Law
	predicts the maximum total program speedup if you speed up fraction
	hot_fraction (0.0 to 1.0) by optimization factor:

	    speedup = 1.0 / ((1.0 - hot_fraction) + (hot_fraction / factor))

	Suppose a program spends 90% (0.90) in math and 10% (0.10) loading config.
	Speeding config loading up 100x gives 1.0 / (0.90 + 0.10/100) = 1.11x total.
	Speeding the 90% math loop up just 10x gives 1.0 / (0.10 + 0.90/10) = 5.26x!

	To turn a 90% hotspot faster, check which of Casey Muratori's Five
	Multipliers holds it back:
	- Waste: doing extra work, heap allocations, or formatting inside the loop.
	- IPC (Instructions Per Clock): stalling CPU execution ports on one serial
	  dependency chain like sum += x instead of independent accumulators.
	- SIMD: crunching 1 scalar value at a time instead of #simd vector lanes.
	- Caching: chasing pointers or bloated structs across scattered cache lines.
	- Multithreading: stalling cores behind locks or shared-cache-line writes.

	One warning when benchmarking with -o:speed: if a loop computes a value you
	never print or inspect afterward, the compiler's dead-code elimination (DCE)
	may delete the entire loop and report 0 cycles! Always print or consume a
	sink variable after the timed zone.
	*/

	cold_check: u64 = 0
	for i in 0..<100 {
		cold_check += u64(i)
	}
	fmt.printfln("Starter baseline cold sum (0..<100): %v", cold_check)

	// Define a local helper amdahl_speedup :: proc(hot_fraction: f64, factor: f64) -> f64
	// Assert hot_fraction >= 0.0 && hot_fraction <= 1.0 && factor > 0.0, then
	// return 1.0 / ((1.0 - hot_fraction) + (hot_fraction / factor)).


	// Instrument a 3-stage pipeline in a fresh pipe_rb: Zone_Ring_Buffer:
	// - "cold_init": sum 0..<100 inside begin_zone/end_zone.
	// - "hot_serial_loop": loop i in 0..<4_000_000 updating a dependent chain:
	//   acc = (acc * 3 + u64(i)) ~ (acc >> 2)
	// - "cold_report": sum 0..<100 inside begin_zone/end_zone.
	// Print acc so -o:speed keeps the hot loop alive, print each zone's cycles
	// and percentage share, then compare amdahl_speedup(hot_frac, 4.0) against
	// amdahl_speedup(cold_frac, 100.0) using your measured fractions.


	// Verify a real post-fix trace (Multiplier #2 — IPC):
	// Notice why "hot_serial_loop" stalls: every iteration waits on the prior
	// iteration's acc before computing the next one. Break that single serial
	// chain into 4 independent accumulators (s0, s1, s2, s3) stepping by 4 in a
	// C-style loop (for i := 0; i < 4_000_000; i += 4) inside a new zone
	// "hot_unrolled_loop" on pipe_rb, combine s0 + s1 + s2 + s3 into a printed
	// sink, and compare the measured hot_serial_loop / hot_unrolled_loop speedup
	// (run with -o:speed to see the full CPU IPC difference!).
}

main :: proc() {

	fmt.println("=== 1. Hardware timers and profiler distortion ===")
	timers_and_overhead()

	fmt.println("\n=== 2. Fixed ring buffer and wraparound ===")
	ring_buffer_and_wraparound()

	fmt.println("\n=== 3. Amdahl's Law, the Five Multipliers, and post-fix traces ===")
	amdahl_pipeline_and_multipliers()
}
