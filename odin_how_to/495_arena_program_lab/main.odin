// odin run 495_arena_program_lab

package main

import "core:fmt"
import "core:mem"
import "core:mem/virtual"

/*
In larger programs, memory is easiest to reason about when partitioned by
lifetime rather than tracked object-by-object:

    level_arena     virtual.Arena holding persistent rooms, names, and
                    connection slices for the active level. Wiped between
                    levels in O(1) time via reset_level(&level_arena).
    scratch_arena   virtual.Arena holding temporary split tokens during
                    parse_level_line. Rewound immediately after each load.
    track           mem.Tracking_Allocator wrapping context.allocator so shutdown
                    verifies zero bytes leaked onto the general heap.
*/

main :: proc() {

	track: mem.Tracking_Allocator
	mem.tracking_allocator_init(&track, context.allocator)
	defer mem.tracking_allocator_destroy(&track)
	context.allocator = mem.tracking_allocator(&track)

	// Register a defer leak-check block right here (after tracking_allocator_destroy's
	// defer, so LIFO order runs your leak check BEFORE the tracker is destroyed!).
	// Loop over track.allocation_map and track.bad_free_array to report any leaks
	// or invalid frees at shutdown.

	level_arena: virtual.Arena
	if level_err := virtual.arena_init_growing(&level_arena); level_err != nil {
		fmt.printfln("Failed to initialize level_arena: %v", level_err)
		return
	}
	defer virtual.arena_destroy(&level_arena)

	scratch_arena: virtual.Arena
	if scratch_err := virtual.arena_init_growing(&scratch_arena); scratch_err != nil {
		fmt.printfln("Failed to initialize scratch_arena: %v", scratch_err)
		return
	}
	defer virtual.arena_destroy(&scratch_arena)

	level_alloc := virtual.arena_allocator(&level_arena)
	scratch_alloc := virtual.arena_allocator(&scratch_arena)

	log_loader_contract("Entrance:1;Hall:0", level_alloc, scratch_alloc)
	print_level(Level{})
	reset_level(&level_arena)
	fmt.printfln("Two-arena startup complete (tracked heap leaks: %d)", len(track.allocation_map))

	// After implementing parse_level_line in loader.odin and print_level /
	// reset_level in level.odin, load Level 1 from:
	// "Dungeon Entrance:1,2;Great Hall:0,3;Armory:0;Throne Room:1"
	// Handle the returned (lvl1, err1) explicitly: if err1 != .None, print the
	// error and return. Otherwise print lvl1 with print_level(lvl1), print both
	// level_arena.total_used and scratch_arena.total_used, and rewind scratch_arena
	// with virtual.arena_free_all(&scratch_arena).


	// Reset level_arena in O(1) time via reset_level(&level_arena), then load
	// Level 2 from "Cave Mouth:1;Underground River:0,2;Dragon Lair:1", check err2,
	// print it with print_level(lvl2), and rewind scratch_arena again.


	// Verify malformed-line error propagation without leaking or corrupting state:
	// call parse_level_line on "BrokenRoomWithoutColon" (expect .Missing_Colon)
	// and on "Entrance:99" (expect .Invalid_Connection_Index), print both errors,
	// and rewind scratch_arena after each attempt.
}
