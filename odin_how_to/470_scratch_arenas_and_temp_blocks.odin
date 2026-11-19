// odin run 470_scratch_arenas_and_temp_blocks.odin -file

package main

import "core:fmt"
import "core:mem"
import "core:mem/virtual"
import "base:runtime"

/*
Procedures frequently need temporary scratch memory (a split buffer, a sorted
copy, an intermediate hash map) just to construct one compact return value.
If a procedure calls arena_free_all on a shared arena, it destroys earlier
persistent allocations. Instead, Odin arenas support lightweight checkpoints
that rewind only the tail created inside a temporary scope.

Just as importantly, passing a scratch arena into a procedure that also takes an
output allocator hides a subtle aliasing bug if both point to the same arena.
Understanding checkpoints and the two-arena scratch rule prevents silent
use-after-free corruption.
*/

manual_and_scoped_checkpoints :: proc() {

	/*
	When we call virtual.arena_temp_begin(&arena), it saves the arena's current
	block and offset inside a virtual.Arena_Temp token. Allocations made after
	that line extend the arena as normal, and calling virtual.arena_temp_end(temp)
	rewinds the arena back to that exact point while preserving every allocation
	created before arena_temp_begin.

	For block-scoped cleanup without manual end calls, virtual.arena_scratch_block(&arena)
	uses @(deferred_out=arena_temp_end) under the hood, so Odin automatically
	rewinds the arena when execution leaves the enclosing { ... } block (even on
	an early break or return).

	Fixed-buffer mem.Arena has the matching pair mem.begin_arena_temp_memory and
	mem.end_arena_temp_memory operating on mem.Arena_Temp_Memory.
	*/

	arena: virtual.Arena
	init_err := virtual.arena_init_growing(&arena)
	if init_err != nil {
		fmt.printfln("Failed to initialize virtual arena: %v", init_err)
		return
	}
	defer virtual.arena_destroy(&arena)

	alloc := virtual.arena_allocator(&arena)
	perm_ids := make([]int, 4, alloc)
	perm_ids[0], perm_ids[1], perm_ids[2], perm_ids[3] = 100, 200, 300, 400
	fmt.printfln("Persistent IDs: %v (baseline used: %d bytes)", perm_ids, arena.total_used)

	// Save a manual checkpoint with checkpoint := virtual.arena_temp_begin(&arena).
	// Allocate a 64 KB temporary buffer scratch := make([]byte, 64 * 1024, alloc),
	// set scratch[0] = 0xAA, and print arena.total_used to observe the spike.


	// Rewind to the checkpoint with virtual.arena_temp_end(checkpoint), then
	// print arena.total_used and perm_ids to confirm arena.total_used returned
	// to baseline while perm_ids is still {100, 200, 300, 400}.


	// Open an inner { ... } block, call virtual.arena_scratch_block(&arena) on
	// the first line, allocate a []f32 of 1,000 floats from alloc, print
	// arena.total_used inside the block, and print arena.total_used again after
	// the closing brace to confirm automatic rollback.


	// Try the fixed-buffer equivalent on a small stack array:
	fixed_buf: [128]byte
	fixed_arena: mem.Arena
	mem.arena_init(&fixed_arena, fixed_buf[:])
	fixed_alloc := mem.arena_allocator(&fixed_arena)
	fixed_cp := mem.begin_arena_temp_memory(&fixed_arena)
	tmp_bytes := make([]u8, 64, fixed_alloc)
	tmp_bytes[0] = 7
	fmt.printfln("Fixed arena mid-temp offset: %d", fixed_arena.offset)
	mem.end_arena_temp_memory(fixed_cp)
	fmt.printfln("Fixed arena after end_arena_temp_memory: %d", fixed_arena.offset)
}

two_arena_scratch_aliasing_hazard :: proc() {

	/*
	Now consider the scratch aliasing hazard. Suppose a helper procedure has
	this shape:

	    collect_even_squares(limit, out_alloc, scratch_arena)

	Inside collect_even_squares, the helper calls virtual.arena_scratch_block(scratch_arena),
	builds a temporary [dynamic]int in scratch_arena, and allocates the final
	returned []int from out_alloc.

	Watch what goes wrong if a caller accidentally passes the SAME arena for
	both out_alloc and scratch_arena:
	    - arena_scratch_block(scratch_arena) saves offset X.
	    - Inside the block, the returned []int is allocated from out_alloc —
	      which is the exact same arena, so it sits above offset X!
	    - When the block exits, arena_temp_end rewinds the arena back to X,
	      putting the returned []int slice into rewound (freed) memory.
	    - The very next allocation on that arena silently overwrites the
	      returned slice's elements!

	To eliminate aliasing, keep distinct persistent and scratch arenas (or keep
	two thread-local scratch arenas and pick whichever one has a different .data
	pointer from out_alloc.data).
	*/

	persistent_arena: virtual.Arena
	scratch_arena: virtual.Arena

	p_err := virtual.arena_init_growing(&persistent_arena)
	if p_err != nil {
		fmt.printfln("Persistent arena init failed: %v", p_err)
		return
	}
	defer virtual.arena_destroy(&persistent_arena)

	s_err := virtual.arena_init_growing(&scratch_arena)
	if s_err != nil {
		fmt.printfln("Scratch arena init failed: %v", s_err)
		return
	}
	defer virtual.arena_destroy(&scratch_arena)

	persistent_alloc: runtime.Allocator = virtual.arena_allocator(&persistent_arena)
	scratch_alloc: runtime.Allocator = virtual.arena_allocator(&scratch_arena)
	fmt.printfln("Distinct arenas (no aliasing): %v", persistent_alloc.data != scratch_alloc.data)

	// Write a helper procedure at file scope (or locally inside this proc):
	// collect_even_squares :: proc(limit: int, out_alloc: runtime.Allocator, scratch_arena: ^virtual.Arena) -> []int
	// Inside it, call virtual.arena_scratch_block(scratch_arena), build a
	// [dynamic]int of even squares using virtual.arena_allocator(scratch_arena),
	// allocate out := make([]int, len(tmp), out_alloc), copy tmp into out, and
	// return out.


	// First reproduce the aliasing bug intentionally on a third throwaway arena
	// named aliased_arena: pass virtual.arena_allocator(&aliased_arena) as
	// out_alloc AND &aliased_arena as scratch_arena into collect_even_squares.
	// Immediately afterward, allocate clobber := make([]int, 16, virtual.arena_allocator(&aliased_arena))
	// and fill clobber with 999, then print the first slice to see its values
	// corrupted!


	// Now call collect_even_squares(10, persistent_alloc, &scratch_arena) using
	// the two separate arenas above. Allocate a second slice in scratch_alloc,
	// print scratch_arena.total_used (rewound back to 0 on exit) and print the
	// persistent slice to verify its values remain intact.
}

main :: proc() {

	fmt.println("=== 1. Manual and scoped checkpoints ===")
	manual_and_scoped_checkpoints()

	fmt.println("\n=== 2. Two-arena scratch aliasing hazard ===")
	two_arena_scratch_aliasing_hazard()
}
