// odin run 240_enums_and_enumerated_arrays.odin -file

package main

import "core:fmt"

/*
Enums in Odin ('Name :: enum Backing_Int { ... }') are strongly typed integers:
unlike C, you cannot accidentally pass a raw int where a Tile_Kind is expected,
and unlike Go, every variant lives inside the enum's own namespace.

Because Odin tracks the expected enum type across assignments, switch cases,
procedure arguments, struct literals, and array indices, you get two powerful
ergonomic features:

    .Variant           implicit selector expression when enum type is known
    [Enum]Value_Type   enumerated array indexed directly by enum variants
*/

Sparse_Flags :: enum {
	Alpha = 1,
	Beta  = 10,
	Gamma = 100,
}

enum_basics_and_implicit_selectors :: proc() {

	/*
	An enum defaults to 'int' (8 bytes on 64-bit) unless you pick a smaller
	backing type such as 'enum u8' or 'enum u16' to pack structs tightly. Variants
	start at 0 and increment by 1 unless you assign explicit values.

	Four built-in operations work directly on any enum type:
	'len(Enum)' gives the variant count, 'min(Enum)' and 'max(Enum)' give the
	lowest and highest backing values, and 'for v in Enum' loops through every
	declared variant in order (even when values are sparse!).

	When the compiler already knows the target type is Sparse_Flags, writing
	'.Beta' (an implicit selector expression) is shorthand for 'Sparse_Flags.Beta':
	    Suppose flag: Sparse_Flags = .Alpha
	    switch flag {
	    case .Alpha: fmt.println("one")
	    case .Beta:  fmt.println("ten")
	    case .Gamma: fmt.println("hundred")
	    }
	Because 'flag' is already typed as Sparse_Flags, neither the assignment nor
	any case label repeats 'Sparse_Flags.'.
	*/

	fmt.printfln(
		"Sparse_Flags: count=%v, min=%v, max=%v, size=%v bytes",
		len(Sparse_Flags),
		min(Sparse_Flags),
		max(Sparse_Flags),
		size_of(Sparse_Flags),
	)

	// Define Tile_Kind :: enum u8 { Grass, Water, Mountain, Road } (at file scope
	// or inside this section if scoped locally, though file scope lets all three
	// sections share Tile_Kind!).
	// Print len(Tile_Kind), min(Tile_Kind), max(Tile_Kind), and size_of(Tile_Kind)
	// (expected: 1 byte because of the u8 backing type).


	// Declare current_tile: Tile_Kind = .Mountain using an implicit selector,
	// loop over every variant with: for kind in Tile_Kind
	// Print each variant's name and numeric backing value int(kind).


	// Write a small helper at file scope:
	// is_passable :: proc(kind: Tile_Kind) -> bool
	// returning false for .Water and true for .Grass, .Mountain, .Road using an
	// exhaustive switch. Call it from here as is_passable(.Water) without writing
	// Tile_Kind.Water!
}

enumerated_arrays_and_partial :: proc() {

	/*
	In C or Go, mapping each enum variant to a lookup value forces you to cast
	'costs[int(kind)]' and silently leaves trailing slots zeroed if someone adds
	a new enum variant later. Odin lets you use the enum type itself as the array
	index type:

	    Suppose costs := [Tile_Kind]f32{ .Grass = 1.0, .Water = 5.0, .Mountain = 3.5, .Road = 0.5 }
	    Then costs[.Mountain] evaluates to 3.5 with zero casting.

	Even better, enumerated array literals are exhaustive by default: omitting
	even one variant fails compilation immediately so lookup tables stay in sync
	with enum definitions. When you intentionally want omitted entries zeroed,
	write '#partial [Tile_Kind]bool{ .Water = true }' instead.

	For enums with wide gaps like Sparse_Flags (1, 10, 100), a dense array would
	allocate 100 slots (0..=100) just to store 3 values. Adding '#sparse' in
	front of the array type ('#sparse [Sparse_Flags]string') packs only the
	declared variants into a compact 3-element array!
	*/

	// Starter #sparse enumerated array for non-contiguous Sparse_Flags:
	sparse_names := #sparse [Sparse_Flags]string{
		.Alpha = "first",
		.Beta  = "second",
		.Gamma = "third",
	}
	fmt.printfln("Sparse Beta=%v, len=%v, size=%v bytes", sparse_names[.Beta], len(sparse_names), size_of(sparse_names))

	// Try uncommenting below to see Odin catch a missing variant when #partial is omitted:
	// incomplete := #sparse [Sparse_Flags]int{.Alpha = 1}


	// Declare movement_cost := [Tile_Kind]f32{ .Grass = 1.0, .Water = 5.0, .Mountain = 3.5, .Road = 0.5 }
	// Index movement_cost[.Mountain] directly and print it, then loop:
	// for kind in Tile_Kind
	// and print each kind alongside movement_cost[kind].


	// Declare a partial boolean hazard table:
	// is_hazard := #partial [Tile_Kind]bool{ .Water = true }
	// Print is_hazard[.Water] (true) and is_hazard[.Grass] (false, zeroed).


	// Try building a dense vs sparse comparison: declare a second sparse enum
	// Http_Status :: enum { Ok = 200, Not_Found = 404, Server_Error = 500 }
	// and a #sparse [Http_Status]string table mapping each code to its message.
	// Print len(status_text) and status_text[.Not_Found].
}

enum_bucket_tables :: proc() {

	/*
	Because [Enum]T is just a fixed-size array indexed by enum variants, the
	element type T can be a dynamic array: '[Tile_Kind][dynamic]string'. That
	gives you an O(1) bucket table with zero hashing overhead whenever your keys
	are a small known enum, replacing 'map[Tile_Kind][dynamic]string'.

	    Suppose buckets: [Tile_Kind][dynamic]string
	    defer for kind in Tile_Kind { delete(buckets[kind]) }
	    append(&buckets[.Grass], "Oak")   // buckets[.Grass] now holds ["Oak"]

	Notice the cleanup rule: each bucket holds its own dynamic array allocation,
	so register a 'defer' loop that deletes every bucket (calling delete on an
	empty bucket is a safe no-op).
	*/

	// Declare buckets: [Tile_Kind][dynamic]string and register cleanup right away:
	// defer for kind in Tile_Kind { delete(buckets[kind]) }
	// Append "Meadow" and "Clover" to &buckets[.Grass], "River" to &buckets[.Water],
	// and "Granite" to &buckets[.Mountain].


	// Iterate over all variants with: for kind in Tile_Kind
	// Print each kind alongside len(buckets[kind]) and buckets[kind], and verify
	// buckets[.Road] is empty without any nil-map lookup boilerplate.


	// Combine enumerated arrays with a helper procedure: write at file scope
	// total_bucket_items :: proc(buckets: [Tile_Kind][dynamic]string) -> int
	// that sums len(buckets[kind]) across all variants and print the total here.
}

main :: proc() {

	fmt.println("=== 1. Enum basics and implicit selectors ===")
	enum_basics_and_implicit_selectors()

	fmt.println("\n=== 2. Enumerated arrays, #partial, and #sparse ===")
	enumerated_arrays_and_partial()

	fmt.println("\n=== 3. Enumerated dynamic-array bucket tables ===")
	enum_bucket_tables()
}
