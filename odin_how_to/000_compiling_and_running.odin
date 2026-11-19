// odin run 000_compiling_and_running.odin -file

package main

import "core:fmt"
import "core:os"

/*
Welcome to Odin.

Before writing variables or loops, it helps to understand how the Odin compiler
looks at your files. By default, Odin treats an entire directory as a single
package: running 'odin run .' gathers every .odin file in the folder and builds
them together with no header files or external build script required.

Because this workspace holds many standalone Primers in one flat folder, passing
the -file flag tells the compiler to treat this single .odin file as its own
self-contained package and ignore sibling .odin files nearby.

This file is split into four small sections called from main at the bottom so
you can read top to bottom and run the program at any point.
*/

single_file_vs_package_builds :: proc() {

	/*
	Three everyday commands cover almost your entire Odin workflow:
	'odin run <file>.odin -file' compiles and runs immediately in one step.
	'odin check <file>.odin -file' runs fast syntax and type checks without
	generating machine code or linking an executable.
	'odin build <file>.odin -file -out:.build/000.exe' compiles a standalone
	executable into the .build folder without launching it immediately.

	When we write ODIN_VERSION, ODIN_OS, or ODIN_ARCH, we are reading built-in
	compile-time constants that the compiler injects automatically for the
	target machine. Notice fmt.printfln works like fmt.printf with an automatic
	trailing newline, and %v is Odin's universal default format verb.
	*/

	// Inspecting three built-in target constants in starter code:

	fmt.printfln("Odin %v on %v (%v)", ODIN_VERSION, ODIN_OS, ODIN_ARCH)

	// Use fmt.println to print "Compiler Vendor:" followed by the built-in
	// constant ODIN_VENDOR.


	// Also print ODIN_ENDIAN using fmt.printfln("Target endianness: %v", ODIN_ENDIAN)
	// to see whether your CPU stores multi-byte integers little- or big-endian.


	// Try running 'odin check 000_compiling_and_running.odin -file' in your
	// terminal, then build a standalone binary into .build/000_primer.exe with:
	// odin build 000_compiling_and_running.odin -file -out:.build/000_primer.exe
}

compiler_flags_and_optimization :: proc() {

	/*
	Odin exposes your build settings directly as compile-time constants too:
	ODIN_DEBUG is a boolean that becomes true only when you pass -debug (which
	also embeds debug symbols for a debugger), and ODIN_OPTIMIZATION_MODE tells
	you which optimization level was chosen (-o:none, -o:minimal, -o:speed, or
	-o:size).

	Because ODIN_DEBUG is known at compile time, you can guard diagnostic code
	with 'when ODIN_DEBUG { fmt.println("debug") }'. Unlike runtime 'if', 'when'
	is evaluated by the compiler: when ODIN_DEBUG is false, the compiler emits
	zero machine instructions for the block inside.
	*/

	// Baseline output showing the current debug and optimization flags:

	fmt.printfln("Debug: %v | Optimization: %v", ODIN_DEBUG, ODIN_OPTIMIZATION_MODE)

	// Print a diagnostic notice inside a compile-time branch using:
	// when ODIN_DEBUG { fmt.println("[debug build active]") }
	// Re-run first with normal flags, then re-run with -debug and -o:speed:
	// odin run 000_compiling_and_running.odin -file -debug -o:speed
	// Observe ODIN_DEBUG flip from false to true and ODIN_OPTIMIZATION_MODE change.


	// Compare compile-time branching with an inverted branch using:
	// when !ODIN_DEBUG { fmt.println("[release/default build]") }
	// Notice only one of the two branches is ever compiled into your executable.
}

runtime_args_after_double_dash :: proc() {

	/*
	Compiler flags go before your program runs, whereas runtime arguments are
	passed to your compiled executable. Separating the two uses a double dash
	'--' on the command line: everything before '--' is read by the Odin
	compiler, and everything after '--' lands inside os.args as a slice of
	strings ([]string).

	Suppose you run:
	    odin run 000_compiling_and_running.odin -file -- alpha beta
	Inside your program, os.args has length 3: os.args[0] holds the path to the
	compiled executable, os.args[1] is "alpha", and os.args[2] is "beta".
	*/

	// Reading the always-present executable entry at index 0:

	fmt.printfln("Executable: %v (total os.args: %v)", os.args[0], len(os.args))

	// Check if any user arguments were passed after '--' by testing:
	// if len(os.args) > 1
	// Print os.args[1] when present, or print "No extra runtime args passed."
	// in an else branch.


	// Walk every user argument after index 0 using a slice loop:
	// for arg, idx in os.args[1:]
	// Inside the loop, print both idx and arg with fmt.printfln.
	// Test it in your terminal with:
	// odin run 000_compiling_and_running.odin -file -- alpha beta 42
}

vetting_and_strict_style :: proc() {

	/*
	Odin includes a built-in static analyzer called the vetter. Passing -vet
	turns on checks for unused declarations, variable shadowing, and stray
	semicolons, while -strict-style enforces canonical Odin formatting such as
	same-line opening braces and tab indentation. Keeping these flags clean as
	you learn prevents silent bugs before your code ever runs.
	*/

	// Clean local variable following Odin's no-semicolon style:

	clean_check := true
	fmt.printfln("Baseline clean_check = %v", clean_check)

	// Run the strict vetter on this file from your terminal:
	// odin check 000_compiling_and_running.odin -file -vet -strict-style
	// Confirm it exits cleanly with zero warnings.


	// Try adding a trailing semicolon on a line or uncommenting the unused
	// declaration below and running with -vet -strict-style to see Odin catch
	// both issues at compile time:
	// unused_value := 123
}

main :: proc() {

	fmt.println("=== 1. Single-file vs package builds ===")
	single_file_vs_package_builds()

	fmt.println("\n=== 2. Compiler flags and optimization ===")
	compiler_flags_and_optimization()

	fmt.println("\n=== 3. Runtime args after double dash ===")
	runtime_args_after_double_dash()

	fmt.println("\n=== 4. Vetting and strict style ===")
	vetting_and_strict_style()
}
