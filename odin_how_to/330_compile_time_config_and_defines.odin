// odin run 330_compile_time_config_and_defines.odin -file

package main

import "core:fmt"

/*
Odin lets you inject build-time constants straight from the compiler command
line without code generators or C-style -D preprocessor macros.

    NAME :: #config(NAME, default_val)   reads -define:NAME=val or falls back to default_val
    #defined(NAME)                       returns a compile-time bool indicating if -define:NAME=... was passed

Because #config produces a true compile-time constant (bool, integer, or string),
you can pass it straight into 'when' branches and array lengths, letting the
compiler strip disabled debug paths completely from release binaries.
*/

// Starter compile-time string configuration with a fallback default:

APP_TITLE :: #config(APP_TITLE, "OdinApp")

// Declare an integer constant MAX_THREADS using #config(MAX_THREADS, 4) and
// a boolean constant VERBOSE using #config(VERBOSE, false).


config_constants_and_defaults :: proc() {

	/*
	Suppose a server defaults to 4 worker threads unless overridden on the CLI:
	    MAX_THREADS :: #config(MAX_THREADS, 4)
	Running with -define:MAX_THREADS=16 sets MAX_THREADS to 16 at compile time
	while keeping the source file untouched.
	*/

	// Here is a live check printing the configured application title:

	fmt.printfln("Application Title: %s", APP_TITLE)

	// Print MAX_THREADS and VERBOSE using fmt.printfln, then re-run this file
	// with CLI overrides:
	// odin run 330_compile_time_config_and_defines.odin -file -define:APP_TITLE=SuperGame -define:MAX_THREADS=16 -define:VERBOSE=true


	// Add a 'when VERBOSE' block that prints an extra diagnostic message when
	// -define:VERBOSE=true is passed on the command line.
}

defined_feature_flags :: proc() {

	/*
	While #config always supplies a fallback value, #defined(NAME) answers a
	different question: did the caller explicitly pass -define:NAME=... on the
	command line? Pairing #defined with 'when' lets you detect optional build
	flags without inventing dummy sentinel defaults.
	*/

	// Here is a live check testing whether APP_TITLE itself was overridden:

	when #defined(APP_TITLE) {
		fmt.println("APP_TITLE was explicitly overridden via -define.")
	} else {
		fmt.println("APP_TITLE is using its built-in default.")
	}

	// Write a compile-time 'when #defined(CUSTOM_FLAG) { ... } else { ... }'
	// block that prints whether CUSTOM_FLAG was supplied on the command line,
	// then test running with -define:CUSTOM_FLAG=true.


	// Declare a typed constant TIMEOUT_MS : int : #config(TIMEOUT_MS, 2500)
	// and print it; then try passing a mismatched string value like
	// -define:TIMEOUT_MS=oops to confirm Odin catches invalid define types at
	// compile time.
}

main :: proc() {

	fmt.println("=== 1. #config constants and defaults ===")
	config_constants_and_defaults()

	fmt.println("\n=== 2. #defined optional feature flags ===")
	defined_feature_flags()
}
