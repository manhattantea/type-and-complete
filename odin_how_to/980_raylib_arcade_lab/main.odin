// odin run 980_raylib_arcade_lab

package main

import "core:fmt"
import "core:mem"
import "core:os"

/*
This Lab brings together vendor:raylib rendering, zero-heap fixed-capacity
entity arrays, per-frame temp_allocator resets, and leak checking via
mem.Tracking_Allocator.

Pass '-- -headless' on the command line (odin run 980_raylib_arcade_lab -- -headless)
to step deterministic simulation ticks without opening a graphical window, so
you can verify gameplay logic and zero memory leaks straight from headless or
CI terminals.

Wrapping context.allocator with mem.Tracking_Allocator at the top of main
records every heap allocation and free across the entire program automatically,
because Odin passes context implicitly down to every procedure call.
*/

main :: proc() {

	fmt.println("=== 1. Allocator Setup and Mode Detection ===")
	track: mem.Tracking_Allocator
	mem.tracking_allocator_init(&track, context.allocator)
	defer mem.tracking_allocator_destroy(&track)
	context.allocator = mem.tracking_allocator(&track)

	headless := false
	for arg in os.args[1:] {
		if arg == "-headless" {
			headless = true
		}
	}

	state: Game_State
	init_game(&state)
	fmt.printfln("Arcade baseline ready: headless=%v player=%v invaders=%d", headless, state.player_pos, len(state.invaders))

	fmt.println("\n=== 2. Headless or Windowed Frame Loop ===")
	if headless {
		fmt.println("Headless mode selected; implement the 10-frame simulation Drill below.")

		// Run 10 deterministic headless ticks at dt := f32(1.0 / 60.0):
		// Loop frame in 0..<10, call update_game(&state, dt, headless = true),
		// and reset scratch memory at the end of every tick with
		// free_all(context.temp_allocator). Print state.score and len(state.invaders)
		// with fmt.printfln after the loop completes.
	} else {
		fmt.println("Windowed mode selected; add import rl \"vendor:raylib\" and implement the 60-FPS loop Drill below.")

		// Add 'import rl "vendor:raylib"' at the top of main.odin when filling in
		// the interactive window loop:
		// Call rl.InitWindow(SCREEN_WIDTH, SCREEN_HEIGHT, "Odin 980 Arcade Lab"),
		// schedule defer rl.CloseWindow(), and call rl.SetTargetFPS(60).
		// Loop while !rl.WindowShouldClose(): call update_game(&state, rl.GetFrameTime()),
		// call draw_game(&state), and call free_all(context.temp_allocator) at the
		// end of each frame.
	}

	fmt.println("\n=== 3. Leak and Bad-Free Verification ===")
	for _, entry in track.allocation_map {
		fmt.eprintfln("Leaked %d bytes at %v", entry.size, entry.location)
	}
	for bf in track.bad_free_array {
		fmt.eprintfln("Bad free %p at %v", bf.memory, bf.location)
	}
	fmt.printfln("Tracking check complete: %d leaked allocation(s), %d bad free(s).", len(track.allocation_map), len(track.bad_free_array))
}
