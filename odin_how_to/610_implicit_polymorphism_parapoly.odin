// odin run 610_implicit_polymorphism_parapoly.odin -file

package main

import "core:fmt"

/*
Passing '$T: typeid' manually at every call site gets noisy when the compiler
can already see the type inside the arguments you pass. Implicit parametric
polymorphism—often called implicit parapoly—places '$' inside a parameter's
type pattern so Odin solves for T or N automatically from the call-site values:

    a: $T         deduces T from a value argument
    ptr: ^$T      deduces T from a pointer to T
    s: []$T       deduces T from a slice element type
    arr: [$N]$T   deduces both fixed length N and element type T
    m: map[$K]$V  deduces both key type K and value type V
    s: $T/[]$E    constrained specialization matching distinct slice types too

One crucial rule: Odin deduces implicit '$' parameters strictly from incoming
procedure arguments, never from the return type alone. A signature with only a
return type '-> $T' has nothing at the call site to solve T from.
*/

read_pointed :: proc(ptr: ^$T) -> T {

	return ptr^
}

// Write an in-place swap procedure using implicit pointer polymorphism:
// swap_values :: proc(a, b: ^$T)
// Because both pointers share the same $T, Odin enforces at compile time that
// a and b point to identical types. Swap a^ and b^ inside the body.

pointer_and_value_deduction :: proc() {

	/*
	When we write 'ptr: ^$T', Odin peels off the pointer '^' from the caller's
	argument (say '^int') and binds T = int. Because T is solved from the
	incoming argument pattern, a return-only '$T' with zero '$'-bearing
	parameters cannot be deduced—in that case you must switch to an explicit
	'$T: typeid' parameter as in Primer 600.

	    Suppose x := 10 and y := 20, and you call swap_values(&x, &y):
	    Both &x and &y have type ^int, so T resolves to int, and after
	    swap_values finishes, x holds 20 and y holds 10.
	*/

	anchor_num := 99
	fmt.printfln("Starter deref: %v", read_pointed(&anchor_num))

	// Declare x, y := 10, 20 and call swap_values(&x, &y), then declare
	// first, second := "hello", "world" and call swap_values(&first, &second).
	// Print both pairs after swapping.


	// Try uncommenting below to see Odin reject conflicting $T deductions:
	// a_int := 1
	// b_str := "two"
	// swap_values(&a_int, &b_str)


	// Try uncommenting below to observe the return-only $T deduction limit
	// (you cannot deduce $T when T never appears in any parameter):
	// make_zero_bad :: proc() -> $T { return {} }
	// bad_val: int = make_zero_bad()
	// fmt.println(bad_val)
}

Score_List :: distinct []int

// Write generic helpers for slices, fixed arrays, and distinct slices:
// reverse_in_place :: proc(items: []$T)
// fixed_array_len :: proc(arr: [$N]$T) -> int
// slice_first :: proc(s: $T/[]$E) -> (val: E, ok: bool)
// In reverse_in_place, loop i in 0..<len(items)/2 and swap items[i] with
// items[len(items) - 1 - i]. In fixed_array_len, return N directly. In
// slice_first, return {}, false when len(s) == 0, otherwise return s[0], true.

slices_and_fixed_arrays :: proc() {

	/*
	Notice the difference between 'items: []$T' and 'arr: [$N]$T'. A slice
	carries its length at runtime inside a 16-byte header, so only the element
	type T is baked at compile time. A fixed array '[N]T' bakes its length into
	the type itself, so 'arr: [$N]$T' deduces both N and T at compile time.

	The slash pattern '$T/[]$E' goes one step further for 'distinct' types.
	Suppose you define 'Score_List :: distinct []int'. A plain '[]$T' parameter
	rejects Score_List because Score_List is a distinct type, whereas '$T/[]$E'
	matches any type T whose underlying structure is a slice of E, binding T to
	Score_List and E to int.
	*/

	base_scores := Score_List{10, 20, 30}
	fmt.printfln("Starter distinct slice length: %d", len(base_scores))

	// Declare nums := [5]int{1, 2, 3, 4, 5}, call reverse_in_place(nums[:]),
	// and print nums (expected: [5, 4, 3, 2, 1]).


	// Declare floats := [8]f64{1, 2, 3, 4, 5, 6, 7, 8} and print
	// fixed_array_len(floats) alongside read_pointed(&floats[0]).


	// Test slice_first on both nums[:] and base_scores (a distinct Score_List),
	// plus an empty []int{} slice, printing both returned (val, ok) pairs.
}

// Write generic helpers for maps and allocator-aware slice filtering:
// map_has_key :: proc(m: map[$K]$V, key: K) -> bool
// filter_slice :: proc(items: []$T, pred: proc(T) -> bool, allocator := context.allocator) -> []T
// In map_has_key, look up _, ok := m[key] and return ok. In filter_slice,
// build result := make([dynamic]T, 0, len(items), allocator), append every
// item where pred(item) is true, and return result[:].

maps_and_allocator_aware_slices :: proc() {

	/*
	Odin maps deduce both key and value types via 'm: map[$K]$V'. Notice that
	adding 'allocator := context.allocator' at the end of a generic procedure
	like filter_slice keeps the call site simple for everyday heap allocations
	while letting callers swap in context.temp_allocator or a custom arena
	without rewriting the generic helper.
	*/

	ports := make(map[string]int)
	defer delete(ports)
	ports["http"] = 80
	ports["https"] = 443
	fmt.printfln("Starter ports count: %d", len(ports))

	// Call map_has_key(ports, "https") and map_has_key(ports, "ssh") and print
	// both booleans.


	// Declare readings := []int{4, 15, 8, 23, 11, 42} and call filter_slice with
	// an inline predicate proc(x: int) -> bool { return x >= 12 } using the
	// default allocator (with defer delete). Print the filtered slice.


	// Call filter_slice again on readings passing context.temp_allocator as the
	// third argument (with defer free_all(context.temp_allocator)), filtering
	// for even numbers, and print the result.
}

main :: proc() {

	fmt.println("=== 1. Pointer and value deduction ===")
	pointer_and_value_deduction()

	fmt.println("\n=== 2. Slices and fixed arrays ===")
	slices_and_fixed_arrays()

	fmt.println("\n=== 3. Maps and allocator-aware slices ===")
	maps_and_allocator_aware_slices()
}
