// odin run 560_cli_args_and_core_flags.odin -file

package main

import "core:flags"
import "core:fmt"
import "core:os"

/*
Command-line tools in Odin have two layers for reading arguments:
- 'os.args' gives you the raw '[]string' slice straight from the OS
  ('os.args[0]' is the executable path; 'os.args[1:]' holds user arguments
  passed after '--' when running via 'odin run <file> -file -- ...').
- 'core:flags' uses runtime type information ('core:reflect') to parse either
  Odin-style flags ('-threads:8 -verbose') or Unix-style flags
  ('--threads=8 --verbose') directly into a typed struct annotated with
  backtick struct tags.

This Primer covers raw 'os.args', Odin-style reflection parsing with enum flags,
and Unix-style parsing with live CLI fallback.
*/

Preview_Flags :: struct {
	target:  string `args:"pos=0" usage:"Preview target"`,
	dry_run: bool   `usage:"Simulate without writing"`,
}

// Define Log_Mode :: enum { Quiet, Normal, Debug } and Cli_Options :: struct
// at file scope using the same backtick struct-tag pattern shown in Preview_Flags:
// - input:   string   tagged args:"pos=0,required" and usage:"Input filename"
// - threads: int      tagged usage:"Worker thread count"
// - mode:    Log_Mode tagged usage:"Output mode"
// - verbose: bool     tagged usage:"Enable verbose output"


raw_os_args_inspection :: proc() {

	/*
	Before reaching for a parser, inspect 'os.args'. Because 'os.args[0]' is
	always the program path, user-supplied flags and positional arguments start
	at 'os.args[1:]'.
	*/

	fmt.printfln("Starter executable: %s (argc=%d)", os.args[0], len(os.args))

	// Loop over os.args[1:] using: for arg, idx in os.args[1:]
	// Print each user argument and its index, or print "(no CLI args passed)"
	// when len(os.args) <= 1.


	// Write a tiny manual flag check scanning os.args[1:] for "--dry-run" so you
	// feel how quickly hand-rolled loops grow messy once typed ints, enums, and
	// required positional arguments enter the picture.
}

reflection_flags_and_odin_style :: proc() {

	/*
	When we call 'flags.parse(&opts, args_slice, .Odin)', 'core:flags' inspects
	every field of 'opts' via runtime reflection and matches names, enum member
	names, and 'args:"pos=0,required"' tags automatically.

	    Suppose Preview_Flags has target (pos=0) and dry_run (bool):
	        args := []string{"scene.dat", "-dry_run"}
	        err := flags.parse(&preview, args, .Odin)
	        // preview.target becomes "scene.dat", preview.dry_run becomes true, err == nil

	Notice that enum flags match the exact enum member identifier (for example
	'-mode:Debug' in .Odin style or '--mode=Debug' in .Unix style).
	*/

	preview := Preview_Flags{target = "default.cfg"}
	preview_err := flags.parse(&preview, []string{"scene.dat", "-dry_run"}, .Odin)
	fmt.printfln("Starter preview (%v): %#v (err=%v)", flags.Parsing_Style.Odin, preview, preview_err)

	// Parse Odin-style arguments into Cli_Options:
	// declare opts := Cli_Options{threads = 4, mode = .Normal}
	// Declare sim_args := []string{"level1.dat", "-threads:8", "-mode:Debug", "-verbose"}
	// Call err := flags.parse(&opts, sim_args, .Odin), check if err != nil to print
	// an error, and otherwise print opts with %#v to confirm all four fields updated.


	// Test error reporting on invalid input:
	// pass []string{"level1.dat", "-mode:Verbose"} (unknown enum value) and
	// []string{"-threads:4"} (missing required pos=0 input) to flags.parse,
	// printing each non-nil flags.Error so you see how validation failures look.
}

unix_style_and_live_cli_fallback :: proc() {

	/*
	Many users expect GNU/Unix flag syntax ('--threads=8 --verbose') instead of
	Odin's colon syntax ('-threads:8'). Switching the third parameter of
	'flags.parse' from '.Odin' to 'flags.Parsing_Style.Unix' handles '--key=val',
	'--key val', and boolean '--flag' without changing your struct definition!
	*/

	fmt.printfln("Starter alternate style: %v", flags.Parsing_Style.Unix)

	// Parse Unix-style arguments with enum flags into a fresh Cli_Options:
	// declare unix_opts := Cli_Options{threads = 2, mode = .Normal}
	// Declare unix_args := []string{"level2.dat", "--threads=16", "--mode=Quiet", "--verbose"}
	// Call err := flags.parse(&unix_opts, unix_args, flags.Parsing_Style.Unix)
	// Verify err == nil and print unix_opts with %#v.


	// Wire live CLI arguments with a safe standalone fallback:
	// set live_args := len(os.args) > 1 ? os.args[1:] : []string{"demo.dat", "--threads=2", "--mode=Debug"}
	// Parse live_args into live_opts: Cli_Options with style .Unix, print any
	// non-nil err via fmt.eprintfln, and test running from your shell with:
	// odin run 560_cli_args_and_core_flags.odin -file -- world.dat --threads=4 --mode=Quiet
}

main :: proc() {

	fmt.println("=== 1. Raw os.args inspection ===")
	raw_os_args_inspection()

	fmt.println("\n=== 2. Reflection flags and .Odin style ===")
	reflection_flags_and_odin_style()

	fmt.println("\n=== 3. .Unix style and live CLI fallback ===")
	unix_style_and_live_cli_fallback()
}
