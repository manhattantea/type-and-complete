// odin run 370_collections_and_ols_setup.odin -file

package main

import "core:fmt"

/*
In Odin, the prefix before ':' in an import path is a collection name mapped to
a root directory on disk. Built-in collections come out of the box:

    base:     runtime essentials and compiler intrinsics (base:runtime, base:intrinsics)
    core:     standard library packages (core:fmt, core:mem, core:os, core:strings)
    vendor:   bundled third-party libraries (vendor:raylib, vendor:glfw, vendor:sdl2)

For larger projects, you can register custom collections via the compiler flag
'-collection:shared=./shared' so any file anywhere in the repo can write
import "shared:math_utils" instead of fragile ../../../shared/math_utils paths.
Placing an ols.json file at the workspace root gives the Odin Language Server
(ols) the exact same collection roots and checker flags for IDE autocomplete.
*/

// Starter struct representing a single collection mapping in ols.json:

Collection_Entry :: struct {
	name: string,
	path: string,
}

builtin_and_custom_collections :: proc() {

	/*
	Suppose your engine splits shared math code into ./shared and game assets
	into ./assets. Passing -collection:shared=./shared -collection:assets=./assets
	lets deeply nested packages import "shared:vec" cleanly without caring how
	many folders deep they sit.
	*/

	// Here is a live check formatting a custom collection CLI flag:

	shared_col := Collection_Entry{name = "shared", path = "./shared"}
	fmt.printfln("Collection flag: -collection:%s=%s", shared_col.name, shared_col.path)

	// Add a second Collection_Entry for "assets" -> "./assets", store both in
	// a slice []Collection_Entry, and loop over them to print each complete
	// '-collection:<name>=<path>' CLI flag.
}

ols_configuration_schema :: proc() {

	/*
	The ols.json file at your repository root mirrors your build command so
	go-to-definition, hover docs, semantic tokens, and inline error squiggles
	understand custom collections and strict vet rules.
	*/

	fmt.println("Model Config_OLS below and print the matching ols.json settings.")

	// Define Config_OLS :: struct with fields:
	// collections: []Collection_Entry, checker_args: string,
	// enable_snippets: bool, enable_hover: bool, enable_semantic_tokens: bool.


	// Construct ols_cfg := Config_OLS{ ... } using your collections slice,
	// checker_args = "-vet -strict-style", and all three boolean flags true.
	// Print ols_cfg and format a matching JSON snippet using fmt.printfln.
}

main :: proc() {

	fmt.println("=== 1. Built-in and custom library collections ===")
	builtin_and_custom_collections()

	fmt.println("\n=== 2. ols.json workspace configuration ===")
	ols_configuration_schema()
}
