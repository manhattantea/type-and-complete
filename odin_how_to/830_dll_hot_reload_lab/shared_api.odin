// Shared ABI memory and plugin table contract for 830_dll_hot_reload_lab (package main).

package main

import "core:dynlib"

/*
Live DLL hot-reloading lets you edit gameplay or simulation code, recompile the
plugin dynamic library, and watch the running host pick up the new behavior
without restarting or losing state.

The core architectural boundary separates persistent state from mutable logic:
'Game_Memory' is owned exclusively by the host process on its own stack or
heap, so every entity, position, and tick counter survives across reloads.
'Plugin_API' holds the dynamic library handle and exported C ABI procedure
pointers loaded at runtime via dynlib.initialize_symbols.

Because only raw pointers cross the dynamic library boundary, every exported
procedure pointer uses 'proc "c"' and both sides must keep identical field
order and field types inside Game_Memory.
*/

Game_Memory :: struct {
	tick:        int,
	player_x:    f32,
	initialized: bool,
}

Plugin_API :: struct {
	__handle:    dynlib.Library,
	game_update: proc "c" (mem: ^Game_Memory),
}

// Once the basic hot-reload loop works, extend both Game_Memory (for example
// adding player_y: f32) and Plugin_API (for example adding
// game_reset: proc "c" (mem: ^Game_Memory)) here and in plugin/plugin.odin,
// keeping the exact same field order on both sides.
