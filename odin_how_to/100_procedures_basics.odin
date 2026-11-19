// odin run 100_procedures_basics.odin -file

package main

import "core:fmt"

/*
In Odin, procedures are compile-time constants declared with 'name :: proc(...) -> ...'.
Notice the double colon '::': just like types and numeric constants, a procedure
has a fixed address baked into your binary at compile time, whereas ':=' is reserved
for runtime variables sitting on the stack or heap.

This file is split into three focused sections called from main at the bottom so
you can read top to bottom and run the program at any point.
*/

// Starter helper used by the first section below.
square :: proc(x: int) -> int {

	return x * x
}

parameters_and_local_procs :: proc() {

	/*
	Every parameter inside an Odin procedure is an immutable constant. If you try
	to reassign 'x = 10' inside square above, the compiler rejects it immediately.
	Making parameters read-only prevents a whole class of silent bugs where you
	accidentally overwrite an input mid-function and then read the wrong value
	twenty lines later.

	When you genuinely need a scratch copy of a parameter, shadow it explicitly
	with 'x := x' to allocate a new mutable local variable on the stack. Also
	notice that consecutive parameters of the same type can share one type name
	after a comma, as in 'a, b: int, scale: int'.

	Odin also lets you declare nested local procedures directly inside another
	procedure body using the same ':: proc' syntax. Because '::' binds at compile
	time, a local procedure is still a plain function pointer with zero closure
	allocation—it can read its own parameters, constants, and imports, but it
	cannot capture runtime local variables from the outer procedure.

	    Suppose compute_score contains:
	        bonus :: proc(n: int) -> int {
	            return 0 if n < 0 else n * 2
	        }
	        // bonus(5) returns 10, while bonus(-3) returns 0.
	        // Trying to read an outer local variable 'base_pts' inside bonus
	        // triggers a compile error because bonus has no hidden closure pointer.
	*/

	// Here is a starter call to the file-scope helper and a tiny nested local proc:

	clamp_non_negative :: proc(n: int) -> int {

		return 0 if n < 0 else n
	}

	input := 5
	fmt.printfln("square(%v) = %v, clamp_non_negative(-4) = %v", input, square(input), clamp_non_negative(-4))

	// Write a procedure named add_and_scale taking grouped a, b: int and scale: int
	// and returning an int equal to (a + b) * scale.
	// Call add_and_scale(3, 4, 2) and print the result (expected: 14).
	//
	// Try assigning 'a = 0' inside add_and_scale to confirm Odin rejects mutating
	// a procedure parameter ("Cannot assign to constant 'a'").


	// Write a nested local procedure named abs_diff :: proc(a, b: int) -> int
	// right inside this section that returns a - b when a >= b and b - a otherwise.
	// Call abs_diff(12, 19) and print the result (expected: 7).
	//
	// Try referencing 'input' directly inside abs_diff to see Odin reject
	// capturing a runtime local variable from an enclosing procedure.


	// Practice explicit mutable shadowing inside a procedure:
	// Write a procedure named step_toward_zero :: proc(start: int, steps: int) -> int
	// Inside it, create a mutable local copy with 'cur := start', loop 'steps'
	// times moving cur by 1 toward 0, and return cur.
	// Call step_toward_zero(5, 3) and print the result (expected: 2).
}

