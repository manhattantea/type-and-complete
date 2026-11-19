// odin run 660_runtime_type_information.odin -file

package main

import "base:runtime"
import "core:fmt"

/*
Every Odin binary embeds a Runtime Type Information (RTTI) table holding a
'runtime.Type_Info' record for every type used by the program. Calling
'type_info_of(T_or_typeid)' returns a '^runtime.Type_Info' pointer with '.id',
'.size', '.align', and a '.variant' tagged union describing the type's shape.

That single table is why fmt.println, encoding/json, core:flags, and
core:reflect can inspect arbitrary structs and enums at runtime with zero
external code generation.
*/

Custom_Int :: distinct i32

// Define two custom types to inspect via RTTI:
// Color :: enum { Red, Green, Blue }
// Player :: struct { id: u64, name: string, score: f32 }

type_info_and_base_unwrapping :: proc() {

	/*
	When you declare 'Custom_Int :: distinct i32', Odin wraps the underlying
	i32 descriptor inside a 'runtime.Type_Info_Named' node so error messages and
	%T formatting keep the name "Custom_Int". Calling 'runtime.type_info_base(ti)'
	peels off those named/distinct layers and returns the underlying structural
	Type_Info (here i32).

	    Suppose ti := type_info_of(Custom_Int):
	    ti.variant is Type_Info_Named (name = "Custom_Int"), while
	    runtime.type_info_base(ti).variant is Type_Info_Integer (signed = true).
	*/

	ti := type_info_of(Custom_Int)
	base_ti := runtime.type_info_base(ti)
	fmt.printfln("Starter RTTI: type=%v, size=%d, align=%d, base=%v", ti.id, ti.size, ti.align, base_ti.id)

	// Switch on ti.variant using #partial switch info in ti.variant to handle
	// runtime.Type_Info_Named and print info.name and info.base.id before
	// unwrapping.


	// Compare size_of(Player) and align_of(Player) against
	// type_info_of(Player).size and type_info_of(Player).align, and print
	// type_info_of(Color).id alongside len(Color).
}

// Write a procedure that inspects a typeid's runtime Type_Info variants:
// print_type_details :: proc(id: typeid)
// Fetch ti := type_info_of(id) and base_ti := runtime.type_info_base(ti), print
// id, ti.size, and ti.align, then use #partial switch info in base_ti.variant
// to handle:
// - runtime.Type_Info_Integer: print bit width (base_ti.size * 8) and info.signed
// - runtime.Type_Info_Float: print bit width (base_ti.size * 8)
// - runtime.Type_Info_Enum: print info.base.id and info.names
// - runtime.Type_Info_Slice: print info.elem.id
// - runtime.Type_Info_Struct: loop i in 0..<info.field_count printing info.names[i] and info.types[i].id

switching_on_type_info_variants :: proc() {

	/*
	Inside 'base_ti.variant', each Odin type category maps to a dedicated struct
	variant. Notice that Type_Info_Struct stores its field arrays in Struct-of-
	Arrays multi-pointers ('info.names', 'info.types', 'info.offsets') bounded
	by 'info.field_count', whereas Type_Info_Enum stores 'info.names' as a
	slice. Using '#partial switch' lets you handle the variants you care about
	without listing every Type_Info variant in base:runtime.
	*/

	sample_ti := type_info_of(f64)
	#partial switch _ in sample_ti.variant {
	case runtime.Type_Info_Float:
		fmt.printfln("Starter variant check: f64 is a %d-bit float", sample_ti.size * 8)
	}

	// Call print_type_details on Custom_Int, Color, Player, and []string.
	// Confirm Custom_Int unwraps to a 32-bit signed integer and Player lists
	// id (u64), name (string), and score (f32).


	// Add cases for runtime.Type_Info_Pointer (printing info.elem.id) and
	// runtime.Type_Info_Array (printing info.count and info.elem.id) in
	// print_type_details, then test both ^Player and [4]u8.


	// Add a case for runtime.Type_Info_Dynamic_Array printing info.elem.id and
	// test print_type_details([dynamic]Color) to inspect growable slice RTTI.
}

// Define a nested struct containing a slice and pointer to test recursion:
// Team :: struct { title: string, leader: ^Player, roster: []Player }
//
// Write a recursive RTTI pretty-printer across runtime.Type_Info variants:
// pretty_print_rtti :: proc(id: typeid, depth := 0)
// Indent each line by depth * 2 spaces, fetch ti := type_info_of(id) and
// base_ti := runtime.type_info_base(ti), print the type name (ti.id) and byte
// size, and recurse on nested types inside #partial switch info in base_ti.variant:
// - runtime.Type_Info_Integer, runtime.Type_Info_Float, runtime.Type_Info_String,
//   runtime.Type_Info_Boolean, runtime.Type_Info_Enum: print leaf details
// - runtime.Type_Info_Slice: print "slice of:" and call pretty_print_rtti(info.elem.id, depth + 1)
// - runtime.Type_Info_Pointer: print "pointer to:" and call pretty_print_rtti(info.elem.id, depth + 1)
// - runtime.Type_Info_Array: print count and call pretty_print_rtti(info.elem.id, depth + 1)
// - runtime.Type_Info_Struct: loop i in 0..<info.field_count, print field name
//   and offset (info.offsets[i]), then call pretty_print_rtti(info.types[i].id, depth + 1)

recursive_rtti_pretty_printer :: proc() {

	/*
	Because every nested field or element pointer inside Type_Info points to
	another '^runtime.Type_Info' with its own '.id', a 30-line recursive switch
	can walk arbitrarily deep compound types—exactly how serializers like
	encoding/json traverse nested structs, slices, and enums at runtime.
	*/

	nested_ti := type_info_of([]Custom_Int)
	fmt.printfln("Starter nested type id: %v (size=%d)", nested_ti.id, nested_ti.size)

	// Call pretty_print_rtti(Player) and pretty_print_rtti([]Color) to verify
	// leaf and slice recursion.


	// Call pretty_print_rtti(Team) to watch the pretty-printer walk through
	// string, ^Player, and []Player recursively.


	// Define a small wrapper struct Match :: struct { home: Team, scores: [2]int }
	// and pass Match to pretty_print_rtti to confirm multi-level struct and
	// fixed-array recursion prints every nested field cleanly.
}

main :: proc() {

	fmt.println("=== 1. Type_Info and base unwrapping ===")
	type_info_and_base_unwrapping()

	fmt.println("\n=== 2. Switching on Type_Info variants ===")
	switching_on_type_info_variants()

	fmt.println("\n=== 3. Recursive RTTI pretty-printer ===")
	recursive_rtti_pretty_printer()
}
