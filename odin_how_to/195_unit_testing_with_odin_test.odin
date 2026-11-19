// odin test 195_unit_testing_with_odin_test.odin -file

package main

import "core:fmt"
import "core:mem"
import "core:testing"

/*
Odin ships with a built-in test runner invoked via 'odin test <file>.odin -file'
(or 'odin test <dir>' for multi-file packages). Unlike 'odin run', which starts
at 'main :: proc()', 'odin test' discovers every procedure annotated with
'@(test)' taking 't: ^testing.T' and executes them in parallel by default.

Every '@(test)' procedure also runs under a tracking allocator automatically:
if a test forgets to free heap memory it allocated, 'odin test' fails that test
and reports the exact source file and line number of every leaked allocation.

This file lets you run both 'odin run 195_unit_testing_with_odin_test.odin -file'
(calling the section demos from 'main') and 'odin test 195_unit_testing_with_odin_test.odin -file'
(running every '@(test)' procedure).
*/

double_int :: proc(x: int) -> int {

	return x * 2
}

@(test)
test_double_int :: proc(t: ^testing.T) {

	testing.expect_value(t, double_int(21), 42)
}

pure_proc_testing_demo :: proc() {

	/*
	Three core helpers in 'core:testing' cover most unit assertions:
	- 'testing.expect_value(t, actual, expected)' checks equality and logs both
	  the actual and expected values automatically when they differ.
	- 'testing.expect(t, cond, msg)' checks a boolean condition with a plain
	  message string.
	- 'testing.expectf(t, cond, fmt_str, ..args)' formats diagnostic values
	  into the failure message when 'cond' is false.
	*/

	fmt.printfln("double_int(21) = %v (run 'odin test 195_unit_testing_with_odin_test.odin -file' to execute @(test) procs)", double_int(21))

	// Write a pure procedure 'clamp_and_double :: proc(x, lo, hi: int) -> int' at
	// file scope that clamps 'x' into the inclusive range '[lo, hi]' and returns
	// the clamped value multiplied by 2.


	// Write '@(test) test_clamp_and_double :: proc(t: ^testing.T)' at file scope.
	// Use 'testing.expect_value' to check in-range (clamp_and_double(5, 0, 10) -> 10),
	// below-lo (clamp_and_double(-5, 0, 10) -> 0), and above-hi
	// (clamp_and_double(15, 0, 10) -> 20), plus 'testing.expect' on a boundary case.


	// Call 'clamp_and_double(5, 0, 10)' and 'clamp_and_double(15, 0, 10)' here
	// and print both results with fmt.printfln so 'odin run' exercises them too.
}

allocation_and_leak_detection_demo :: proc() {

	/*
	Suppose a procedure returns a freshly allocated slice. During 'odin test',
	Odin's default test runner wraps 'context.allocator' in a 'mem.Tracking_Allocator'
	for you, so missing 'defer delete(res)' fails the test automatically.

	You can also wire up 'mem.Tracking_Allocator' explicitly inside a procedure
	or '@(test)' whenever you want to assert 'len(track.allocation_map) == 0'
	and 'len(track.bad_free_array) == 0' directly over a sub-allocator scope.
	Notice the 'defer' order below: 'delete(nums, tracked_alloc)' runs before
	'mem.tracking_allocator_destroy(&track)' so the map is inspected and freed
	before the tracker itself is destroyed.
	*/

	track: mem.Tracking_Allocator
	mem.tracking_allocator_init(&track, context.allocator)
	defer mem.tracking_allocator_destroy(&track)

	tracked_alloc := mem.tracking_allocator(&track)
	nums := make([]int, 4, tracked_alloc)
	nums[0] = 10
	delete(nums, tracked_alloc)
	fmt.printfln("Explicit tracker check: leaks=%v, bad_frees=%v", len(track.allocation_map), len(track.bad_free_array))

	// Write 'build_squares :: proc(count: int) -> []int' at file scope that
	// allocates 'out := make([]int, count)', fills 'out[i] = i * i', and returns 'out'.


	// Write '@(test) test_build_squares_no_leak :: proc(t: ^testing.T)' at file
	// scope calling 'sq := build_squares(5)' with 'defer delete(sq)'. Assert
	// 'len(sq) == 5' and 'sq[4] == 16' with 'testing.expect_value'.
	// Try commenting out 'defer delete(sq)' and running 'odin test 195_unit_testing_with_odin_test.odin -file'
	// to watch Odin catch the memory leak automatically.


	// Write '@(test) test_explicit_tracking_allocator :: proc(t: ^testing.T)' at
	// file scope that initializes 'track: mem.Tracking_Allocator' against
	// 'context.allocator', assigns 'tracked := mem.tracking_allocator(&track)',
	// allocates and appends to a '[dynamic]int' using 'tracked', calls
	// 'delete(arr)' (or wraps the allocation inside an inner '{ ... }' block
	// with 'defer delete(arr)') BEFORE checking
	// 'testing.expect_value(t, len(track.allocation_map), 0)' and
	// 'testing.expect_value(t, len(track.bad_free_array), 0)', and cleans up with
	// 'mem.tracking_allocator_destroy(&track)'.
}

edge_cases_and_test_flags_demo :: proc() {

	/*
	Because tests run concurrently by default, keep every '@(test)' procedure
	isolated from shared mutable globals (or pass '-define:ODIN_TEST_THREADS=1'
	when diagnosing order-sensitive behavior).

	Suppose you want to verify a table of input/output pairs in a single loop.
	Using 'testing.expectf(t, got == tc.want, "input %v: got %v, want %v", tc.in, got, tc.want)'
	prints the exact failing test case instead of a bare line number.
	*/

	fmt.println("Use testing.expectf in table-driven checks to pinpoint failing inputs.")

	// Write 'safe_ratio :: proc(num, den: int) -> (q: int, ok: bool)' at file scope
	// returning '0, false' when 'den == 0' and 'num / den, true' otherwise.


	// Write '@(test) test_safe_ratio :: proc(t: ^testing.T)' at file scope testing
	// both valid division (20, 4 -> 5, true) and division by zero (20, 0 -> 0, false)
	// with 'testing.expect_value' and 'testing.expectf'.


	// Call 'safe_ratio(20, 4)' and 'safe_ratio(20, 0)' here and print both
	// '(q, ok)' pairs with fmt.printfln.
}

main :: proc() {

	fmt.println("=== 1. Core assertions and pure procedure tests ===")
	pure_proc_testing_demo()

	fmt.println("\n=== 2. mem.Tracking_Allocator and leak detection ===")
	allocation_and_leak_detection_demo()

	fmt.println("\n=== 3. Error-path tests and table-driven checks ===")
	edge_cases_and_test_flags_demo()
}
