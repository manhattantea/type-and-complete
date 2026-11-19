// odin run 245_bit_sets_and_bit_fields.odin -file

package main

import "core:fmt"

/*
In C and C++, bitmasks rely on manual '(1 << FLAG)' shifts and untyped integers
that happily mix unrelated flag sets, while C bitfields leave bit ordering and
padding up to the compiler. Odin provides two deterministic, type-safe tools:

    bit_set[Domain; Backing_Int]   each enum variant or range integer maps to one bit
    bit_field Backing_Int { ... }  packs exact bit widths LSB-to-MSB into an integer
*/

Small_Digits :: bit_set[0..<8; u8]

bit_set_basics_and_mutations :: proc() {

	/*
	A 'bit_set[Domain; Backing_Int]' stores membership as single bits inside the
	backing integer (or defaults to the smallest unsigned integer that fits if
	you omit '; Backing_Int'). Because every bit_set is its own distinct type, the
	compiler stops you from mixing bits from two different enums.

	Key built-in operations on a bit_set 'bs':
	'x in bs' and 'x not_in bs' test single-bit membership, 'card(bs)' returns the
	population count (number of set bits), 'incl(&bs, .Flag)' turns a bit on, and
	'excl(&bs, .Flag)' turns a bit off.

	    Suppose digits := Small_Digits{1, 3, 5}
	    incl(&digits, 7)      // digits becomes {1, 3, 5, 7}, card(digits) == 4
	    excl(&digits, 3)      // digits becomes {1, 5, 7}, 3 not_in digits == true
	*/

	// Starter range-based bit_set packed into a single byte (size_of == 1):
	digits := Small_Digits{1, 3, 5}
	fmt.printfln("Starter bit_set: %v (card=%v, size=%v, has 3=%v)", digits, card(digits), size_of(Small_Digits), 3 in digits)

	// Try uncommenting below to see Odin reject values outside 0..<8 at compile time:
	// bad_digits := Small_Digits{9}


	// Define Status_Effect :: enum { Poisoned, Burning, Frozen, Shielded }
	// and Status_Set :: bit_set[Status_Effect; u8] (at file scope so the next
	// section can reuse them too).
	// Create active := Status_Set{.Poisoned, .Shielded}, print active and card(active).


	// Add .Burning using incl(&active, .Burning), remove .Poisoned using
	// excl(&active, .Poisoned), check .Frozen not_in active, and loop through
	// active statuses using: for eff in Status_Effect { if eff in active { ... } }
}

bit_set_algebra :: proc() {

	/*
	Beyond single-bit toggles, bit_set supports mathematical set operators right
	in expressions:

	    a + b   or   a | b    union (bits present in either a or b)
	    a & b                 intersection (bits present in both a and b)
	    a - b   or   a &~ b   difference (bits in a that are NOT in b)
	    a ~ b                 symmetric difference (bits in exactly one of a or b)
	    a <= b                subset check (every bit in a is also set in b)

	    Suppose required := Status_Set{.Poisoned, .Burning} and
	    immune := Status_Set{.Burning, .Frozen}:
	        unblocked := required - immune   // evaluates to {.Poisoned}
	        overlap   := required & immune   // evaluates to {.Burning}
	*/

	// Create two Status_Set values:
	// player_buffs := Status_Set{.Shielded, .Burning}
	// arena_auras  := Status_Set{.Burning, .Poisoned}
	// Compute and print their union (player_buffs + arena_auras), intersection
	// (player_buffs & arena_auras), difference (arena_auras - player_buffs), and
	// symmetric difference (player_buffs ~ arena_auras).


	// Test subset checks cleanly: declare fire_ward := Status_Set{.Burning} and
	// verify fire_ward <= player_buffs (true) vs fire_ward <= arena_auras (true)
	// vs Status_Set{.Frozen} <= player_buffs (false).


	// Define a second bit_set for permissions:
	// Perm :: enum { Read, Write, Execute, Admin }
	// Perm_Set :: bit_set[Perm; u8]
	// Write a helper at file scope:
	// has_all_perms :: proc(held, required: Perm_Set) -> bool
	// returning required <= held, and also print missing := required - held when
	// held is Perm_Set{.Read, .Execute} and required is Perm_Set{.Read, .Write}.
}

bit_fields_and_enum_packing :: proc() {

	/*
	When we write 'bit_field u16 { ... }', Odin packs fields sequentially from
	least-significant bit (bit 0) upward into an exact 16-bit integer. Unlike C
	bitfields, the bit layout is 100% portable and deterministic, and Odin rejects
	any field whose bit width cannot hold its type or whose total exceeds the
	backing integer's width.

	You can pack unsigned/signed integers, booleans (1 bit), and even enums
	directly inside a bit_field:
	    Suppose Sprite_Shape :: enum u8 { Square, Horizontal, Vertical }
	    Here Sprite_Shape values 0..=2 fit inside 2 bits ('shape: Sprite_Shape | 2').
	Once constructed, you read and mutate fields with dot syntax ('attr.mode = 2')
	and convert the whole packed register to/from its backing integer with
	'u16(attr)' or 'transmute(u16)attr'.
	*/

	// Define Sprite_Shape :: enum u8 { Square, Horizontal, Vertical } and
	// Gba_Sprite_Attr :: bit_field u16 {
	//     y_coord:     u8           | 8,
	//     affine:      bool         | 1,
	//     double_size: bool         | 1,
	//     mode:        u8           | 2,
	//     mosaic:      bool         | 1,
	//     palette_256: bool         | 1,
	//     shape:       Sprite_Shape | 2,
	// }
	// Verify #assert(size_of(Gba_Sprite_Attr) == 2).


	// Instantiate attr := Gba_Sprite_Attr{ y_coord = 120, affine = true, mode = 1, palette_256 = true, shape = .Horizontal }
	// Print attr.y_coord, attr.shape, and its raw packed 16-bit integer value
	// transmute(u16)attr formatted in hex with %#04x.


	// Mutate fields in place with dot syntax (attr.mosaic = true; attr.mode = 3)
	// and print transmute(u16)attr again to watch only those specific bits flip.


	// Unpack a raw hardware value in reverse: declare raw_reg: u16 = 0x8478,
	// convert it with unpacked := transmute(Gba_Sprite_Attr)raw_reg, and print
	// unpacked.y_coord, unpacked.mode, unpacked.palette_256, and unpacked.shape.


	// Try uncommenting below to see Odin reject a bit_field whose field widths
	// exceed the backing integer's width (10 bits > u8) or fail to hold an enum:
	// Bad_Bits :: bit_field u8 { low: u8 | 5, high: u8 | 5 }
}

main :: proc() {

	fmt.println("=== 1. bit_set basics and mutations ===")
	bit_set_basics_and_mutations()

	fmt.println("\n=== 2. bit_set algebra ===")
	bit_set_algebra()

	fmt.println("\n=== 3. bit_field and enum packing ===")
	bit_fields_and_enum_packing()
}
