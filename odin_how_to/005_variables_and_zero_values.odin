// odin run 005_variables_and_zero_values.odin -file

package main

import "core:fmt"

/*
In Odin, there is no 'var', 'let', or 'auto' keyword. Every variable declaration
follows one visual pattern:

    name : Type = value

From that single rule, all four declaration forms fall out naturally:
explicit type with value (x: int = 42), inferred type where ':' and '=' touch
(x := 42), zero-initialized when '= value' is omitted (x: int), and explicitly
uninitialized when '= ---' is written (x: int = ---).

Odin also enforces a strict unused-variable rule: every local variable must be
genuinely read by your code, or the compiler reports 'declared but not used'.
The blank identifier '_' is reserved for discarding unwanted slots in
multi-return calls rather than silencing unused variables.

This file is split into three small sections called from main at the bottom so
you can read top to bottom and run the program at any point.
*/

colon_declaration_and_reassignment :: proc() {

	/*
	Notice how ':' always sits between the identifier on the left and the type
	on the right. When you leave out the type, ':' and '=' touch to form ':='
	and Odin infers the type from the right-hand side: untyped integer literals
	default to 'int', untyped floating-point literals default to 'f64', and
	double-quoted literals default to 'string'.

	Once a variable exists, changing its value later uses plain '=' (never ':=').
	Suppose score: int = 10; writing score = 25 updates the existing stack slot
	to 25, whereas score := 25 fails because score is already declared.
	*/

	// Explicit type declaration and formatted printing:

	explicit_number: int = 10
	fmt.printfln("explicit_number = %v (type: %T)", explicit_number, explicit_number)

	// Declare an integer variable named number_variable with explicit type int
	// and initial value 42. Print it with fmt.println, then reassign it to 99
	// using '=' and print it again.


	// Declare inferred_float := 3.14 and inferred_int := 7 using ':='.
	// Print both values and types using:
	// fmt.printfln("%v (%T) | %v (%T)", inferred_float, inferred_float, inferred_int, inferred_int)


	// Declare inferred_name := "Odin" and inferred_ok := true, then print their
	// inferred types with %T to confirm string and bool inference.


	// Try uncommenting the line below to see why ': Type :=' is illegal syntax
	// (because ':=' already means "omit the explicit type"):
	// bad_decl: int := 42
}

deterministic_zero_initialization :: proc() {

	/*
	In C and C++, declaring 'int x;' leaves whatever garbage bytes happened to
	sit on the stack inside 'x', creating bugs that depend on optimization flags
	or prior function calls. Odin eliminates that whole class of bugs by
	deterministically zeroing every 'name: Type' variable: integers become 0,
	floats become 0.0, booleans become false, strings become "", and pointers or
	slices become nil.

	Suppose you declare count: int and flag: bool without initializers. On
	entry to the procedure, Odin emits zero stores so count is guaranteed 0
	and flag is guaranteed false on every run.
	*/

	// Verifying a zero-initialized float with %#v:

	zero_float: f64
	fmt.printfln("zero_float = %#v (type: %T)", zero_float, zero_float)

	// Declare three zero-initialized variables without assigning values:
	// zero_int of type int, zero_bool of type bool, and zero_string of type string.
	// Print all three in one fmt.printfln call using %#v so you see 0, false, "".


	// Declare a zero-initialized fixed array zero_pair: [2]int and a zero
	// pointer zero_ptr: ^int without '=' initializers, and print both with %#v
	// to confirm compound values and pointers zero cleanly to [0, 0] and nil.
}

parallel_declarations_swaps_and_uninitialized :: proc() {

	/*
	Odin lets you declare multiple variables in one statement (a, b := 1, 2) and
	assign multiple variables in parallel (a, b = b, a). Because Odin evaluates
	the entire right-hand side before writing to the left-hand side, swapping two
	variables needs no temporary variable.

	Suppose width, height := 1920, 1080. Writing width, height = height, width
	reads both 1080 and 1920 first, then writes width = 1080 and height = 1920.

	For rare hot-path stack buffers where zeroing a big array would waste CPU
	cycles right before you overwrite every byte yourself, writing '= ---' tells
	Odin to skip automatic zero-initialization and leave raw stack memory.
	*/

	// Parallel declaration starter:

	left_x, left_y := 10, 20
	fmt.printfln("Start coordinates: (%v, %v)", left_x, left_y)

	// Declare width and height in one statement initialized to 1920 and 1080.
	// Swap them in a single line: width, height = height, width
	// Print both before and after the swap to confirm the values exchanged.


	// Declare three variables in one statement: tag, count, ready := "frame", 60, true
	// Print all three values and types using fmt.printfln.


	// Declare two variables sharing one explicit type: min_x, max_x: f32 = 0.0, 100.0
	// Print both alongside %T to confirm both received type f32.


	// Declare raw_scratch: int = --- (explicitly uninitialized), then assign
	// raw_scratch = 7 before printing it.
	// Experiment: try printing raw_scratch before assigning 7 and check with:
	// odin check 005_variables_and_zero_values.odin -file -vet-uninitialized
}

main :: proc() {

	fmt.println("=== 1. Colon declaration and reassignment ===")
	colon_declaration_and_reassignment()

	fmt.println("\n=== 2. Deterministic zero initialization ===")
	deterministic_zero_initialization()

	fmt.println("\n=== 3. Parallel declarations, swaps, and uninitialized ===")
	parallel_declarations_swaps_and_uninitialized()
}
