// odin run 596_profiling_with_tracy_zones_and_frames.odin -file

package main

import "base:intrinsics"
import "base:runtime"
import "core:fmt"

/*
Offline traces (595_profiling_with_spall.odin) record to disk after the fact.
Tracy Profiler instead runs as a live client-server stream over TCP port 8086
while your program executes.

This Primer focuses strictly on the Odin language hooks that make Tracy
instrumentation zero-friction: compile-time elimination via #config and
when, automatic RAII-free zone closing via @(deferred_out), and call-site
metadata capture via #caller_location. For persistent source-location table
rules, nested Self-Time forensics, plots, and multi-thread timelines, continue
to ../tracy_how_to/100_odin_tracy_c_api_and_zero_cost_flags.odin and
../tracy_how_to/200_frame_marks_and_scoped_zones.odin.
*/

TRACY_ENABLE :: #config(TRACY_ENABLE, false)

Tracy_Source_Location_Data :: struct {
	name:     cstring,
	function: cstring,
	file:     cstring,
	line:     u32,
	color:    u32,
}

Tracy_C_Zone_Ctx :: struct {
	id:     u32,
	active: i32,
}

when TRACY_ENABLE {
	foreign import tracy "TracyClient.lib"

	foreign tracy {
		___tracy_emit_zone_begin :: proc "c" (srcloc: ^Tracy_Source_Location_Data, active: i32) -> Tracy_C_Zone_Ctx ---
		___tracy_emit_zone_end   :: proc "c" (ctx: Tracy_C_Zone_Ctx) ---
		___tracy_emit_frame_mark :: proc "c" (name: cstring) ---
	}
}

Tracy_Zone_Ctx :: struct {
	name:        string,
	start_cycle: u64,
	c_ctx:       Tracy_C_Zone_Ctx,
}

anchor_zone_preview :: proc(
	name: string,
	loc: runtime.Source_Code_Location = #caller_location,
) -> Tracy_Zone_Ctx {

	c := intrinsics.read_cycle_counter()
	fmt.printfln("Preview zone '%s' @ %s:%d | TRACY_ENABLE=%v | start=%d",
		name, loc.procedure, loc.line, TRACY_ENABLE, c)
	return Tracy_Zone_Ctx{name = name, start_cycle = u64(c)}
}

compile_time_tracy_toggle :: proc() {

	/*
	Writing TRACY_ENABLE :: #config(TRACY_ENABLE, false) creates a compile-time
	boolean constant that defaults to false and flips to true only when you
	pass -define:TRACY_ENABLE=true on the odin command line.

	Because 'when TRACY_ENABLE' is evaluated at compile time, untaken branches
	are neither linked nor even type-checked against TracyClient.lib. When
	TRACY_ENABLE is false, your binary ships zero foreign imports, zero DLL
	dependencies, and zero profiling instructions.
	*/

	anchor_ctx := anchor_zone_preview("BootCheck")
	fmt.printfln("ABI sizes: SourceLoc=%dB, C_Zone_Ctx=%dB, Tracy_Zone_Ctx=%dB (start=%d)",
		size_of(Tracy_Source_Location_Data), size_of(Tracy_C_Zone_Ctx),
		size_of(Tracy_Zone_Ctx), anchor_ctx.start_cycle)

	// Write a procedure at file scope above or right after anchor_zone_preview:
	// tracy_frame_mark :: proc(name: cstring = nil)
	// Inside it, wrap ___tracy_emit_frame_mark(name) inside when TRACY_ENABLE.
	// In an else branch, increment a lightweight local/package frame_count so
	// standalone runs can still report how many frames ran without TracyClient.


	// Verify untaken-branch elimination: write a small when TRACY_ENABLE block
	// that calls tracy_frame_mark() or prints "Tracy C API active", and an
	// else block printing "Tracy disabled (zero C ABI overhead)".
}