value_vs_pointer_parameters :: proc() {

	/*
	Because parameters are passed by value unless you ask for a pointer, passing a
	variable to a procedure copies its value onto the call frame. Even if you make
	a mutable local shadow 'val := val' inside the procedure, changing that copy
	never touches the caller's original variable.

	    Suppose score := 10 and you call try_add(score, 5) where try_add copies val:
	        score remains 10 in the caller, because val lived in try_add's stack frame.

	When a procedure truly needs to mutate caller state, accept a pointer type '^T'
	and dereference it with postfix 'ptr^'. Unlike C's overloaded '*' symbol, Odin
	uses prefix '^' for "pointer to T", '&' for "address of x", and postfix '^' for
	"follow the pointer". Passing '&score' hands the procedure the memory address
	of score instead of a copy, so writing 'target^ += delta' updates score directly.

	Watch out for the nil pointer trap too: a '^T' pointer can hold 'nil', and
	dereferencing 'nil^' crashes at runtime. Always guard nullable pointers with
	'if target == nil do return' before touching 'target^'.
	*/

	// Notice how calling square(original) leaves original untouched:

	original := 6
	squared := square(original)
	fmt.printfln("original stays %v while squared is %v", original, squared)

	// Declare a procedure add_in_place :: proc(target: ^int, delta: int) that
	// guards against nil ('if target == nil do return') and then adds delta to
	// target^ directly.
	//
	// Declare a mutable variable counter := 10, pass &counter and 5 to
	// add_in_place(&counter, 5), and print counter (expected: 15).
	// Also call add_in_place(nil, 5) to verify your nil guard exits safely.


	// See the value-copy trap firsthand:
	// Write reset_if_negative :: proc(val: int) -> int that shadows 'v := val',
	// sets v = 0 when v < 0, and returns v.
	// Declare hp := -20, call reset_if_negative(hp) without assigning it back to hp,
	// and print both hp (still -20!) and the returned 0.


	// Write a swap_ints :: proc(a, b: ^int) procedure that swaps the values stored
	// at a^ and b^ (guarding that neither a nor b is nil).
	// Declare left := 100 and right := 250, call swap_ints(&left, &right), and
	// print left and right (expected: 250 and 100).
}

procedure_types_and_callbacks :: proc() {

	/*
	Because every procedure in Odin is a plain compile-time function pointer with
	zero hidden closure state, a procedure signature is itself a first-class type.
	You can name a signature with '::' just like a struct:

	    Binary_Op :: proc(a, b: int) -> int

	Any procedure whose parameter types and return type match 'Binary_Op' can be
	stored in a variable of type Binary_Op or passed straight into another
	procedure as a callback. You can also write an inline anonymous procedure
	literal right at the call site:

	    proc(a, b: int) -> int { return a - b }

	Notice that inline procedure literals follow the exact same no-capture rule as
	nested local procedures: they can only use their own parameters, constants, and
	imports, which guarantees a Binary_Op variable is always a single pointer-sized
	address in memory.
	*/

	// Here is a quick starter variable holding a procedure type:

	Unary_Op :: proc(x: int) -> int
	op: Unary_Op = square
	fmt.printfln("Unary_Op square(4) = %v", op(4))

	// Define a procedure type Binary_Op :: proc(a, b: int) -> int
	// Write a helper multiply :: proc(a, b: int) -> int returning a * b.
	// Write apply_op :: proc(x, y: int, fn: Binary_Op) -> int returning fn(x, y).
	//
	// Call apply_op(6, 7, multiply) and print the result (expected: 42).
	// Then call apply_op(10, 3, proc(a, b: int) -> int { return a - b }) using an
	// inline procedure literal and print the result (expected: 7).


	// Practice selecting a callback at runtime via a procedure variable:
	// Declare chosen: Binary_Op = multiply, call apply_op(4, 5, chosen), then
	// reassign chosen to an inline proc literal that returns a + b and call
	// apply_op(4, 5, chosen) again (expected: 20, then 9).
	//
	// Also test what happens if you leave 'uninit_op: Binary_Op' zero-initialized
	// (nil) and check 'if uninit_op == nil' before calling it.
}

main :: proc() {

	fmt.println("=== 1. Parameters and local procedures ===")
	parameters_and_local_procs()

	fmt.println("\n=== 2. Value vs pointer parameters ===")
	value_vs_pointer_parameters()

	fmt.println("\n=== 3. Procedure types and callbacks ===")
	procedure_types_and_callbacks()
}
