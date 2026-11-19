// odin run 020_booleans_and_comparisons.odin -file

package main

import "core:fmt"

/*
Along with standard 1-byte 'bool', Odin provides explicit-width boolean types:
b8 (1 byte), b16 (2 bytes), b32 (4 bytes), and b64 (8 bytes).

In systems programming, boolean size matters whenever your struct layout must
match an external binary ABI. Win32 defines BOOL as a 4-byte integer, and GPU
uniform buffers in Vulkan or DirectX align boolean flags to 4 bytes, matching
b32 directly without manual integer conversions.

This file is split into three small sections called from main at the bottom so
you can read top to bottom and run the program at any point.
*/

sized_booleans_and_memory_layout :: proc() {

	/*
	Comparison operators (==, !=, <, <=, >, >=) produce an untyped boolean
	result, so a comparison like 10 < 20 adapts directly into bool, b8, or b32
	without a cast. Typed boolean variables, however, never implicitly convert
	between widths (bool cannot be assigned straight to b32 without an explicit
	conversion such as bool(win32_flag) or b32(is_active)), keeping struct ABI
	layouts strict.
	*/

	// Comparing 1-byte bool against 4-byte b32 using size_of:

	is_active: bool = true
	win32_flag: b32 = true
	fmt.printfln("is_active = %v (%vB), win32_flag = %v (%vB)", is_active, size_of(bool), win32_flag, size_of(b32))

	// Reassign win32_flag to the untyped comparison result 10 < 20 (no cast
	// needed!) and print win32_flag afterward.


	// Declare flag_b8: b8 = false, flag_b16: b16 = true, and flag_b64: b64 = false.
	// Print all three values alongside size_of(b8), size_of(b16), and size_of(b64).


	// Try uncommenting below to verify that distinct boolean types do not mix
	// implicitly, then fix it with an explicit bool(win32_flag) conversion:
	// is_active = win32_flag


	// Test converting a boolean into an integer width for bitmasks or ABI structs:
	// declare raw_flag := u32(is_active) and print raw_flag (expected: 1).
}

comparisons_and_logical_operators :: proc() {

	/*
	Logical operators combine boolean values into compound conditions:
	'&&' (AND) is true only when both sides are true, '||' (OR) is true when
	either side is true, and '!' (NOT) flips true to false and false to true.

	Suppose temp := 22. Evaluating (temp >= 18) && (temp <= 26) checks whether
	temp sits inside [18, 26] and evaluates to true. Note that Odin's '==' and
	'!=' also compare strings by their UTF-8 byte contents rather than pointer
	addresses.
	*/

	// Checking a passing score threshold:

	min_score := 50
	fmt.printfln("Passing threshold met: %v", min_score >= 50)

	// Declare has_permission := true and is_admin := false. Compute three
	// booleans and print all three with fmt.printfln:
	// allowed (has_permission && is_admin), can_view (has_permission || is_admin),
	// and denied (!has_permission).


	// Declare score := 85 and evaluate a compound range condition checking that
	// score is at least 0, at most 100, and not equal to 50. Also compare two
	// strings ("odin" == "odin") and print both boolean results.


	// Combine '!' with grouping parentheses: declare is_locked := false and
	// has_key := true, then evaluate can_enter := !is_locked && has_key and
	// print can_enter.
}

short_circuit_evaluation_and_guards :: proc() {

	/*
	Both '&&' and '||' use short-circuit evaluation from left to right. In
	'false && rhs', Odin jumps straight past 'rhs' without executing it because
	the overall AND can never become true. In 'true || rhs', Odin jumps straight
	past 'rhs' because the overall OR is already guaranteed to be true.

	Suppose divisor := 0. In (divisor != 0) && (100 / divisor > 5), the left
	side is false, so the CPU skips 100 / divisor completely and prevents a
	divide-by-zero crash!
	*/

	// Short-circuit baseline:

	ready := false
	fmt.printfln("Short-circuit baseline: %v", ready && (10 > 2))

	// Declare divisor := 0 and compute:
	// safe_to_divide := (divisor != 0) && (100 / divisor > 5)
	// Print safe_to_divide to confirm short-circuiting prevented division by zero.


	// Practice a slice bounds guard: declare nums := []int{10, 20, 30} and
	// idx := 5, then compute:
	// valid_slot := (idx >= 0 && idx < len(nums)) && (nums[idx] > 0)
	// Print valid_slot to verify the out-of-bounds read nums[idx] never runs.


	// Practice a nil-pointer guard: declare ptr: ^int = nil and compute:
	// safe_ptr := (ptr != nil) && (ptr^ == 42)
	// Print safe_ptr, then test an OR fallback with is_cached := true || (100 / divisor == 0).
}

main :: proc() {

	fmt.println("=== 1. Sized booleans and memory layout ===")
	sized_booleans_and_memory_layout()

	fmt.println("\n=== 2. Comparisons and logical operators ===")
	comparisons_and_logical_operators()

	fmt.println("\n=== 3. Short-circuit evaluation and guards ===")
	short_circuit_evaluation_and_guards()
}
