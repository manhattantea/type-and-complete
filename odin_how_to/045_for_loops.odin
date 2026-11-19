// odin run 045_for_loops.odin -file

package main

import "core:fmt"

/*
In Odin, there is only one loop keyword: 'for'. There is no 'while' and no
'do-while'.

Instead of splitting iteration across three separate loop constructs, Odin keeps
everything under one roof: range loops, C-style three-part loops, condition-only
loops, infinite loops, and collection loops. Just like 'if', loop headers never
wrap conditions in parentheses, and the loop body must either use braces or a
single-statement 'do' clause.

This file is split into four small sections called from main at the bottom so
you can read top to bottom and run the program at any point.
*/

range_and_c_style_loops :: proc() {

	/*
	When you know your bounds up front, integer range loops are the cleanest way
	to iterate. Odin offers two range operators:

	    0..<n   half-open: visits 0, 1, ..., n - 1 (stops before n)
	    1..=n   inclusive: visits 1, 2, ..., n

	Half-open ranges (0..<n) are the everyday workhorse because you can pass an
	array or slice length straight in without subtracting 1. Odin evaluates both
	bounds once before the loop starts, and the loop counter is read-only inside
	the body so you cannot accidentally corrupt your own iteration.
	*/

	// Here is a quick half-open loop over 0..<4 printing 0 1 2 3:

	for i in 0..<4 {
		fmt.printf("%v ", i)
	}
	fmt.println()

	// Now try an inclusive range loop using 1..=5. Accumulate the sum of 1
	// through 5 into a variable named total (expected: 15) and print it with
	// fmt.printfln.


	/*
	Watch out for a classic systems bug with inclusive ranges when your bounds
	are unsigned integers. Suppose count is u32(0) and you write 0..=count - 1.
	Because an unsigned u32 cannot hold negative numbers, 0 - 1 wraps around to
	4294967295 and turns an empty loop into four billion passes! Writing
	0..<count avoids subtraction completely, so 0..<0 runs zero times.
	*/

	// Declare empty_len: u32 = 0
	// Write a safe half-open loop: for i in 0..<empty_len
	// Print i inside it and confirm nothing prints.
	//
	// Next, see the unsigned wraparound hazard live without hanging your PC:
	// write a second loop using 0..=empty_len - 1
	// Declare failsafe := 0 before it, print i inside, increment failsafe,
	// and break once failsafe >= 3.


	/*
	Range loops always count upward by 1. When you want a custom step (like +2)
	or want to count downward, use a C-style three-part loop:

	    Suppose you want to print even numbers 0, 2, 4:
	        for i := 0; i <= 4; i += 2 {
	            fmt.printf("%v ", i)   // prints: 0 2 4
	        }

	The three parts separated by semicolons do three distinct jobs: 'i := 0'
	creates your counter once before the loop begins, 'i <= 4' checks before
	each pass whether to keep going, and 'i += 2' updates the counter after each
	pass. Odin has no ++ or -- operators, so write i += 1 or i -= 1. Also keep
	countdown counters signed (int rather than u32), because an unsigned variable
	is always >= 0 and wraps around instead of stopping below zero.
	*/

	// Write a C-style loop that counts by twos from 0 through 10 using:
	// for step := 0; step <= 10; step += 2
	// Print each step on one line.
	//
	// Then write a plain C-style for loop going from 10 down to 0 using a
	// signed int counter (i -= 1) and print each number.
}

conditional_and_infinite_loops :: proc() {

	/*
	Because there is no 'while' keyword, a conditional loop is simply 'for' with
	a boolean check, and an infinite loop is bare 'for { ... }'.

	Two keywords steer execution inside any loop:
	'break' exits the loop immediately and jumps past its closing brace.
	'continue' skips the rest of the current pass and jumps back to the header.

	Odin also pairs cleanly with 'defer' inside conditional loops. When we write
	'defer' in front of a statement inside a loop body, it means "run this line
	automatically whenever execution leaves this loop body". Unlike Go (where
	defer waits for the whole function to return), Odin's defer runs at the end
	of each loop pass, even on 'continue' or 'break'.

	    Suppose step := 0 and you run:
	        for step < 4 {
	            defer step += 1
	            if step == 1 do continue   // skips printing 1, defer still runs step += 1
	            if step == 3 do break      // exits loop, defer still runs step += 1 (step becomes 4)
	            fmt.println(step)          // prints 0, then 2
	        }

	Putting your counter update in a defer near the top of the loop prevents the
	classic infinite loop caused by forgetting an increment before 'continue'.
	*/

	// Declare countdown := 3 and write a conditional loop: for countdown > 0
	// Print countdown each pass, subtract 1 from it, and print "Liftoff!" after
	// the loop finishes.


	// Declare ticks := 0 and write an infinite loop: for { ... }
	// Increment ticks += 1 at the top, skip even numbers using:
	// if ticks % 2 == 0 do continue
	// Print odd ticks, and exit with break once ticks >= 5.


	// See loop-scoped defer in action: declare turn := 0 and write a loop:
	// for turn < 6
	// Make the very first line inside the loop body: defer turn += 1
	// Skip even turns with: if turn % 2 == 0 do continue
	// Print odd turns, and break when turn == 5.
	// Print turn after the loop (expected: 6, because defer still ran when
	// break exited after turn hit 5; move the break check above defer to see
	// turn stay 5 instead).
}

