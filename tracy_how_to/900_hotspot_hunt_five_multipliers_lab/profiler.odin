// 900_hotspot_hunt_five_multipliers_lab/profiler.odin
// Run this Lab from the workspace folder via: odin run 900_hotspot_hunt_five_multipliers_lab

package main

import "base:intrinsics"
import "base:runtime"

/*
Why rank functions by Self Cycles instead of Total Cycles?
When Outer calls Inner, Outer's inclusive time (Total Cycles) swallows every
cycle spent inside Inner. If Outer is just a thin frame wrapper around one
slow helper, sorting by Total Cycles blames Outer at the top of the report.

    Suppose SimFrame starts at cycle 1,000, calls step_entity_kinematics
    for 90,000 cycles, and finishes at cycle 95,000.
    SimFrame's Total Cycles = 94,000, child_cycles = 90,000, so:
        self_cycles = elapsed - child_cycles = 4,000 cycles
        parent.child_cycles += elapsed (propagated up when a child exits)

Sorting descending by self_cycles exposes the leaf bottleneck immediately and
proves which cold systems (< 1% of frame cycles) should be left alone.

Two systems inside this Scaffold protect your measurements from corrupting
themselves:
- Wrapping context.allocator with profiler_allocator(&prof) intercepts every
  Alloc, Resize, and Free inside your zones so you catch per-frame heap churn.
- When TRACY_ENABLE is true (-define:TRACY_ENABLE=true), Tracy's background
  telemetry thread reads ^Tracy_Source_Location_Data pointers asynchronously
  after zone_enter returns. Storing those structs and their cstring bytes in a
  fixed non-wrapping Srcloc_Slot table inside Profiler guarantees zero heap
  allocations, zero overwrites, and zero dangling temp_allocator pointers.
*/

TRACY_ENABLE :: #config(TRACY_ENABLE, false)
MAX_ZONE_STATS :: 32
MAX_ZONE_STACK :: 16
MAX_SRCLOCS :: 32

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
		___tracy_emit_zone_begin        :: proc "c" (srcloc: ^Tracy_Source_Location_Data, active: i32) -> Tracy_C_Zone_Ctx ---
		___tracy_emit_zone_end          :: proc "c" (ctx: Tracy_C_Zone_Ctx) ---
		___tracy_emit_frame_mark        :: proc "c" (name: cstring) ---
		___tracy_emit_memory_alloc_named :: proc "c" (ptr: rawptr, size: uint, secure: i32, name: cstring) ---
		___tracy_emit_memory_free_named :: proc "c" (ptr: rawptr, secure: i32, name: cstring) ---
	}
}

Zone_Stat :: struct {
	name:         string,
	calls:        u64,
	total_cycles: u64,
	self_cycles:  u64,
	items_total:  u64,
	alloc_bytes:  u64,
	alloc_calls:  u64,
}

Active_Frame :: struct {
	stat_index:       int,
	start_cycle:      u64,
	child_cycles:     u64,
	items:            u64,
	alloc_bytes_base: u64,
	alloc_calls_base: u64,
}

Zone_Scope :: struct {
	prof:      ^Profiler,
	stack_pos: int,
	c_ctx:     Tracy_C_Zone_Ctx,
}

Srcloc_Slot :: struct {
	data:     Tracy_Source_Location_Data,
	key_name: string,
	key_file: string,
	key_line: i32,
	name_buf: [64]u8,
	func_buf: [96]u8,
	file_buf: [192]u8,
}

Profiler :: struct {
	stats:             [MAX_ZONE_STATS]Zone_Stat,
	stat_count:        int,
	stack:             [MAX_ZONE_STACK]Active_Frame,
	stack_depth:       int,
	srclocs:           [MAX_SRCLOCS]Srcloc_Slot,
	srcloc_count:      int,
	total_frame_calls: int,
	last_frame_cycle:  u64,
	alloc_bytes_now:   u64,
	alloc_calls_now:   u64,
	backing_alloc:     runtime.Allocator,
}

profiler_init :: proc(p: ^Profiler, backing: runtime.Allocator) {

	p^ = Profiler {
		backing_alloc    = backing,
		last_frame_cycle = u64(intrinsics.read_cycle_counter()),
	}
}

copy_cstr_into_buf :: proc(buf: []u8, s: string) -> cstring {

	if len(buf) == 0 do return nil
	n := min(len(s), len(buf) - 1)
	for i in 0..<n {
		buf[i] = s[i]
	}
	buf[n] = 0
	return cstring(&buf[0])
}

register_srcloc :: proc(
	p: ^Profiler,
	name: string,
	loc: runtime.Source_Code_Location = #caller_location,
	color: u32 = 0,
) -> ^Tracy_Source_Location_Data {

	for i in 0..<p.srcloc_count {
		slot := &p.srclocs[i]
		if slot.key_name == name && slot.key_line == loc.line && slot.key_file == loc.file_path {
			return &slot.data
		}
	}
	if p.srcloc_count >= MAX_SRCLOCS {
		return nil
	}
	idx := p.srcloc_count
	p.srcloc_count += 1
	slot := &p.srclocs[idx]
	slot.key_name = name
	slot.key_file = loc.file_path
	slot.key_line = loc.line
	slot.data = Tracy_Source_Location_Data {
		name     = copy_cstr_into_buf(slot.name_buf[:], name),
		function = copy_cstr_into_buf(slot.func_buf[:], loc.procedure),
		file     = copy_cstr_into_buf(slot.file_buf[:], loc.file_path),
		line     = u32(loc.line),
		color    = color,
	}
	return &slot.data
}

