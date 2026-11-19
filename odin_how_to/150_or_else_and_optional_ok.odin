// odin run 150_or_else_and_optional_ok.odin -file

package main

import "core:fmt"

/*
Instead of throwing hidden exceptions or forcing multi-line 'if val, ok := ...'
checks for every fallback value, Odin pairs its '(value, ok_bool)' convention
with the 'or_else' expression, '#optional_ok' procedures, and 'Maybe(T)'.
Because 'or_else' works identically on procedures, 'Maybe(T)', maps, and
tagged unions, you learn one fallback rule and use it everywhere.

This file is split into three sections called from main at the bottom so you
can read top to bottom and run the program at any point.
*/

// Starter helper marked #optional_ok returning half of an even integer.
half_even :: proc(n: int) -> (half: int, ok: bool) #optional_ok {

	if n % 2 != 0 do return 0, false
	return n / 2, true
}

Setting :: union {
	int,
	string,
	bool,
}

or_else_and_optional_ok_procs :: proc() {

	/*
	Whenever an expression produces two values '(T, bool)', writing:

	    val := expr or_else fallback

	evaluates 'expr', checks its trailing boolean, and yields the 'T' value when
	ok is true or evaluates 'fallback' when ok is false. Crucially, 'fallback'
	is short-circuited: if ok is true, the right-hand side never runs at all.

	    Suppose half_even(7) returns (0, false):
	        x := half_even(7) or_else -1   // ok is false, so x becomes -1
	        y := half_even(8) or_else -1   // ok is true, so y becomes 4

	Adding the '#optional_ok' directive to a '(T, bool)' procedure tells Odin
	that callers are also allowed to ignore the boolean directly via 'v := fn(x)'
	when failure is already handled or guaranteed impossible—while still keeping
	'v, ok := fn(x)' and 'fn(x) or_else def' available whenever you need them.
	*/

	fmt.printfln("half_even(8) = %v, half_even(7) or_else -1 = %v", half_even(8), half_even(7) or_else -1)

	// Write safe_sqrt :: proc(x: f64) -> (res: f64, ok: bool) #optional_ok
	// If x < 0, return 0, false.
	// If x == 0, return 0, true.
	// Otherwise start from guess := x and run 10 iterations of Newton's method
	// (guess = 0.5 * (guess + x / guess)), then return guess, true.


	// Call safe_sqrt three ways and print v1, v2, and v3:
	// v1 := safe_sqrt(16) or_else -1.0   (expected: 4)
	// v2 := safe_sqrt(-4) or_else 0.0    (expected: 0)
	// v3 := safe_sqrt(25)                (1-value call enabled by #optional_ok; expected: 5)


	// Capture both values explicitly on a failing call:
	// val, ok := safe_sqrt(-9)
	// Print val and ok (expected: 0 and false), then test what happens if you
	// write a normal '(int, bool)' proc WITHOUT '#optional_ok' and try calling
	// it with a single assignment 'x := my_proc()' (compile error!).
}

maybe_type_unwrapping :: proc() {

	/*
	Odin represents an optional value with the built-in generic union 'Maybe(T)',
	which holds either a value of type T or 'nil'. For pointer types like
	'Maybe(^Node)', Odin uses the null pointer itself as the nil state so
	'Maybe(^Node)' adds zero extra bytes!

	You cannot read a 'Maybe(T)' directly as T—you unwrap it with the '.?'
	operator, which yields '(T, bool)'. That means '.?' plugs straight into
	'or_else' or a two-variable assignment:

	    Suppose opt_limit: Maybe(int) = nil:
	        limit := opt_limit.? or_else 100   // opt_limit is nil, so limit becomes 100
	        val, has_val := opt_limit.?        // val is 0, has_val is false
	*/

	sample_opt: Maybe(int) = 42
	unwrapped := sample_opt.? or_else 0
	fmt.printfln("sample_opt unwrapped = %v", unwrapped)

	// Declare opt_port: Maybe(u16) = nil, unwrap it into port1 using:
	// port1 := opt_port.? or_else 8080
	// Print port1 (expected: 8080).
	// Then assign opt_port = 3000, unwrap into port2 using .? or_else 8080, and
	// print port2 (expected: 3000).


	// Unwrap a Maybe(string) using explicit two-value form:
	// Declare opt_name: Maybe(string) = "odin"
	// Check 'if name, ok := opt_name.?; ok' to print name, then set
	// opt_name = nil and verify the else branch runs instead.


	// Write find_first_positive :: proc(nums: []int) -> Maybe(int)
	// Return the first element > 0, or nil if none exists.
	// Call find_first_positive([]int{-5, -1, 12, 8}).? or_else 0 (expected: 12)
	// and find_first_positive([]int{-5, -1}).? or_else 0 (expected: 0).
}

or_else_on_maps_and_unions :: proc() {

	/*
	Because map lookups and union type assertions can both produce '(T, bool)',
	'or_else' solves two everyday traps cleanly.

	First, on a 'map[K]V', reading 'scores["missing"]' as a single value does not
	fail—it silently returns the zero value (0 for int), which looks identical
	to a real entry '{"missing" = 0}'! Writing 'scores["missing"] or_else -1'
	lets you tell a missing key apart from a stored zero in one expression.
	(Remember that maps allocate on the heap, so pair 'make' or a map literal
	with 'defer delete(m)'.)

	Second, on a tagged union like 'Setting :: union { int, string, bool }',
	a bare type assertion 's.(int)' panics at runtime if 's' currently holds a
	'string'. Pairing it with 'or_else' ('s.(int) or_else 8080') turns that
	assertion into a safe fallback expression with zero runtime panic.

	    Suppose s: Setting = "localhost":
	        port := s.(int) or_else 8080     // s holds string, so port becomes 8080
	        host := s.(string) or_else "0"   // s holds string, so host becomes "localhost"
	*/

	current: Setting = "localhost"
	safe_port := current.(int) or_else 8080
	fmt.printfln("current.(int) or_else 8080 = %v", safe_port)

	// Practice or_else on map[string]int lookups:
	// Declare timeouts := map[string]int{"connect" = 5, "retry" = 0}
	// Add 'defer delete(timeouts)' right below it so the map frees cleanly.
	// Read connect_sec := timeouts["connect"] or_else 10  (expected: 5)
	// Read retry_sec := timeouts["retry"] or_else 10      (expected: 0, stored!)
	// Read write_sec := timeouts["write"] or_else 10      (expected: 10, missing!)
	// Print all three values to confirm stored 0 stays 0 while missing keys fall back.


	// Practice or_else on tagged union type assertions:
	// Declare a slice settings := []Setting{8000, "127.0.0.1", true}
	// Loop over each item in settings and compute:
	// as_int := item.(int) or_else -1
	// as_str := item.(string) or_else "<not string>"
	// Print as_int and as_str for each entry without triggering any type-assertion panic.


	// Try uncommenting an unguarded union type assertion below to observe the
	// runtime panic when the active variant is bool instead of int:
	// bad_item: Setting = true
	// crashed_int := bad_item.(int)
	// fmt.println(crashed_int)
}

main :: proc() {

	fmt.println("=== 1. or_else and #optional_ok procedures ===")
	or_else_and_optional_ok_procs()

	fmt.println("\n=== 2. Maybe(T) and .? unwrapping ===")
	maybe_type_unwrapping()

	fmt.println("\n=== 3. or_else on maps and tagged unions ===")
	or_else_on_maps_and_unions()
}