collection_and_reference_loops :: proc() {

	/*
	Iterating a fixed array ([N]T) or slice ([]T) directly is much cleaner and
	safer than juggling manual indices. Notice Odin's variable order in
	collection loops: the element value comes first, and the optional index
	comes second.

	    Suppose items := [3]string{"a", "b", "c"}:
	        for val, idx in items {
	            fmt.printfln("%v:%v", idx, val)   // prints 0:a, 1:b, 2:c
	        }

	(If you know Go or Python's enumerate, watch out: those put the index first
	and value second; Odin does the opposite. The exact same shape also decodes
	UTF-8 runes on strings and iterates key, value pairs on maps.)

	When we use '#reverse' in front of a collection loop:

	        #reverse for val, idx in items {
	            fmt.printfln("%v:%v", idx, val)   // prints 2:c, 1:b, 0:a
	        }

	it means Odin starts at the final slot of the array or slice and walks
	backward down to index 0, while still handing you each element's real index.
	Because #reverse walks an existing collection in memory, it does not work on
	plain integer ranges like 0..<5 (for numbers, use a C-style countdown).

	Now consider mutating elements in place. Suppose nums := [3]int{10, 20, 30}:

	        for val in nums {
	            // val += 1   <- compile error: val is a fresh read-only copy
	        }

	        for &val in nums {
	            val += 1      // mutates nums directly -> nums becomes {11, 21, 31}
	        }

	In 'for &val in nums', 'val' is freshly bound by the loop itself (not an
	outer variable defined before the loop); putting '&' before 'val' simply
	tells Odin "bind val straight to each slot inside nums instead of copying
	it", so assigning to val updates the original array in place.
	*/

	// Here is a quick read-only pass over a fixed array:

	scores := [4]int{10, 20, 30, 40}
	for score in scores {
		fmt.printf("%v ", score)
	}
	fmt.println()

	// Walk scores forward using: for score, idx in scores
	// Print both idx and score on each line.
	// Then walk scores backward using: #reverse for score, idx in scores
	// Print idx and score again to verify idx counts from 3 down to 0.
	//
	// Try uncommenting below to see Odin reject #reverse on an integer range:
	// #reverse for i in 0..<5 { fmt.println(i) }


	// Test the value-vs-reference rule directly:
	// declare health := [4]int{25, 50, 75, 100}
	// First try uncommenting the by-value line below to confirm Odin rejects
	// modifying a read-only value copy, then write a loop using:
	// for &hp in health
	// Add 10 to each element in place (hp += 10) and print health afterward to
	// confirm [35, 60, 85, 110].
	//
	// for hp in health { hp += 10 }


	// Practice an everyday min/max scan over a slice:
	// declare readings := []int{18, 42, -5, 31, 9, 54, 12}
	// Initialize low := readings[0] and high := readings[0], iterate over the
	// rest of the slice using: for r in readings[1:]
	// Update low and high whenever r beats the current extreme, and print both.
}

nested_loops_and_traps :: proc() {

	/*
	A 2D array like [3][4]int is 3 rows with 4 integers per row. When one loop
	sits inside another, plain 'break' or 'continue' controls only the inner
	loop. Instead of juggling boolean exit flags, Odin lets you name an outer
	loop with a label so you can jump straight out of both loops at once:

	    Suppose grid := [2][2]int{{1, 2}, {3, -1}}:
	        search: for row, y in grid {
	            for cell, x in row {
	                if cell < 0 do break search   // hits -1 at (y=1, x=1); exits both loops
	            }
	        }

	Similarly, 'continue search' skips straight to the next outer row.

	One last trap to remember is removing elements from a dynamic array while
	iterating over it. A [dynamic]int is a growable heap array created with
	make([dynamic]int) and freed when the procedure exits with
	defer delete(items). Calling ordered_remove(&items, i) deletes slot i and
	slides every later item left by one slot to keep the remaining order intact.

	    Suppose items holds [10, 20, 20, 30] and you remove every 20:
	    Walking forward with i := 0 removes slot 1, so the second 20 slides
	    left into slot 1, and i += 1 jumps straight to slot 2 (30) — leaving
	    [10, 20, 30] with a missed 20! Using 0..<len(items) is worse because
	    the upper bound was frozen before items shrank, panicking out of bounds.
	    Walking backward from i = 3 down to 0 removes slot 2, then slot 1,
	    leaving [10, 30] cleanly.
	*/

	// Build and print a 4x4 multiplication table using nested range loops.
	// Declare table: [4][4]int and fill table[row][col] = (row + 1) * (col + 1)
	// using nested loops: for row in 0..<4 and for col in 0..<4
	// Then walk table with nested collection loops (row_vals in table, then
	// cell in row_vals) to print each row neatly on its own line.


	// Combine nested collection loops with a labeled break on a 2D search:
	// declare grid := [3][4]int{{5, 0, 8, 2}, {0, 3, 9, 4}, {7, -1, 6, 1}}
	// Label the outer loop: search: for row, y in grid
	// Loop cells inside it: for cell, x in row
	// Skip zero cells with continue, print visited non-zero coordinates, and
	// when cell < 0 print the coordinates (y, x) and exit both loops at once
	// using break search.


	// Solve the backward-deletion trap cleanly:
	// declare items := make([dynamic]int) with defer delete(items)
	// Populate it with: append(&items, 1, 2, 2, 3, 2, 4)
	// Notice the two consecutive 2s at indices 1 and 2! Remove every 2 using a
	// signed C-style backward loop: for i := len(items) - 1; i >= 0; i -= 1
	// Call ordered_remove(&items, i) whenever items[i] == 2, then print items
	// afterward (expected: [1, 3, 4]).
}

main :: proc() {

	fmt.println("=== 1. Range and C-style loops ===")
	range_and_c_style_loops()

	fmt.println("\n=== 2. Conditional and infinite loops ===")
	conditional_and_infinite_loops()

	fmt.println("\n=== 3. Collection and reference loops ===")
	collection_and_reference_loops()

	fmt.println("\n=== 4. Nested loops, 2D grids, and traps ===")
	nested_loops_and_traps()
}
