// odin run 500_tracy_plots_messages_and_frame_budgets.odin -file

package main

import "core:fmt"
import "core:slice"
import "core:strings"
import "core:time"

/*
Scoped CPU zones answer how long a procedure ran, yet when a frame suddenly blows
its 16.67 ms (60 FPS) latency budget, timing bars alone do not tell you what
system state changed right before the spike. Plots and colored timeline messages
turn Tracy into an application flight recorder:

- Plots (___tracy_emit_plot, ___tracy_emit_plot_config) draw numerical curves
  above the CPU timeline such as Active_Entities, Cache_Hit_Pct, or Frame_KB.
- Timeline messages (___tracy_emit_messageC) drop colored vertical flags on the
  exact nanosecond a state transition fires, such as "Wave_Spawn_Cache_Burst".
- Frame budgets (BUDGET_60FPS_NS :: 16_666_667) highlight every tick overrun
  alongside those curves so you can tie tail latency directly to its cause.

When we store message text as a persistent cstring literal instead of calling
fmt.ctprintf, we avoid the temp-allocator dangling-pointer trap because Tracy's
background thread may read the string pointer after the current frame resets
context.temp_allocator.
*/

TRACY_ENABLE :: #config(TRACY_ENABLE, false)
BUDGET_60FPS_NS :: 16_666_667

Plot_Format_Type :: enum i32 {
	Number     = 0,
	Memory     = 1,
	Percentage = 2,
}

when TRACY_ENABLE {
	when ODIN_OS == .Windows {
		foreign import tracy "TracyClient.lib"
	} else {
		foreign import tracy "system:TracyClient"
	}

	foreign tracy {
		___tracy_emit_plot        :: proc "c" (name: cstring, val: f64) ---
		___tracy_emit_plot_int    :: proc "c" (name: cstring, val: i64) ---
		___tracy_emit_plot_config :: proc "c" (name: cstring, type: i32, step: i32, fill: i32, color: u32) ---
		___tracy_emit_messageC    :: proc "c" (txt: cstring, size: uint, color: u32, callstack: i32) ---
		___tracy_emit_frame_mark  :: proc "c" (name: cstring) ---
	}
}

Plot_Sample :: struct {
	frame:  int,
	series: string,
	value:  f64,
}

Timeline_Message :: struct {
	frame: int,
	text:  cstring,
	color: u32,
}

Frame_Budget_Record :: struct {
	frame:      int,
	start_ns:   i64,
	elapsed_ns: i64,
	over_60fps: bool,
}

Telemetry_Recorder :: struct {
	origin_tick:   time.Tick,
	current_frame: int,
	plots:         [64]Plot_Sample,
	plot_count:    int,
	messages:      [32]Timeline_Message,
	msg_count:     int,
	frames:        [16]Frame_Budget_Record,
	frame_count:   int,
}

// Define tracy_plot_config :: proc(name: cstring, fmt_type: Plot_Format_Type, step: bool = false, fill: bool = true, color: u32 = 0)
// Inside when TRACY_ENABLE, forward the configuration to
// ___tracy_emit_plot_config(name, i32(fmt_type), i32(step), i32(fill), color).
// In the else branch, verify len(name) > 0 so all parameters stay active.


// Define tracy_plot :: proc(rec: ^Telemetry_Recorder, series: string, c_name: cstring, value: f64)
// Bounds-check rec.plot_count < len(rec.plots), store
// Plot_Sample{frame = rec.current_frame, series = series, value = value},
// increment rec.plot_count += 1, and inside when TRACY_ENABLE emit
// ___tracy_emit_plot(c_name, value).


// Define tracy_message :: proc(rec: ^Telemetry_Recorder, text: cstring, color: u32 = 0xFFAA00)
// Bounds-check rec.msg_count < len(rec.messages), store
// Timeline_Message{frame = rec.current_frame, text = text, color = color},
// increment rec.msg_count += 1, and inside when TRACY_ENABLE emit
// ___tracy_emit_messageC(text, uint(len(text)), color, 0) using a persistent
// cstring literal (never a temp_allocator pointer).


// Define end_frame_budget :: proc(rec: ^Telemetry_Recorder, frame_start: time.Tick)
// Compute start_ns := time.duration_nanoseconds(time.tick_diff(rec.origin_tick, frame_start))
// and elapsed_ns := time.duration_nanoseconds(time.tick_since(frame_start)).
// Bounds-check rec.frame_count < len(rec.frames), append Frame_Budget_Record with
// over_60fps = elapsed_ns > BUDGET_60FPS_NS, increment rec.frame_count += 1 and
// rec.current_frame += 1, and emit ___tracy_emit_frame_mark(nil) when TRACY_ENABLE.


plots_and_colored_messages :: proc() {

	/*
	Suppose Frame #5 jumps from 0.4 ms to 24.0 ms while Frames #0..#4 stay fast.
	Without plots and messages, you know Frame #5 stalled, not why. Pairing a
	red Timeline_Message ("Wave_Spawn_Cache_Burst") with plot curves for
	Active_Entities and Cache_Hit_Pct immediately reveals that an entity spawn
	triggered a strided cache-miss storm on that exact frame.
	*/

	rec := Telemetry_Recorder{origin_tick = time.tick_now()}
	t0 := time.tick_now()
	dt_ns := time.duration_nanoseconds(time.tick_since(t0))
	fmt.printfln(
		"Budget_60FPS=%v ns (16.67 ms) | sample_tick=%v ns | Recorder=%v B",
		BUDGET_60FPS_NS,
		dt_ns,
		size_of(rec),
	)

	// Implement the four telemetry procedures above, then initialize a
	// recorder := Telemetry_Recorder{origin_tick = time.tick_now()} and configure
	// two plot series via tracy_plot_config:
	// - "Active_Entities" as .Number (step = true, fill = true, color = 0x33AAFF)
	// - "Cache_Hit_Pct" as .Percentage (step = false, fill = false, color = 0x44DD88)
	// Emit one baseline plot sample on frame 0 and one persistent message
	// tracy_message(&recorder, "Telemetry_Armed", 0x44DD88) to confirm recording.
}

