// odin run 040_if_and_init_statements.odin -file

package main

import "core:fmt"

/*
Odin's 'if' statement strips away parentheses and tightens variable lifetimes so
conditions stay readable and temporary results cannot leak into outer code.

Unlike C, you never wrap conditions in parentheses, and every branch requires
either braces or the single-statement 'do' keyword. That rule eliminates C's
dangling-else bug completely because the compiler never has to guess which 'if'
owns an 'else'.

This file is split into three small sections called from main at the bottom so
you can read top to bottom and run the program at any point.
*/

lookup_port :: proc(service: string) -> (port: u16, ok: bool) {

	if service == "http"  do return 80, true
	if service == "https" do return 443, true
	if service == "ssh"   do return 22, true
	return 0, false
}

branches_and_do_clause :: proc() {

	/*
	When we write 'do' after an 'if' or 'else' header, it tells Odin that the
	branch body is strictly one statement, so curly braces are optional.

	    Suppose temperature := 32:
	        if temperature > 30 do fmt.println("Hot!")

	For multi-line work or chained checks, switch to braces with 'else if' and
	'else'. Notice there are no parentheses around any condition.
	*/

	// Here is a quick one-line 'if ... do' guard:

	temperature := 32
	if temperature > 30 do fmt.printfln("Alert: %vC exceeds 30C threshold!", temperature)

	// Write an if / else if / else chain inspecting temperature:
	// - When temperature > 30, print "Weather: Hot"
	// - Else when temperature >= 15, print "Weather: Pleasant"
	// - Otherwise, print "Weather: Cold"


	// Practice 'do' on both sides of an if/else branch:
	// declare is_humid := true and write a single-line branch using:
	// if is_humid do fmt.println("Humid air") else do fmt.println("Dry air")


	// Combine multiple conditions without outer parentheses:
	// declare wind_kph := 28 and has_rain := false
	// Print "Storm watch" when wind_kph > 25 && has_rain is true,
	// else if wind_kph > 20 && !has_rain is true print "Breezy and dry",
	// otherwise print "Calm".
}

scoped_init_and_multi_return :: proc() {

	/*
	Most bugs from temporary variables come from declaring a helper variable
	above an 'if' and accidentally reusing it thirty lines later. Odin solves
	this with an optional initialization clause right inside the 'if' header:

	    Suppose base := 28:
	        if doubled := base * 2; doubled > 50 {
	            fmt.println(doubled)   // doubled exists here (56)
	        } else {
	            fmt.println(doubled)   // doubled still exists in else
	        }
	        // doubled is gone after this closing brace!

	Because Odin procedures return (value, ok) pairs instead of sentinel -1 or
	null values, combining multi-return calls with an 'if' init statement gives
	you a tight, self-contained lookup pattern:

	    if port, ok := lookup_port("https"); ok { ... }

	Both 'port' and 'ok' live across the entire if / else if / else chain and
	vanish as soon as the chain ends.
	*/

	// Here is a live multi-return lookup scoped to an if block:

	if port, ok := lookup_port("https"); ok {
		fmt.printfln("Found service 'https' on port %v", port)
	}

	// Write an if statement with an initialization clause using temperature := 28:
	// if heat_index := temperature * 2; heat_index > 50
	// Print heat_index inside both the if branch and the else branch.
	// Then try uncommenting a print of heat_index below the closing brace to
	// confirm Odin rejects out-of-scope access.


	// Practice a failing multi-return lookup with an else branch:
	// write if port, ok := lookup_port("ftp"); ok { ... } else { ... }
	// Print the port when ok is true, and print both ok and port inside else to
	// confirm both variables remain readable across the else branch.


	// Chain an else if with its own scoped init clause:
	// look up "telnet" first; in the else if branch bind fallback, fb_ok := lookup_port("ssh")
	// and check fb_ok so you only fall back when the primary lookup fails.


	// Write a helper procedure above main named:
	// parse_percent :: proc(n: int) -> (clamped: int, valid: bool)
	// Return n, true when 0 <= n && n <= 100, and return 0, false otherwise.
	// Test parse_percent(85) and parse_percent(120) here using multi-return
	// if val, ok := parse_percent(...); ok blocks.
}

runtime_if_vs_compile_time_when :: proc() {

	/*
	Beginners often mix up 'if' and 'when'. Even when an 'if' condition is a
	compile-time constant like false, 'if' is still a runtime statement: Odin
	type-checks EVERY branch of an 'if', including branches that can never run.

	By contrast, 'when' is evaluated during compilation. It emits zero runtime
	branch instructions and skips type-checking any untaken branch completely.
	*/

	// Here is a constant runtime 'if' (both branches are type-checked):

	RUNTIME_FLAG :: false
	if RUNTIME_FLAG {
		fmt.println("Runtime branch ran")
	} else {
		fmt.println("Runtime if always type-checks both branches even on false")
	}

	// Write a compile-time when RUNTIME_FLAG { ... } else { ... } block right below.
	// Inside the untaken when branch, try uncommenting a call to an undeclared
	// name like missing_helper() to confirm it compiles cleanly, then try putting
	// that same call inside an untaken 'if false { ... }' branch to see the
	// compiler reject it.


	// Contrast runtime vs compile-time conditions:
	// declare env := "prod" and write an 'if env == "dev"' branch printing a log.
	// Try temporarily changing 'if' to 'when' on that runtime variable to see
	// Odin explain why 'when' requires a compile-time constant expression.
}

main :: proc() {

	fmt.println("=== 1. Branches and the do clause ===")
	branches_and_do_clause()

	fmt.println("\n=== 2. Scoped init statements and multi-return lookups ===")
	scoped_init_and_multi_return()

	fmt.println("\n=== 3. Runtime if vs compile-time when ===")
	runtime_if_vs_compile_time_when()
}