profiler_allocator_proc :: proc(
	allocator_data: rawptr,
	mode: runtime.Allocator_Mode,
	size, alignment: int,
	old_memory: rawptr,
	old_size: int,
	location := #caller_location,
) -> (data: []byte, err: runtime.Allocator_Error) {

	p := (^Profiler)(allocator_data)
	data, err = p.backing_alloc.procedure(p.backing_alloc.data, mode, size, alignment, old_memory, old_size, location)
	if err == .None {
		#partial switch mode {
		case .Alloc, .Alloc_Non_Zeroed:
			if len(data) > 0 {
				p.alloc_bytes_now += u64(len(data))
				p.alloc_calls_now += 1
				when TRACY_ENABLE {
					___tracy_emit_memory_alloc_named(raw_data(data), uint(len(data)), 0, "SimHeap")
				}
			}
		case .Resize, .Resize_Non_Zeroed:
			if len(data) > old_size {
				p.alloc_bytes_now += u64(len(data) - old_size)
				p.alloc_calls_now += 1
			}
			when TRACY_ENABLE {
				if old_memory != nil {
					___tracy_emit_memory_free_named(old_memory, 0, "SimHeap")
				}
				if len(data) > 0 {
					___tracy_emit_memory_alloc_named(raw_data(data), uint(len(data)), 0, "SimHeap")
				}
			}
		case .Free:
			when TRACY_ENABLE {
				if old_memory != nil {
					___tracy_emit_memory_free_named(old_memory, 0, "SimHeap")
				}
			}
		}
	}
	return data, err
}

profiler_allocator :: proc(p: ^Profiler) -> runtime.Allocator {

	return runtime.Allocator{procedure = profiler_allocator_proc, data = p}
}

find_or_add_stat :: proc(p: ^Profiler, name: string) -> int {

	for i in 0..<p.stat_count {
		if p.stats[i].name == name {
			return i
		}
	}
	if p.stat_count < MAX_ZONE_STATS {
		idx := p.stat_count
		p.stat_count += 1
		p.stats[idx] = Zone_Stat{name = name}
		return idx
	}
	return -1
}

frame_mark :: proc(p: ^Profiler) {

	p.total_frame_calls += 1
	p.last_frame_cycle = u64(intrinsics.read_cycle_counter())
	when TRACY_ENABLE {
		___tracy_emit_frame_mark(nil)
	}
}

/*
Wait on writing report output until zone enter and exit actually record nested
frames. Implement the three procedures below in this file so callers can open
automatic RAII zones with @(deferred_out = zone_exit). Remember that
@(deferred_out = fn) tells Odin to invoke fn(returned_value) automatically at
the end of the caller's lexical scope, removing manual defer boilerplate.
*/

// Implement zone_exit :: proc(scope: Zone_Scope)
// Read end_cycle := u64(intrinsics.read_cycle_counter()) right at entry, and
// guard p := scope.prof; if p == nil || scope.stack_pos < 0 || p.stack_depth <= 0 do return.
// Pop p.stack_depth -= 1, load frame := p.stack[p.stack_depth], and compute
// elapsed := end_cycle - frame.start_cycle alongside
// self := elapsed > frame.child_cycles ? elapsed - frame.child_cycles : 0.
// Add 1 to stat.calls, elapsed to stat.total_cycles, self to stat.self_cycles,
// frame.items to stat.items_total, (p.alloc_bytes_now - frame.alloc_bytes_base)
// to stat.alloc_bytes, and (p.alloc_calls_now - frame.alloc_calls_base) to
// stat.alloc_calls on stat := &p.stats[frame.stat_index].
// Whenever p.stack_depth > 0, add elapsed into p.stack[p.stack_depth - 1].child_cycles,
// and inside when TRACY_ENABLE call ___tracy_emit_zone_end(scope.c_ctx).


// Implement @(deferred_out = zone_exit) zone_enter :: proc(p: ^Profiler, name: string, items: u64 = 0, loc: runtime.Source_Code_Location = #caller_location) -> Zone_Scope
// Resolve stat_idx := find_or_add_stat(p, name) and guard against stat_idx < 0
// or p.stack_depth >= MAX_ZONE_STACK by returning Zone_Scope{prof = p, stack_pos = -1}.
// Otherwise claim pos := p.stack_depth, increment p.stack_depth += 1, and push
// Active_Frame{stat_index = stat_idx, start_cycle = u64(intrinsics.read_cycle_counter()), items = items, alloc_bytes_base = p.alloc_bytes_now, alloc_calls_base = p.alloc_calls_now}.
// Under when TRACY_ENABLE, call srcloc := register_srcloc(p, name, loc) and if
// srcloc != nil set c_ctx = ___tracy_emit_zone_begin(srcloc, 1). Return
// Zone_Scope{prof = p, stack_pos = pos, c_ctx = c_ctx}.


// Implement print_hotspot_report :: proc(p: ^Profiler, label: string)
// Add import "core:fmt" and import "core:slice" at the top of profiler.odin,
// copy p.stats[:p.stat_count] into a local sorted: [MAX_ZONE_STATS]Zone_Stat,
// sort sorted[:p.stat_count] descending by self_cycles via slice.sort_by,
// sum total_self across all entries, and print a ranked table showing
// Name | Calls | Self Cycles | Self % | Total Cycles | Cycles/Item | Heap B (Allocs).
