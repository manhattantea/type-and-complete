// odin run 200_frame_marks_and_scoped_zones.odin -file

package main

import "core:fmt"
import "core:time"

/*
When you open a continuous simulation, server, or game in the Tracy GUI, the
first thing your eyes jump to is the Frame Time Histogram along the top bar.
Without frame marks, a continuous loop looks like one endless stream of calls.
Calling frame_mark(nil) at the end of every tick slices execution into discrete
frames so you can immediately spot a single-frame spike above your 16.67 ms
(60 FPS) or 8.33 ms (120 FPS) budget even when average frame rate looks fine.

To instrument scopes without repeating defer zone_end(ctx) everywhere, Odin
supports @(deferred_out = zone_end). Putting @(deferred_out = zone_end) above
a procedure tells the compiler: whenever a caller invokes zone_scoped(...),
automatically run zone_end(result) when the caller's current scope exits.
Even calling zone_scoped("RenderWorld") without saving its return value still
triggers zone_end cleanly at the closing brace.

To diagnose nested scopes accurately, a profiler must separate Inclusive Time
(total wall duration of a zone) from Self Time (work done by that zone alone).
Suppose FrameTick takes 10.0 ms total, and inside it calls Broadphase (1.5 ms)
and Narrowphase (8.2 ms). Subtracting child time yields FrameTick's Self Time:

    self_ns = elapsed_ns - child_ns  ->  10.0 - (1.5 + 8.2) = 0.3 ms

An active parent stack computes this in O(1) per zone: push an entry onto
g_active_stack on entry, pop it on exit to compute self_ns, and add the
elapsed_ns into the parent's child_ns if g_active_depth > 0.
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
		___tracy_emit_zone_begin       :: proc "c" (srcloc: ^Tracy_Source_Location_Data, active: i32) -> Tracy_C_Zone_Ctx ---
		___tracy_emit_zone_end         :: proc "c" (ctx: Tracy_C_Zone_Ctx) ---
		___tracy_emit_zone_text        :: proc "c" (ctx: Tracy_C_Zone_Ctx, txt: cstring, size: uint) ---
		___tracy_emit_zone_value       :: proc "c" (ctx: Tracy_C_Zone_Ctx, value: u64) ---
		___tracy_emit_frame_mark       :: proc "c" (name: cstring) ---
		___tracy_emit_frame_mark_start :: proc "c" (name: cstring) ---
		___tracy_emit_frame_mark_end   :: proc "c" (name: cstring) ---
	}
}

Zone_Ctx :: struct {
	slot_index: int,
	name:       string,
	color:      u32,
	start_tick: time.Tick,
	c_ctx:      Tracy_C_Zone_Ctx,
}

Active_Zone :: struct {
	name:     string,
	child_ns: i64,
}

Zone_Record :: struct {
	frame:        int,
	name:         string,
	color:        u32,
	depth:        int,
	inclusive_ns: i64,
	self_ns:      i64,
	value_tag:    u64,
	text_tag:     string,
}

Zone_Summary :: struct {
	name:               string,
	calls:              int,
	total_self_ns:      i64,
	total_inclusive_ns: i64,
	active_depth:       int,
}

g_zone_records: [128]Zone_Record
g_zone_count: int
g_active_stack: [16]Active_Zone
g_active_depth: int
g_zone_summaries: [32]Zone_Summary
g_summary_count: int
g_current_frame: int
g_last_frame_tick: time.Tick
g_frame_durations_ns: [32]i64

// Define find_or_add_summary :: proc(name: string) -> ^Zone_Summary
// Scan g_zone_summaries[0..<g_summary_count] for a matching name and return
// &g_zone_summaries[i], or append a new entry if not found.


// Define zone_end :: proc(ctx: Zone_Ctx)
// Measure elapsed_ns := time.duration_nanoseconds(time.tick_since(ctx.start_tick)).
// Pop the top Active_Zone from g_active_stack (decrementing g_active_depth),
// compute self_ns := max(i64(0), elapsed_ns - popped.child_ns), and if
// g_active_depth > 0 add g_active_stack[g_active_depth - 1].child_ns += elapsed_ns.
// Store inclusive_ns and self_ns into g_zone_records[ctx.slot_index] (bounds
// checked). Also update summary := find_or_add_summary(ctx.name): increment
// summary.calls += 1, add summary.total_self_ns += self_ns, and ONLY add
// summary.total_inclusive_ns += elapsed_ns if summary.active_depth == 1 before
// decrementing summary.active_depth -= 1. Inside when TRACY_ENABLE, call
// ___tracy_emit_zone_end(ctx.c_ctx).


// Define @(deferred_out = zone_end) zone_scoped :: proc(name: string, color: u32 = 0x00AAFF) -> Zone_Ctx
// Reserve slot := g_zone_count %% len(g_zone_records) and increment g_zone_count.
// Push Active_Zone{name = name, child_ns = 0} onto g_active_stack[g_active_depth]
// and increment g_active_depth. Increment find_or_add_summary(name).active_depth += 1.
// Store Zone_Record{frame = g_current_frame, name = name, color = color, depth = g_active_depth}
// at g_zone_records[slot]. When TRACY_ENABLE is true, emit ___tracy_emit_zone_begin
// using a persistent Tracy_Source_Location_Data (never fmt.ctprintf!). Return
// Zone_Ctx{slot_index = slot, name = name, color = color, start_tick = time.tick_now(), c_ctx = c_ctx}.


// Define zone_value :: proc(ctx: Zone_Ctx, val: u64) and
// zone_text :: proc(ctx: Zone_Ctx, text: string)
// Store val / text into g_zone_records[ctx.slot_index] (bounds checked) and
// forward inside when TRACY_ENABLE to ___tracy_emit_zone_value / ___tracy_emit_zone_text.


// Define frame_mark :: proc(name: cstring = nil) -> i64
// Initialize g_last_frame_tick = time.tick_now() before your frame loop, then
// inside frame_mark compute now := time.tick_now(), frame_ns :=
// time.duration_nanoseconds(time.tick_diff(g_last_frame_tick, now)), update
// g_last_frame_tick = now, store frame_ns into
// g_frame_durations_ns[g_current_frame %% len(g_frame_durations_ns)], increment
// g_current_frame += 1, emit ___tracy_emit_frame_mark(name) inside when TRACY_ENABLE,
// and return frame_ns.


// Define frame_mark_start :: proc(name: cstring) and frame_mark_end :: proc(name: cstring)
// Forward inside when TRACY_ENABLE to ___tracy_emit_frame_mark_start(name) and
// ___tracy_emit_frame_mark_end(name) for discontinuous periodic subsystems.


scoped_zones_and_nested_self_time :: proc() {

	/*
	Notice why Self Time matters in a nested hierarchy: if FrameTick wraps
	Broadphase and Narrowphase, FrameTick always shows ~100% of Inclusive Time.
	Subtracting child_ns reveals that FrameTick itself is nearly free while
	one specific child owns the frame budget.

	    Suppose FrameTick runs for 12.0 ms:
	        Broadphase  -> inclusive = 1.0 ms, self = 1.0 ms
	        Narrowphase -> inclusive = 10.8 ms, self = 10.8 ms
	        FrameTick   -> inclusive = 12.0 ms, self = 0.2 ms (12.0 - 11.8)
	*/

	boot := time.tick_now()
	elapsed_ns := time.duration_nanoseconds(time.tick_since(boot))
	fmt.printfln(
		"Timer anchor: %v ns | Zone_Record=%v B | Max stack=%v",
		elapsed_ns,
		size_of(Zone_Record),
		len(g_active_stack),
	)

	// Build a nested 3-zone frame helper step_nested_frame :: proc(entity_count: int) -> f64:
	// Open frame_ctx := zone_scoped("FrameTick", 0x3399FF) at the top, then open
	// nested sub-blocks for:
	// - "Broadphase": a lightweight O(N) loop over 0..<entity_count * 20
	// - "Narrowphase": tag ctx := zone_scoped("Narrowphase", 0xFF5500) with
	//   zone_value(ctx, u64(entity_count)) and zone_text(ctx, entity_count > 1000 ? "HIGH_ENTITY_SPIKE" : "normal"),
	//   then run an O(N^2) pair check scaled as i in 0..<entity_count and
	//   j in i..<min(entity_count, i + entity_count / 2) accumulating f64 math
	//   so 4096 entities cleanly spikes over 16.67 ms!
	// - "RenderWorld": call zone_scoped("RenderWorld", 0x22CC66) and run 0..<5_000.
	// Run one test frame and print each Zone_Record's depth, inclusive_ns, and self_ns.
}

