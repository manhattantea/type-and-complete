// odin run 490_pool_and_handle_allocations.odin -file

package main

import "core:fmt"
import "core:mem"

/*
Long-lived entities, particles, and network sessions create two classic memory
problems: variable-sized allocation growth and stale-pointer use-after-free bugs.
In Odin, systems programmers address them with two complementary tools:

- mem.Dynamic_Pool grows in fixed-size backing blocks (slabs) and resets or
  destroys all pooled allocations in O(1) without tracking individual frees.
- Generational handle pools pack an array index alongside a generation counter
  so any handle pointing to a recycled slot is caught immediately instead of
  silently corrupting the newly spawned occupant.
*/

Entity_Handle :: struct {
	idx: u32,
	gen: u32,
}

Entity_Slot :: struct {
	gen:    u32,
	active: bool,
	name:   string,
}

// Define slot_alloc :: proc(slots: []Entity_Slot, name: string) -> (handle: Entity_Handle, ok: bool)
// Find the first slot where !slot.active. If slot.gen == 0, set slot.gen = 1.
// Set slot.active = true and slot.name = name, and return
// Entity_Handle{idx = u32(i), gen = slot.gen}, true. If all slots are active,
// return {}, false.

// Define slot_free :: proc(slots: []Entity_Slot, h: Entity_Handle) -> bool
// Validate int(h.idx) < len(slots), slots[h.idx].active, and
// slots[h.idx].gen == h.gen. When valid, set slots[h.idx].active = false,
// increment slots[h.idx].gen += 1, and return true (otherwise return false).

// Define slot_get :: proc(slots: []Entity_Slot, h: Entity_Handle) -> (slot: ^Entity_Slot, ok: bool)
// Return &slots[h.idx], true only when int(h.idx) < len(slots),
// slots[h.idx].active, and slots[h.idx].gen == h.gen (otherwise nil, false).

dynamic_pool_slab_allocations :: proc() {

	/*
	When we call mem.dynamic_arena_init(&pool), the arena prepares a list of
	fixed-size backing slabs allocated lazily from context.allocator. Each
	new or make through mem.dynamic_arena_allocator(&pool) bumps inside the
	current slab; when a slab fills up, the arena grabs another slab instead of
	returning Out_Of_Memory or invalidating pointers to earlier nodes.

	Calling mem.dynamic_arena_free_all(&pool) resets the arena in bulk so existing
	slabs can be reused right away, and defer mem.dynamic_arena_destroy(&pool)
	frees every slab back to the backing allocator on exit. (For an out-of-the-box
	generational pool container, Odin also ships core:container/handle_map.)
	*/

	pool: mem.Dynamic_Arena
	mem.dynamic_arena_init(&pool)
	defer mem.dynamic_arena_destroy(&pool)

	pool_alloc := mem.dynamic_arena_allocator(&pool)
	starter_val := new_clone(u32(42), pool_alloc)
	fmt.printfln("Dynamic_Arena starter value: %d", starter_val^)

	// Define a local struct Pool_Node :: struct { id: int, next: ^Pool_Node }
	// and allocate a 5-node linked list out of pool_alloc using new(Pool_Node, pool_alloc)
	// without calling free on any individual node. Walk the list from head to nil
	// printing each node id.


	// Allocate a []f64 slice of 128 elements from pool_alloc, fill each entry
	// with f64(i) * 0.5, print the sum, and then wipe all nodes and slices at
	// once with mem.dynamic_arena_free_all(&pool).


	// Confirm the pool is immediately reusable after dynamic_arena_free_all:
	// allocate a fresh ^Pool_Node from pool_alloc, set id = 999, and print it.
}

generational_handles_and_stale_checks :: proc() {

	/*
	Suppose a projectile targets an enemy stored at slots[0]. If you stored a raw
	pointer ^Entity_Slot, then when that Goblin dies and slot 0 is reused for a
	Dragon, the raw pointer silently points at the Dragon!

	Generational handles prevent that aliasing bug:
	    - Goblin spawns in slot 0 (gen = 1): goblin_h = {idx = 0, gen = 1}.
	    - Goblin is freed: slots[0].active = false and slots[0].gen becomes 2.
	    - Dragon spawns in slot 0: dragon_h = {idx = 0, gen = 2}.
	    - Stale lookup with goblin_h checks slots[0].gen == 1 (false, it is 2!)
	      and returns nil, false cleanly instead of touching Dragon.
	*/

	slots: [8]Entity_Slot
	slots[0] = Entity_Slot{gen = 1, active = true, name = "StarterUnit"}
	first_h := Entity_Handle{idx = 0, gen = 1}
	raw_bytes := mem.slice_to_bytes(slots[:])
	fmt.printfln("Slot[0]=%q (handle idx=%d, gen=%d, pool_bytes=%d)", slots[first_h.idx].name, first_h.idx, first_h.gen, len(raw_bytes))

	// Reset slots = {}, call slot_alloc(slots[:], "Goblin") to obtain goblin_h,
	// look it up with slot_get(slots[:], goblin_h), and print Goblin's name and
	// generation.


	// Free the Goblin with slot_free(slots[:], goblin_h), then allocate "Dragon"
	// with slot_alloc(slots[:], "Dragon") into dragon_h. Print both handles to
	// confirm slot 0 was reused with dragon_h.gen > goblin_h.gen.


	// Verify stale handle rejection: call slot_get(slots[:], goblin_h) and
	// confirm ok == false, call slot_free(slots[:], goblin_h) again and confirm
	// it returns false, then look up dragon_h and print "Dragon".


	// Exhaust the remaining 7 slots in a loop using slot_alloc, then attempt a
	// 9th allocation and verify slot_alloc returns ok == false cleanly without
	// panicking out of bounds.
}

main :: proc() {

	fmt.println("=== 1. mem.Dynamic_Pool slab allocations ===")
	dynamic_pool_slab_allocations()

	fmt.println("\n=== 2. Generational handles and stale checks ===")
	generational_handles_and_stale_checks()
}
