// odin run 230_structs_and_literals.odin -file

package main

import "core:fmt"

/*
Structs in Odin (Name :: struct { ... }) are pure data aggregates without
hidden methods, constructors, destructors, or access specifiers. What you
declare in the braces is what sits in memory.

Every struct supports positional literals (Vec2{1, 2}), designated field-named
literals (Player{name = "Aria"}), and zero literals (Vec2{}). Any omitted field
in a designated literal is guaranteed to be deterministically zero-initialized,
and Odin automatically enables == and != comparison whenever all fields are
comparable.

This Primer is split into three focused sections called from main at the bottom.
*/

Vec2 :: struct {
	x, y: f32,
}

Player :: struct {
	name:   string,
	pos:    Vec2,
	health: int,
	alive:  bool,
}

defining_structs_and_literals :: proc() {

	/*
	When the compiler already knows the expected type of a struct or field, you
	can omit the type name in a compound literal and write bare { ... }:

	    Suppose Player has a field pos: Vec2:
	        hero := Player{name = "Aria", pos = {10, 20}, health = 100}
	    Notice pos = {10, 20} omits Vec2, and omitted field 'alive' becomes false!

	Positional literals (without field names) are strict: you must either pass
	ALL fields in declaration order or pass ZERO fields ({}) to zero-init all.
	*/

	// Starter anchor: a zero-initialized Vec2 constructed with {}.
	origin := Vec2{}
	fmt.printfln("Origin: %v", origin)

	// Construct hero of type Player using designated fields:
	// name = "Aria", pos = {10.0, 20.0}, health = 100, alive = true
	// Print hero using fmt.printfln with %v and %#v to compare formats.


	// Construct ghost := Player{name = "Shade"} omitting pos, health, and alive,
	// then print ghost to verify all omitted fields start zero-initialized.
	// Also construct spawn_point := Vec2{3.0, 4.0} using positional syntax.


	// Build an array of structs with inferred nested types:
	// party := [?]Player{ {name = "Aria", health = 100, alive = true}, {name = "Bram", pos = {5, 5}, alive = true} }
	// Print each member with for member in party.


	// Try uncommenting the line below to see Odin reject a partial positional literal:
	// bad_vec := Vec2{10.0}
}

nested_structs_and_mutation :: proc() {

	/*
	Because structs are value types, passing Player to a procedure copies all
	fields, whereas passing ^Player lets the procedure modify the caller's struct
	directly. In Odin, field access through a pointer auto-dereferences—so you
	write p.health -= 10 instead of (*p).health -= 10 or p->health -= 10:

	    Suppose damage_player :: proc(p: ^Player, dmg: int):
	        p.health -= dmg   // updates caller's struct directly without ^

	You can also define inline anonymous structs directly inside a field (for
	grouping sub-fields like bounds: struct { w, h: int } without polluting file
	scope) and attach reflection/serialization metadata tags after a field type
	using a string literal (such as id: int "json:\"id\"").
	*/

	// Starter anchor: build a new Vec2 by reading fields from existing structs.
	start := Vec2{1.0, 2.0}
	step := Vec2{5.0, 0.0}
	moved := Vec2{start.x + step.x, start.y + step.y}
	fmt.printfln("Moved: %v", moved)

	// Declare scout := Player{name = "Kael", pos = {10.0, 20.0}, health = 100, alive = true}.
	// Mutate scout.pos.x += 5.0 and scout.health -= 15, then define a helper
	// damage_player :: proc(p: ^Player, amount: int) that subtracts amount via
	// p.health -= amount (auto-deref) and sets p.alive = false if p.health <= 0.
	// Call damage_player(&scout, 90) and print scout.


	// Define a factory helper make_player :: proc(name: string, x, y: f32) -> Player
	// returning a Player value by copy, then copy-and-reset scout into
	// respawned := scout with respawned.health = 100 and respawned.alive = true.


	// Define Crate :: struct { label: string, bounds: struct { w, h: int } }
	// and instantiate ammo := Crate{label = "Ammo", bounds = {4, 2}} using nested
	// untyped literals, then print ammo.bounds.w and ammo.bounds.h.


	// Define Tagged_Record :: struct { id: int "json:\"id\"", label: string "json:\"label\"" }
	// Instantiate one and print it with %#v (we will inspect struct tags via RTTI in Tier 600).
}

struct_equality_and_comparability :: proc() {

	/*
	Unlike C (which forbids a == b on structs) or Rust (which requires deriving
	PartialEq), Odin automatically generates == and != for any struct whose
	fields are all comparable—even nested structs like Player containing Vec2.
	Unlike C's memcmp, Odin compares fields logically so uninitialized padding
	bytes between fields never cause false inequalities.

	If a struct holds an incomparable field—such as a slice []T, dynamic array
	[dynamic]T, or map[K]V—then == is forbidden at compile time because Odin
	refuses to guess whether you wanted shallow header pointer comparison or a
	deep element-by-element comparison.
	*/

	// Starter anchor: compare two Vec2 values directly with ==.
	a := Vec2{15.0, 20.0}
	b := Vec2{15.0, 20.0}
	fmt.printfln("a == b: %v", a == b)

	// Construct two identical Player values p1 and p2 (same name, pos, health,
	// alive) and verify p1 == p2 prints true. Then set p2.alive = false and
	// print p1 != p2.


	// Define Padded :: struct { flag: u8, id: u64 } (7 bytes of padding between
	// flag and id!) and compare two Padded values initialized identically with
	// == to confirm field-by-field equality ignores alignment padding.


	// Define Bag :: struct { items: []int } and test comparability:
	// Try uncommenting the lines below to see Odin reject == on structs with slices:
	// b1 := Bag{}; b2 := Bag{}; fmt.println(b1 == b2)
}

main :: proc() {

	fmt.println("=== 1. Defining structs and compound literals ===")
	defining_structs_and_literals()

	fmt.println("\n=== 2. Nested structs, pointers, and tags ===")
	nested_structs_and_mutation()

	fmt.println("\n=== 3. Struct equality and comparability ===")
	struct_equality_and_comparability()
}
