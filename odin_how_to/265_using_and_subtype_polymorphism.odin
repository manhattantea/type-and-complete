// odin run 265_using_and_subtype_polymorphism.odin -file

package main

import "core:fmt"

/*
Odin has no classes, no 'virtual' methods, and no hidden inheritance vtables.
Instead, it pairs explicit struct composition ('using') with tagged unions so
data stays flat in memory and polymorphism stays visible in the types:

    using field: Base   forwards Base's fields AND allows ^Derived -> ^Base upcasts
                        when the field sits at byte offset 0
    #subtype field: Base allows ^Derived -> ^Base upcasts without forwarding fields
    variant: union      enables safe pattern-matched downcasting via switch
*/

Transform :: struct {
	pos: [2]f32,
}

Prop :: struct {
	using transform: Transform,
	name:            string,
}

Offset_Prop :: struct {
	tag:             u32,
	using transform: Transform,
}

inspect_transform :: proc(t: ^Transform) {

	fmt.printfln("Transform pos=%v", t.pos)
}

using_field_forwarding_and_upcasting :: proc() {

	/*
	When we put 'using transform: Transform' inside Prop, Odin promotes every
	field of Transform directly into Prop's namespace so you can read 'crate.pos'
	instead of 'crate.transform.pos'.

	Even better, because 'transform' sits at byte offset 0 inside Prop, the
	address '&crate' points to the exact same byte as '&crate.transform'. That
	lets you pass '&crate' straight to any procedure expecting '^Transform' with
	zero explicit casting!

	If another field comes first (like 'tag: u32' in Offset_Prop), 'transform'
	moves past offset 0: 'bad_prop.pos' still forwards, but implicit upcasting
	'^Offset_Prop' -> '^Transform' is rejected because '&bad_prop' no longer
	points at the Transform bytes.
	*/

	// Starter offset-0 composition and implicit ^Prop -> ^Transform upcast:
	crate := Prop{transform = {pos = {1.0, 2.0}}, name = "Crate"}
	fmt.printfln("Prop '%v' at pos=%v (offset_of transform=%v)", crate.name, crate.pos, offset_of(Prop, transform))
	inspect_transform(&crate)

	// Try uncommenting the two lines below to see Odin reject non-offset-0
	// implicit pointer upcasting (^Offset_Prop -> ^Transform):
	// bad_prop := Offset_Prop{tag = 7, transform = {pos = {3.0, 4.0}}}
	// inspect_transform(&bad_prop)


	// Prove that Offset_Prop still supports field forwarding and explicit field
	// addressing: declare offset_crate := Offset_Prop{tag = 7, transform = {pos = {3.0, 4.0}}},
	// print offset_crate.pos directly, and call inspect_transform(&offset_crate.transform).


	// Define a value-level #subtype struct without namespace pollution:
	// Sprite_Info :: struct { #subtype transform: Transform, tint: u32 }
	// Instantiate s := Sprite_Info{transform = {pos = {8.0, 9.0}}, tint = 0xFF},
	// pass &s directly to inspect_transform(&s) (works because offset == 0!),
	// and verify s.transform.pos works while s.pos would not be forwarded.
}

entity_hierarchy_and_variant_downcasting :: proc() {

	/*
	Upcasting from ^Player to ^Entity only solves half of polymorphism. When a
	shared procedure receives '^Entity' and needs player-specific or door-specific
	behavior, Odin avoids unsafe blind casts by storing a tagged union on the
	base struct:

	    Suppose Entity :: struct { id: u64, pos: [2]f32, variant: union { ^Player, ^Door } }
	    and Player :: struct { using base: Entity, stamina: f32 }:
	        p := Player{base = {id = 1, pos = {0, 0}}, stamina = 100}
	        p.variant = &p
	Any procedure taking '^Entity' can then switch on 'e.variant' to reach
	'^Player' safely at runtime with zero hidden vtable indirection.
	*/

	// Define at file scope:
	// Entity :: struct { id: u64, pos: [2]f32, variant: union { ^Player, ^Door } }
	// Player :: struct { using base: Entity, stamina: f32 }
	// Door   :: struct { using base: Entity, locked: bool }


	// Write two procedures at file scope:
	// move_entity :: proc(e: ^Entity, delta: [2]f32)   (adds delta to e.pos)
	// interact    :: proc(e: ^Entity)                  (switches on e.variant)
	// Inside interact, handle case ^Player:, case ^Door:, and case nil:, printing
	// each subtype's specific state (stamina vs locked) and toggling door.locked!


	// Instantiate player: Player and door: Door here with id, pos, stamina, and
	// locked initialized, and wire player.variant = &player and door.variant = &door.
	// Call move_entity(&player, {1, 2}) and move_entity(&door, {0, 5}) with zero
	// casting, then store both in entities := [2]^Entity{&player, &door} and loop
	// 'for ent in entities' calling interact(ent).
}

using_hygiene_and_enums :: proc() {

	/*
	While 'using' inside structs is Odin's backbone for composition, bringing
	arbitrary namespaces into scope with 'using' inside procedures or parameters
	makes it hard to see where identifiers come from (which is why '-vet-using-stmt'
	and '-vet-using-param' warn against those forms).

	Two practical caveats keep composition bug-free:
	First, if two embedded 'using' fields inside the same struct define fields
	with the same name (for example two bases that both have 'id: u64'), Odin
	rejects the ambiguous promotion at compile time.
	Second, copying a derived struct by value copies its embedded 'variant'
	pointer verbatim—so the copy's 'variant' still points back to the original
	struct until you rebind 'copy_val.variant = &copy_val'.
	*/

	// Practice the value-copy pointer caveat on a self-contained instance:
	// create original: Player with base = {id = 10, pos = {5, 5}}, stamina = 80
	// and original.variant = &original. Copy it with clone := original, change
	// clone.pos = {99, 99}, and rebind clone.variant = &clone before passing
	// &clone to interact(&clone) so interact updates clone rather than original!


	// Demonstrate why two 'using' fields with colliding names fail to compile:
	// declare Named_A :: struct { tag: int } and Named_B :: struct { tag: int }
	// and verify uncommenting:
	// Both_Clash :: struct { using a: Named_A, using b: Named_B }
	// triggers a field-name collision error.
}

main :: proc() {

	fmt.println("=== 1. Field forwarding, offset-0 upcasting, and #subtype ===")
	using_field_forwarding_and_upcasting()

	fmt.println("\n=== 2. Entity hierarchy and variant downcasting ===")
	entity_hierarchy_and_variant_downcasting()

	fmt.println("\n=== 3. Composition hygiene and value-copy caveats ===")
	using_hygiene_and_enums()
}
