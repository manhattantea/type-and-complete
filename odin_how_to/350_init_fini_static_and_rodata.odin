// odin run 350_init_fini_static_and_rodata.odin -file

package main

import "core:fmt"

/*
Odin gives you explicit attributes to control when setup/teardown hooks run
and which memory segment holds persistent or constant data:

    @(init)             procedure runs automatically before main
    @(fini)             procedure runs automatically after main returns
    @(priority_index=N) sets ordering across @(init) or @(fini) hooks
    @(static)           local variable stored in static memory across calls
    @(rodata)           array or table placed in read-only .rodata with a real address
    @(cold)             tells the optimizer a procedure is rarely taken
    @(deprecated="msg") emits a compile-time warning whenever called

Unlike C++ global constructors that can fire in unpredictable order across
translation units, @(priority_index=N) gives you explicit startup sequencing.
*/

// Starter read-only lookup table stored in .rodata so &SIN_TABLE[i] is valid:

@(rodata)
SIN_TABLE := [4]f32{0.0, 0.7071, 1.0, 0.7071}

// Define three @(init) hooks with explicit @(priority_index=N) ordering,
// such as @(init) @(priority_index=-10) init_early :: proc(),
// @(init) @(priority_index=1) init_memory :: proc(), and
// @(init) @(priority_index=2) init_audio :: proc(), each printing a banner
// so you can verify lower priority_index values run first before main.


// Define two @(fini) hooks with @(priority_index=1) and @(priority_index=2)
// (for example fini_audio and fini_memory) that print shutdown messages after
// main exits, and run the program to verify their exact teardown order.


init_and_fini_lifecycle :: proc() {

	/*
	Suppose a subsystem needs logging initialized before the audio mixer starts.
	Attaching @(init) @(priority_index=1) to init_logger and @(init)
	@(priority_index=2) to init_mixer guarantees init_logger finishes before
	init_mixer runs, and both finish before main begins. Hooks without an
	explicit priority_index default to priority 0, so negative values like -10
	run even earlier.

	Because fmt.println uses Odin's implicit context, use regular proc() for
	hooks that print. If an @(init) hook needs zero runtime context setup,
	you can mark it proc "contextless" ().
	*/

	fmt.println("Inside main lifecycle: @(init) hooks already ran before main started.")

	// Once you define the @(init) and @(fini) hooks above, run this Primer and
	// verify the console shows: init hooks (-10, 1, 2) -> main -> fini hooks.
}

static_local_state :: proc() {

	/*
	A normal local variable lives on the stack and vanishes as soon as its
	procedure returns. Putting @(static) on a local variable moves it into
	static program memory (like a file-scope variable), so it initializes once
	and keeps its value across calls while staying invisible to other procs:

	    Suppose next_ticket :: proc() -> int has @(static) ticket: int = 100:
	        first call  -> increments ticket to 101, returns 101
	        second call -> increments ticket to 102, returns 102
	*/

	fmt.println("Define next_id and bounded_tick using @(static) locals to persist state.")

	// Define next_id :: proc() -> int above main with a local
	// @(static) counter: int = 0 that increments counter += 1 and returns
	// counter. Call next_id() three times here to verify it prints 1, 2, 3.


	// Define bounded_tick :: proc(limit: int) -> int with @(static) tick: int = 0
	// that advances tick = (tick + 1) % limit and returns it, then call it
	// five times with limit = 3 to observe 1, 2, 0, 1, 2.


	// Write a one-time setup helper ensure_booted :: proc() using a local
	// @(static) booted: bool = false that prints a message only on the very
	// first call, then sets booted = true. Call it twice to prove it runs once.
}

rodata_and_attributes :: proc() {

	/*
	An untyped constant array or scalar lives only in the compiler and has no
	memory address (taking &MY_CONST is an error). Suppose you keep a 4-entry
	sine lookup table and want to pass pointers to its elements into a DSP
	routine without letting callers overwrite the table: marking the global
	with @(rodata) places its bytes in the OS read-only .rodata segment so
	&SIN_TABLE[2] works while hardware page protection guards against writes.
	*/

	// Here is a live check taking a pointer into the @(rodata) lookup table:

	peak_ptr := &SIN_TABLE[2]
	fmt.printfln("SIN_TABLE[2] = %.4f at rodata address %p", peak_ptr^, peak_ptr)

	// Declare another read-only table @(rodata) LUT_SQUARES := [5]int{0, 1, 4, 9, 16}
	// at file scope, take &LUT_SQUARES[3], and print its value and pointer.


	// Define @(cold) @(deprecated="use new_handler instead") legacy_handler :: proc()
	// above main that prints a legacy warning, then try calling legacy_handler()
	// here to observe the compiler's deprecation warning message.
}

main :: proc() {

	fmt.println("=== 1. @(init), @(fini), and @(priority_index) lifecycle ===")
	init_and_fini_lifecycle()

	fmt.println("\n=== 2. @(static) local state ===")
	static_local_state()

	fmt.println("\n=== 3. @(rodata), @(cold), and @(deprecated) ===")
	rodata_and_attributes()
}
