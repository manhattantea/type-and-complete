// odin run 140_explicit_procedure_overloading.odin -file

package main

import "core:fmt"

/*
In C++, any function name can be overloaded implicitly across dozens of headers
and namespaces, forcing the compiler and the reader to trace complex implicit
conversion rules. Go and Rust swing to the opposite extreme and forbid
overloading altogether.

Odin takes a pragmatic middle path with explicit procedure overload groups
written as 'proc{...}'. Every concrete procedure keeps its own distinct,
searchable name (like area_square, area_rect, area_dims), and you bind them
together in one visible list. Anyone jumping to the definition of 'area'
immediately sees every candidate in a single place.

This file is split into two focused sections called from main at the bottom.
*/

Vec2 :: [2]f32

Rect :: struct {
	x, y, w, h: f32,
}

// Starter helper extracting the top-left corner of a Rect as a Vec2.
rect_origin :: proc(r: Rect) -> Vec2 {

	return Vec2{r.x, r.y}
}

explicit_overload_groups :: proc() {

	/*
	When we write 'area :: proc{area_square, area_rect, area_dims}', it tells
	the compiler "whenever a caller invokes 'area(...)', check the argument
	types and count against these three exact procedures and pick the matching
	candidate at compile time". There is zero runtime dispatch overhead.

	    Suppose a group lists calc :: proc{calc_i32, calc_f32}:
	        calc(i32(4)) resolves directly to a call to calc_i32.
	        calc(f32(4)) resolves directly to a call to calc_f32.

	Because every candidate still has its own unique name, callers can also invoke
	'area_rect(r)' directly when they want to be explicit or pass a single
	concrete procedure as a callback.
	*/

	fmt.printfln("Sample rect origin: %v", rect_origin(Rect{x = 1, y = 2, w = 4, h = 3}))

	// Write three distinctly named candidate procedures returning f32:
	// area_square :: proc(side: f32) -> f32 returning side * side
	// area_rect :: proc(r: Rect) -> f32 returning r.w * r.h
	// area_dims :: proc(w, h: f32) -> f32 returning w * h


	// Bind the three candidates into one explicit overload group:
	// area :: proc{area_square, area_rect, area_dims}
	// Call area(5.0), area(Rect{0, 0, 4, 3}), and area(6.0, 2.0), printing all
	// three results with fmt.printfln (expected: 25, 12, and 12).
}

overload_resolution_rules :: proc() {

	/*
	Odin resolves an overload group solely by the parameter types and arity—never
	by the return type alone. If two procedures in the same 'proc{...}' group
	accept identical parameter types, the compiler immediately rejects the group
	as ambiguous rather than guessing.

	Also notice that you can pass untyped compound literals like '{4, 3}' to an
	overload only if a single candidate matches that shape cleanly; otherwise
	give the type explicitly, such as Vec2{4, 3} or Rect{w = 4, h = 3}.
	*/

	// Add a fourth candidate area_size :: proc(size: Vec2) -> f32 returning
	// size[0] * size[1], include area_size in the 'area :: proc{...}' group,
	// and call area(Vec2{7, 3}) (expected: 21).


	// Try calling area("invalid") below (uncomment to test) and read how Odin
	// prints every candidate signature in the proc{...} group so you can see
	// at a glance why none matched:
	// fmt.println(area("invalid"))


	// Observe why two candidates cannot share the exact same parameter signature:
	// Try defining double_area_f32 :: proc(side: f32) -> f32 and adding it to
	// 'area :: proc{...}' to confirm Odin rejects overlapping parameter signatures.
}

main :: proc() {

	fmt.println("=== 1. Explicit overload groups ===")
	explicit_overload_groups()

	fmt.println("\n=== 2. Overload resolution rules ===")
	overload_resolution_rules()
}
