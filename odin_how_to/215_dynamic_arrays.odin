// odin run 215_dynamic_arrays.odin -file

package main

import "base:runtime"
import "core:fmt"

/*
A dynamic array [dynamic]T in Odin is a growable, heap-backed buffer managed by
a 32-byte header (runtime.Raw_Dynamic_Array) storing four fields: data (rawptr),
len (int), cap (int), and allocator (runtime.Allocator).

Because the allocator lives right inside the header, subsequent append and
delete calls automatically use the same allocator that created the array. Any
operation that might change len, cap, or data—such as append(&arr, x),
pop(&arr), ordered_remove(&arr, i), unordered_remove(&arr, i), clear(&arr),
resize(&arr, n), reserve(&arr, cap), and shrink(&arr)—requires a pointer
^[dynamic]T so the caller's header updates in place.

This Primer is split into three focused sections called from main at the bottom.
*/

header_and_growth :: proc() {

	/*
	You allocate a dynamic array with make([dynamic]T) or
	make([dynamic]T, len, cap) and always pair it with defer delete(arr).
	Watch the two-argument vs three-argument form carefully:
	make([dynamic]int, 4) sets len = 4 with 4 zero-initialized elements, so the
	next append lands at index 4! When you only want to pre-allocate capacity,
	write make([dynamic]int, 0, 4).

	    Suppose nums := make([dynamic]int, 0, 2):
	        append(&nums, 10, 20)           // fits in cap 2, no realloc
	        append(&nums, ..[]int{30, 40})  // splats slice, grows cap
	*/

	// Starter anchor: inspect a dynamic array's 32-byte header fields.
	demo := make([dynamic]int, 0, 4)
	defer delete(demo)
	append(&demo, 1, 2, 3)
	raw_demo := transmute(runtime.Raw_Dynamic_Array)demo
	fmt.printfln("demo: %v (len=%v, cap=%v, data=%v)", demo, raw_demo.len, raw_demo.cap, raw_demo.data)

	// Create nums := make([dynamic]int, 0, 8) with defer delete(nums).
	// Append 10, 20, 30 individually with append(&nums, ...), then splat a slice
	// using append(&nums, ..[]int{40, 50}) and print nums, len(nums), cap(nums).


	// Compare make([dynamic]int, 4) against make([dynamic]int, 0, 4): create
	// prefilled := make([dynamic]int, 4) with defer delete(prefilled), call
	// append(&prefilled, 99), and print prefilled to see 99 land at index 4.


	// Practice capacity management on nums: call reserve(&nums, 16), then
	// resize(&nums, 7) (adds zero-initialized slots), print nums and cap(nums),
	// then call clear(&nums) (resets len to 0, keeps cap) and shrink(&nums).


	// Observe automatic growth: declare curve := make([dynamic]int) with
	// defer delete(curve), track prev_cap := cap(curve), and loop 0..<20
	// appending i and printing len and cap whenever cap(curve) != prev_cap.


	// Try uncommenting the line below to see why append requires ^[dynamic]int:
	// append(demo, 99)
}

pointer_invalidation_and_removals :: proc() {

	/*
	Never store an element pointer like p := &arr[0] across an append! Whenever
	append grows past cap(arr), Odin allocates a new block on the heap and frees
	the old one, turning p into a dangling pointer:

	    Suppose items has cap 2 and holds {100, 200}:
	        p := &items[0]              // points into old buffer A
	        append(&items, 300, 400)    // items reallocates to buffer B; A is freed!
	        // dereferencing p^ now reads freed memory

	For removing elements, Odin offers two distinct built-ins:
	ordered_remove(&arr, idx) preserves relative order by shifting later items
	left in O(N) time; unordered_remove(&arr, idx) swaps the final element into
	idx in O(1) time without preserving order. When deleting matching items in a
	loop with either removal proc, walk backward from len(arr) - 1 down to 0 so
	removing or swapping at index i never disturbs unvisited indices below i!
	*/

	// Starter anchor: start with capacity 2 so the next append forces reallocation.
	items := make([dynamic]int, 0, 2)
	defer delete(items)
	append(&items, 100, 200)
	fmt.printfln("items before growth: %v (cap=%v)", items, cap(items))

	// Live pointer invalidation check: capture first_ptr := &items[0] and print
	// first_ptr and first_ptr^. Now call append(&items, 300, 400, 500) to force
	// reallocation past capacity 2. Print &items[0] alongside first_ptr to see
	// the buffer moved (do not dereference first_ptr^ after the append!).


	// Call val := pop(&items) and safe_val, ok := pop_safe(&items), then test
	// ordered_remove(&items, 1) and unordered_remove(&items, 0), printing items
	// after each operation. Also test pop_safe on an empty [dynamic]int to see
	// ok == false without panicking.


	// Safe backward loop with unordered_remove: create bag := make([dynamic]int)
	// with defer delete(bag), call append(&bag, 5, 0, 0, 8, 0, 3), and remove
	// every 0 using for i := len(bag) - 1; i >= 0; i -= 1 { ... }. Notice that
	// any item swapped from the end came from an index > i that was already checked!
}

passing_dynamic_arrays_to_procs :: proc() {

	/*
	Procedures that only read or mutate existing elements should accept a slice
	[]T (so callers can pass fixed arrays, slices, or arr[:]). Reserve
	^[dynamic]T parameters strictly for procedures that append, remove, or
	resize the caller's array header. When a procedure allocates and returns a
	new [dynamic]T, the caller owns it and must defer delete(result).
	*/

	// Starter anchor: a dynamic log ready to be extended by a helper proc.
	build_log := make([dynamic]int)
	defer delete(build_log)
	append(&build_log, 99)
	fmt.printfln("Initial build_log: %v", build_log)

	// Define append_countdown :: proc(list: ^[dynamic]int, start: int) that loops
	// from start down to 1 and appends each number via append(list, i) (notice
	// list is already a ^[dynamic]int pointer, so no extra & is needed).


	// Define a read-only helper print_summary :: proc(vals: []int) that prints
	// len(vals) and the elements. Call append_countdown(&build_log, 4) and then
	// pass build_log[:] to print_summary.


	// Define filter_positive :: proc(vals: []int) -> [dynamic]int that builds a
	// fresh [dynamic]int holding only elements > 0. Call it on a slice with
	// negatives, defer delete the returned array, and print the filtered result.
}

main :: proc() {

	fmt.println("=== 1. Dynamic array headers and growth ===")
	header_and_growth()

	fmt.println("\n=== 2. Pointer invalidation and removals ===")
	pointer_invalidation_and_removals()

	fmt.println("\n=== 3. Passing dynamic arrays to procedures ===")
	passing_dynamic_arrays_to_procs()
}
