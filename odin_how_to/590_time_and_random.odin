// odin run 590_time_and_random.odin -file

package main

import "core:fmt"
import "core:math/rand"
import "core:time"

/*
Games, simulations, and benchmarks depend on two things behaving reliably: a
clock that never jumps backward, and random numbers you can replay on demand.

Odin's core:time separates wall-clock calendar time (which can jump backward if
NTP or daylight savings adjusts the OS clock) from monotonic hardware ticks
(time.tick_now and time.Stopwatch), which strictly count forward for measuring
durations. Meanwhile, core:math/rand routes random calls through
context.random_generator so you can swap in a seeded local state whenever you
want reproducible results without polluting global state.
*/

monotonic_ticks_and_stopwatches :: proc() {

	/*
	Calling time.tick_now() reads the OS high-resolution monotonic timer and
	returns a time.Tick timestamp. Subtracting two ticks with
	time.tick_since(start) or time.tick_diff(start, end) produces a
	time.Duration (an integer count of nanoseconds under the hood), which you
	convert to floating-point units with time.duration_microseconds(d) or
	time.duration_milliseconds(d).

	When you want to time multiple separate bursts while pausing between them,
	use time.Stopwatch instead of raw Tick variables:

	    Suppose sw: time.Stopwatch starts at zero:
	        time.stopwatch_start(&sw)
	        // work burst A (accumulated)
	        time.stopwatch_stop(&sw)
	        // unmeasured setup gap (ignored)
	        time.stopwatch_start(&sw)
	        // work burst B (added onto burst A)
	        time.stopwatch_stop(&sw)

	Calling time.stopwatch_duration(sw) returns the combined Duration across
	both active intervals, and time.stopwatch_reset(&sw) clears it back to 0.
	*/

	boot_tick := time.tick_now()
	elapsed_us := time.duration_microseconds(time.tick_since(boot_tick))
	fmt.printfln("Monotonic tick probe: %.2f us", elapsed_us)

	// Declare sw: time.Stopwatch, start it with time.stopwatch_start(&sw), run a
	// loop accumulating 0..<100_000 into total: u64, stop with
	// time.stopwatch_stop(&sw), and print total alongside both
	// time.duration_microseconds(time.stopwatch_duration(sw)) and
	// time.duration_milliseconds(time.stopwatch_duration(sw)).


	// Test pause/resume accumulation: start sw again, run a second 100,000-step
	// loop, stop sw, sleep 2 * time.Millisecond outside the stopwatch, and
	// confirm stopwatch_duration(sw) excluded the sleep. Reset with
	// time.stopwatch_reset(&sw) afterward and verify duration == 0.
}

explicit_random_state_and_context :: proc() {

	/*
	In C, rand() pulls from a single global seed shared by the whole program, so
	one stray call in an unrelated module shifts every subsequent number. Odin
	avoids that by storing the active PRNG inside context.random_generator.

	When we write state := rand.create(1337) and bind it via
	context.random_generator = rand.default_random_generator(&state), it means
	every rand.* call in this scope (and any procedure called from it) pulls
	deterministically from our stack-allocated Default_Random_State instead of
	shared global state!

	    Suppose two procedures both seed state := rand.create(1337):
	    Calling rand.int_max(100) three times produces the exact same three
	    integers on every run and every machine, even if another thread is
	    generating random numbers concurrently.

	You can also pass a generator directly as the trailing gen argument to any
	rand.* procedure (such as rand.int_max(100, my_gen)) to keep two independent
	streams side by side without modifying context.random_generator.
	*/

	d6_roll := rand.int_max(6) + 1
	fmt.printfln("Default generator d6 roll: %d", d6_roll)

	// Save the outer generator with prev_gen := context.random_generator and
	// defer context.random_generator = prev_gen. Then create an explicit state:
	// state: rand.Default_Random_State = rand.create(1337)
	// Assign context.random_generator = rand.default_random_generator(&state)
	// and print 3 integers from rand.int_max(100) plus 1 float from
	// rand.float32_range(10.0, 25.0).


	// Verify deterministic replay without modifying context.random_generator:
	// declare replay := rand.create(1337), capture replay_gen := rand.default_random_generator(&replay),
	// and call rand.int_max(100, replay_gen) three times to confirm the output
	// matches your seeded sequence identically.
}

shuffling_and_scoped_replay :: proc() {

	/*
	Shuffling a slice in place with rand.shuffle(slice) runs a Fisher-Yates
	swap across indices from back to front in O(n) time and zero heap
	allocations. Because rand.shuffle defaults to gen := context.random_generator,
	combining it with a seeded Default_Random_State makes card decks, spawn
	orders, and randomized unit tests completely reproducible.
	*/

	sample_vals := [4]int{10, 20, 30, 40}
	fmt.printfln("Unshuffled sample array: %v", sample_vals)

	// Declare deck := [5]int{1, 2, 3, 4, 5}, shuffle deck[:] in place using
	// rand.shuffle(deck[:]), and print the shuffled array.


	// Test scoped replay: open two { ... } blocks that each initialize a fresh
	// Default_Random_State with seed 42 and shuffle separate copies of
	// [6]int{1, 2, 3, 4, 5, 6} via rand.default_random_generator(&local_state).
	// Assert that both shuffled copies end up equal element for element.
}

main :: proc() {

	fmt.println("=== 1. Monotonic ticks and stopwatches ===")
	monotonic_ticks_and_stopwatches()

	fmt.println("\n=== 2. Explicit random state and context ===")
	explicit_random_state_and_context()

	fmt.println("\n=== 3. Shuffling and scoped replay ===")
	shuffling_and_scoped_replay()
}
