// odin run 170_or_break_and_or_continue.odin -file

package main

import "core:fmt"

/*
Just as 'or_return' unwraps a '(value, status)' expression or exits the
enclosing procedure, 'or_continue' and 'or_break' unwrap '(value, status)'
directly inside 'for' loops.

When we write 'val := expr or_continue', Odin checks the trailing status
('bool', error 'enum', 'union', or pointer). If it succeeded, 'val' receives the
payload; if it failed, Odin skips the rest of the loop body and jumps to the
next pass. Writing 'val := expr or_break' does the same on success, but exits
the loop immediately on failure. Both operators also accept an optional loop
label (such as 'or_continue outer' or 'or_break row_loop') to steer an outer
nested loop in one expression.
*/

parse_digit :: proc(ch: u8) -> (digit: int, ok: bool) {

	if ch >= '0' && ch <= '9' do return int(ch - '0'), true
	return 0, false
}

filtering_with_or_continue :: proc() {

	/*
	Suppose 'text := "1a2"' and you loop over its bytes with 'd := parse_digit(text[i]) or_continue'.
	On '1' (index 0), 'parse_digit' returns '(1, true)', so 'd' becomes 1 and the
	body runs. On 'a' (index 1), 'parse_digit' returns '(0, false)', so
	'or_continue' skips the rest of the pass and jumps straight to index 2 ('2').

	In nested loops, plain 'or_continue' skips only the inner loop's current
	iteration. Attaching an outer label like 'or_continue outer' abandons the
	entire inner row and jumps straight to the next outer row.
	*/

	sample_digit, sample_ok := parse_digit('7')
	fmt.printfln("parse_digit('7') -> digit = %v, ok = %v", sample_digit, sample_ok)

	// Loop over the bytes of "1a2b3c" with 'for i in 0..<len(s)', unwrap each byte
	// using 'd := parse_digit(s[i]) or_continue', sum only the valid digits into
	// a variable named 'sum', and print 'sum' with fmt.printfln (expected: 6).


	// Write a helper 'parse_hex_nibble :: proc(ch: u8) -> (val: int, ok: bool)' at
	// file scope handling '0'..='9', 'a'..='f', and 'A'..='F'. Then loop over
	// "G1_a!F" using 'or_continue' to sum all valid hex digits (expected: 26).


	// Test 'or_continue outer' on a 2D slice of rows:
	// declare 'rows := []string{"12", "3?4", "5x6"}'
	// Label the outer loop 'outer: for row in rows', track a running 'clean_sum := 0',
	// and inside an inner byte loop unwrap 'd := parse_digit(row[i]) or_continue outer'.
	// Accumulate each digit into a per-row 'row_sum', and only add 'row_sum' into
	// 'clean_sum' after the inner loop finishes without bad characters (expected:
	// only "12" completes cleanly, so clean_sum = 3; contrast this with plain
	// 'or_continue', which would only skip '?' and still count '4').
}

stopping_with_or_break :: proc() {

	/*
	When an invalid item means "stop scanning right here" rather than "skip this
	one item", replace 'or_continue' with 'or_break'.

	    Suppose 'text := "45!6"':
	    Looping with 'd := parse_digit(text[i]) or_break' reads 4 and 5, then
	    hits '!' and exits the loop immediately without touching 6.

	Just like 'or_continue', 'or_break label' exits all the way out of the named
	enclosing loop instead of needing a manual boolean 'done' flag.
	*/

	// Loop over the bytes of "456!789", unwrap each byte using
	// 'd := parse_digit(ch) or_break', and accumulate a base-10 integer with
	// 'acc = acc * 10 + d'. Print 'acc' afterward (expected: 456).


	// Write 'parse_positive_even :: proc(n: int) -> (val: int, ok: bool)' at file
	// scope returning 'n, true' only when 'n > 0 && n % 2 == 0'. Loop over
	// '[]int{4, 8, 12, 7, 16}' using 'or_break' to sum the leading even prefix
	// (expected: 24).


	// Break out of a nested loop with 'or_break row_loop':
	// given 'rows := []string{"12", "3!4", "56"}', write 'row_loop: for row in rows'
	// around an inner byte loop summing digits with 'd := parse_digit(row[i]) or_break row_loop'.
	// Print the total sum after 'row_loop' exits (expected: 6 from 1 + 2 + 3).
}

enum_errors_with_or_break :: proc() {

	/*
	Both 'or_break' and 'or_continue' work with error enums as well as booleans,
	using Odin's zero-is-success convention: '.None' (0) unwraps the value, and
	any non-zero enum variant triggers the break or continue.

	    Suppose 'tokens := []string{"3", "5", "STOP", "9"}':
	    Walking with 'v := decode_token(tok) or_break' adds 3 and 5, then sees
	    '.Stop_Token' (non-zero) on "STOP" and exits the loop immediately at 8.

	Notice one deliberate trade-off compared to 'or_return': because 'or_break'
	and 'or_continue' do not return a value, they discard which specific error
	variant occurred. Use them when the loop simply needs to stop or skip on any
	error; if you need to inspect or log the exact error variant, capture
	'val, err := ...' and branch on 'err' explicitly instead.
	*/

	fmt.println("or_break and or_continue also treat enum value 0 (.None) as success.")

	// Define 'Scan_Error :: enum { None, Comment_Token, Stop_Token, Bad_Digit }'
	// at file scope, and write 'decode_token :: proc(tok: string) -> (val: int, err: Scan_Error)'
	// that returns '0, .Comment_Token' when 'len(tok) == 0 || tok[0] == '#' ' is
	// true (no spaces inside the rune literal), returns '0, .Stop_Token' when
	// 'tok == "STOP"', returns 'int(tok[0] - '0'), .None' for a single ASCII digit
	// ('len(tok) == 1 && tok[0] >= '0' && tok[0] <= '9''), and returns
	// '0, .Bad_Digit' otherwise.


	// Loop over '[]string{"3", "5", "STOP", "9"}' using 'v := decode_token(tok) or_break'
	// to sum the valid tokens before "STOP" (expected: 8).


	// Loop over '[]string{"3", "#skip", "5", "bad", "4"}' first with 'or_continue'
	// (summing 3 + 5 + 4 = 12), then write a second loop that captures
	// 'v, err := decode_token(tok)' explicitly so it skips '.Comment_Token' with
	// 'continue' but breaks and prints the failing token on '.Stop_Token' or '.Bad_Digit'.
}

main :: proc() {

	fmt.println("=== 1. Filtering passes with or_continue ===")
	filtering_with_or_continue()

	fmt.println("\n=== 2. Early exit with or_break and labels ===")
	stopping_with_or_break()

	fmt.println("\n=== 3. Enum-based or_break and trade-offs ===")
	enum_errors_with_or_break()
}
