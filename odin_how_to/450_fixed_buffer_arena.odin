// odin run 450_fixed_buffer_arena.odin -file

package main

import "core:fmt"
import "core:mem"

/*
General-purpose heap allocators like malloc or Odin's default allocator track
every individual allocation on free lists so they can free any block in any
order. That flexibility costs bookkeeping headers, pointer chasing, and
fragmentation.

When a group of allocations shares the same lifetime (one network packet, one
frame's scratch math, one parser pass), a fixed-buffer mem.Arena eliminates all
of that overhead. You hand it a plain []byte slice (on the stack, in global
memory, or from a single heap buffer), and every allocation simply bumps an
integer offset forward with alignment padding. When the work is done,
free_all(alloc) resets arena.offset back to 0 in O(1) time.
*/

bump_allocation_and_alignment :: proc() {

	/*
	When we call mem.arena_init(&arena, backing_buf[:]), it binds the arena to
	that byte slice and sets arena.offset = 0. Calling mem.arena_allocator(&arena)
	then hands back a standard runtime.Allocator that any Odin procedure (new,
	new_clone, make, strings.clone) can use without knowing it is talking to a
	fixed stack buffer.

	Even a bump allocator respects CPU alignment rules. Suppose backing_buf has
	1024 bytes and arena.offset is 0:
	    - Allocate 1 byte (new(u8, alloc)): offset moves from 0 to 1.
	    - Allocate a u64 (8-byte alignment): the arena rounds offset up from 1
	      to 8 (7 bytes of alignment padding), then bumps 8 bytes to offset 16.
	    - arena.peak_used records the highest offset reached so far so you can
	      size fixed buffers from real runs rather than guessing.
	*/

	backing_buf: [1024]byte
	arena: mem.Arena
	mem.arena_init(&arena, backing_buf[:])
	alloc := mem.arena_allocator(&arena)

	header_magic := new_clone(u64(0xCAFE_BABE), alloc)
	fmt.printfln("Arena magic: 0x%X | offset: %d | peak: %d", header_magic^, arena.offset, arena.peak_used)

	// Allocate a []int slice of length 10 named nums using make([]int, 10, alloc),
	// set nums[0] = 42 and nums[9] = 99, and print nums, arena.offset, and
	// arena.peak_used.


	// Observe alignment padding directly: allocate a single byte with
	// pad_byte := new(u8, alloc), print arena.offset, then allocate a vector
	// vec_ptr := new([3]f32, alloc) and assign vec_ptr^ = {1.0, 2.0, 3.0}.
	// Print vec_ptr^ and arena.offset afterward to see the offset jump past
	// the alignment gap before storing the 12-byte [3]f32.
}

checkpoints_and_temp_memory :: proc() {

	/*
	Resetting an entire arena with free_all wipes everything inside it. Often
	you want to keep earlier allocations intact while borrowing the unused tail
	of the same arena for short-lived scratch work.

	When we call mem.begin_arena_temp_memory(&arena), it snapshots the current
	arena.offset into a small mem.Arena_Temp_Memory struct and increments
	arena.temp_count. Allocations made afterward bump arena.offset forward as
	usual, and calling mem.end_arena_temp_memory(temp) rewinds arena.offset back
	to the saved snapshot in O(1) time.

	    Suppose arena.offset is 16 after storing a persistent header:
	        cp := mem.begin_arena_temp_memory(&arena)   // saves prev_offset = 16
	        tmp := make([]u8, 200, alloc)               // offset becomes 216
	        mem.end_arena_temp_memory(cp)               // offset snaps back to 16

	The persistent header below offset 16 is untouched, and arena.peak_used
	still remembers 216 so you know the combined high-water mark.
	*/

	temp_buf: [512]byte
	temp_arena: mem.Arena
	mem.arena_init(&temp_arena, temp_buf[:])
	temp_alloc := mem.arena_allocator(&temp_arena)

	keep := new_clone(i32(77), temp_alloc)
	fmt.printfln("Persistent value: %d | baseline offset: %d", keep^, temp_arena.offset)

	// Capture a checkpoint with cp := mem.begin_arena_temp_memory(&temp_arena).
	// Allocate scratch := make([]u8, 256, temp_alloc), set scratch[0] = 0xAA,
	// and print temp_arena.offset and temp_arena.peak_used.


	// Rewind to the checkpoint using mem.end_arena_temp_memory(cp).
	// Print temp_arena.offset (expected: back to baseline), temp_arena.peak_used,
	// and keep^ (expected: still 77).


	// Test nested checkpoints: open outer_cp := mem.begin_arena_temp_memory(&temp_arena),
	// allocate a [4]int with new([4]int, temp_alloc), then open
	// inner_cp := mem.begin_arena_temp_memory(&temp_arena), allocate 64 bytes,
	// and print temp_arena.temp_count (expected: 2). End inner_cp first, print
	// temp_arena.offset, then end outer_cp and verify temp_arena.temp_count is 0.
}

out_of_memory_and_reset :: proc() {

	/*
	Because a fixed-buffer mem.Arena never calls the OS for more RAM, any
	allocation whose aligned size exceeds len(arena.data) - arena.offset fails
	deterministically with mem.Allocator_Error.Out_Of_Memory (which is an alias
	for runtime.Allocator_Error.Out_Of_Memory). Individual free or delete calls
	on a mem.Arena are no-ops because the arena has no per-block metadata;
	reclaiming space happens either via Arena_Temp_Memory checkpoints or via
	free_all(alloc), which sets arena.offset = 0 while preserving peak_used.
	*/

	small_buf: [128]byte
	small_arena: mem.Arena
	mem.arena_init(&small_arena, small_buf[:])
	small_alloc := mem.arena_allocator(&small_arena)

	tag := new_clone(u32(42), small_alloc)
	fmt.printfln("Small arena tag: %d | offset: %d / %d", tag^, small_arena.offset, len(small_buf))

	// Attempt an oversized allocation: huge, err := make([]byte, 256, small_alloc)
	// Verify err == .Out_Of_Memory and print both err and len(huge).


	// Reset the arena in O(1) time with free_all(small_alloc) and print
	// small_arena.offset (expected: 0) alongside small_arena.peak_used.


	// Prove the backing buffer is immediately reusable after free_all: allocate
	// reused := make([]u8, 64, small_alloc), write reused[0] = 0xFF, and print
	// small_arena.offset and small_arena.peak_used.
}

main :: proc() {

	fmt.println("=== 1. Bump allocation and alignment ===")
	bump_allocation_and_alignment()

	fmt.println("\n=== 2. Checkpoints and Arena_Temp_Memory ===")
	checkpoints_and_temp_memory()

	fmt.println("\n=== 3. Out_Of_Memory and O(1) reset ===")
	out_of_memory_and_reset()
}
