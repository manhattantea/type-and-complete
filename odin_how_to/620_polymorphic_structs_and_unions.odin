// odin run 620_polymorphic_structs_and_unions.odin -file

package main

import "core:fmt"

/*
Polymorphic structs and unions let you parameterize data layouts at compile
time using '$T: typeid' and '$N: int', producing zero-overhead specialized
containers and tagged result types with no runtime type erasure.

When a procedure takes a pointer or value of a polymorphic container—such as
'rb: ^Ring_Buffer($N, $T)'—Odin extracts both N and T automatically from the
concrete struct passed by the caller.
*/

Box :: struct($T: typeid) {
	value: T,
}

Result :: union($T, $E: typeid) {
	T,
	E,
}

// Define a fixed-capacity generic ring buffer struct:
// Ring_Buffer :: struct($N: int, $T: typeid) { data: [N]T, read_idx: int, write_idx: int, count: int }
//
// Then write three procedures operating on it:
// ring_push :: proc(rb: ^Ring_Buffer($N, $T), item: T) -> bool
// ring_pop :: proc(rb: ^Ring_Buffer($N, $T)) -> (item: T, ok: bool)
// ring_is_full :: proc(rb: ^Ring_Buffer($N, $T)) -> bool
// In ring_push, return false if rb.count == N; otherwise write item at
// rb.data[rb.write_idx], wrap rb.write_idx = (rb.write_idx + 1) % N,
// increment rb.count, and return true. In ring_pop, return {}, false when
// rb.count == 0; otherwise read rb.data[rb.read_idx], wrap
// rb.read_idx = (rb.read_idx + 1) % N, decrement rb.count, and return item, true.
// In ring_is_full, return rb.count == N.

polymorphic_structs_and_ring_buffer :: proc() {

	/*
	Because Ring_Buffer embeds '[N]T' directly inside the struct, all N slots
	live inline in contiguous memory—no extra heap pointer indirection. Every
	instantiation such as Ring_Buffer(4, int) becomes its own concrete struct
	type whose size is known at compile time.

	    Suppose rb: Ring_Buffer(4, int) has 4 items pushed (10, 20, 30, 40):
	    rb.count reaches 4, so pushing 50 returns false without overwriting 10.
	    Popping 10 and 20 advances read_idx to 2 and drops count to 2, so two
	    more pushes wrap write_idx around modulo 4 into slots 0 and 1.
	*/

	anchor_box := Box(int){value = 42}
	fmt.printfln("Starter box: %v (size=%d)", anchor_box, size_of(anchor_box))

	// Instantiate rb: Ring_Buffer(4, int), push 10, 20, 30, 40, check
	// ring_is_full(&rb) is true, and confirm pushing a 5th value (50) returns false.


	// Pop two items from rb, push 50 and 60 to test modulo-4 wrap-around, then
	// pop all remaining items in a loop until ok == false and print each value
	// to verify FIFO order (30, 40, 50, 60).


	// Instantiate a second ring buffer of a different size and element type,
	// Ring_Buffer(3, string), push two messages, and pop one to verify both
	// Ring_Buffer(4, int) and Ring_Buffer(3, string) coexist cleanly.
}

// Define a dynamic-array-backed generic LIFO stack struct and its helpers:
// Stack :: struct($T: typeid) { items: [dynamic]T }
// stack_push :: proc(s: ^Stack($T), item: T)
// stack_pop :: proc(s: ^Stack($T)) -> (item: T, ok: bool)
// stack_peek :: proc(s: ^Stack($T)) -> (item: T, ok: bool)
// stack_destroy :: proc(s: ^Stack($T))
// In stack_push, call append(&s.items, item). In stack_pop, return {}, false
// when len(s.items) == 0, otherwise return pop(&s.items), true. In
// stack_peek, return {}, false when empty or s.items[len(s.items) - 1], true
// without removing the top item. In stack_destroy, call delete(s.items).

dynamic_generic_stack :: proc() {

	/*
	Notice how Stack($T: typeid) wraps Odin's built-in '[dynamic]T'. Zero
	initialization leaves 'items' empty and ready for append, and writing
	's: ^Stack($T)' in stack_push and stack_pop lets Odin infer T cleanly from
	whatever Stack(string) or Stack(f64) variable you pass.
	*/

	label_box := Box(string){value = "LIFO"}
	fmt.printfln("Container mode: %s", label_box.value)

	// Declare s: Stack(string) with defer stack_destroy(&s). Push "first",
	// "second", and "third" using stack_push.


	// Pop elements from s using stack_pop in a loop until ok == false and print
	// each popped string to verify LIFO order ("third", "second", "first").
}

// Write a generic unwrap helper for Result($T, $E):
// result_unwrap_or :: proc(res: Result($T, $E), fallback: T) -> T
// Switch on the union value using switch v in res: return v for case T, and
// return fallback for case E.

polymorphic_unions_and_result :: proc() {

	/*
	A polymorphic union like 'Result($T, $E)' stores a compact tag byte plus
	enough space for the larger of T or E—no heap allocation and no virtual
	methods. Note one important Odin rule: every variant inside a union must be
	a distinct type, because 'switch v in res' dispatches by type. That means
	Result(int, string) is valid, whereas Result(int, int) is rejected at
	compile time since Odin could not distinguish T from E.
	*/

	ok_status: Result(int, string) = 200
	switch v in ok_status {
	case int:
		fmt.printfln("Starter Result ok: %d", v)
	case string:
		fmt.printfln("Starter Result err: %s", v)
	}

	// Declare ok_val: Result(f32, string) = 3.14 and err_val: Result(f32, string) = "Division by zero".
	// Use switch v in ... on both values to print either the f32 result or the
	// string error message.


	// Test result_unwrap_or on both ok_val and err_val with fallback 0.0 and
	// print the returned f32 values.


	// Try uncommenting below to see Odin reject duplicate variant types in a
	// polymorphic union:
	// ambiguous: Result(int, int) = 7
	// fmt.println(ambiguous)
}

main :: proc() {

	fmt.println("=== 1. Polymorphic structs and Ring_Buffer ===")
	polymorphic_structs_and_ring_buffer()

	fmt.println("\n=== 2. Dynamic generic Stack ===")
	dynamic_generic_stack()

	fmt.println("\n=== 3. Polymorphic unions and Result ===")
	polymorphic_unions_and_result()
}
