// odin run 630_where_clauses_and_intrinsics.odin -file

package main

import "base:intrinsics"
import "core:fmt"

/*
Unconstrained generics fail late: if a procedure writes 'a + b' on an
unconstrained '$T', the compiler only complains deep inside the body when it
tries to instantiate 'T = string'. A 'where' clause attaches compile-time
boolean preconditions directly to a procedure or polymorphic struct signature,
rejecting unsupported types at the call site with clear diagnostics.

Combined with type predicates from 'base:intrinsics', you can constrain types
by category or structural shape without inheritance or interfaces:

    intrinsics.type_is_numeric(T)          integer, float, or complex
    intrinsics.type_is_integer(T)          signed or unsigned integer
    intrinsics.type_is_float(T)            floating-point number
    intrinsics.type_is_enum(T)             any enum type
    intrinsics.type_is_struct(T)           any struct type
    intrinsics.type_has_field(T, "id")     struct T declares field "id"
    intrinsics.type_field_type(T, "id")    typeid of field "id" in struct T
*/

add_numeric :: proc(a, b: $T) -> T where intrinsics.type_is_numeric(T) {

	return a + b
}

// Write a constrained fixed-array dot product procedure:
// dot_product :: proc(a, b: [$N]$T) -> T where N > 0, intrinsics.type_is_numeric(T)
// Accumulate sum: T = 0 across i in 0..<N by adding a[i] * b[i], and return sum.

numeric_procedure_constraints :: proc() {

	/*
	A 'where' clause can combine value constraints like 'N > 0' with type
	predicates like 'intrinsics.type_is_numeric(T)', separated by commas. Both
	must evaluate to true at compile time before Odin will instantiate the
	procedure body.

	    Suppose you call dot_product([3]f32{1, 2, 3}, [3]f32{4, 5, 6}):
	    N deduces to 3 (> 0) and T deduces to f32 (numeric), so the where
	    clause passes and the loop computes 1*4 + 2*5 + 3*6 = 32.0.
	*/

	fmt.printfln("Starter numeric sum: %v", add_numeric(15, 27))

	// Call dot_product on [3]f32{1.0, 2.0, 3.0} with [3]f32{4.0, 5.0, 6.0}
	// (expected: 32.0) and [4]int{1, 0, -2, 3} with [4]int{2, 4, 1, 5}
	// (expected: 15), and print both results.


	// Write a small float-only helper lerp :: proc(a, b, t: $T) -> T where intrinsics.type_is_float(T)
	// returning a + (b - a) * t, and test it on f32 and f64 values.


	// Write an integer-only bit-alignment helper align_up_pow2 :: proc(val, align: $T) -> T where intrinsics.type_is_integer(T)
	// computing (val + align - 1) & ~(align - 1), and test it on u32(100) with
	// alignment 64 (expected: 128).


	// Try uncommenting below to verify the where clause rejects non-numeric
	// elements and empty zero-length arrays at the call site:
	// bad_dot := dot_product([2]string{"a", "b"}, [2]string{"c", "d"})
	// empty_dot := dot_product([0]int{}, [0]int{})
}

// Define two unrelated structs that share an id field:
// User :: struct { id: u64, name: string }
// Order :: struct { id: u64, total: f64 }
//
// Write a compile-time structural getter constrained by base:intrinsics:
// extract_id :: proc(record: $T) -> u64 where intrinsics.type_is_struct(T), intrinsics.type_has_field(T, "id"), intrinsics.type_field_type(T, "id") == u64
// Return record.id.
//
// Also write an enum helper constrained by type_is_enum:
// enum_variant_count :: proc($E: typeid) -> int where intrinsics.type_is_enum(E)
// Return len(E).

structural_duck_typing_constraints :: proc() {

	/*
	Notice what 'extract_id' achieves without interfaces or base classes: any
	struct that carries an 'id: u64' field satisfies the 'where' clause at
	compile time. Checking 'intrinsics.type_field_type(T, "id") == u64' guards
	against structs whose 'id' field has an incompatible type like string.
	*/

	fmt.printfln("Starter complex sum: %v", add_numeric(1 + 2i, 3 - 1i))

	// Construct a User and an Order with distinct u64 IDs and print
	// extract_id(user) and extract_id(order).


	// Define a small local enum Direction :: enum { North, South, East, West }
	// and print enum_variant_count(Direction).


	// Try uncommenting below to confirm extract_id rejects a struct whose id
	// field is a string instead of u64:
	// Bad_Record :: struct { id: string }
	// bad_id := extract_id(Bad_Record{id = "abc"})
	// fmt.println(bad_id)
}

// Define a where-constrained polymorphic struct and a helper over it:
// Numeric_Range :: struct($T: typeid) where intrinsics.type_is_numeric(T) { lo: T, hi: T }
// range_contains :: proc(r: Numeric_Range($T), val: T) -> bool
// Return val >= r.lo && val <= r.hi.

constrained_polymorphic_structs :: proc() {

	/*
	Putting a 'where' clause directly on a polymorphic struct definition blocks
	invalid instantiations before any procedure even runs. Writing
	'Numeric_Range :: struct($T: typeid) where intrinsics.type_is_numeric(T)'
	means Numeric_Range(string) is illegal anywhere in the program, not just
	inside a helper procedure.
	*/

	fmt.printfln("Starter float sum: %v", add_numeric(f64(1.25), f64(2.75)))

	// Instantiate temp_range := Numeric_Range(f32){lo = -10.0, hi = 40.0} and
	// port_range := Numeric_Range(u16){lo = 1024, hi = 65535}. Test
	// range_contains on in-bounds and out-of-bounds values and print results.


	// Write a second helper range_span :: proc(r: Numeric_Range($T)) -> T where intrinsics.type_is_numeric(T)
	// returning r.hi - r.lo, and print range_span(temp_range) and range_span(port_range).


	// Try uncommenting below to observe the where clause rejecting Numeric_Range(string)
	// right at the type instantiation site:
	// bad_range := Numeric_Range(string){lo = "a", hi = "z"}
	// fmt.println(bad_range)
}

main :: proc() {

	fmt.println("=== 1. Numeric procedure constraints ===")
	numeric_procedure_constraints()

	fmt.println("\n=== 2. Structural duck-typing constraints ===")
	structural_duck_typing_constraints()

	fmt.println("\n=== 3. Constrained polymorphic structs ===")
	constrained_polymorphic_structs()
}
