// odin run 110_multiple_and_named_returns.odin -file

package main

import "core:fmt"

/*
In C, returning two answers from one function forces you either to invent a
one-off struct or to pass output pointers like 'int *out_rem' that callers can
accidentally pass as NULL. Odin follows Go's lead and returns multiple values
directly on the stack (or in CPU registers) with zero heap allocation.

This file is split into three sections called from main at the bottom so you
can read top to bottom and run the program at any point.
*/

// Starter helper returning two unnamed values.
swap_pair :: proc(a, b: int) -> (int, int) {

	return b, a
}

multiple_return_values :: proc() {

	/*
	To return more than one value, wrap the return types in parentheses after
	'->':

	    swap_pair :: proc(a, b: int) -> (int, int)

	At the call site, Odin unpacks those positions left-to-right into fresh
	variables with ':=' (or existing ones with '='). Every returned slot must be
	accounted for—if you ignore a position, the compiler stops you with an arity
	mismatch. When you genuinely do not care about one of the slots, put the
	blank identifier '_' in that slot to throw it away without creating an
	unused local variable.

	    Suppose split_pair returns (10, 20):
	        left, right := split_pair()   // left is 10, right is 20
	        _, only_right := split_pair() // 10 is discarded, only_right is 20
	*/

	first, second := swap_pair(1, 2)
	fmt.printfln("swap_pair(1, 2) -> %v, %v", first, second)

	// Write a procedure safe_divide :: proc(a, b: int) -> (int, bool) that returns
	// 0, false when b == 0, and a / b, true otherwise.
	// Call safe_divide(20, 4) capturing quotient, ok and print both (expected: 5, true).
	//
	// Call safe_divide(20, 0) discarding the quotient with '_' (_, ok2 := safe_divide(20, 0))
	// and print ok2 (expected: false).


	// Write a procedure split_seconds :: proc(total_secs: int) -> (int, int, int)
	// that splits total_secs into hours, minutes, and remaining seconds.
	// Call split_seconds(3665) capturing h, m, s and print them (expected: 1, 1, 5).
	// Then call split_seconds(125) capturing only minutes and seconds (_, mins, secs := ...)
	// and print mins and secs (expected: 2, 5).


	// Combine a multi-return call with an if-init statement:
	// Call safe_divide inside 'if val, ok := safe_divide(84, 7); ok' and print val
	// inside the true branch, with an else branch printing "Cannot divide by zero".
}

named_returns_and_naked_return :: proc() {

	/*
	Instead of writing bare types like '-> (int, int, bool)', you can give each
	return slot a name right in the signature:

	    divmod :: proc(a, b: int) -> (quotient: int, remainder: int, ok: bool)

	Naming return values does two things at once. First, callers immediately see
	what each position means when hovering over the procedure in an editor.
	Second, Odin automatically declares 'quotient', 'remainder', and 'ok' as
	mutable, zero-initialized local variables inside the procedure body (0, 0,
	and false here).

	Because those variables already hold valid zero values on entry, a bare
	'return' statement (called a naked return) exits immediately and returns
	whatever values the named return variables currently hold. Just like
	parameters, consecutive named returns sharing the same type can be grouped
	before one type name, as in '-> (min_val, max_val: int)'.

	    Suppose find_bounds returns (min_val, max_val: int):
	        If you hit an early error and execute 'return' right away, Odin
	        returns (0, 0) without you repeating 'return 0, 0' on every error path.
	*/

	// Here is a quick starter helper showing a grouped named return and naked return:

	order_two :: proc(x, y: int) -> (lo, hi: int) {

		if x <= y {
			lo = x
			hi = y
		} else {
			lo = y
			hi = x
		}
		return
	}

	low_a, high_a := order_two(9, 4)
	fmt.printfln("order_two(9, 4) -> lo=%v, hi=%v", low_a, high_a)

	// Write divmod :: proc(a, b: int) -> (quotient: int, remainder: int, ok: bool)
	// If b == 0, execute a naked 'return' immediately (returning 0, 0, false).
	// Otherwise assign quotient = a / b, remainder = a % b, and ok = true, then return.
	//
	// Call divmod(17, 5) capturing q, r, ok and print them (expected: 3, 2, true).
	// Call divmod(10, 0) discarding the remainder with 'q2, _, ok2 := divmod(10, 0)'
	// and print q2 and ok2 (expected: 0, false).


	// Write min_max :: proc(nums: []int) -> (min_val, max_val: int, ok: bool)
	// If len(nums) == 0, execute a naked return (returns 0, 0, false).
	// Otherwise initialize min_val = nums[0], max_val = nums[0], ok = true, loop
	// over nums[1:] updating min_val and max_val, and end with a naked return.
	//
	// Test min_max on both []int{14, -3, 27, 8} and an empty []int{} slice.


	// Write parse_port_pair :: proc(lo, hi: int) -> (start, end: int, valid: bool)
	// Return early with a naked return if lo < 1 or hi > 65535 or lo > hi.
	// Otherwise set start = lo, end = hi, valid = true and return.
	// Test both (8000, 8080) and an invalid range (9000, 8000).
}

named_return_traps :: proc() {

	/*
	Named returns are convenient in short procedures, but two subtle traps bite
	people who forget that named returns are ordinary local variables in the
	outer procedure scope.

	First, if you accidentally write ':=' instead of '=' inside an inner 'if' or
	'for' block (for example 'total := 100' when 'total' is a named return), Odin
	creates a brand-new block-local variable that shadows the named return! The
	inner 'total' receives 100 and disappears at the closing brace, so a naked
	'return' at the bottom silently returns the untouched outer 0. Running with
	'-vet-shadowing' catches this mistake immediately.

	    Suppose sum_if_positive :: proc(x: int) -> (total: int) does:
	        if x > 0 {
	            total := x * 2   // trap: creates inner total, outer total stays 0!
	        }
	        return               // returns 0 instead of x * 2

	Second, Odin forbids mixing named and unnamed return values in the same
	signature: either every return slot has a name, or none of them do. Also, in
	longer procedures, explicit 'return a, b, true' often reads clearer than a
	naked return because the reader does not have to scroll up to remember what
	variables are being returned.
	*/

	// Starter check showing how an explicit return overrides named variables if needed:

	clamp_byte :: proc(n: int) -> (clamped: int) {

		if n < 0 do return 0
		if n > 255 do return 255
		clamped = n
		return
	}

	fmt.printfln("clamp_byte(300) = %v, clamp_byte(42) = %v", clamp_byte(300), clamp_byte(42))

	// Observe the inner-block shadowing trap directly:
	// Write a small helper proc named buggy_double :: proc(x: int) -> (res: int)
	// Inside 'if x > 0 { res := x * 2 }', intentionally shadow res with ':=',
	// then call 'return'. Print buggy_double(5) (it prints 0 instead of 10!).
	// Next, change ':=' to '=' inside the if block and re-run to verify it returns 10.
	// You can also run 'odin check 110_multiple_and_named_returns.odin -file -vet-shadowing'
	// to see the compiler flag the shadowing bug automatically.


	// Verify the all-or-nothing naming rule:
	// Try uncommenting the mixed signature below to see Odin reject mixing named
	// and unnamed return values in one procedure:
	// bad_sig :: proc() -> (val: int, bool) { return 1, true }
}

main :: proc() {

	fmt.println("=== 1. Multiple return values and _ discarding ===")
	multiple_return_values()

	fmt.println("\n=== 2. Named returns and naked return ===")
	named_returns_and_naked_return()

	fmt.println("\n=== 3. Named return traps ===")
	named_return_traps()
}
