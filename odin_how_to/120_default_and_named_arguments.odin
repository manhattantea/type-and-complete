// odin run 120_default_and_named_arguments.odin -file

package main

import "base:runtime"
import "core:fmt"

/*
In C and Go, every call site must pass every parameter in rigid positional order,
which leads to cryptic calls like 'init_server("127.0.0.1", 8080, 64, false, true)'
where nobody reading the line knows what 'false' and 'true' mean without jumping
to the definition. Odin solves this cleanly with default parameter values and
named arguments, and replaces C's preprocessor '__FILE__', '__LINE__', and '#expr'
macros with type-safe compile-time caller directives.

This file is split into three sections called from main at the bottom so you
can read top to bottom and run the program at any point.
*/

// Starter helper demonstrating a default string parameter and #caller_location.
log_ping :: proc(label: string = "ping", loc: runtime.Source_Code_Location = #caller_location) {

	fmt.printfln("[%v:%v] %v", loc.procedure, loc.line, label)
}

default_and_named_args :: proc() {

	/*
	Any procedure parameter can declare a default value using either an explicit
	type ('port: u16 = 8080') or type inference ('max_conns := 64'). That default
	must be a compile-time constant (or one of Odin's special caller directives).
	When a caller omits an argument, the compiler fills in the default value
	directly at the call site with zero runtime branching.

	At any call site, you can also pass arguments by name ('port = 9000, tls = true').
	Named arguments let you skip middle defaults and supply options in any order
	so boolean flags and magic numbers become self-documenting:

	    Suppose connect :: proc(host := "localhost", port := 80, tls := false):
	        connect()                         // uses all defaults
	        connect(tls = true, port = 443)   // skips host, reorders port and tls

	One ordering rule applies: positional arguments must always appear before
	named arguments. Once you pass a named argument (or skip a middle default),
	every remaining argument in that call must also be named.
	*/

	log_ping()

	// Write a procedure configure_server taking four parameters with defaults:
	// host: string = "127.0.0.1", port: u16 = 8080, max_conns := 64, tls := false
	// Print all four configuration fields on one line using fmt.printfln.
	//
	// Call configure_server three times:
	// First with no arguments () to inspect all defaults.
	// Second with (port = 9000, tls = true) skipping host and max_conns.
	// Third with out-of-order named arguments (tls = true, host = "0.0.0.0").


	// Write a helper draw_rect :: proc(x := 0, y := 0, w := 100, h := 50, filled := true)
	// that prints the rectangle bounds and fill flag.
	// Call it once mixing one positional x first and named width/fill after:
	// draw_rect(12, w = 320, filled = false)
	//
	// Try uncommenting a positional argument after a named argument below to see
	// Odin reject the call:
	// draw_rect(x = 12, 24)


	// Verify that default parameter values must be known at compile time:
	// Declare a local runtime variable 'fallback := 10' and try writing a local
	// proc with a non-constant default like:
	// bad_default :: proc(n: int = fallback) { fmt.println(n) }
	// Odin rejects it because default values are baked into call sites at compile time.
}

caller_location_introspection :: proc() {

	/*
	When a logging helper, test check, or allocator fails, printing the line
	number inside the helper itself is useless—you want the caller's file, line,
	column, and procedure name.

	When you give a parameter the default value '#caller_location':

	    loc: runtime.Source_Code_Location = #caller_location

	the compiler injects a small constant struct describing the call site where
	the procedure was invoked (not where the helper was defined!). That struct,
	'runtime.Source_Code_Location', exposes four fields: '.file_path', '.line',
	'.column', and '.procedure'.

	    Suppose debug_log :: proc(msg: string, loc := #caller_location) is called on line 95:
	        loc.line is 95 and loc.procedure is the caller's procedure name.
	        If debug_log then calls emit_line(msg, loc) and passes 'loc' explicitly,
	        emit_line still reports line 95 instead of the line inside debug_log.
	*/

	log_ping("section two ready")

	// Write a procedure debug_log :: proc(tag: string, msg: string, loc: runtime.Source_Code_Location = #caller_location)
	// that prints loc.file_path, loc.line, loc.column, loc.procedure, tag, and msg.
	// Call debug_log("NET", "socket bound") and inspect the line and procedure name.


	// Practice forwarding #caller_location across two helpers without losing the
	// real call site:
	// Write format_diag :: proc(level: string, text: string, loc: runtime.Source_Code_Location)
	// that prints "[<level>] <file_path>(<line>:<column>) in <procedure>: <text>".
	// Then write warn_at :: proc(text: string, loc := #caller_location) that
	// forwards its received 'loc' directly to format_diag("WARN", text, loc).
	// Call warn_at("buffer near capacity") and confirm the printed line matches
	// the call site of warn_at rather than the body of warn_at.
}

caller_expression_and_assert :: proc() {

	/*
	Odin goes one step beyond '#caller_location' with '#caller_expression(param)'.
	When we write 'expr := #caller_expression(val)' as a default parameter, it
	means "capture the exact source code text the caller wrote for 'val' as a
	compile-time string". There is no C preprocessor text substitution and no
	runtime reflection needed—the compiler simply passes the literal snippet
	alongside the evaluated value.

	    Suppose trace_value :: proc(val: int, expr := #caller_expression(val)):
	        Calling trace_value(2 + 3 * 4) binds val to 14 and expr to "2 + 3 * 4".

	Pairing '#caller_expression(cond)' with '#caller_location' lets you build
	your own expressive assertion helpers in pure Odin that tell you both where
	a check failed and the exact boolean condition that evaluated to false.
	*/

	// Starter example showing #caller_expression with type inference on a string:

	show_expr :: proc(val: int, expr := #caller_expression(val)) {

		fmt.printfln("expression '%v' evaluated to %v", expr, val)
	}

	base := 6
	show_expr(base * 7)

	// Write trace_value :: proc(val: int, expr := #caller_expression(val), loc := #caller_location)
	// that prints "<file_path>(<line>) in <procedure>: <expr> = <val>".
	// Call trace_value(2 + 3 * 4) so expr captures "2 + 3 * 4" and val is 14.
	// Also pass a named custom label manually: trace_value(99, expr = "override_label")
	// to verify '#caller_expression' is still just a normal default parameter.


	// Build a custom assert helper combining #caller_expression and #caller_location:
	// Write assert_expr :: proc(cond: bool, msg: string = "", expr := #caller_expression(cond), loc := #caller_location) -> bool
	// When cond is true, return true silently.
	// When cond is false, print:
	// "Assertion failed at <loc.file_path>(<loc.line>:<loc.column>) in <loc.procedure>: '<expr>' (<msg>)"
	// and return false (in real production code you could call panic here after printing).
	//
	// Test assert_expr on a passing condition like assert_expr(base * 2 == 12, "math check")
	// and on a failing condition like assert_expr(base > 100, "expected larger base")
	// to inspect the full diagnostic message without aborting the rest of the run.


	// Extend the same trick to compare two values in one helper:
	// Write assert_eq :: proc(got, expected: int, got_expr := #caller_expression(got), exp_expr := #caller_expression(expected), loc := #caller_location) -> bool
	// When got != expected, print both expressions alongside their evaluated
	// values and the caller line/procedure, then return false.
	// Call assert_eq(base + 1, 10) to inspect the output.
}

main :: proc() {

	fmt.println("=== 1. Default and named arguments ===")
	default_and_named_args()

	fmt.println("\n=== 2. Caller location introspection ===")
	caller_location_introspection()

	fmt.println("\n=== 3. Caller expression and custom assert helper ===")
	caller_expression_and_assert()
}
