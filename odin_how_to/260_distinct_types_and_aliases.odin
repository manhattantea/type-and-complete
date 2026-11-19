// odin run 260_distinct_types_and_aliases.odin -file

package main

import "core:fmt"

/*
In C, 'typedef double Seconds; typedef double Meters;' creates weak aliases
that let you pass Seconds where Meters is expected without a peep from the
compiler. Odin draws a sharp line between transparent aliases and strict
nominal types:

    Float64_Alias :: f64        transparent alias; mixes freely with f64
    Seconds :: distinct f64     brand-new nominal type; never mixes implicitly

A 'distinct' type keeps the exact same memory representation and built-in
operators (+, -, *, /, <, ==) as its underlying type, so there is zero runtime
overhead—just compile-time safety against unit and ID mix-ups.
*/

Entity_Id :: distinct u64

aliases_vs_distinct_types :: proc() {

	/*
	Untyped numeric literals ('0.5', '1001') automatically adapt to any compatible
	distinct type without an explicit cast. Once a value carries a distinct
	type, however, assigning it to the base type or another distinct type
	requires an explicit conversion like 'u64(player_id)'.

	    Suppose Seconds :: distinct f64 and Meters :: distinct f64:
	        dt: Seconds = 0.5        // untyped 0.5 adapts to Seconds
	        sum := dt + Seconds(1.0) // same distinct type adds cleanly -> Seconds(1.5)
	        // bad := dt + 1.0       // works because 1.0 is untyped, whereas f64(1.0) fails!
	*/

	// Starter distinct integer ID that cannot mix with raw u64 or Texture_Id:
	player_id: Entity_Id = 1001
	fmt.printfln("Starter Entity_Id: %v (size=%v bytes)", player_id, size_of(Entity_Id))

	// Try uncommenting below to see Odin reject mixing Entity_Id with raw u64:
	// raw_id: u64 = player_id


	// Define at file scope:
	// Seconds :: distinct f64
	// Meters :: distinct f64
	// Float64_Alias :: f64
	// Declare dt: Seconds = 0.5 and dist: Meters = 10.0, then compute
	// doubled_dt := dt + Seconds(1.0) and print both.


	// Verify transparent aliases mix freely: declare raw_val: f64 = 2.5 and
	// alias_val: Float64_Alias = raw_val, add them directly (raw_val + alias_val),
	// and print the sum.
}

unit_safe_procedures :: proc() {

	/*
	Distinct types shine in procedure boundaries: if 'velocity' accepts
	'(d: Meters, t: Seconds)', swapping the arguments at the call site becomes
	a compile-time error instead of a silent physics bug. Inside the procedure,
	convert explicitly with 'f64(d) / f64(t)' to combine the two distinct types.
	*/

	// Write velocity :: proc(d: Meters, t: Seconds) -> f64 at file scope returning
	// f64(d) / f64(t). Call velocity(Meters(100.0), Seconds(8.0)) here and print
	// the speed.


	// Test the compile-time safety net: write a commented-out wrong-order call
	// velocity(Seconds(8.0), Meters(100.0)) and verify uncommenting fails to check.


	// Practice distinct ID safety: define Texture_Id :: distinct u64 and write a
	// helper bind_entity :: proc(id: Entity_Id) that prints id. Try passing
	// Entity_Id(42) vs confirming Texture_Id(42) cannot be passed without casting.
}

main :: proc() {

	fmt.println("=== 1. Transparent aliases vs distinct types ===")
	aliases_vs_distinct_types()

	fmt.println("\n=== 2. Unit-safe procedures ===")
	unit_safe_procedures()
}
