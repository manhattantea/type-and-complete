package main

import "core:fmt"
import "core:mem/virtual"

/*
level.odin defines the persistent domain contract (Room and Level) stored
inside level_arena, along with display and O(1) arena reset helpers. Because
every room name string and connections slice is allocated out of level_arena,
reset_level never needs a loop to free individual rooms or strings.
*/

Room :: struct {
	name:        string,
	connections: []int,
}

Level :: struct {
	rooms: []Room,
}

print_level :: proc(lvl: Level) {

	fmt.printfln("=== Level Map (%d rooms) ===", len(lvl.rooms))

	// Walk lvl.rooms with for room, idx in lvl.rooms and print each room's
	// index, room.name, and room.connections slice using fmt.printfln.
}

reset_level :: proc(level_arena: ^virtual.Arena) {

	fmt.printfln("Resetting level_arena (currently used: %d bytes)", level_arena.total_used)

	// Wipe all persistent rooms, connection slices, and cloned strings in O(1)
	// time by calling virtual.arena_free_all(level_arena).
}