recursive_zones_and_discontinuous_frames :: proc() {

	/*
	Recursive procedures break naive Inclusive Time summation! Suppose
	walk_bvh(4) takes 8 ms and recursively calls walk_bvh(3) (4 ms),
	walk_bvh(2) (2 ms), and walk_bvh(1) (1 ms). If zone_end blindly adds
	elapsed_ns to WalkBVH's aggregate inclusive total on every exit, WalkBVH
	reports 8 + 4 + 2 + 1 = 15 ms—nearly double the true 8 ms wall time!

	Applying the depth == 1 rule solves this cleanly: track active_depth per
	zone name. Add self_ns on every exit, and add inclusive_ns ONLY when
	active_depth == 1 (the outermost entry unwinding).

	Secondary subsystems (such as an audio mixer callback or periodic save
	flush running every few frames) do not fire once per render tick. Marking
	them with frame_mark_start("AudioChunk") and frame_mark_end("AudioChunk")
	gives them their own discontinuous frame track in Tracy without distorting
	the main 60 FPS histogram.
	*/

	fmt.printfln("Current frame=%v | summary slots=%v", g_current_frame, g_summary_count)

	// Test recursive inclusive-time safety with depth == 1 accounting:
	// Write a recursive proc walk_bvh :: proc(depth: int) -> int that opens
	// zone_scoped("WalkBVH", 0xAA44FF), does a small loop over 0..<2_000, and
	// if depth > 1 returns walk_bvh(depth - 1) + 1. Call walk_bvh(5) inside
	// an outer zone_scoped("BVHRoot") and inspect g_zone_summaries to verify
	// WalkBVH's total_inclusive_ns <= BVHRoot's total_inclusive_ns (never >100%!).


	// Practice discontinuous frame marks alongside primary ticks:
	// Simulate 4 ticks where on even ticks (tick % 2 == 0) you wrap an
	// audio-mix burst inside frame_mark_start("AudioChunk") and
	// frame_mark_end("AudioChunk"), while calling frame_mark() at the end of
	// each tick. Print g_current_frame and the recorded AudioChunk zone rows.
}

