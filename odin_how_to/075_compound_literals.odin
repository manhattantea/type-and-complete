// odin run 075_compound_literals.odin -file

package main

import "core:fmt"

/*
Odin uses one unified '{ ... }' compound literal syntax across structs, fixed
arrays, slices, maps, and bit sets instead of splitting initialization across
separate rules.

Even better, whenever Odin already knows the target type from a variable
declaration or procedure parameter, you can drop the type name before '{ ... }'
and let the compiler infer it for you.

This file is split into three small sections called from main at the bottom so
you can read top to bottom and run the program at any point.
*/

Color :: struct {
	r, g, b, a: u8,
}

draw_pixel :: proc(pos: [2]int, col: Color) {

	fmt.printfln("draw_pixel at %v with RGBA %v", pos, col)
}

structs_and_type_elision :: proc() {

	/*
	You can populate structs either positionally or by field name. Any omitted
	fields in a designated literal are deterministically zero-initialized:

	    Suppose c: Color = {g = 255, a = 128}:
	        c becomes Color{r = 0, g = 255, b = 0, a = 128} — zero garbage!

	And because draw_pixel expects ([2]int, Color), calling draw_pixel({10, 20}, {255, 0, 0, 255})
	needs no repeated type names at the call site.
	*/

	// Here we pass an elided position literal and an explicit Color literal:

	draw_pixel({0, 0}, Color{255, 255, 255, 255})

	// Declare red: Color = {255, 0, 0, 255} using type elision, and declare
	// transparent_green := Color{g = 255, a = 128} using designated fields.
	// Print both colors to confirm r and b in transparent_green are 0.


	// Call draw_pixel passing untyped { ... } literals for BOTH arguments:
	// position {10, 20} and color {0, 128, 255, 255}.


	// Practice nested type elision:
	// define Sprite :: struct { pos: [2]int, tint: Color } above main, then
	// declare hero: Sprite = {{5, 8}, {r = 255, a = 255}} and print hero.
}

fixed_arrays_and_inferred_length :: proc() {

	/*
	Writing [3]int{1, 2, 3} builds a fixed-size stack array of length 3. When
	you write [?]int{1, 2, 3}, the compiler counts the elements for you and
	locks the array length at compile time—useful when editing lookup tables so
	you never have to update the length in two places.

	You can also assign specific array indices by number:
	    Suppose slots := [4]int{1 = 50, 3 = 90}:
	        slots holds {0, 50, 0, 90}.
	*/

	// Here is an explicit fixed array literal:

	axes := [3]int{1, 0, -1}
	fmt.printfln("axes = %v (type %T)", axes, axes)

	// Declare primes := [?]int{2, 3, 5, 7, 11} and print its value and %T type
	// (expected: [5]int).


	// Declare sparse := [6]int{1 = 100, 4 = 400} and print it to verify indices
	// 0, 2, 3, and 5 are deterministically zero-initialized.


	// Declare a 2D fixed array literal grid := [2][3]int{{1, 2, 3}, {4, 5, 6}}
	// and print grid[1][2] (expected: 6).
}

slice_literals_and_escape_trap :: proc() {

	/*
	Watch out for how slice literals live in memory! Writing nums := []int{10, 20, 30}
	inside a procedure does NOT allocate on the heap. Instead, Odin places a
	hidden [3]int{10, 20, 30} backing array on the current procedure's stack
	frame and builds a slice header pointing into that stack array.

	That makes local slice literals fast and leak-free—but creates a classic
	dangling-pointer trap if you try to return one:

	    Suppose bad_slice :: proc() -> []int {
	        return []int{10, 20, 30}   // DANGER: stack frame disappears on return!
	    }

	Once bad_slice returns, its stack frame is popped and the next procedure
	call overwrites that memory. Whenever a slice must outlive the procedure that
	created it, allocate it explicitly with make([]int, ...) and delete it later.
	*/

	// Here is a safe local stack-backed slice literal:

	local_nums := []int{10, 20, 30}
	fmt.printfln("local_nums = %v (len=%v, type=%T)", local_nums, len(local_nums), local_nums)

	// Declare a slice literal of structs using elided element types:
	// palette := []Color{{255, 0, 0, 255}, {0, 255, 0, 255}, {0, 0, 255, 255}}
	// Loop over palette with for col in palette and print each color.


	// Practice returning heap-allocated slices safely instead of escaping a stack
	// slice literal: write a helper procedure above main named:
	// make_safe_nums :: proc() -> []int
	// Inside make_safe_nums, allocate res := make([]int, 3), assign 10, 20, 30,
	// and return res. Call it here, register defer delete(safe_nums), and print it.
	// (Note in your head why returning []int{10, 20, 30} instead of make([]int, 3)
	// would hand back a dangling pointer into dead stack memory!)


	// Inspect where local_nums lives in memory:
	// declare stack_arr := [3]int{1, 2, 3} right next to local_nums and print
	// raw_data(local_nums) alongside &stack_arr[0] to confirm both sit on the stack.
}

main :: proc() {

	fmt.println("=== 1. Struct literals and type elision ===")
	structs_and_type_elision()

	fmt.println("\n=== 2. Fixed arrays and inferred [?] length ===")
	fixed_arrays_and_inferred_length()

	fmt.println("\n=== 3. Slice literals and the stack escape trap ===")
	slice_literals_and_escape_trap()
}
