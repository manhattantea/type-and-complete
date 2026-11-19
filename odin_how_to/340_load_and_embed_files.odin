// odin run 340_load_and_embed_files.odin -file

package main

import "core:fmt"

/*
Instead of shipping fragile relative asset folders next to an executable and
reading them with file I/O at startup, Odin can bake files directly into your
program's read-only data segment at compile time:

    #exists("relative_path")              compile-time bool (true if file exists next to this .odin file)
    #load("relative_path")                compile-time []u8 byte slice baked into the binary
    #load("relative_path", string)        same embedded bytes viewed as an immutable UTF-8 string
    #load_hash("relative_path", "sha256") compile-time hash digest computed during compilation

Because #load resolves paths relative to the .odin file containing it, your
executable carries shaders, lookup tables, or config defaults with zero
runtime disk opens and zero missing-file errors.
*/

// Starter compile-time check confirming plan.md sits alongside this file:

HAS_PLAN :: #exists("plan.md")

// Embed "001_first.odin" as a compile-time string constant named
// EMBEDDED_SOURCE using #load("001_first.odin", string).


// Embed "README.md" as a raw []u8 slice named README_BYTES using
// #load("README.md"), and check HAS_MISSING :: #exists("does_not_exist.txt").


// Declare README_HASH :: #load_hash("README.md", "sha256") to compute a
// compile-time SHA-256 digest of README.md without any runtime hashing cost.


exists_and_load_basics :: proc() {

	/*
	Combining #exists with 'when' lets a build embed an optional local asset
	when present and fall back cleanly when absent, without failing compilation:

	    Suppose a renderer checks for a local shader override file:
	        when #exists("plan.md") {
	            PLAN_TEXT :: #load("plan.md", string)
	        } else {
	            PLAN_TEXT :: "fallback default"
	        }

	Because untaken 'when' branches are not evaluated, putting #load inside
	'when #exists(...)' avoids compile errors when optional files are absent.
	*/

	// Here is a live check confirming HAS_PLAN was resolved at compile time:

	fmt.printfln("plan.md exists next to this Primer: %v", HAS_PLAN)

	// Print len(EMBEDDED_SOURCE), the first 30 bytes EMBEDDED_SOURCE[:30],
	// len(README_BYTES), README_BYTES[0], and HAS_MISSING using fmt.printfln.


	// Write a 'when #exists("plan.md")' block that loads "plan.md" into a
	// local constant PLAN_DATA :: #load("plan.md", string) and prints its byte
	// length, proving optional assets can be gated at compile time.


	// Write a 'when #exists("does_not_exist.txt")' block with an 'else' branch
	// printing a fallback message so you see missing files handled safely.
}

compile_time_hashes :: proc() {

	/*
	When an application embeds shaders, web templates, or asset packs, you
	often want a content fingerprint (for cache busting or version stamps).
	#load_hash computes the digest at compile time and stores the resulting
	fixed byte array straight in the binary.

	    Suppose README_HASH :: #load_hash("README.md", "sha256"):
	        len(README_HASH) is 32 bytes at compile time, so you can even write
	        #assert(len(README_HASH) == 32) with zero runtime overhead.
	*/

	fmt.println("Inspect README_HASH once declared at file scope above.")

	// Add #assert(len(README_HASH) == 32), then print README_HASH with
	// fmt.printfln("%v", README_HASH) and format its 32 bytes in lowercase hex
	// using 'for b in README_HASH' with fmt.printf("%02x", b).
}

source_location_directives :: proc() {

	/*
	Alongside file embedding, Odin provides four source-introspection
	directives that expand to compile-time constants wherever they appear:

	    #file        full path of the current .odin source file
	    #directory   directory path containing the current .odin file
	    #line        integer line number where #line is written
	    #procedure   name of the enclosing procedure as a string

	Notice the difference from #caller_location: #file and #line always report
	the exact spot where they are written, whereas #caller_location (as a
	default procedure parameter) captures the caller's file and line instead.
	*/

	// Here is a live check using #file and #line directly inside this proc:

	fmt.printfln("Compiled from %s at line %d", #file, #line)

	// Print all four directives (#file, #directory, #line, and #procedure)
	// with fmt.printfln inside this procedure, then compare #procedure here
	// against printing #procedure inside main at the bottom of the file.


	// Format a compact diagnostic banner with fmt.printfln("[%s @ %s:%d]", #procedure, #file, #line)
	// to see how compile-time location tags work without runtime reflection.
}

main :: proc() {

	fmt.println("=== 1. #exists and #load file embedding ===")
	exists_and_load_basics()

	fmt.println("\n=== 2. Compile-time #load_hash digests ===")
	compile_time_hashes()

	fmt.println("\n=== 3. Source location directives ===")
	source_location_directives()
}
