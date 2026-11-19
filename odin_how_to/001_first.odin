// odin run 001_first.odin -file

package main

import "core:fmt"

/*
Every Odin file begins with a package declaration (package main for an
executable entry point) followed by any import statements. Writing
import "core:fmt" pulls in formatting and printing procedures from Odin's
standard 'core' library collection.

Execution starts at main :: proc(). When we write '::', it binds a name at
compile time to a procedure, constant, or type definition. Unlike C or C++,
no header files or forward declarations are needed, and semicolons at line
ends are omitted.

This file is split into three small sections called from main at the bottom so
you can read top to bottom and run the program at any point.
*/

packages_imports_and_comments :: proc() {

	/*
	Odin supports single-line comments with '//' and block comments with paired
	slashes and stars. Unlike C, Odin tracks block comment nesting depth
	properly. Suppose you wrap a whole block of code in a block comment that
	already contains an inner '/* note */' comment: C stops at the first
	closing marker and turns the remaining code into syntax errors, whereas
	Odin matches each opening marker to its paired closing marker.
	*/

	// Here is the traditional first Odin greeting using fmt.println:

	fmt.println("Hellope!")

	// Write a nested block comment containing an inner block comment around a
	// short note of your own to verify Odin compiles nested comments cleanly:
	// /* outer /* inner */ still inside outer */


	// Call fmt.println with three separate arguments ("Hello from", "Odin", 2026)
	// and observe how fmt.println places a single space between each argument
	// automatically before ending with a newline.


	// Try passing a multi-word mix of strings, integers, and booleans to
	// fmt.println("Ready:", true, "Workers:", 4) to confirm fmt.println accepts
	// any combination of types with zero format strings.
}

print_vs_println_and_spacing :: proc() {

	/*
	The core:fmt package gives you two unformatted printing helpers:
	fmt.print writes its arguments straight to stdout with no automatic newline,
	joining strings directly unless you include spacing yourself.
	fmt.println inserts a space between each argument and appends a newline.

	Suppose you call fmt.print("HP:", 100) followed by fmt.println("ok"):
	the terminal shows 'HP:100ok' because fmt.print neither inserts spaces
	between arguments nor starts a new line.
	*/

	// Joining two print calls onto a single output line:

	fmt.print("Status: ")
	fmt.println("Ready")

	// Use fmt.print to output "Player Status -> " (with the trailing space and
	// no newline), then on the next line use fmt.println to print "Score:", 100,
	// "Active:", true.


	// Build one output line out of three separate fmt.print calls (for example
	// "[tick ", 4, "]") followed by an empty fmt.println() to finish the line.


	// Test what happens when fmt.print receives two adjacent numbers: call
	// fmt.print(10, 20) followed by fmt.println(" <- no space added") to observe
	// how fmt.print concatenates arguments back-to-back.
}

formatted_verbs_and_type_inspection :: proc() {

	/*
	When you need exact control over layout or want to inspect types, use
	fmt.printf (no trailing newline) or fmt.printfln (automatic newline). Unlike
	Jai's bare '%', Odin always requires a format verb character right after '%':
	    %v   default formatting for any Odin value
	    %T   the exact compile-time Odin type name
	    %#v  Odin literal syntax (quotes around strings, field names on structs)
	    %q   double-quoted string or character literal
	    %%   a literal percent sign

	Suppose count := 7 and tag := "boss". Calling
	fmt.printfln("val=%v type=%T lit=%#v", tag, tag, tag) prints:
	val=boss type=string lit="boss"
	*/

	// Inspecting a starter integer with %v and %T:

	starter_id := 1
	fmt.printfln("Starter -> Value: %v, Type: %T", starter_id, starter_id)

	// Pass the integer 42 three times to fmt.printfln with the format string
	// "Int    -> Value: %v, Type: %T, Syntax: %#v"


	// Call fmt.printfln with "String -> Value: %v, Type: %T, Syntax: %#v",
	// passing "Odin" three times, and compare %v against %#v in the output.


	// Combine three different types in one formatted call: declare level := 3,
	// speed := 1.25, and title := "Scout", then print all three values and their
	// types using %v and %T in a single fmt.printfln call.


	// Format a table row using fmt.printf twice on the same line (ending the
	// second call with "\n"), printing a label with %q and a padded integer
	// with %04d (for example, id = 7 prints as 0007).


	// Print a completion rate of 95 followed by a literal percent sign using
	// fmt.printfln and the escaped %% verb ("Completion rate: %v%%").
	// Try uncommenting below to see Odin reject a bare % without a verb:
	// fmt.printfln("Broken: %", 42)
}

main :: proc() {

	fmt.println("=== 1. Packages, imports, and comments ===")
	packages_imports_and_comments()

	fmt.println("\n=== 2. print vs println and spacing ===")
	print_vs_println_and_spacing()

	fmt.println("\n=== 3. Formatted verbs and type inspection ===")
	formatted_verbs_and_type_inspection()
}
