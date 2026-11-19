// odin run 360_bounds_check_and_type_assert_directives.odin -file

package main

import "core:fmt"

/*
By default, Odin checks every array/slice/string index (0 <= i < len(arr)) and
every union or 'any' type assertion (u.(T)) at runtime, panicking loudly instead
of corrupting adjacent memory. When a hot inner loop has already proven its
bounds once up front, directive toggles let you strip or enforce those checks
locally without disabling safety for the whole program:

    #no_bounds_check   disables index checks on the attached statement, loop, or proc
    #bounds_check      forces index checks ON even under CLI -no-bounds-check
    #no_type_assert    skips runtime tag checks on union/any assertions u.(T)
    #type_assert       forces runtime tag checks ON even under CLI -no-type-assert
*/

bounds_check_directives :: proc() {

	/*
	Always verify lengths once with assert(...) right before entering a
	#no_bounds_check loop. Suppose a 2D image of width * height pixels sits in
	a flat slice: checking assert(len(grid) >= width * height) once before the
	nested loops guarantees every grid[y * width + x] access is in range,
	letting #no_bounds_check remove the per-pixel bounds compare cleanly.
	*/

	// Here is a live check reading a fixed array inside #no_bounds_check:

	numbers := [4]int{10, 20, 30, 40}
	first := 0
	#no_bounds_check {
		first = numbers[0]
	}
	fmt.printfln("First element via #no_bounds_check: %d", first)

	// Write dot_product_fast :: proc(a, b: []f32) -> f32 above main that
	// checks assert(len(a) == len(b)) once at the top and accumulates
	// sum += a[i] * b[i] inside '#no_bounds_check for i in 0..<len(a)'.
	// Call it here with []f32{1, 2, 3} and []f32{4, 5, 6} (expected: 32).


	// Write sum_flat_grid :: proc(grid: []int, width, height: int) -> int above
	// main that checks assert(width >= 0 && height >= 0 && len(grid) >= width * height)
	// once up front, then uses '#no_bounds_check for y in 0..<height' and an inner
	// 'for x in 0..<width' to sum grid[y * width + x]. Test it on a 3x2 grid.


	// Read numbers[3] inside a '#bounds_check { ... }' block so safety stays
	// enforced even if someone compiles with -no-bounds-check.
}

type_assert_directives :: proc() {

	/*
	Type assertions like p.(int) verify a tagged union's active variant at
	runtime. You can force that tag check with #type_assert or omit it in a
	branch where an earlier check already guaranteed the tag via #no_type_assert.
	*/

	fmt.println("Define Payload :: union { int, string } and unwrap it with #type_assert.")

	// Define Payload :: union { int, string }, declare p: Payload = 42, and
	// unwrap val := p.(int) inside a '#type_assert { ... }' block and print val.


	// Write an 'if _, ok := p.(int); ok { ... }' check and unwrap p.(int) inside
	// a '#no_type_assert { ... }' block now that the tag is known.
}

main :: proc() {

	fmt.println("=== 1. #bounds_check and #no_bounds_check ===")
	bounds_check_directives()

	fmt.println("\n=== 2. #type_assert and #no_type_assert ===")
	type_assert_directives()
}
