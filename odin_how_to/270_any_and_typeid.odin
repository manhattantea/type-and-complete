// odin run 270_any_and_typeid.odin -file

package main

import "core:fmt"

/*
Odin's 'any' is a 16-byte runtime-typed view containing a raw pointer and a
runtime type identifier: '{ data: rawptr, id: typeid }'. Packages like
'core:fmt' and 'core:reflect' use 'any' to inspect arbitrary values without
generating separate code for every type.

Because 'any' does NOT own or copy heap memory—it merely points at existing
memory—you must watch stack lifetimes carefully whenever you construct one.
*/

inspecting_any_and_typeid :: proc() {

	/*
	Every type in Odin has a unique compile-time 'typeid' queried with
	'typeid_of(T)'. When you assign a concrete value to an 'any':
	    Suppose sample: any = 42
	Odin puts 42 in a stack slot in the current frame, points 'sample.data' at
	that slot, and sets 'sample.id = typeid_of(int)'.

	You can compare 'sample.id == typeid_of(int)', extract the typed value with
	a comma-ok assertion ('num, ok := sample.(int)'), or inspect raw bytes
	through 'sample.data'.
	*/

	// Starter 16-byte any inspecting its runtime typeid and size_of:
	sample: any = 42
	fmt.printfln(
		"Starter any: val=%v, id=%v, size=%v, is_int=%v",
		sample,
		sample.id,
		size_of(any),
		sample.id == typeid_of(int),
	)

	// Extract the concrete integer from sample using a comma-ok type assertion:
	// num, ok := sample.(int)
	// Also test a mismatched assertion: str_val, is_str := sample.(string)
	// Print num, ok, str_val, and is_str.


	// Store typeid values directly in a variable or slice:
	// types := []typeid{typeid_of(int), typeid_of(f64), typeid_of(string)}
	// Loop over types and print each typeid alongside sample.id == tid.
}

type_switches_and_lifetime_trap :: proc() {

	/*
	Just like tagged unions, 'any' supports pattern matching via 'switch v in a'.
	Because 'any' can hold any type in the entire program, always include a
	default 'case:' branch to handle unexpected types cleanly.

	Watch out for the stack-lifetime hazard:
	    Suppose bad_wrap :: proc() -> any {
	        local := 99
	        return local   // DANGER: local dies when bad_wrap returns!
	    }
	Because 'any' only stores a pointer to 'local', returning an 'any' backed by
	a local variable creates a dangling pointer! Only pass 'any' downward into
	procedures (like fmt.println) or point it at data that outlives the 'any'.
	*/

	// Write describe_any :: proc(a: any) at file scope that prints a.id and uses
	// 'switch v in a' with case int:, case string:, case bool:, and a default
	// case: printing a formatted summary of the value.


	// Call describe_any from here with 123, "Odin", true, and [2]int{1, 2}.


	// Verify how 'any' points straight at existing local variables:
	// declare count := 10 and view: any = count. Print rawptr(&count) vs view.data
	// to confirm view.data points directly at count's stack address without copying.
}

main :: proc() {

	fmt.println("=== 1. Inspecting any and typeid ===")
	inspecting_any_and_typeid()

	fmt.println("\n=== 2. Type switches on any and stack lifetime trap ===")
	type_switches_and_lifetime_trap()
}
