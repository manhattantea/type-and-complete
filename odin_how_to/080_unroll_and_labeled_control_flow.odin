// odin run 080_unroll_and_labeled_control_flow.odin -file

package main

import "core:fmt"

/*
Odin gives you two sharp low-level control-flow tools: compile-time loop
unrolling ('#unroll for') and labeled jumps ('break label' / 'continue label')
that work not only on nested loops, but also on 'if' and 'switch' blocks.

Instead of inventing boolean exit flags or scattering goto labels, you can name
the exact outer construct you want to exit or advance.

This file is split into three small sections called from main at the bottom so
you can read top to bottom and run the program at any point.
*/

Direction :: enum {
	North,
	East,
	South,
	West,
}

compile_time_unroll :: proc() {

	/*
	When we put '#unroll' in front of a 'for' loop, it asks the compiler to
	duplicate the loop body once per iteration at compile time, removing the
	runtime loop counter and branch instruction.

	    Suppose powers: [4]int:
	        #unroll for i in 0..<4 {
	            powers[i] = 1 << uint(i)
	        }
	    Odin expands this at compile time into four flat assignments (1, 2, 4, 8).

	Because '#unroll for' expands at compile time, the loop bounds must be
	compile-time constants—which works naturally for both constant integer
	ranges (0..<4) and iterating over an 'enum' type (for dir in Direction).
	*/

	// Here is an unrolled range loop computing powers of 2:

	powers: [4]int
	#unroll for i in 0..<4 {
		powers[i] = 1 << uint(i)
	}
	fmt.printfln("Unrolled powers of 2: %v", powers)

	// Write an #unroll for loop over the Direction enum:
	// #unroll for dir in Direction
	// Print each variant name and its integer backing value int(dir).


	// Combine #unroll for over Direction with an enumerated lookup array:
	// declare steps := [Direction][2]int{
	//     .North = {0, -1}, .East = {1, 0}, .South = {0, 1}, .West = {-1, 0},
	// }
	// Use #unroll for dir in Direction to print each direction and steps[dir].


	// Test the compile-time bound requirement:
	// declare runtime_limit := 4 and try uncommenting the line below to see Odin
	// reject #unroll on a non-constant runtime bound:
	// #unroll for i in 0..<runtime_limit { fmt.println(i) }
}

labeled_loop_break_and_continue :: proc() {

	/*
	Inside nested loops, bare 'break' and 'continue' always act on the innermost
	loop. Prefixing an outer loop with a label such as 'row_scan:' lets you:
	    continue row_scan   abandon the rest of the inner loop and start the next outer pass
	    break row_scan      exit both the inner and outer loops at once

	    Suppose grid := [2][3]int{{1, -1, 9}, {4, 5, 6}}:
	        row_scan: for row, y in grid {
	            for val, x in row {
	                if val < 0 do continue row_scan   // skips 9, jumps to row 1
	            }
	        }
	*/

	// Here is a 3x3 grid we will search in the drills below:

	grid := [3][3]int{
		{1, 2, 3},
		{4, -1, 6},
		{7, 8, 9},
	}
	fmt.printfln("Grid center cell grid[1][1] = %v", grid[1][1])

	// Practice continue outer_label on grid:
	// write row_scan: for row, y in grid and inner for val, x in row
	// Whenever val < 0, print a message saying row y is skipped and execute
	// continue row_scan. Print every non-negative cell visited so you confirm
	// cell 6 in row 1 is skipped while row 2 (7, 8, 9) still runs.


	// Practice break outer_label on a coordinate search:
	// write search_grid: for y in 0..<3 and inner for x in 0..<3
	// When x == 1 && y == 2, print the found coordinates and immediately exit
	// both loops using break search_grid.


	// Write one more nested loop pair labeled outer: for r in 0..<2 and inner
	// for c in 0..<3 where hitting r == 1 && c == 1 prints "Hit target" and
	// exits with break outer without using any extra boolean flag variable.
}

labeled_if_and_switch_blocks :: proc() {

	/*
	Odin also lets you label 'if' and 'switch' statements! Instead of nesting
	four levels of 'if ok { if step2 { ... } }', you can open a labeled block
	and 'break' out of it early whenever a precondition fails. Any 'defer' inside
	that block still runs cleanly on exit.
	*/

	// Here is a short labeled 'if' block demonstration:

	fast_check: if true {
		if 2 + 2 != 4 do break fast_check
		fmt.println("fast_check passed")
	}

	// Write a labeled 'if' block validate: if true { ... } simulating a 2-step check:
	// print "Step 1 OK", declare step2_failed := true, use:
	// if step2_failed do break validate
	// and place fmt.println("All steps passed") below it so you confirm the
	// trailing line is skipped when step2_failed is true.


	// Add a defer fmt.println("validate cleanup") at the top of a labeled
	// validate_defer: if true { ... } block that breaks early, confirming defer
	// still executes on a labeled break.


	// Practice a labeled 'switch' block:
	// write dispatch: switch code := 200; code { case 200: ... }
	// Inside case 200, declare dry_run := true, exit early with:
	// if dry_run do break dispatch
	// before a trailing fmt.println("Committed response") line.
}

main :: proc() {

	fmt.println("=== 1. Compile-time #unroll for ===")
	compile_time_unroll()

	fmt.println("\n=== 2. Labeled loop break and continue ===")
	labeled_loop_break_and_continue()

	fmt.println("\n=== 3. Labeled if and switch blocks ===")
	labeled_if_and_switch_blocks()
}
