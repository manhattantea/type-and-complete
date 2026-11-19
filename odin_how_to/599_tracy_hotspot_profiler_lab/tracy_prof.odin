// Lab 599 module: Odin @(deferred_out) zone stack and context.allocator hooks

package main

import "base:intrinsics"
import "base:runtime"
import "core:fmt"

/*
This module supplies the Odin profiling contracts used by workload.odin and
main.odin. It pairs two Odin features—@(deferred_out) scoped zones and
context.allocator interception—to isolate which single procedure in a pipeline
is burning cycles or allocating heap memory inside a frame loop.

When TRACY_ENABLE is false (default), zones record hardware RDTSC cycles and
allocation counts directly into Profiler_State with zero external DLLs. When
you pass -define:TRACY_ENABLE=true, the exact same hooks forward live events
to TracyClient.lib. For the full five-system Five-Multipliers Hotspot Hunt
capstone, continue to ../tracy_how_to/900_hotspot_hunt_five_multipliers_lab/.
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
		___tracy_emit_zone_begin         :: proc "c" (srcloc: ^Tracy_Source_Location_Data, active: i32) -> Tracy_C_Zone_Ctx ---
		___tracy_emit_zone_end           :: proc "c" (ctx: Tracy_C_Zone_Ctx) ---
		___tracy_emit_frame_mark         :: proc "c" (name: cstring) ---
		___tracy_emit_memory_alloc_named :: proc "c" (ptr: rawptr, size: uint, secure: i32, name: cstring) ---
		___tracy_emit_memory_free_named  :: proc "c" (ptr: rawptr, secure: i32, name: cstring) ---
	}
}

Zone_Entry :: struct {
	name:         string,
	calls:        u64,
	total_cycles: u64,
	self_cycles:  u64,
	alloc_bytes:  int,
	alloc_count:  int,
}

Active_Zone :: struct {
	entry_idx:         int,
	start_cycle:       u64,
	child_cycles:      u64,
	start_alloc_bytes: int,
	start_alloc_count: int,
	c_ctx:             Tracy_C_Zone_Ctx,
}

Profiler_State :: struct {
	entries:            [32]Zone_Entry,
	entry_count:        int,
	stack:              [32]Active_Zone,
	stack_depth:        int,
	frames_marked:      int,
	total_frame_cycles: u64,
	backing:            runtime.Allocator,
	total_alloc_bytes:  int,
	total_alloc_count:  int,
}

Zone_Scope :: struct {
	prof:      ^Profiler_State,
	stack_pos: int,
}

g_prof: Profiler_State

prof_reset :: proc(prof: ^Profiler_State = nil) {

	p := prof != nil ? prof : &g_prof
	p.entry_count = 0
	p.stack_depth = 0
	p.frames_marked = 0
	p.total_frame_cycles = 0
	p.total_alloc_bytes = 0
	p.total_alloc_count = 0
}

prof_find_or_add_entry :: proc(prof: ^Profiler_State, name: string) -> int {

	for i in 0 ..< prof.entry_count {
		if prof.entries[i].name == name do return i
	}
	if prof.entry_count < len(prof.entries) {
		idx := prof.entry_count
		prof.entries[idx] = Zone_Entry{name = name}
		prof.entry_count += 1
		return idx
	}
	return 0
}

/*
prof_allocator_proc wraps prof.backing so every heap allocation inside an
active zone bumps total_alloc_bytes and total_alloc_count. When prof_zone_end
pops a zone, subtracting start_alloc_bytes from total_alloc_bytes attributes
exact allocation churn to whichever procedure triggered it.
*/
prof_allocator_proc :: proc(
	allocator_data: rawptr,
	mode: runtime.Allocator_Mode,
	size, alignment: int,
	old_memory: rawptr,
	old_size: int,
	location := #caller_location,
) -> ([]byte, runtime.Allocator_Error) {

	prof := (^Profiler_State)(allocator_data)
	res, err := prof.backing.procedure(prof.backing.data, mode, size, alignment, old_memory, old_size, location)
	#partial switch mode {
	case .Alloc, .Alloc_Non_Zeroed, .Resize:
		if err == nil && size > 0 {
			prof.total_alloc_bytes += size
			prof.total_alloc_count += 1
			when TRACY_ENABLE {
				if raw_data(res) != nil {
					___tracy_emit_memory_alloc_named(raw_data(res), uint(size), 0, "FrameHeap")
				}
			}
		}
	case .Free:
		when TRACY_ENABLE {
			if old_memory != nil {
				___tracy_emit_memory_free_named(old_memory, 0, "FrameHeap")
			}
		}
	}
	return res, err
}

