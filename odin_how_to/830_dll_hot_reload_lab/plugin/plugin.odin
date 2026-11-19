// odin build 830_dll_hot_reload_lab/plugin -build-mode:dll -out:plugin.dll

package plugin

import "base:runtime"
import "core:fmt"

/*
This package compiles into a standalone dynamic library loaded at runtime by
host.odin (on Linux or macOS pass -out:libplugin.so or -out:libplugin.dylib).

Two rules govern every DLL export:
First, Game_Memory must match the exact field order and field types declared in
shared_api.odin, because only a raw pointer crosses the C ABI boundary.
Second, '@(export)' exposes an unmangled C symbol and 'proc "c"' receives no
Odin context pointer, so any exported entry point that calls core:fmt or an
allocator must start by setting 'context = runtime.default_context()'.
*/

Game_Memory :: struct {
	tick:        int,
	player_x:    f32,
	initialized: bool,
}

@(export)
game_update :: proc "c" (mem: ^Game_Memory) {

	context = runtime.default_context()
	if mem == nil {
		fmt.printfln("[plugin] nil Game_Memory pointer")
		return
	}

	// Initialize persistent Game_Memory on the first tick:
	// When !mem.initialized, set mem.player_x = 10.0, mark mem.initialized = true,
	// and print a one-time initialization message with fmt.printfln.


	// Advance the simulation for this tick:
	// Increment mem.tick += 1 and add 2.5 to mem.player_x. Once hot-reloading
	// runs, change 2.5 to 10.0, rebuild the DLL, and watch the host pick up the
	// new velocity without resetting mem.tick.


	// Log mem.tick and mem.player_x (formatted with %.2f) using fmt.printfln.
}

// Add a second exported procedure:
// @(export) game_reset :: proc "c" (mem: ^Game_Memory)
// Restore context = runtime.default_context(), guard mem == nil, reset
// mem.tick = 0 and mem.player_x = 0.0, and wire it into shared_api.odin.
