// odin run 300_packages_and_imports

package main

import "core:fmt"
import "geometry"
import geo "geometry"

/*
In Odin, a folder of .odin files is one package, not a loose collection of
independent translation units like C. When you run or check a directory without
the -file flag (odin run 300_packages_and_imports), the compiler gathers every
.odin file in that folder and compiles them together as one unit.

Because main.odin and sibling.odin sit in the same directory and both declare
package main, they share one order-independent package scope. Declarations in
sibling.odin are immediately visible here with zero import statements or header
files. By contrast, a child folder like geometry/ is its own separate package,
so you pull it in with import "geometry" (or bind a shorter alias with
import geo "geometry") and qualify its symbols through the package name.
*/

sibling_scope_and_shared_types :: proc() {

	/*
	Because sibling files compile as one package, types and procedures declared
	in sibling.odin can be used directly inside main.odin without any prefix.

	    Suppose sibling.odin declares:
	        App_Info :: struct { name: string, version: string }
	        sibling_helper :: proc(x: int) -> int { return x * 2 }
	    Then inside main.odin you can write:
	        info := App_Info{name = "OdinLab", version = "1.0.0"}
	        doubled := sibling_helper(21)   // 42, no import or prefix needed
	*/

	// Here is a live reference to a constant declared in sibling.odin:

	fmt.printfln("Sibling ready: %v", SIBLING_READY)

	// After defining sibling_helper(x: int) -> int and MODULE_VERSION :: "1.0.0"
	// in sibling.odin, call sibling_helper(21) and store the result in doubled.
	// Print both doubled and MODULE_VERSION with fmt.printfln.


	// After defining App_Info :: struct { name: string, major: int } and
	// format_app_label :: proc(info: App_Info) -> string in sibling.odin,
	// construct an App_Info value here and print the label returned by
	// format_app_label.
}

subpackage_imports_and_aliases :: proc() {

	/*
	Importing a subdirectory package binds its folder name as the qualifier
	prefix (geometry.PI). When a package path is long or collides with a local
	variable name, adding an alias before the string path lets you choose a
	shorter qualifier (import geo "geometry", then geo.PI).

	Unlike C #include, importing a package never pastes text into your file.
	Imported symbols stay inside their own namespace unless you explicitly
	qualify them, which prevents accidental name collisions across modules.
	*/

	// Here is a live check reading the same constant via geometry and geo:

	fmt.printfln("PI via geometry: %.4f | PI via geo: %.4f", geometry.PI, geo.PI)

	// After defining Circle and circle_area(c: Circle) -> f32 inside
	// geometry/shapes.odin, construct c := geometry.Circle{radius = 5.0},
	// compute its area with both geometry.circle_area(c) and geo.circle_area(c),
	// and print the result.


	// After defining Rectangle, rect_perimeter(r: Rectangle) -> f32, and
	// rectangle_area(r: Rectangle) -> f32 in geometry/shapes.odin, construct
	// rect := geo.Rectangle{width = 4.0, height = 8.0}, compute both area and
	// perimeter, and print them.


	// Try uncommenting the line below to see why Odin requires the package
	// qualifier for symbols from geometry/ rather than exposing them globally:
	// fmt.println(PI)
}

main :: proc() {

	fmt.println("=== 1. Sibling scope and package-shared types ===")
	sibling_scope_and_shared_types()

	fmt.println("\n=== 2. Subpackage imports and aliases ===")
	subpackage_imports_and_aliases()
}
