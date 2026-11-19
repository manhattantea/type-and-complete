// odin run 410_new_make_free_and_delete.odin -file

package main

import "core:fmt"
import "core:mem"
import "base:runtime"

/*
Odin does not hide heap allocations behind destructors or a garbage collector,
and it keeps single-item allocation separate from collection allocation with an
unambiguous pairing rule:

  new(T) or new_clone(val) -> returns ^T             -> release with free(ptr)
  make([]T, len)           -> returns slice []T      -> release with delete(s)
  make([dynamic]T, l, cap) -> returns [dynamic]T     -> release with delete(d)
  make(map[K]V, cap)       -> returns map[K]V        -> release with delete(m)

Every allocation procedure accepts an optional trailing allocator parameter
and an optional second return value of type runtime.Allocator_Error. Checking
that error explicitly prevents null-pointer dereferences when an arena or OS
heap refuses an oversized request.

This file is split into four sections called from main at the bottom so you can
read top to bottom and run the program at any point.
*/

Transform :: struct {
	pos:   [3]f32,
	scale: f32,
}

Inventory :: struct {
	owner:   string,
	weights: []f32,
	items:   [dynamic]int,
}

single_item_new_and_free :: proc() {

	/*
	Calling new(T) allocates enough bytes for one T from context.allocator,
	zero-initializes every field, and returns a typed pointer ^T. Calling
	new_clone(val) allocates one T initialized to a copy of val. Both must be
	paired with free(ptr), never delete(ptr).

	    Suppose p := new(Transform):
	        defer free(p)       // scheduled immediately so early returns never leak
	        p.scale = 1.0       // auto-dereferences p^.scale
	*/

	// Starter single-item allocation showing explicit error inspection:

	anchor_t, anchor_err := new(Transform)
	defer free(anchor_t)
	fmt.printfln("Zeroed Transform from new(): %v (err=%v)", anchor_t^, anchor_err)

	// Allocate t1 := new(Transform), pair it immediately with defer free(t1),
	// set t1.pos = {10, 20, 0} and t1.scale = 1.5, and print t1^.


	// Allocate t2 := new_clone(Transform{pos = {1.0, 2.0, 3.0}, scale = 2.0}),
	// pair it immediately with defer free(t2), and print t2.pos and t2.scale.


	// Allocate checked_t, err := new(Transform), verify if err == .None before
	// setting checked_t.scale = 4.0 and calling defer free(checked_t).
	// Also try uncommenting delete(anchor_t) below to see Odin reject mixing
	// delete with a single ^Transform pointer:
	// delete(anchor_t)
}

collection_make_and_delete :: proc() {

	/*
	Collections are fat values: a slice []T is a 16-byte {data, len} header,
	and a [dynamic]T is a {data, len, cap, allocator} header. Calling make
	allocates the backing array on the heap and fills in that header; calling
	delete frees the backing array.

	Watch the difference between length and capacity on dynamic arrays.
	Suppose you write make([dynamic]int, 4): len is 4 and slots 0..3 already
	exist filled with zeros, so append(&arr, 99) puts 99 at index 4! Writing
	make([dynamic]int, 0, 16) sets len to 0 while reserving space for 16
	integers up front, so the first 16 appends need zero reallocations.
	*/

	// Starter slice allocation showing the two-value error form:

	sample_buf, buf_err := make([]byte, 8)
	defer delete(sample_buf)
	fmt.printfln("Allocated %d-byte slice (err=%v)", len(sample_buf), buf_err)

	// Allocate weights := make([]f32, 8) paired with defer delete(weights),
	// assign weights[0] = 3.14 and weights[7] = 2.718, and print weights.


	// Allocate scores := make([dynamic]int, 0, 16) paired with defer delete(scores),
	// append(&scores, 10, 20, 30), and print len(scores), cap(scores), and scores.
	// Compare with zeroed := make([dynamic]int, 4) (defer delete(zeroed)) and
	// print len(zeroed) after appending one item.


	// Allocate ages := make(map[string]int, 16) paired with defer delete(ages),
	// insert "Ada" = 36 and "Grace" = 85, and print len(ages) and ages["Ada"].


	// Try uncommenting free(sample_buf) below to confirm Odin catches mixing
	// free with a slice header at compile time:
	// free(sample_buf)
}

