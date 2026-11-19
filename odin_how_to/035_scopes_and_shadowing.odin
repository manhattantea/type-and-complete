// odin run 035_scopes_and_shadowing.odin -file

package main

import "core:fmt"

/*
Odin separates scoping into two clean rules based on where a declaration sits:
file/package scope is completely order-independent (eliminating C forward
declarations and header files), while procedure and block lexical scope runs
strictly top-to-bottom from a variable's declaration line down to its closing '}'.

Knowing the boundary between outer mutation ('=') and inner shadowing (':=')
prevents one of the sneakiest bugs in colon-declaration languages.

This file is split into three small sections called from main at the bottom so
you can read top to bottom and run the program at any point.
*/

package_scope_order_independence :: proc() {

	/*
	Top-level constants ('::'), types (struct, enum, union), and procedures
	can be referenced anywhere in the package even when their definitions sit
	further down in the file. Odin resolves package-level symbols in multiple
	compiler passes rather than scanning a single pass top-to-bottom like C.
	*/

	// Referencing FILE_SCOPE_MAGIC even though it is declared below:

	fmt.printfln("FILE_SCOPE_MAGIC from below = 0x%X", FILE_SCOPE_MAGIC)

	// Declare a constant MAX_SESSIONS :: 128 at file scope below this procedure
	// (near FILE_SCOPE_MAGIC or below main) and print MAX_SESSIONS here.


	// Write a file-scope helper procedure bottom_helper :: proc(x: int) -> int
	// below this procedure (returning x * 2) and call bottom_helper(21) here
	// without any forward declaration.


	// Define a tiny file-scope struct Point :: struct { x, y: int } below main
	// and construct Point{3, 4} inside this procedure to confirm types also
	// follow order-independent package scope.
}

lexical_blocks_and_lifetimes :: proc() {

	/*
	Inside any procedure, variables live only from the line where they are
	declared down to the closing '}' of their enclosing block. You can open an
	anonymous brace block at any time to keep temporary scratch variables
	tightly scoped and let their names be reused cleanly later.

	Suppose outer := 10. Inside '{ temp := 99; outer += 5 }', outer becomes 15
	and stays visible after '}', whereas temp ceases to exist at '}'.
	*/

	// Mutating an outer variable from inside an anonymous brace block:

	outer_score := 50
	{
		bonus := 10
		outer_score += bonus
	}
	fmt.printfln("outer_score after anonymous block = %v", outer_score)

	// Declare counter := 10 and print it. Open an anonymous brace block,
	// add 5 to outer counter (counter += 5), declare block-local temp_val := 99,
	// and print both inside the block. After '}', print counter again to verify
	// the mutation persisted.


	// Try uncommenting a print of temp_val after the closing '}' of your block
	// to verify Odin rejects referencing a variable outside its lexical scope:
	// fmt.println(temp_val)


	// Write two back-to-back anonymous brace blocks that each declare their
	// own local variable named 'scratch': put 'scratch := 1' in the first block
	// and 'scratch := "done"' in the second block, printing each inside its
	// own block to confirm sibling blocks have completely disjoint lifetimes.
}

shadowing_vs_mutation_and_vet :: proc() {

	/*
	Inside a nested brace block, 'if' branch, or 'for' body, writing
	'counter = 20' updates the outer variable, whereas accidentally writing
	'counter := 20' declares a brand-new inner variable that shadows (hides)
	the outer one and vanishes at '}', leaving the outer variable untouched!

	Suppose balance := 100, and inside '{ balance := 200 }' you forget you wrote
	':=' instead of '=': the inner block sees 200, yet outer balance stays 100.
	Passing -vet-shadowing to odin check catches this mistake automatically.
	*/

	// Outer variable baseline:

	mode := "normal"
	fmt.printfln("Outer mode = %v", mode)

	// Declare balance := 100. Open an anonymous brace block and first try
	// shadowing it intentionally with balance := 200; print balance inside
	// (200) and outside (still 100!).


	// Run the shadowing vetter on that shadowed version:
	// odin check 035_scopes_and_shadowing.odin -file -vet-shadowing
	// Watch Odin flag the shadowed inner 'balance', then replace ':=' with '='
	// so the outer balance mutates to 200 cleanly and -vet-shadowing passes.


	// Practice an 'if' init-statement scope: write
	// if doubled := 21 * 2; doubled > 30 { fmt.println("In branch:", doubled) }
	// Notice doubled exists across the 'if'/'else' chain and goes out of scope
	// at its final '}'.
}

// File-scope constant placed below the procedures that reference it:
FILE_SCOPE_MAGIC :: 0xCAFE_BABE

main :: proc() {

	fmt.println("=== 1. Package scope order independence ===")
	package_scope_order_independence()

	fmt.println("\n=== 2. Lexical blocks and lifetimes ===")
	lexical_blocks_and_lifetimes()

	fmt.println("\n=== 3. Shadowing vs mutation and -vet-shadowing ===")
	shadowing_vs_mutation_and_vet()
}
