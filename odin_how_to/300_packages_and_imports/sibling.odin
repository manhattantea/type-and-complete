package main

/*
Sibling files in the same directory (main.odin and sibling.odin) both declare
package main. Odin merges all declarations across sibling files into one
order-independent package scope before resolving types and procedure bodies.

This means you never write import "sibling" and you never maintain .h header
files or forward declarations. Splitting a large package into multiple files
is purely a human organization choice; the compiler sees one unified package.
*/

// Minimal anchor constant read directly by main.odin:

SIBLING_READY :: true

// Declare an untyped string constant named MODULE_VERSION set to "1.0.0"
// so main.odin can print it directly without any package prefix.


// Define a procedure sibling_helper :: proc(x: int) -> int that computes and
// returns x * 2.


// Define a package-shared struct App_Info :: struct { name: string, major: int }
// and a procedure format_app_label :: proc(info: App_Info) -> string that
// returns info.name (or formats a label using fmt.tprintf if you import "core:fmt").
