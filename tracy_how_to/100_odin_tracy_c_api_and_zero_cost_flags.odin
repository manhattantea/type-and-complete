// odin run 100_odin_tracy_c_api_and_zero_cost_flags.odin -file

package main

import "base:intrinsics"
import "base:runtime"
import "core:fmt"
import "core:time"

/*
How do you talk to Tracy without pulling in any third-party Odin wrapper
library? Tracy compiles down to a small C runtime (TracyClient.lib on Windows,
libTracyClient.so / libTracyClient.dylib on POSIX) whose public C ABI lives in
TracyC.h. Odin calls C ABI symbols directly through a foreign block.

Even better, Odin lets you turn that instrumentation into true zero-cost
abstraction using #config and when:
- #config(TRACY_ENABLE, false) creates a compile-time boolean constant that
  defaults to false unless you pass -define:TRACY_ENABLE=true on the command
  line.
- when TRACY_ENABLE { ... } is compile-time conditional compilation. Unlike a
  runtime if statement, the compiler discards any false when branch before
  machine-code generation. In default builds, foreign import tracy and all
  Tracy C calls vanish into zero instructions and zero linker dependencies.
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
	when ODIN_OS == .Windows {
		foreign import tracy "TracyClient.lib"
	} else {
		foreign import tracy "system:TracyClient"
	}

	foreign tracy {
		___tracy_emit_zone_begin :: proc "c" (srcloc: ^Tracy_Source_Location_Data, active: i32) -> Tracy_C_Zone_Ctx ---
		___tracy_emit_zone_end   :: proc "c" (ctx: Tracy_C_Zone_Ctx) ---
		___tracy_emit_frame_mark :: proc "c" (name: cstring) ---
	}
}

/*
Look carefully at ___tracy_emit_zone_begin above:
- proc "c" tells Odin to use the platform C calling convention instead of
  Odin's default calling convention, and passes no implicit Odin context.
- When you call ___tracy_emit_zone_begin(srcloc, 1), Tracy does NOT copy the
  strings inside Tracy_Source_Location_Data into its ring buffer. It stores
  only the raw pointer address srcloc so zone entry stays a few nanoseconds.
  Milliseconds later, Tracy's background telemetry thread reads srcloc.name,
  srcloc.function, and srcloc.file asynchronously to send labels to the GUI.

That creates a dangerous pointer-lifetime bug if you pass fmt.ctprintf(...)
into Tracy_Source_Location_Data! Why? Because fmt.ctprintf allocates inside
context.temp_allocator. The moment your frame calls free_all(context.temp_allocator)
or the temp ring wraps, Tracy's background thread reads freed memory—a textbook
use-after-free bug! Always use compile-time constant cstring literals OR pin
strings once inside a persistent static/arena registry table.
*/

Srcloc_Registry :: struct {
	entries:  [64]Tracy_Source_Location_Data,
	files:    [64]string,
	lines:    [64]i32,
	names:    [64]cstring,
	str_buf:  [8192]u8,
	str_used: int,
	count:    int,
}

g_srcloc_registry: Srcloc_Registry
g_fallback_zones_begun: int
g_fallback_zones_ended: int

// Define pin_cstring :: proc(reg: ^Srcloc_Registry, s: string) -> cstring
// Copy s's raw bytes into reg.str_buf[reg.str_used:] followed by a 0 byte
// terminator, advance reg.str_used += len(s) + 1 (asserting bounds fit inside
// len(reg.str_buf)), and return cstring(&reg.str_buf[start]). Notice this lives
// in static storage for the whole process with zero temp_allocator usage!


// Define register_srcloc :: proc(name: cstring, color: u32 = 0, loc := #caller_location) -> ^Tracy_Source_Location_Data
// Scan g_srcloc_registry.count entries for a matching (loc.file_path, loc.line, name)
// and return &g_srcloc_registry.entries[i] if already registered. Otherwise
// append a new slot, pin loc.procedure and loc.file_path via pin_cstring, fill
// Tracy_Source_Location_Data{name = name, function = fn_cstr, file = file_cstr,
// line = u32(loc.line), color = color}, increment count, and return its pointer.


// Define zone_begin :: proc(srcloc: ^Tracy_Source_Location_Data) -> Tracy_C_Zone_Ctx
// Inside a when TRACY_ENABLE { ... } else { ... } branch:
// - when true: return ___tracy_emit_zone_begin(srcloc, 1)
// - else: increment g_fallback_zones_begun += 1 and return
//   Tracy_C_Zone_Ctx{id = u32(g_fallback_zones_begun), active = 1}.


// Define zone_end :: proc(ctx: Tracy_C_Zone_Ctx)
// Inside a when TRACY_ENABLE { ... } else { ... } branch:
// - when true: call ___tracy_emit_zone_end(ctx)
// - else: if ctx.active != 0 { g_fallback_zones_ended += 1 }.


probe_caller_location :: proc(loc := #caller_location) -> runtime.Source_Code_Location {

	return loc
}