prof_allocator :: proc(prof: ^Profiler_State = nil) -> runtime.Allocator {

	p := prof != nil ? prof : &g_prof
	return runtime.Allocator{procedure = prof_allocator_proc, data = p}
}

prof_summary_header :: proc(prof: ^Profiler_State = nil) {

	p := prof != nil ? prof : &g_prof
	now_cycle := intrinsics.read_cycle_counter()
	fmt.printfln("Profiler ready: zones=%d, frames=%d, total_cycles=%d, clock=%d",
		p.entry_count, p.frames_marked, p.total_frame_cycles, now_cycle)
}

/*
Why subtract child_cycles from elapsed when a parent zone exits?

    Suppose "Frame" runs for 100,000 cycles and calls "transform_records"
    which takes 94,000 cycles. Without subtracting child time, both zones look
    almost equally expensive. Subtracting child_cycles leaves "Frame" at
    6,000 self cycles and reveals "transform_records" as the 94% hotspot!
*/

// Implement prof_zone_begin below:
// prof_zone_begin :: proc(name: string, prof: ^Profiler_State = nil, loc: runtime.Source_Code_Location = #caller_location) -> Zone_Scope
// Resolve p := prof != nil ? prof : &g_prof. Guard if p.stack_depth >= len(p.stack)
// by returning Zone_Scope{stack_pos = -1}. Find/add entry_idx := prof_find_or_add_entry(p, name),
// claim pos := p.stack_depth and increment p.stack_depth += 1, and fill p.stack[pos]
// with entry_idx, start_cycle = u64(intrinsics.read_cycle_counter()), child_cycles = 0,
// start_alloc_bytes = p.total_alloc_bytes, and start_alloc_count = p.total_alloc_count.
// Under when TRACY_ENABLE, emit ___tracy_emit_zone_begin using a persistent
// Tracy_Source_Location_Data table entry, then return Zone_Scope{prof = p, stack_pos = pos}.


// Implement prof_zone_end below:
// prof_zone_end :: proc(scope: Zone_Scope)
// Capture end_cycle := u64(intrinsics.read_cycle_counter()) first so lookup work
// does not pollute the zone measurement. Guard nil/negative stack_pos, decrement
// scope.prof.stack_depth -= 1, compute elapsed := end_cycle - active.start_cycle
// and self_delta := elapsed > active.child_cycles ? elapsed - active.child_cycles : 0.
// Add elapsed into scope.prof.stack[scope.stack_pos - 1].child_cycles when
// scope.stack_pos > 0 (or into scope.prof.total_frame_cycles when stack_pos == 0).
// Accumulate calls, total_cycles, self_cycles, alloc_bytes, and alloc_count on
// scope.prof.entries[active.entry_idx], and emit ___tracy_emit_zone_end under when TRACY_ENABLE.


// Wrap both in an @(deferred_out = prof_zone_end) entry procedure:
// @(deferred_out = prof_zone_end)
// prof_zone :: proc(name: string, prof: ^Profiler_State = nil, loc: runtime.Source_Code_Location = #caller_location) -> Zone_Scope
// Return prof_zone_begin(name, prof, loc).


// Implement frame marking and ranked reporting below:
// prof_frame_mark :: proc(prof: ^Profiler_State = nil, name: cstring = nil)
// Increment p.frames_marked += 1 and call ___tracy_emit_frame_mark(name) under when TRACY_ENABLE.
//
// Add import "core:slice" at the top of this file and write:
// prof_print_table :: proc(prof: ^Profiler_State = nil)
// Sort p.entries[:p.entry_count] descending by self_cycles with slice.sort_by,
// then print each zone's name, calls, self_cycles, share of total_frame_cycles,
// total_cycles, alloc_count, and alloc_bytes.
