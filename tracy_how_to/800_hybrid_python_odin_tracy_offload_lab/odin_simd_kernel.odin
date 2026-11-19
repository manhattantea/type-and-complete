// odin run 800_hybrid_python_odin_tracy_offload_lab/odin_simd_kernel.odin -file

package main

import "base:intrinsics"
import "core:fmt"
import "core:simd"

/*
When a profiler proves that 95%+ of a Python application's frame time sits
inside one tight numerical loop, you do not need to rewrite the whole program.
Keep high-level orchestration in Python over contiguous array("f") buffers,
and export ONE focused C-ABI kernel from Odin using @(export) and proc "c".

Why proc "c"? Standard Odin procedures silently pass Odin's implicit context
pointer (allocators, logger, temp_allocator). A C caller such as Python ctypes
knows nothing about Odin's context, so exported DLL entry points use proc "c"
with zero context overhead—which fits pure SIMD math cleanly. (If an exported
proc "c" ever needs core:fmt or Odin allocators, restore
context = runtime.default_context() at the top of the procedure.)

Supported modes for this file:
- Standalone check/benchmark:
  odin check 800_hybrid_python_odin_tracy_offload_lab/odin_simd_kernel.odin -file
  odin run 800_hybrid_python_odin_tracy_offload_lab/odin_simd_kernel.odin -file -o:speed
- Shared DLL for Python ctypes:
  odin build 800_hybrid_python_odin_tracy_offload_lab/odin_simd_kernel.odin -file -build-mode:dll -o:speed -out:800_hybrid_python_odin_tracy_offload_lab/odin_simd_kernel.dll
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
		___tracy_emit_zone_value :: proc "c" (ctx: Tracy_C_Zone_Ctx, value: u64) ---
	}
}

g_simd_kernel_srcloc := Tracy_Source_Location_Data {
	name     = "odin_kernel_simd_sum_distances",
	function = "kernel_simd_sum_distances",
	file     = "odin_simd_kernel.odin",
	line     = 76,
	color    = 0x22DD88,
}

kernel_scalar_serial :: proc(x0, y0, x1, y1: [^]f32, count: i64) -> f32 {

	total: f32 = 0.0
	for i in 0..<count {
		dx := x1[i] - x0[i]
		dy := y1[i] - y0[i]
		total += dx * dx + dy * dy
	}
	return total
}

// Implement the exported C-ABI #simd[4]f32 kernel:
// @(export)
// kernel_simd_sum_distances :: proc "c" (x0, y0, x1, y1: [^]f32, count: i64) -> f32
// - Inside when TRACY_ENABLE, start a Tracy zone with
//   zctx := ___tracy_emit_zone_begin(&g_simd_kernel_srcloc, 1), tag
//   ___tracy_emit_zone_value(zctx, u64(count)), and close with
//   defer ___tracy_emit_zone_end(zctx).
// - Maintain two independent vector accumulators acc0, acc1: #simd[4]f32 so
//   superscalar ports execute 8 floats per iteration without stalling on one
//   accumulator chain.
// - Under #no_bounds_check, step i += 8 while i + 8 <= count:
//   load lanes [i:i+4] via simd.from_slice(#simd[4]f32, x0[i:i+4]) (and y0, x1, y1),
//   compute dx0 := vx1_0 - vx0_0 and dy0 := vy1_0 - vy0_0, accumulate
//   acc0 = simd.fma(dx0, dx0, acc0) and acc0 = simd.fma(dy0, dy0, acc0),
//   and do the same on lanes [i+4:i+8] into acc1.
// - Reduce horizontally via total := simd.reduce_add_ordered(acc0 + acc1),
//   finish any remaining i < count items in a scalar tail loop, and return total.


main :: proc() {

	ax0 := [4]f32{0.0, 1.0, 2.0, 3.0}
	ay0 := [4]f32{0.0, 1.0, 2.0, 3.0}
	ax1 := [4]f32{3.0, 5.0, 2.0, 6.0}
	ay1 := [4]f32{4.0, 4.0, 2.0, 7.0}

	when TRACY_ENABLE {
		zctx := ___tracy_emit_zone_begin(&g_simd_kernel_srcloc, 1)
		___tracy_emit_zone_value(zctx, 4)
		defer ___tracy_emit_zone_end(zctx)
	}

	t0 := intrinsics.read_cycle_counter()
	s_serial := kernel_scalar_serial(raw_data(ax0[:]), raw_data(ay0[:]), raw_data(ax1[:]), raw_data(ay1[:]), 4)
	t1 := intrinsics.read_cycle_counter()

	v_probe := simd.fma(#simd[4]f32{3, 4, 0, 3}, #simd[4]f32{3, 4, 0, 3}, #simd[4]f32{16, 9, 0, 16})
	fmt.printfln(
		"Hybrid Odin kernel anchor (%s, TRACY_ENABLE=%v): scalar=%.2f | probe_sum=%.2f | cycles=%d",
		g_simd_kernel_srcloc.name,
		TRACY_ENABLE,
		s_serial,
		simd.reduce_add_ordered(v_probe),
		t1 - t0,
	)

	// Measure the N-size SIMD vs scalar crossover inside Odin:
	// Test both small N = 16 and large N = 50_000 using 4 contiguous []f32
	// slices (x0, y0, x1, y1 with defer delete). Populate deterministic inputs,
	// repetition-test kernel_scalar_serial vs kernel_simd_sum_distances across
	// 64 runs taking min_cycles for each N, assert abs(res_serial - res_simd) < 1e-1,
	// and print cycles/pair and speedup for N = 16 vs N = 50_000!
}