explicit_allocator_and_error_handling :: proc() {

	/*
	Every new and make call takes an optional final allocator argument. Notice a
	subtle asymmetry: [dynamic]T and map[K]V store their allocator inside their
	own header, so delete(dyn) remembers which allocator to call. Plain ^T
	pointers and []T slices store NO allocator metadata—if you pass a custom
	allocator to new(T, my_alloc) or make([]T, n, my_alloc), any manual
	free(ptr, my_alloc) or delete(slice, my_alloc) must pass the same one!
	*/

	// Starter explicit-allocator allocation inside a small stack arena:

	scratch_mem: [512]byte
	arena: mem.Arena
	mem.arena_init(&arena, scratch_mem[:])
	arena_alloc := mem.arena_allocator(&arena)

	pinned, pin_err := new(Transform, arena_alloc)
	pinned.scale = 3.0
	fmt.printfln("Arena Transform scale=%.1f (err=%v, offset=%d)", pinned.scale, pin_err, arena.offset)

	// Allocate arena_nums, num_err := make([]int, 10, arena_alloc), assert or
	// check num_err == .None, fill arena_nums[i] = i * 2, and print arena_nums.
	// Next, try allocating huge, huge_err := make([]byte, 4096, arena_alloc)
	// and print huge_err to observe runtime.Allocator_Error.Out_Of_Memory cleanly
	// instead of crashing.


	// Allocate tmp_t := new(Transform, context.temp_allocator), set tmp_t.pos,
	// print tmp_t^, and release it via free_all(context.temp_allocator) rather
	// than calling free(tmp_t).
}

deep_free_struct_vs_arena :: proc() {

	/*
	Calling free(inv) on a struct that owns slices or dynamic arrays only frees
	the outer Inventory struct bytes—it leaks inv.weights and inv.items! With
	general-purpose heap allocations, every compound type forces you to write a
	matching deep-free teardown procedure freeing children before the parent.

	With an arena, you keep the exact same Inventory struct but route all of
	its allocations into one arena. When the level or task ends, one call to
	free_all(arena_alloc) drops the parent and every child slice together in
	constant time, with zero teardown code to maintain.
	*/

	// Manual deep-free on a heap-allocated Inventory:

	heap_inv := new(Inventory)
	heap_inv.owner = "Scout"
	heap_inv.weights = make([]f32, 2)
	heap_inv.items = make([dynamic]int, 0, 4)
	append(&heap_inv.items, 101)
	fmt.printfln("Heap inventory (%s): weights=%d, items=%v", heap_inv.owner, len(heap_inv.weights), heap_inv.items)
	delete(heap_inv.items)
	delete(heap_inv.weights)
	free(heap_inv)

	// Extract that manual teardown into destroy_inventory :: proc(inv: ^Inventory)
	// above main that deletes inv.items, deletes inv.weights, and frees inv.
	// Allocate a new ^Inventory with a 3-element weights slice and 2 appended
	// items, print it, and clean it up via defer destroy_inventory(inv).


	// Now build the arena contrast: declare backing: [1024]byte, init a
	// mem.Arena, set context.allocator = mem.arena_allocator(&arena) inside a
	// scoped block, and allocate an arena_inv := new(Inventory) with its own
	// weights slice and items dynamic array. Print arena.offset, then wipe the
	// entire object graph in one line with free_all(context.allocator) inside
	// that scope without writing any per-field delete or free calls.
}

main :: proc() {

	fmt.println("=== 1. Single-item allocations: new and free ===")
	single_item_new_and_free()

	fmt.println("\n=== 2. Collection allocations: make and delete ===")
	collection_make_and_delete()

	fmt.println("\n=== 3. Explicit allocators and Allocator_Error ===")
	explicit_allocator_and_error_handling()

	fmt.println("\n=== 4. Deep-free struct teardown vs. arena bulk reset ===")
	deep_free_struct_vs_arena()
}
