// odin run 380_vet_flags_and_compiler_hygiene.odin -file

package main

import "core:fmt"

/*
Odin ships with a built-in static analyzer and style checker rather than
relying on separate third-party linters. Passing -vet and -strict-style to
'odin check' catches silent bugs (shadowed variables, unread locals, dead
imports, redundant casts) and enforces one consistent layout across a codebase:

    -vet                    bundle enabling unused, shadowing, using, cast, semicolon, uninitialized
    -vet-unused-variables   errors when a local variable is written but never read
    -vet-unused-imports     errors when an imported package is never referenced
    -vet-shadowing          errors when an inner declaration hides an outer name
    -vet-cast               errors on redundant casts where the expression already has that type
    -vet-semicolon          errors on unnecessary trailing semicolons at line ends
    -vet-tabs               enforces tab indentation across the file
    -vet-uninitialized      flags reads from '= ---' variables before assignment
    -strict-style           enforces 1TBS attached braces, trailing commas, and aligned switch cases
    -warnings-as-errors     promotes compiler warnings into hard errors

This unfilled Primer itself is clean under:
odin check 380_vet_flags_and_compiler_hygiene.odin -file -vet -strict-style
*/

// Starter struct demonstrating 1TBS attached braces and aligned fields:

Server_Config :: struct {
	host: string,
	port: int,
	tls:  bool,
}

strict_style_formatting :: proc() {

	/*
	Under -strict-style, Odin checks three formatting rules automatically:
	opening '{' stays on the same line as the declaration or control statement
	(1TBS), every line of a multi-line compound literal ends with a comma, and
	'case' labels inside a 'switch' align at the exact same indentation column
	as 'switch' rather than being indented one tab inward.
	*/

	// Here is a live multi-line compound literal passing -vet -strict-style:

	config := Server_Config{
		host = "127.0.0.1",
		port = 8080,
		tls  = true,
	}
	fmt.printfln("Server %s:%d (TLS=%v)", config.host, config.port, config.tls)

	// Define Connection_State :: enum { Disconnected, Connecting, Connected }
	// above main, then declare a second multi-line backup_cfg := Server_Config{ ... }
	// here with trailing commas on every field line and print it.


	// Write a -strict-style switch over state := Connection_State.Connecting
	// where every 'case' sits at the exact same tab column as 'switch', and
	// verify with:
	// odin check 380_vet_flags_and_compiler_hygiene.odin -file -vet -strict-style
}

vet_shadowing_and_unused :: proc() {

	/*
	Variable shadowing happens when you accidentally write ':=' instead of '='
	inside an inner block:

	    Suppose retry_limit := 3 at the top of a procedure:
	        if fast_mode {
	            retry_limit := 1   // creates a NEW inner variable; outer stays 3!
	        }
	        // Here retry_limit is still 3, silently ignoring fast_mode!

	Passing -vet-shadowing (included in -vet) turns that silent logic bug into
	an immediate compile error. Similarly, -vet-unused-variables and
	-vet-unused-imports prevent stale code from piling up during refactoring.
	*/

	active_limit := 3
	fmt.printfln("Active retry limit: %d", active_limit)

	// Interactive -vet-shadowing experiment: uncomment the block below and run
	// odin check 380_vet_flags_and_compiler_hygiene.odin -file -vet -strict-style
	// to see Odin catch the inner 'active_limit := 1' shadow:
	// if active_limit > 0 {
	// 	active_limit := 1
	// 	fmt.printfln("Shadowed inner limit: %d", active_limit)
	// }


	// Interactive -vet-unused-variables experiment: uncomment the line below
	// and run -vet to see Odin reject an unread local variable:
	// unused_val := 123


	// Interactive -vet-unused-imports experiment: temporarily add
	// import "core:strings" at the top of this file without calling it, run
	// -vet to watch the unused import error, then remove it again.
}

vet_casts_semicolons_and_overrides :: proc() {

	/*
	Extra syntax noise also gets flagged under -vet: redundant casts such as
	int(42) when 42 already resolves to int (-vet-cast), trailing semicolons at
	the end of statements (-vet-semicolon), spaces used for indentation instead
	of tabs (-vet-tabs), and 'using' statements (-vet-using-stmt).

	When a single file legitimately needs to relax one check (for instance a
	generated file or a Scratch Primer testing unused locals), place a tag like
	#+vet !unused-variables before 'package' at the top of the file.
	*/

	base_port := 8080
	fmt.printfln("Verified base port: %d", base_port)

	// Interactive -vet-cast experiment: uncomment the lines below and run
	// -vet to see Odin flag the redundant int(...) conversion:
	// redundant := int(base_port)
	// fmt.println(redundant)


	// Interactive -vet-semicolon experiment: uncomment the line below and run
	// -vet to see Odin flag the unnecessary trailing semicolon:
	// extra_semi := 7; fmt.println(extra_semi);


	// Interactive -strict-style comma experiment: delete the trailing comma
	// after 'tls = true,' in strict_style_formatting above, run -strict-style
	// to see the style failure, restore the comma, and confirm clean pass with:
	// odin check 380_vet_flags_and_compiler_hygiene.odin -file -vet -strict-style -warnings-as-errors
}

main :: proc() {

	fmt.println("=== 1. -strict-style formatting rules ===")
	strict_style_formatting()

	fmt.println("\n=== 2. -vet shadowing and unused checks ===")
	vet_shadowing_and_unused()

	fmt.println("\n=== 3. -vet casts, semicolons, and #+vet overrides ===")
	vet_casts_semicolons_and_overrides()
}