frame_spike_triage_and_fix :: proc() {

	/*
	When Frame #3 blows past the 16.67 ms (16_666_667 ns) budget while Frames
	#1, #2, #4, and #5 finish in under 1 ms, zone_value and zone_text turn the
	mystery into a 5-second diagnosis: Frame #3 carried value_tag = 4096 with
	text_tag = "HIGH_ENTITY_SPIKE", exposing an O(N^2) Narrowphase loop!

	Never stop after flagging the spike—replace the O(N^2) algorithm with an
	O(N) linear/spatial-cell pass, reset the profiler counters, and re-run the
	same 5 frames to verify Frame #3 drops cleanly below 16.67 ms.
	*/

	budget_ns := i64(16_666_667)
	fmt.printfln("60 FPS frame budget threshold: %.2f ms (%v ns)", f64(budget_ns) / 1_000_000.0, budget_ns)

	// Run a 5-frame baseline trace (for f in 0..<5) after setting
	// g_last_frame_tick = time.tick_now(), where Frame #3 (f == 2) passes 4096
	// entities to step_nested_frame and all other frames pass 256, calling
	// frame_mark() at the end of every frame. Print each frame's duration in milliseconds plus any Zone_Record exceeding 5.0 ms
	// along with its value_tag and text_tag to pinpoint Frame #3's spike.


	// Remediate Narrowphase and verify the post-fix trace:
	// Write step_nested_frame_fast :: proc(entity_count: int) -> f64 keeping
	// the exact same Broadphase and RenderWorld zones, but replacing the O(N^2)
	// Narrowphase pair scan with a linear O(N) swept/cell pass over 0..<entity_count
	// (using a small fixed cell-accumulator or neighbor stride). Reset
	// g_zone_count, g_summary_count, and g_current_frame to 0, re-run the same
	// 5 frames (256, 256, 4096, 256, 256), and assert every recorded frame
	// duration is < 16_666_667 ns (16.67 ms)! Print before-vs-after Frame #3 ms.
}

main :: proc() {

	fmt.println("=== 1. Scoped zones, @(deferred_out), and nested Self Time ===")
	scoped_zones_and_nested_self_time()

	fmt.println("\n=== 2. Recursive zones (depth == 1) and discontinuous frame marks ===")
	recursive_zones_and_discontinuous_frames()

	fmt.println("\n=== 3. Frame #3 spike triage and post-fix trace verification ===")
	frame_spike_triage_and_fix()
}