c_abi_layout_and_lifetime :: proc() {

	/*
	In C/C++, ZoneScoped relies on preprocessor macros (__FUNCTION__, __FILE__,
	__LINE__) to build a static const struct ___tracy_source_location_data.
	In Odin, writing loc := #caller_location as a default parameter tells the
	compiler to capture the caller's procedure, file_path, line, and column
	automatically at every call site.

	Because Tracy_Source_Location_Data crosses the C ABI, every field offset and
	total struct size must match TracyC.h byte for byte:
	On 64-bit targets, 3 cstring pointers (24 bytes) + line (u32, 4 bytes) +
	color (u32, 4 bytes) = 32 bytes total, while Tracy_C_Zone_Ctx (u32 + i32)
	is 8 bytes passed and returned by value in registers.
	*/

	anchor_loc := probe_caller_location()
	fmt.printfln(
		"SourceLoc=%v B, ZoneCtx=%v B | caller=%s:%v",
		size_of(Tracy_Source_Location_Data),
		size_of(Tracy_C_Zone_Ctx),
		anchor_loc.procedure,
		anchor_loc.line,
	)

	// Verify the C ABI layout at compile time and runtime:
	// Add #assert(size_of(Tracy_C_Zone_Ctx) == 8) and
	// #assert(offset_of(Tracy_C_Zone_Ctx, active) == 4).
	// Print offset_of(Tracy_Source_Location_Data, function) and
	// offset_of(Tracy_Source_Location_Data, line) with fmt.printfln.


	// Test persistent source-location pinning and deduplication:
	// Call p1 := register_srcloc("StartupProbe", 0x33AAFF) and
	// p2 := register_srcloc("StartupProbe", 0x33AAFF) inside a helper proc or
	// loop from the exact same call site, assert p1 == p2, and print
	// g_srcloc_registry.count (expected: 1) plus p1.function and p1.line.
}

zero_cost_gates_and_zones :: proc() {

	/*
	Suppose you instrument 40 procedures with zone_begin and zone_end. In a
	default build where TRACY_ENABLE == false, any code guarded by
	when TRACY_ENABLE is stripped completely by Odin's compiler front-end.
	In a profiling build (-define:TRACY_ENABLE=true), the exact same call site
	emits ___tracy_emit_zone_begin and ___tracy_emit_zone_end without changing a
	single caller.

	Notice that even static @(static) locals inside a procedure work cleanly when
	labels are compile-time cstring literals:

	    @(static) srcloc := Tracy_Source_Location_Data{
	        name     = "Physics",
	        function = "step_world",
	        file     = "sim.odin",
	        line     = 42,
	    }

	Attaching @(static) gives that variable process-long static storage rather
	than living on the temporary stack frame.
	*/

	fmt.printfln(
		"TRACY_ENABLE=%v | fallback begun=%v, ended=%v",
		TRACY_ENABLE,
		g_fallback_zones_begun,
		g_fallback_zones_ended,
	)

	// Practice zone_begin and zone_end with both static and registered srclocs:
	// Declare a @(static) srcloc: Tracy_Source_Location_Data using constant
	// cstring literals (or obtain srcloc := register_srcloc("LoopSum", 0x00AAFF)),
	// call ctx := zone_begin(srcloc), sum i in 0..<10_000 into a local total,
	// call zone_end(ctx), and print total alongside g_fallback_zones_begun and
	// g_fallback_zones_ended to verify begun == ended.
}

early_return_safety_and_timing :: proc() {

	/*
	Manually calling zone_begin at the top of a procedure and zone_end at the
	bottom breaks the moment someone adds an early return:

	    Suppose process_item(x: int) -> int begins a zone and checks:
	        if x < 0 { return -1 }   // BUG: skips zone_end at the bottom!
	    Tracy's per-thread zone stack stays unpopped, corrupting every outer zone!

	Writing defer zone_end(ctx) immediately after zone_begin guarantees the
	compiler emits zone_end(ctx) on every exit path (normal return, early return,
	or break). (Primer 200 goes one step further with @(deferred_out) so callers
	cannot forget defer either.)
	*/

	t0 := time.tick_now()
	c0 := intrinsics.read_cycle_counter()
	baseline := 0
	for i in 0..<1_000 {
		baseline += i
	}
	c1 := intrinsics.read_cycle_counter()
	ns := time.duration_nanoseconds(time.tick_since(t0))
	fmt.printfln("Baseline 1k loop: sum=%v | %v cycles | %v ns", baseline, c1 - c0, ns)

	// Demonstrate an early-return zone leak and fix it with defer:
	// Write a local proc risky_step(x: int) -> int that calls zone_begin(...)
	// and returns -1 early when x < 0 without defer before calling zone_end at
	// the bottom. Call risky_step(-5) and print g_fallback_zones_begun vs.
	// g_fallback_zones_ended to observe the mismatch (begun > ended).
	// Then add defer zone_end(ctx) right after zone_begin, reset or track the
	// delta around risky_step(-5) and risky_step(10), and assert begun == ended.


	// Benchmark zero-cost gating (TRACY_ENABLE == false vs. active zone calls):
	// Time 100,000 iterations of a simple accumulator loop wrapped in
	// when TRACY_ENABLE { ... } (which compiles to 0 extra instructions when
	// false) vs. 100,000 iterations calling your fallback zone_begin /
	// defer zone_end pair. Print both total cycles and nanoseconds (and pass
	// -define:TRACY_ENABLE=true when TracyClient.lib is available to verify live
	// C ABI linking).
}

main :: proc() {

	fmt.println("=== 1. C ABI layout and persistent Srcloc lifetime ===")
	c_abi_layout_and_lifetime()

	fmt.println("\n=== 2. Compile-time zero-cost gates and zones ===")
	zero_cost_gates_and_zones()

	fmt.println("\n=== 3. Early-return zone safety and gate timing ===")
	early_return_safety_and_timing()
}