compute_burst_and_percentiles :: proc() {

	/*
	Never fake frame latency with time.sleep in CPU budget drills: sleeping parks
	your thread in the OS scheduler rather than loading CPU execution ports or
	cache lines. Driving latency with real strided memory touches and arithmetic
	over an entity buffer produces authentic timing spikes and measured cache
	hit rates.

	Average frame time also hides single-frame hitches. Suppose 9 frames run in
	0.5 ms and 1 frame spikes to 22.0 ms: the mean is 2.65 ms (looks fine!),
	while P95 and P99 immediately expose the 22.0 ms budget failure. Sorting a
	copy of frame durations lets us compute any nearest-rank percentile P:

	    Suppose sorted holds 10 durations [d0 .. d9].
	    For P95, rank = clamp(int(math.ceil(0.95 * 10)) - 1, 0, 9) = 9 -> d9!
	*/

	sample := [3]i64{1_200_000, 19_400_000, 900_000}
	slice.sort(sample[:])
	fmt.printfln("Sorted sample durations (ns): %v", sample)

	// Write simulate_entity_burst :: proc(buf: []f64, steps: int, stride: int) -> (sink: f64, cache_hit_pct: f64)
	// Do NOT call time.sleep. Instead, step i in 0..<steps indexing
	// idx := (i * stride) %% len(buf), updating buf[idx] = buf[idx] * 1.0001 + 0.5
	// and accumulating into sink. Count cache_hits whenever stride == 1 (or the
	// next index stays within the same 8-f64 64-byte cache line) vs cache_misses
	// when jumping to a new cache line, returning cache_hit_pct = 100.0 * hits / total.


	// Write percentile_ns :: proc(rec: ^Telemetry_Recorder, pct: f64) -> i64
	// Copy the active rec.frames[:rec.frame_count] elapsed_ns values into a local
	// [16]i64 array, sort with slice.sort(durations[:rec.frame_count]), and return
	// the nearest-rank element for 0.0 <= pct <= 100.0 (returning 0 if empty).


	// Allocate buf := make([]f64, 524_288) (4 MB, larger than typical L2 cache!)
	// with defer delete(buf), and run a 10-frame loop (for f in 0..<10):
	// - Normal frames (f != 5): entities = 256, run simulate_entity_burst(buf, 32_000, 1).
	// - Frame #5 (f == 5): emit tracy_message(&rec, "Wave_Spawn_Cache_Burst", 0xFF3333),
	//   set entities = 4096, and run simulate_entity_burst(buf, 8_000_000, 17) so
	//   strided cache misses push elapsed_ns past BUDGET_60FPS_NS (16.67 ms).
	// Emit tracy_plot for "Active_Entities" and "Cache_Hit_Pct" (using the real
	// measured cache_hit_pct), call end_frame_budget, print the correlated frame
	// table (consuming sink so -o:speed never erases the work), and print P50,
	// P95, P99, and Max frame times.
}

chrome_spall_export_and_post_fix :: proc() {

	/*
	Even when TracyClient.lib is not linked, Odin programs can serialize recorded
	frames, plots, and messages into Chrome Trace Event JSON (which opens directly
	in ui.perfetto.dev and pairs cleanly with Odin's core:prof/spall timelines):
	- "ph": "X" for frame duration spans (ts and dur in microseconds)
	- "ph": "C" for plot counter samples
	- "ph": "i" for instant timeline messages
	*/

	sb: strings.Builder
	strings.builder_init(&sb)
	defer strings.builder_destroy(&sb)
	fmt.sbprintf(&sb, "{\"ph\":\"i\",\"name\":\"%s\",\"s\":\"g\",\"ts\":0.0,\"pid\":1}", "AnchorMarker")
	fmt.printfln("Sample Chrome/Spall JSON marker: %s", strings.to_string(sb))

	// Write export_chrome_trace_json :: proc(rec: ^Telemetry_Recorder, sb: ^strings.Builder)
	// Format a valid JSON array "[" ... "]" containing every Frame_Budget_Record
	// ("ph": "X"), Plot_Sample ("ph": "C"), and Timeline_Message ("ph": "i") using
	// microsecond timestamps (f64(ns) / 1000.0). Inspect the generated JSON string
	// and verify "ph":"X", "ph":"C", and "ph":"i" all appear.


	// Post-fix trace validation: eliminate the strided cache-miss storm on Frame #5
	// by switching the burst frame to contiguous unit-stride access (stride = 1)
	// and capping the per-frame pass (e.g. steps = 256_000) across the same 4 MB
	// buffer. Re-run the 10-frame loop into fixed_rec: Telemetry_Recorder, print the
	// updated P50, P95, P99, and Cache_Hit_Pct, and assert both
	// percentile_ns(&fixed_rec, 95.0) < BUDGET_60FPS_NS and
	// percentile_ns(&fixed_rec, 99.0) < BUDGET_60FPS_NS!
}

main :: proc() {

	fmt.println("=== 1. Tracy plots and persistent colored messages ===")
	plots_and_colored_messages()

	fmt.println("\n=== 2. Real compute/cache bursts and P50/P95/P99 budgets ===")
	compute_burst_and_percentiles()

	fmt.println("\n=== 3. Chrome/Spall JSON export and post-fix budget check ===")
	chrome_spall_export_and_post_fix()
}
