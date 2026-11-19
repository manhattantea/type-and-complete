// odin run 130_variadic_and_by_ptr_params.odin -file

package main

import "core:fmt"

/*
Every parameter passing rule in Odin balances two goals: keeping call sites clean
to read while avoiding hidden heap allocations or accidental copies on the stack.
Variadic parameters ('..T'), '#by_ptr', and '#any_int' each solve a specific
call-site friction without changing how memory works underneath.

This file is split into three sections called from main at the bottom so you
can read top to bottom and run the program at any point.
*/

Big_Payload :: struct {
	data: [64]f64,
	id:   int,
}

// Starter helper inspecting a large struct passed via #by_ptr.
payload_capacity :: proc(#by_ptr p: Big_Payload) -> int {

	return len(p.data)
}

variadic_slices_and_expansion :: proc() {

	/*
	Unlike C's unsafe '...' varargs (which require format strings or sentinel
	values because the callee does not know how many arguments arrived), Odin's
	variadic parameter 'nums: ..int' is simply a typed slice '[]int' built on the
	caller's stack! Inside the procedure, 'nums' has a normal 'len(nums)' and can
	be iterated with 'for n in nums'.

	    Suppose sum_ints :: proc(nums: ..int) -> int:
	        Calling sum_ints(10, 20, 30) packs {10, 20, 30} on the caller's stack
	        and hands sum_ints a 3-element []int slice header.
	        Calling sum_ints() with zero arguments passes an empty slice (len 0).

	When you already hold a slice 'my_slice := []int{10, 20, 30}', prefixing it
	with '..' at the call site ('sum_ints(..my_slice)') forwards your existing
	slice header straight to 'nums' with zero copying. Remember two rules: a
	variadic parameter must be the last positional parameter (after any fixed
	parameters like 'tag: string, vals: ..int'), and you cannot mix discrete
	items and '..slice' in the same call.
	*/

	// Starter helper showing a variadic slice parameter in action:

	count_args :: proc(vals: ..int) -> int {

		return len(vals)
	}

	fmt.printfln("count_args(4, 8, 15) = %v, count_args() = %v", count_args(4, 8, 15), count_args())

	// Write sum_ints :: proc(nums: ..int) -> int that returns the sum of all
	// elements in nums (returning 0 when nums is empty).
	// Call sum_ints(1, 2, 3, 4) and print the result (expected: 10).
	// Also call sum_ints() with zero arguments and print the result (expected: 0).


	// Declare a slice my_slice := []int{10, 20, 30} and expand it into sum_ints
	// using sum_ints(..my_slice), printing the result (expected: 60).
	//
	// Try uncommenting a mixed expansion call below to see Odin reject mixing
	// discrete arguments with ..slice:
	// fmt.println(sum_ints(5, ..my_slice))


	// Practice mixed fixed and variadic parameters:
	// Write format_tagged :: proc(tag: string, vals: ..int) that prints the tag
	// followed by each integer in vals on one line (for example: "[METRICS] 4 9 16").
	// Call format_tagged("METRICS", 4, 9, 16) and also call format_tagged("EMPTY")
	// with no variadic values.


	// Use a fixed leading parameter to enforce at least one value at compile time:
	// Write min_of_ints :: proc(first: int, rest: ..int) -> int that initializes
	// best := first, loops over rest to find the smallest value, and returns best.
	// Call min_of_ints(14, 3, 27, 9) and print the result (expected: 3).
}

by_ptr_large_structs :: proc() {

	/*
	Big_Payload above holds 64 f64 values plus an int—520 bytes per value. Copying
	520 bytes onto the stack on every small helper call wastes memory bandwidth
	and cache lines. In C++, people reach for 'const Big_Payload&' so callers can
	still pass temporary values without writing '&'.

	Odin solves this with the '#by_ptr' parameter directive:

	    inspect_payload :: proc(#by_ptr p: Big_Payload) -> int

	When we put '#by_ptr' in front of a parameter, it tells the compiler "pass
	the caller's struct by immutable pointer under the hood, even when the caller
	writes a value or compound literal without '&'". Inside inspect_payload, 'p'
	behaves like an immutable value parameter (you read 'p.id' directly with a dot,
	not 'p^'), and you still cannot mutate 'p.id = 99'. If you actually want to
	modify the caller's struct, use an explicit pointer 'p: ^Big_Payload' instead.

	    Suppose items := Big_Payload{id = 7}:
	        inspect_payload(items)              // passes &items under the hood, zero 520-byte copy
	        inspect_payload(Big_Payload{id=7})  // materializes temporary on stack and passes its address
	*/

	fmt.printfln("Big_Payload data len = %v", payload_capacity(Big_Payload{}))

	// Write inspect_payload :: proc(#by_ptr p: Big_Payload) -> int returning p.id.
	// Call inspect_payload(Big_Payload{id = 7}) directly without '&' and print
	// the returned id (expected: 7).
	//
	// Try mutating 'p.id = 99' inside inspect_payload to confirm '#by_ptr' still
	// enforces parameter immutability.


	// Write max_payload_id :: proc(#by_ptr a: Big_Payload, #by_ptr b: Big_Payload) -> int
	// returning a.id if a.id >= b.id else b.id.
	// Create two local variables first := Big_Payload{id = 12} and
	// second := Big_Payload{id = 45}, call max_payload_id(first, second), and
	// print the result (expected: 45).
}

any_int_width_adaptation :: proc() {

	/*
	Odin strictly forbids implicit integer conversions: a 'u8' never silently
	widens to an 'int', and an 'i32' never silently converts to an 'i64'. That
	strictness prevents hidden sign bugs, yet it can make simple utility helpers
	like index printers annoying to call when one caller has a 'u8' and another
	has an 'i32' or 'u64'.

	When we put '#any_int' in front of an integer parameter:

	    print_index :: proc(#any_int idx: int)

	it means the compiler automatically inserts an explicit conversion to 'int' at
	the call site for any integer type ('u8', 'i16', 'i32', 'u64', 'int', and
	untyped integer literals), while still rejecting floats or strings. Inside
	the procedure body, 'idx' always has exact type 'int'.
	*/

	// Starter helper accepting any integer width and returning it as int:

	double_any_int :: proc(#any_int n: int) -> int {

		return n * 2
	}

	small_u8: u8 = 9
	fmt.printfln("double_any_int(u8(9)) = %v", double_any_int(small_u8))

	// Write print_index :: proc(#any_int idx: int) that prints idx with fmt.printfln.
	// Declare three variables: byte_idx: u8 = 7, signed_idx: i32 = 1200, and
	// big_idx: u64 = 999999. Pass all three directly to print_index without casts.
	//
	// Try uncommenting a float call below to verify '#any_int' still rejects floats:
	// print_index(f32(3.5))


	// Combine '#any_int' across multiple parameters in a bounds-check helper:
	// Write clamp_index :: proc(#any_int idx: int, #any_int count: int) -> int
	// Return 0 if count <= 0 or idx < 0, count - 1 if idx >= count, otherwise idx.
	// Test clamp_index(u8(5), i32(4)) (expected: 3) and
	// clamp_index(i16(-2), u64(10)) (expected: 0).
}

main :: proc() {

	fmt.println("=== 1. Variadic slices and expansion ===")
	variadic_slices_and_expansion()

	fmt.println("\n=== 2. Pass-by-pointer with #by_ptr ===")
	by_ptr_large_structs()

	fmt.println("\n=== 3. Integer width adaptation with #any_int ===")
	any_int_width_adaptation()
}
