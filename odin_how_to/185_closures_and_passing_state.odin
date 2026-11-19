// odin run 185_closures_and_passing_state.odin -file

package main

import "core:fmt"
import "core:slice"

/*
Languages with garbage collection or boxed closure traits let an inline lambda
capture local variables from the surrounding function by silently allocating a
closure environment behind the scenes.

Odin procedures never capture local variables. Every 'proc(...)' literal—even
one written inline inside another procedure—compiles to a plain, C-compatible
code pointer with zero hidden heap allocation. Referencing an outer local
variable inside an inline 'proc' literal is a compile-time error.

When a callback needs runtime state, Odin gives you two explicit, zero-magic
mechanisms:
- Pass a state pointer directly alongside the callback ('proc(x: T, s: ^State)').
- When a fixed signature like 'slice.sort_by' has no state parameter, pass
  '&state' through the implicit 'context.user_ptr' field.
*/

Filter_State :: struct {
	min_val, max_val: int,
}

in_bounds :: proc(x: int, s: Filter_State) -> bool {

	return x >= s.min_val && x <= s.max_val
}

proc_literals_and_no_capture :: proc() {

	/*
	Because an inline procedure literal is just a constant function address
	(an 8-byte pointer on 64-bit targets with no hidden environment pointer),
	you can assign it to a variable or pass it directly as an argument, as long
	as its body uses only its own parameters, file-scope constants, and 'context'.

	    Suppose you write 'fn := proc(x: int) -> int { return x * 2 }':
	    'size_of(fn)' is identical to a C function pointer, and calling 'fn(6)'
	    jumps straight to the compiled code with zero heap allocation.
	*/

	double_fn := proc(x: int) -> int { return x * 2 }
	fmt.printfln("double_fn(6) = %v, in_bounds(5, [1, 10]) = %v", double_fn(6), in_bounds(5, Filter_State{1, 10}))

	// Write an inline procedure literal 'clamp_fn := proc(x, lo, hi: int) -> int'
	// and print 'clamp_fn(-3, 0, 10)', 'clamp_fn(5, 0, 10)', and 'clamp_fn(25, 0, 10)'.


	// Try uncommenting the two lines below to see Odin reject local variable capture:
	// threshold := 10
	// bad_fn := proc(x: int) -> bool { return x > threshold }


	// Define a procedure type 'Int_Transform :: proc(x: int) -> int' at file scope
	// and a helper 'apply_twice :: proc(x: int, fn: Int_Transform) -> int' that
	// returns 'fn(fn(x))'. Call 'apply_twice(3, double_fn)' and also pass an
	// inline 'proc(x: int) -> int { return x + 5 }' directly as the argument.
}

explicit_state_pointer_and_sort_by :: proc() {

	/*
	Whenever you design your own callback API, the cleanest Odin idiom is to
	accept an explicit 'state: ^State' (or 'rawptr') parameter and forward it to
	the callback on every call. Anyone reading the call site immediately sees
	which data the callback reads or mutates.

	For stateless comparisons, 'core:slice' provides 'slice.sort_by(items, less)'
	taking 'less: proc(a, b: T) -> bool' (returning 'true' when 'a' belongs
	before 'b').
	*/

	baseline := [4]int{40, 10, 30, 20}
	slice.sort(baseline[:])
	fmt.printfln("slice.sort baseline: %v", baseline)

	// Write 'count_matching :: proc(items: []int, state: ^Filter_State, pred: proc(x: int, s: ^Filter_State) -> bool) -> int'
	// at file scope returning how many elements satisfy 'pred(item, state)'.


	// Declare 'nums := []int{2, 5, 12, 19, 25, 30}' and
	// 'state := Filter_State{min_val = 10, max_val = 25}'. Call 'count_matching'
	// passing 'nums', '&state', and an inline 'proc(x: int, s: ^Filter_State) -> bool'
	// that checks 'x >= s.min_val && x <= s.max_val'. Print the result (expected: 3).


	// Define 'Score_Entry :: struct { name: string, points: int }' at file scope.
	// Create a slice of four 'Score_Entry' values and sort them in descending
	// order by 'points' using 'slice.sort_by' with an inline comparator
	// 'proc(a, b: Score_Entry) -> bool'. Print the sorted slice.
}

context_user_ptr_callbacks :: proc() {

	/*
	What if you must pass runtime state into a callback whose signature is fixed
	and has no user-data parameter, such as 'slice.sort_by' or a 1-argument
	predicate 'proc(x: int) -> bool'?

	Every normal Odin procedure silently receives an implicit 'context' struct.
	Its 'context.user_ptr' field is a 'rawptr' reserved for passing caller state
	down through fixed callback signatures. Always save the previous pointer and
	restore it with 'defer' so callers above you never lose their own state:

	    Suppose 'state := Filter_State{10, 25}':
	        prev := context.user_ptr
	        defer context.user_ptr = prev
	        context.user_ptr = &state

	Inside the callback, cast 's := (^Filter_State)(context.user_ptr)' to read
	's.min_val' and 's.max_val'.
	*/

	fmt.println("context.user_ptr bridges fixed callback signatures with zero heap closures.")

	// Write 'count_with_context :: proc(items: []int, pred: proc(x: int) -> bool) -> int'
	// at file scope that counts elements where 'pred(item)' returns true.


	// Save 'prev_ptr := context.user_ptr', add 'defer context.user_ptr = prev_ptr',
	// assign 'context.user_ptr = &state' using 'Filter_State{min_val = 10, max_val = 25}',
	// and call 'count_with_context' on '[]int{2, 5, 12, 19, 25, 30}' with a
	// 1-argument 'proc(x: int) -> bool' that recovers 's := (^Filter_State)(context.user_ptr)'.
	// Print the returned count (expected: 3).


	// Combine 'slice.sort_by' with 'context.user_ptr': declare 'target := 10' and
	// 'pts := []int{2, 15, 8, 21, 11}'. Point 'context.user_ptr = &target' (with
	// save/restore), then call 'slice.sort_by(pts, proc(a, b: int) -> bool { ... })'
	// where the comparator casts 't := (^int)(context.user_ptr)' and compares
	// 'abs(a - t^) < abs(b - t^)'. Print 'pts' (expected: [11, 8, 15, 2, 21]).
}

main :: proc() {

	fmt.println("=== 1. Non-capturing procedure literals ===")
	proc_literals_and_no_capture()

	fmt.println("\n=== 2. Explicit state pointers and slice.sort_by ===")
	explicit_state_pointer_and_sort_by()

	fmt.println("\n=== 3. Passing state via context.user_ptr ===")
	context_user_ptr_callbacks()
}
