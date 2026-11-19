// odin run 160_or_return_error_propagation.odin -file

package main

import "base:runtime"
import "core:fmt"

/*
Checking error return values at every step by hand quickly fills a procedure
with repetitive 'if err != nil { return ..., err }' blocks. Odin gives you a
single postfix operator, 'or_return', to propagate failures up the call stack
without hiding control flow behind exceptions.

When we write 'or_return' at the end of a call, it means "inspect the very last
return value; if it signals a failure, return immediately from the enclosing
procedure using that error, otherwise strip the status value and hand me the
rest". What counts as a failure depends on the trailing return type:
- For a 'bool', 'false' fails and 'true' succeeds.
- For an 'enum', 'union', or pointer, any non-zero / non-nil value fails, while
  0 or 'nil' succeeds.

This file walks through boolean propagation, zero-is-success error enums with
'@(require_results)', and combining multiple error types using 'union #shared_nil'
alongside '#optional_allocator_error'.
*/

non_negative :: proc(x: int) -> (val: int, ok: bool) {

	if x < 0 do return 0, false
	return x, true
}

double_non_negative :: proc(x: int) -> (res: int, ok: bool) {

	v := non_negative(x) or_return
	return v * 2, true
}

boolean_ok_propagation :: proc() {

	/*
	Suppose you call 'v := non_negative(-5) or_return' inside 'double_non_negative'.
	Because 'non_negative(-5)' returns '(0, false)', 'or_return' sees 'false' on
	the trailing 'bool', assigns 'ok = false' on 'double_non_negative', and exits
	immediately with '(0, false)'. When you pass '21', 'non_negative(21)' returns
	'(21, true)', so 'or_return' strips 'true' and binds 'v = 21'.

	If a called procedure returns only a status value with no payload (such as
	'proc(x: int) -> bool'), you can write 'check_it(x) or_return' as a
	standalone statement.
	*/

	res, ok := double_non_negative(21)
	fmt.printfln("double_non_negative(21) -> res = %v, ok = %v", res, ok)

	bad_res, bad_ok := double_non_negative(-3)
	fmt.printfln("double_non_negative(-3) -> res = %v, ok = %v", bad_res, bad_ok)

	// Write a procedure named 'clamp_positive :: proc(x, limit: int) -> (val: int, ok: bool)'
	// at file scope that returns '0, false' when 'x <= 0', clamps values above
	// 'limit' down to 'limit', and returns 'val, true'. Then write
	// 'sum_two_positives :: proc(a, b: int) -> (total: int, ok: bool)' that
	// unwraps both inputs with 'or_return' and returns 'va + vb, true'.


	// Call 'sum_two_positives(12, 30)' and 'sum_two_positives(12, -1)' here and
	// print both '(total, ok)' pairs with fmt.printfln.


	// Write a single-return validation procedure 'ensure_even :: proc(n: int) -> bool'
	// (returning 'n % 2 == 0') and a procedure 'half_if_even :: proc(x: int) -> (half: int, ok: bool)'
	// that calls 'ensure_even(x) or_return' as a standalone statement before
	// returning 'x / 2, true'. Call 'half_if_even' on 14 and 7 and print results.
}

