// odin run 810_calling_conventions_and_c_callbacks.odin -file

package main

import "base:runtime"
import "core:c"
import "core:c/libc"
import "core:fmt"

/*
Every Odin procedure has a calling convention that controls how arguments move
across CPU registers and the stack, and whether Odin passes its hidden context
pointer.

By default, every procedure uses the "odin" calling convention, which silently
passes a pointer to the caller's 'context' (carrying context.allocator,
context.temp_allocator, context.logger, and user_index / user_ptr).

By contrast, 'proc "contextless"' follows Odin's native ABI while omitting the
hidden context pointer, which is ideal for pure leaf math helpers. Meanwhile,
'proc "c"' matches the platform C ABI (System V on POSIX, MS x64 on Windows)
and also receives NO context pointer. Other specialized conventions include
"stdcall" (legacy 32-bit Win32), "fastcall", and "system" (stdcall on x86
Windows, C ABI elsewhere).

Because foreign C code knows nothing about Odin's context, calling fmt.println,
make, or log.info inside a 'proc "c"' without setting 'context' first will
not compile (or would crash if unchecked). Always restore it at the top of a
C callback using either:
    context = runtime.default_context()
or, when C passes your context back through a void* user_data pointer:
    context = (^runtime.Context)(user_data)^
*/

clamp_i32 :: proc "contextless" (val, lo, hi: i32) -> i32 {

	if val < lo do return lo
	if val > hi do return hi
	return val
}

compare_ints_c :: proc "c" (a, b: rawptr) -> c.int {

	context = runtime.default_context()
	va := (^int)(a)^
	vb := (^int)(b)^
	if va < vb do return -1
	if va > vb do return 1
	return 0
}

simulate_c_dispatch :: proc "c" (count: c.int, cb: proc "c" (val: c.int, user_data: rawptr), user_data: rawptr) {

	for i in 0..<count {
		cb((i + 1) * 10, user_data)
	}
}

on_tick_c :: proc "c" (val: c.int, user_data: rawptr) {

	context = (^runtime.Context)(user_data)^
	fmt.printfln("  [c callback] val=%d, restored user_index=%d", val, context.user_index)
}

calling_conventions_and_contextless :: proc() {

	/*
	When we mark a procedure 'proc "contextless"', we tell the compiler it
	neither needs nor receives Odin's hidden context argument. Pure arithmetic,
	bit manipulation, and array indexing work seamlessly inside it, whereas
	anything that allocates, logs, or formats via context is rejected at
	compile time.

	Suppose you call clamp_i32(150, 0, 100) from main: no context pointer is
	pushed or moved into a register, and you get 100 back directly.
	*/

	clamped := clamp_i32(150, 0, 100)
	fmt.printfln("Contextless clamp_i32(150, 0, 100) = %d", clamped)

	// Write a pure contextless helper outside this procedure:
	// sum_pair_contextless :: proc "contextless" (a, b: i64) -> i64
	// Call it with (120, 30) and print the result here.


	// Try adding fmt.println("inside") temporarily inside clamp_i32 above to
	// observe why Odin rejects context-dependent calls inside "contextless"
	// procedures at compile time.
}

c_callbacks_with_qsort :: proc() {

	/*
	C libraries like libc.qsort accept function pointers shaped like:
	    compar: proc "c" (a, b: rawptr) -> c.int
	Notice how compare_ints_c above starts with 'context = runtime.default_context()'.
	Suppose numbers holds [6]int{42, 13, 88, 7, 25, 60}. Passing &numbers[0],
	len(numbers), size_of(int), and compare_ints_c into libc.qsort sorts the
	array in place to {7, 13, 25, 42, 60, 88}.
	*/

	numbers := [6]int{42, 13, 88, 7, 25, 60}
	fmt.printfln("Before qsort: %v", numbers)
	libc.qsort(&numbers[0], len(numbers), size_of(int), compare_ints_c)
	fmt.printfln("After qsort:  %v", numbers)

	// Try adding a fmt.printfln trace line inside compare_ints_c (safe because
	// context was restored), then try commenting out context = runtime.default_context()
	// to see the compile error when a "c" callback uses fmt without context.


	// Write a second comparator outside this procedure:
	// compare_ints_desc_c :: proc "c" (a, b: rawptr) -> c.int
	// Restore context = runtime.default_context(), sort a fresh [5]int array
	// in descending order with libc.qsort, and print the result.


	// Define a tiny struct Item :: struct { id: int, priority: int }, write a
	// comparator compare_items_c :: proc "c" (a, b: rawptr) -> c.int sorting by
	// priority ascending, and sort a [3]Item array with libc.qsort.
}

restoring_context_from_user_data :: proc() {

	/*
	Using runtime.default_context() gives a C callback the default heap
	allocator and logger, which drops any custom arena, tracking allocator,
	or user_index active in the caller.

	Real C APIs (GLFW, SDL, SQLite, Win32) solve this by accepting an opaque
	void* argument called user_data alongside the callback and forwarding it
	back on every invocation. Suppose a caller sets context.user_index = 77 and
	passes rawptr(&context) as user_data. Inside the 'proc "c"' callback:
	    context = (^runtime.Context)(user_data)^
	rehydrates the exact caller context on the stack before calling Odin code.
	*/

	local_ctx := context
	local_ctx.user_index = 77
	simulate_c_dispatch(2, on_tick_c, &local_ctx)

	// Write a real C callback outside this procedure:
	// on_filtered_event_c :: proc "c" (val: c.int, user_data: rawptr)
	// Define a struct Callback_State :: struct { ctx: runtime.Context, items: [dynamic]int }
	// Inside on_filtered_event_c, restore context = state.ctx (after casting
	// state := (^Callback_State)(user_data)), append val if val >= 20 into
	// state.items, and invoke simulate_c_dispatch(4, on_filtered_event_c, &state).
	// Remember defer delete(state.items) and print the collected items!
}

main :: proc() {

	fmt.println("=== 1. Calling conventions and contextless ===")
	calling_conventions_and_contextless()

	fmt.println("\n=== 2. C callbacks with libc.qsort ===")
	c_callbacks_with_qsort()

	fmt.println("\n=== 3. Restoring caller context via user_data ===")
	restoring_context_from_user_data()
}
