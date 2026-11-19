// odin run 830_dll_hot_reload_lab

package main

import "core:dynlib"
import "core:fmt"
import "core:os"
import "core:time"

/*
On Windows, loading plugin.dll directly locks the file on disk so running
'odin build ... -out:plugin.dll' fails with "Access is denied" while the host
runs. To hot-reload safely, the host copies plugin.dll to a separate runtime
filename (plugin_live.dll), loads plugin_live.dll instead, and polls
os.last_write_time_by_name on plugin.dll so the compiler can overwrite it
freely.

Suppose plugin.dll has not been built yet when you launch the host: instead of
crashing or sitting idle, the host falls back to a tiny standalone simulation
loop so you can verify state progression immediately.
*/

when ODIN_OS == .Windows {
	SRC_LIB  :: "plugin.dll"
	LIVE_LIB :: "plugin_live.dll"
} else when ODIN_OS == .Darwin {
	SRC_LIB  :: "libplugin.dylib"
	LIVE_LIB :: "libplugin_live.dylib"
} else {
	SRC_LIB  :: "libplugin.so"
	LIVE_LIB :: "libplugin_live.so"
}

simulate_standalone_step :: proc(mem: ^Game_Memory) {

	if !mem.initialized {
		mem.player_x = 10.0
		mem.initialized = true
	}
	mem.tick += 1
	mem.player_x += 1.0
	fmt.printfln("[host-fallback] tick=%d player_x=%.2f", mem.tick, mem.player_x)
}

// Implement a dedicated reload helper right above main with signature:
// load_plugin_api :: proc(api: ^Plugin_API, src_lib, live_lib: string) -> bool
// Inside load_plugin_api:
// First, if api.__handle != nil, call dynlib.unload_library(api.__handle) and
// reset api^ = {} so Windows releases the lock on live_lib before overwriting.
// Next, copy src_lib to live_lib with os.read_entire_file(src_lib) (returning
// false on read failure and scheduling defer delete(dll_bytes)) followed by
// os.write_entire_file(live_lib, dll_bytes).
// Finally, call count, sym_ok := dynlib.initialize_symbols(api, live_lib),
// print dynlib.last_error() to stderr with fmt.eprintfln if !sym_ok or
// count == 0, and return true when bound.

main :: proc() {

	game_memory: Game_Memory
	api: Plugin_API
	src_lib := SRC_LIB
	live_lib := LIVE_LIB

	fmt.printfln("[host] Hot-reload host ready (src=%s, live=%s, present=%v)", src_lib, live_lib, os.exists(src_lib))

	if os.exists(src_lib) {
		count, ok := dynlib.initialize_symbols(&api, src_lib)
		if !ok || count == 0 {
			fmt.eprintfln("[host] Failed to load %s: %s", src_lib, dynlib.last_error())
			return
		}
		defer dynlib.unload_library(api.__handle)
		if api.game_update != nil {
			api.game_update(&game_memory)
		}
	} else {
		fmt.printfln("[host] %s not built yet; running standalone fallback (build via: odin build 830_dll_hot_reload_lab/plugin -build-mode:dll -out:%s)", src_lib, src_lib)
		for _ in 0..<3 {
			simulate_standalone_step(&game_memory)
			time.sleep(25 * time.Millisecond)
		}
	}

	// Replace the one-shot os.exists load above with your hot-reload loop:
	// Call load_plugin_api(&api, src_lib, live_lib) when os.exists(src_lib) is
	// true, record last_mod, _ := os.last_write_time_by_name(src_lib), and
	// schedule defer if api.__handle != nil { dynlib.unload_library(api.__handle) }.


	// Write a bounded 20-tick polling loop: for step in 0..<20
	// Query mod_time, mod_err := os.last_write_time_by_name(src_lib); when
	// mod_err == os.ERROR_NONE && mod_time > last_mod, sleep 50 * time.Millisecond so the
	// linker finishes flushing, call load_plugin_api(&api, src_lib, live_lib),
	// update last_mod = mod_time, invoke api.game_update(&game_memory) when
	// non-nil, and sleep 250 * time.Millisecond between ticks.
}