error_enums_and_require_results :: proc() {

	/*
	Booleans tell a caller that something failed, but not why. In Odin, error
	enums solve this using the zero-is-success convention: place 'None' as the
	very first variant so its integer value is 0. Because Odin zero-initializes
	unassigned variables and named returns, any untouched error variable
	automatically starts in the '.None' state, and 'or_return' treats any
	non-zero variant as a failure to propagate upward.

	    Suppose 'Parse_Error :: enum { None, Empty_String, Invalid_Header }':
	    'Parse_Error.None' is 0, while '.Empty_String' is 1 and '.Invalid_Header' is 2.

	When we put '@(require_results)' in front of a procedure declaration, it
	means the compiler rejects any call site that silently throws away the
	return values. That turns forgotten error checks into immediate compile
	errors instead of silent runtime bugs.
	*/

	fmt.println("Error enums put None at value 0 so zero-initialization means success.")

	// Define 'Parse_Error :: enum { None, Empty_String, Invalid_Header, Out_Of_Bounds }'
	// at file scope so procedures across the file can share it.


	// Write '@(require_results) check_header :: proc(s: string) -> (body: string, err: Parse_Error)'
	// at file scope. Return '"", .Empty_String' if 'len(s) == 0', return
	// '"", .Invalid_Header' if 'len(s) < 4 || s[:4] != "HDR:"', and otherwise
	// return 's[4:], .None'.


	// Write '@(require_results) parse_payload :: proc(s: string) -> (code: int, err: Parse_Error)'
	// that unwraps 'body := check_header(s) or_return', returns '0, .Out_Of_Bounds'
	// when 'len(body) == 0', and otherwise returns 'len(body), .None'.


	// Call 'parse_payload' on "HDR:packet_ok", "", "BAD_INPUT", and "HDR:" here,
	// capturing both 'code' and 'err' and printing them with fmt.printfln
	// (expected for "HDR:packet_ok": code = 9, err = None).
	//
	// Try calling 'parse_payload("bad")' without capturing its return values to
	// observe the '@(require_results)' compiler error.
}

alloc_scratch_bytes :: proc(count: int) -> (buf: []u8, err: runtime.Allocator_Error) {

	if count <= 0 do return nil, .Invalid_Argument
	buf = make([]u8, count) or_return
	return buf, .None
}

shared_nil_unions_and_allocator_errors :: proc() {

	/*
	Real procedures often call steps that fail with different error types, such
	as a 'Parse_Error' from text validation and a 'runtime.Allocator_Error' from
	heap allocation. If you combine them into a plain 'union { Parse_Error, runtime.Allocator_Error }',
	the union has three distinct "no error" values: 'nil', 'Parse_Error.None',
	and 'runtime.Allocator_Error.None'. Checking 'err == nil' would miss '.None'!

	When we write 'union #shared_nil { Parse_Error, runtime.Allocator_Error }', it
	tells Odin that every member type's zero value ('.None' / 'nil') collapses
	into the union's single 'nil' state. Then 'or_return' can widen either
	'Parse_Error' or 'runtime.Allocator_Error' straight into the union, and
	'err == nil' reliably means success.

	Allocator calls like 'make([]u8, n)' carry the '#optional_allocator_error'
	directive, which means they normally return 1 value ('[]u8') if you omit the
	error, or 2 values ('[]u8, runtime.Allocator_Error') when you capture it or
	append 'or_return' as shown in 'alloc_scratch_bytes' above.
	*/

	if sample_buf, alloc_err := alloc_scratch_bytes(8); alloc_err == .None {
		defer delete(sample_buf)
		fmt.printfln("alloc_scratch_bytes(8) -> len = %v, err = %v", len(sample_buf), alloc_err)
	}

	// Define 'Load_Error :: union #shared_nil { Parse_Error, runtime.Allocator_Error }'
	// at file scope.


	// Write '@(require_results) allocate_and_parse :: proc(s: string) -> (buf: []u8, err: Load_Error)'
	// at file scope. Unwrap 'body := check_header(s) or_return', return
	// 'nil, Parse_Error.Out_Of_Bounds' if 'len(body) == 0', then allocate with
	// 'buf = make([]u8, len(body)) or_return' (propagating 'runtime.Allocator_Error'
	// into 'Load_Error'), copy the bytes of 'body' into 'buf', and return 'buf, nil'.


	// Call 'allocate_and_parse("HDR:hello")' and 'allocate_and_parse("BAD_INPUT")'
	// here. When 'err == nil', remember 'defer delete(buf)' and print 'string(buf)';
	// when 'err != nil', switch on 'e in err' to print whether a 'Parse_Error'
	// or 'runtime.Allocator_Error' occurred.
}

main :: proc() {

	fmt.println("=== 1. Boolean ok propagation with or_return ===")
	boolean_ok_propagation()

	fmt.println("\n=== 2. Error enums and @(require_results) ===")
	error_enums_and_require_results()

	fmt.println("\n=== 3. union #shared_nil and #optional_allocator_error ===")
	shared_nil_unions_and_allocator_errors()
}
