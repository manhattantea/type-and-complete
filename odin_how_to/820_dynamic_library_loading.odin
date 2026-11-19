// odin run 820_dynamic_library_loading.odin -file

package main

import "core:dynlib"
import "core:fmt"

/*
While 'foreign import' binds shared or static libraries at compile time, many
systems load shared libraries dynamically at runtime: game-engine plugins,
optional GPU extensions, audio drivers, and hot-reloadable modules.

Under the hood, Windows uses LoadLibraryW, GetProcAddress, and FreeLibrary,
while Linux and macOS use dlopen, dlsym, and dlclose. Odin's "core:dynlib"
package wraps both behind one cross-platform API:
    dynlib.load_library(path) -> (dynlib.Library, bool)
    dynlib.symbol_address(lib, name) -> (rawptr, bool)
    dynlib.unload_library(lib) -> bool
    dynlib.last_error() -> string

Because system shared library filenames differ across OSes (kernel32.dll on
Windows, libc.so.6 on Linux, libSystem.B.dylib on macOS), we select both the
library path and the target symbols under 'when ODIN_OS' compile-time guards.
*/

when ODIN_OS == .Windows {
	SYSTEM_LIB_PATH :: "kernel32.dll"

	System_API :: struct {
		__handle:            dynlib.Library,
		GetCurrentProcessId: proc "system" () -> u32,
	}
} else when ODIN_OS == .Darwin {
	SYSTEM_LIB_PATH :: "libSystem.B.dylib"

	System_API :: struct {
		__handle: dynlib.Library,
		getpid:   proc "c" () -> i32,
	}
} else {
	SYSTEM_LIB_PATH :: "libc.so.6"

	System_API :: struct {
		__handle: dynlib.Library,
		getpid:   proc "c" () -> i32,
	}
}

manual_library_loading :: proc() {

	/*
	Loading a library manually works in three steps: load the library handle
	with dynlib.load_library, query a symbol's raw address with
	dynlib.symbol_address, and cast that rawptr to the exact C or system
	procedure signature before calling it.

	Suppose you load SYSTEM_LIB_PATH into 'lib, ok := dynlib.load_library(SYSTEM_LIB_PATH)'.
	Always guard '!ok' by printing dynlib.last_error(), and schedule
	'defer dynlib.unload_library(lib)' immediately after a successful load so
	the OS reference count drops back to zero on return.
	*/

	lib, ok := dynlib.load_library(SYSTEM_LIB_PATH)
	if !ok {
		fmt.printfln("Failed to load %s: %s", SYSTEM_LIB_PATH, dynlib.last_error())
		return
	}
	defer dynlib.unload_library(lib)
	fmt.printfln("Loaded %s handle: %v", SYSTEM_LIB_PATH, lib)

	// Query the process ID symbol manually with dynlib.symbol_address:
	// On Windows look up "GetCurrentProcessId" and cast raw_sym to
	// (proc "system" () -> u32); on Linux/macOS look up "getpid" and cast to
	// (proc "c" () -> i32). Check 'found', call the function pointer into pid,
	// and print pid with fmt.printfln.


	// Try loading a non-existent library path like "missing_plugin_123.dll"
	// using dynlib.load_library and print dynlib.last_error() when !ok.
}

reflected_symbol_tables :: proc() {

	/*
	Resolving twenty functions by hand with symbol_address is tedious and easy
	to mistype. Odin's dynlib.initialize_symbols(&api, path, prefix) uses
	compile-time reflection to walk every procedure-pointer field on your API
	struct and bind it automatically.

	Two struct conventions make hot-reloading effortless:
	First, when a struct includes '__handle: dynlib.Library', initialize_symbols
	stores the loaded handle there; if '__handle' is already non-nil from an
	earlier load, initialize_symbols unloads the old library before loading the
	new one. Second, attaching a struct tag like 'dynlib:"ActualCName"' lets
	your Odin field keep a clean name while binding a different exported symbol.
	*/

	api: System_API
	fmt.printfln("System_API layout size = %d bytes (initial handle = %v)", size_of(System_API), api.__handle)

	// Bind api automatically using:
	// count, ok := dynlib.initialize_symbols(&api, SYSTEM_LIB_PATH)
	// If !ok, print dynlib.last_error() and return; otherwise schedule
	// defer dynlib.unload_library(api.__handle) and print count.


	// Invoke the bound procedure on api (api.GetCurrentProcessId() on Windows
	// or api.getpid() on Linux/macOS) and print the returned process ID.


	// Extend System_API above with a second OS-appropriate symbol field:
	// GetTickCount: proc "system" () -> u32 on Windows, or
	// strlen: proc "c" (s: cstring) -> uint on Linux/macOS.
	// Call the newly bound symbol through api and print its result.


	// Define a small struct Tagged_API with __handle: dynlib.Library and a
	// renamed field using a dynlib struct tag (wrap the tag in Odin backticks):
	// proc_id: proc "system" () -> u32 with tag dynlib:"GetCurrentProcessId" on Windows
	// (or c_abs: proc "c" (x: i32) -> i32 with tag dynlib:"abs" on POSIX).
	// Bind it with dynlib.initialize_symbols, call it, and defer unload.


	// Call dynlib.initialize_symbols(&api, SYSTEM_LIB_PATH) a second time
	// before returning to verify automatic unload-and-rebind when api.__handle
	// is already populated.


	// Write a tiny helper call_if_bound :: proc(api: ^System_API) that checks
	// every procedure pointer field for nil before invoking it. In real
	// dynamic loaders, optional symbols can remain nil if a newer API
	// extension is absent on the user's machine.


	// Experiment with the third prefix parameter of dynlib.initialize_symbols:
	// suppose a C library exports mylib_init and mylib_step. Define a dummy
	// struct with fields init and step and note how calling
	// dynlib.initialize_symbols(&tbl, lib_path, "mylib_") prepends "mylib_"
	// automatically during symbol lookup.
}

main :: proc() {

	fmt.println("=== 1. Manual library loading ===")
	manual_library_loading()

	fmt.println("\n=== 2. Reflected symbol tables ===")
	reflected_symbol_tables()
}
