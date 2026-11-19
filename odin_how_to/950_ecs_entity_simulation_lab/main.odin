// odin run 950_ecs_entity_simulation_lab

package main

import "core:fmt"

/*
This Lab ties together generational handles, bit_set component masks, #soa
field arrays, #simd[4]f32 batch integration, and per-frame temporary memory
resets across a three-file Odin package:
- world.odin defines the World layout and generational handle lifecycle.
- systems.odin defines the SIMD movement and health cleanup systems.
- main.odin drives the simulation loop and verifies handle invalidation.

Inside a multi-tick simulation loop, 'defer free_all(context.temp_allocator)'
runs automatically at the end of every loop iteration (not when main returns),
making it ideal for transient per-tick formatting via fmt.tprintf without
accumulating heap garbage across frames.
*/

main :: proc() {

	fmt.println("=== 1. ECS World Baseline ===")
	w: World
	handles: [16]Entity_Handle
	fmt.printfln("ECS World ready: capacity=%d active=%d slot0_alive=%v", MAX_ENTITIES, w.active_count, is_alive(&w, handles[0]))

	// Spawn 16 entities and initialize their SOA components.
	// Loop i over 0..<16, call h, ok := spawn_entity(&w, {.Position, .Velocity, .Health}),
	// assert(ok, "failed to spawn entity"), and save handles[i] = h.
	// Set w.positions[h.idx] = Vec2{f32(i) * 2.0, 0} and
	// w.velocities[h.idx] = Vec2{10.0, f32(i) + 1.0}.
	// Drop w.health[handles[0].idx] = 10 so damage_system despawns entity #0 mid-run.


	fmt.println("\n=== 2. Ten-Tick Simulation Loop ===")

	// Step the simulation for 10 ticks with: for tick in 0..<10
	// Place defer free_all(context.temp_allocator) at the top of the loop body so
	// temporary strings from each tick are reclaimed before the next tick starts.
	// Call movement_system(&w, 1.0 / 60.0) every tick.
	// On tick == 5, subtract 50 from w.health[handles[0].idx] and call damage_system(&w).
	// Format a summary line using fmt.tprintf("tick=%d active=%d e1_pos=(%.2f, %.2f)", ...)
	// and print it with fmt.println.


	fmt.println("\n=== 3. Generational Handle Invalidation ===")

	// Confirm that is_alive(&w, handles[0]) is now false after tick 5.
	// Spawn a replacement entity: replacement, ok := spawn_entity(&w, {.Position, .Health})
	// Because slot 0 was freed, replacement.idx is still 0, yet replacement.gen
	// is now 1. Verify is_alive(&w, handles[0]) remains false while
	// is_alive(&w, replacement) is true, then print w.active_count and the
	// surviving handles[1]'s position.
}