deferred_out_and_caller_location :: proc() {

	/*
	How does a single call like tracy_zone("Physics") close itself at every
	return path without C++ RAII destructors? Odin provides two compile-time
	tools that pair together cleanly:

	When we put loc := #caller_location as a default parameter, Odin fills it
	with a runtime.Source_Code_Location describing the call site (.procedure,
	.file_path, .line, .column)—not tracy_zone itself.

	When we annotate tracy_zone with @(deferred_out = tracy_zone_end), the
	compiler automatically rewrites every call site into a scope-bound pair:

	    Suppose update_physics() starts with:
	        tracy_zone("Physics")
	        if paused do return   // early exit still closes the zone!
	    Odin compiles that as if you wrote:
	        _tmp := tracy_zone("Physics")
	        defer tracy_zone_end(_tmp)

	One C lifetime detail to remember when TRACY_ENABLE is true: Tracy's C API
	keeps the ^Tracy_Source_Location_Data pointer and reads .file/.function on
	a background thread after your function returns, so production wrappers
	store persistent cstring records rather than temporary stack buffers
	(covered in detail in ../tracy_how_to/100_odin_tracy_c_api_and_zero_cost_flags.odin).
	*/

	loc_check := anchor_zone_preview("CallerSiteCheck")
	fmt.printfln("Captured start cycle from #caller_location check: %d", loc_check.start_cycle)

	// Implement tracy_zone_end :: proc(ctx: Tracy_Zone_Ctx) at file scope:
	// - Read end_cycle := u64(intrinsics.read_cycle_counter()) and compute
	//   elapsed := end_cycle - ctx.start_cycle.
	// - Inside when TRACY_ENABLE, call ___tracy_emit_zone_end(ctx.c_ctx).
	// - Otherwise print or accumulate ctx.name and elapsed into a small
	//   package summary so standalone mode shows each closed zone.


	// Implement @(deferred_out = tracy_zone_end) on:
	// tracy_zone :: proc(name: string, loc: runtime.Source_Code_Location = #caller_location) -> Tracy_Zone_Ctx
	// Read start_cycle := u64(intrinsics.read_cycle_counter()). When TRACY_ENABLE
	// is true, keep a persistent static Tracy_Source_Location_Data (or fixed
	// table) and call ___tracy_emit_zone_begin(srcloc_ptr, 1). Return
	// Tracy_Zone_Ctx{name = name, start_cycle = start_cycle, c_ctx = c_ctx}.


	// Try changing tracy_zone_end's parameter type from Tracy_Zone_Ctx to int
	// after implementing it—Odin's @(deferred_out) rejects mismatched return
	// and parameter types right at compile time!
}

instrumenting_odin_procedures :: proc() {

	/*
	Once tracy_zone and tracy_frame_mark are in place, adding instrumentation
	to any Odin procedure takes a single line at the top of its body. Even if
	the procedure branches out early on an error check or validation guard,
	the compiler-generated defer guarantees tracy_zone_end runs before control
	leaves the scope.
	*/

	fmt.println("Ready to instrument Odin procedures with @(deferred_out) hooks.")

	// Define two small helper procedures at file scope:
	// - step_physics :: proc(dt: f32, count: int) -> f32 (place tracy_zone("step_physics")
	//   at the top, return early if count <= 0, otherwise sum a tiny loop).
	// - cull_entities :: proc(count: int) -> int (place tracy_zone("cull_entities")
	//   at the top and count visible items).


	// Call both procedures across 3 simulated frames inside this section,
	// closing each iteration with tracy_frame_mark(). Confirm frame #0 with
	// count = 0 still triggers tracy_zone_end via the early return!
	// Continue to ../tracy_how_to/200_frame_marks_and_scoped_zones.odin for
	// nested Self-Time stacks and recursive zone handling.
}

main :: proc() {

	fmt.println("=== 1. Compile-time TRACY_ENABLE toggle ===")
	compile_time_tracy_toggle()

	fmt.println("\n=== 2. @(deferred_out) and #caller_location ===")
	deferred_out_and_caller_location()

	fmt.println("\n=== 3. Instrumenting Odin procedures ===")
	instrumenting_odin_procedures()
}
