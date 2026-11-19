// odin run 600_explicit_parametric_polymorphism.odin -file

package main

import "core:fmt"

/*
Parametric polymorphism—often called generics or "parapoly" in Odin—lets you
write a single procedure or data structure that works across many types without
copy-pasting code or wrapping values in heap-allocated interface boxes.

When we put a dollar sign '$' in front of a parameter name, it means "this
argument must be known at compile time". Writing '$T: typeid' asks the caller
to pass an actual type (such as int, f32, or string) just like a value, and
writing '$N: int' asks for a compile-time integer constant. Every distinct
combination of compile-time arguments causes Odin to monomorphize—generate and
typecheck—a dedicated machine-code procedure tailored to those exact types and
sizes, with zero runtime dispatch cost.
*/

make_pair :: proc($T: typeid, a, b: T) -> [2]T {

	return {a, b}
}

// Write a generic procedure named first_or_default that accepts an explicit
// type parameter and returns the first element of a slice or a fallback value:
// first_or_default :: proc($T: typeid, items: []T, fallback: T) -> T
// Return fallback when len(items) == 0, otherwise return items[0].

explicit_type_parameters :: proc() {

	/*
	Look at make_pair above. Inside the body, T behaves like any concrete type:
	you can declare locals of type T, build compound types like [2]T, and
	enforce that both a and b share the exact same type T.

	    Suppose you call make_pair(int, 10, 20):
	    Odin stamps out a concrete procedure taking (a, b: int) -> [2]int,
	    returning [10, 20] on the stack with no heap allocation at all.
	*/

	int_pair := make_pair(int, 10, 20)
	fmt.printfln("Starter pair: %v (type %T)", int_pair, int_pair)

	// Call make_pair with string and f64 arguments (e.g. "left", "right" and
	// 1.5, 2.5) and print both results using fmt.printfln.


	// Declare empty_scores := []int{} and active_scores := []int{42, 88, 95}.
	// Call first_or_default(int, empty_scores, -1) and
	// first_or_default(int, active_scores, -1) and print both results.


	// Try uncommenting below to confirm Odin catches mismatched argument types
	// against the explicit $T parameter at compile time:
	// bad_pair := make_pair(int, 10, "oops")
}

// Write a procedure that builds a fixed-size array filled with one value:
// make_filled_array :: proc($N: int, $T: typeid, value: T) -> [N]T
// Declare result: [N]T, loop for i in 0..<N assigning result[i] = value,
// and return result.

compile_time_value_parameters :: proc() {

	/*
	Because '$N: int' is fixed at compile time, the return type '[N]T' has a
	known byte size before the program runs. That lets Odin return fixed arrays
	directly by value on the stack, whereas a runtime 'count: int' could only
	return a heap-allocated slice.

	    Suppose you call make_filled_array(4, f32, 1.5):
	    Odin bakes N = 4 and T = f32 into the procedure, creating a 16-byte
	    stack array [1.5, 1.5, 1.5, 1.5] of concrete type [4]f32.
	*/

	sample_pair := make_pair(f32, 0.25, 0.75)
	fmt.printfln("Sample f32 pair bytes: %d", size_of(sample_pair))

	// Call make_filled_array(4, f32, 1.5) into floats and
	// make_filled_array(3, string, "hi") into greetings, then print both values
	// and inspect their concrete monomorphized types using the %T format verb.


	// Combine multiple compile-time arrays by declaring zeros using
	// make_filled_array(5, u8, 0) and printing len(zeros) and size_of(zeros).


	// Try uncommenting below to see why $N rejects a runtime variable:
	// runtime_len := 5
	// dynamic_arr := make_filled_array(runtime_len, int, 42)
	// fmt.println(dynamic_arr)
}

// Write two generic slice allocation helpers:
// alloc_slice :: proc($T: typeid, count: int) -> []T
// clone_slice :: proc($T: typeid, src: []T) -> []T
// In alloc_slice, allocate and return make([]T, count). In clone_slice,
// allocate dest := make([]T, len(src)), copy elements with copy(dest, src),
// and return dest.
//
// Next, write two concrete specializations over make_pair:
// pair_int :: proc(a, b: int) -> [2]int
// pair_f32 :: proc(a, b: f32) -> [2]f32
// Have each forward to make_pair(int, a, b) and make_pair(f32, a, b), then
// bind them into an explicit overload group:
// pair_of :: proc{pair_int, pair_f32}

generic_allocators_and_overloads :: proc() {

	/*
	Explicit '$T: typeid' shines when a procedure takes no value of type T to
	infer from—such as allocating a brand-new slice of 'count' elements. You
	tell Odin what element type to allocate by passing 'T' directly, and the
	caller remains responsible for freeing the returned slice with 'delete'.

	When calling 'make_pair(int, 1, 2)' repeatedly feels verbose, Odin lets you
	wrap concrete specializations into an explicit overload group with
	'proc{...}'. Unlike C++ implicit overloading scattered across headers, every
	candidate in 'pair_of :: proc{pair_int, pair_f32}' lives in one visible
	declaration, so 'pair_of(3, 4)' picks pair_int while 'pair_of(1.0, 2.0)'
	picks pair_f32 without passing a typeid at every call site.
	*/

	baseline := make_pair(string, "heap", "stack")
	fmt.printfln("Baseline tags: %v", baseline)

	// Allocate buf := alloc_slice(int, 4) with defer delete(buf), fill each
	// slot with (i + 1) * 10 across 0..<len(buf), and print buf.


	// Duplicate buf into copy_buf := clone_slice(int, buf) with defer delete(copy_buf),
	// modify copy_buf[0] = 999, and print both buf and copy_buf to prove their
	// backing memory is independent.


	// Call your explicit overload group pair_of(12, 34) and pair_of(f32(1.5), f32(2.5))
	// and print both results with %T to verify the overload dispatch.
}

main :: proc() {

	fmt.println("=== 1. Explicit typeid parameters ===")
	explicit_type_parameters()

	fmt.println("\n=== 2. Compile-time value parameters ===")
	compile_time_value_parameters()

	fmt.println("\n=== 3. Generic allocators and overload groups ===")
	generic_allocators_and_overloads()
}
