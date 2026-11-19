// Lab 599 module: four-stage pipeline workload with one allocating hotspot

package main

import "core:fmt"

/*
This file models a four-stage processing pipeline. Three stages are cold
setup or checksum steps (parse_header_cold, build_lookup_cold, and
verify_checksum_cold). One stage (transform_records_hotspot) looks ordinary
at a glance yet allocates a formatted string and temporary slice on the heap
for every single record inside its loop.

Follow the Hotspot-First workflow: instrument all four baseline stages with
prof_zone(#procedure), measure first, and replace only the proven hotspot
while leaving the three cold procedures completely untouched.
*/

Record :: struct {
	id:     u32,
	x, y:   f32,
	vx, vy: f32,
	weight: f32,
}

Pipeline_Data :: struct {
	header_magic: u32,
	records:      []Record,
	lookup:       [16]f32,
	scratch_out:  []f32,
	checksum:     f64,
}

// Once prof_zone is implemented in tracy_prof.odin, place prof_zone(#procedure)
// as the first statement inside each of the four baseline procedures below so
// your profile isolates self_cycles and alloc_bytes per stage.

parse_header_cold :: proc(data: ^Pipeline_Data) {

	if data == nil || len(data.records) == 0 do return
	data.header_magic = 0x4F44_494E
}

build_lookup_cold :: proc(data: ^Pipeline_Data) {

	if data == nil do return
	for i in 0 ..< 16 {
		data.lookup[i] = 1.0 + f32(i) * 0.0625
	}
}

transform_records_hotspot :: proc(data: ^Pipeline_Data) {

	if data == nil do return
	n := min(len(data.records), len(data.scratch_out))
	for i in 0 ..< n {
		rec := data.records[i]
		tag := fmt.aprintf("rec-%d", rec.id)
		tmp := make([]f32, 4)
		tmp[0] = rec.x + rec.vx * 0.016
		tmp[1] = rec.y + rec.vy * 0.016
		scale := data.lookup[rec.id & 15]
		tmp[2] = (tmp[0] * tmp[0] + tmp[1] * tmp[1]) * scale * rec.weight
		if len(tag) > 0 {
			data.scratch_out[i] = tmp[2]
		}
		delete(tmp)
		delete(tag)
	}
}

verify_checksum_cold :: proc(data: ^Pipeline_Data) {

	if data == nil do return
	sum: f64 = 0
	for val in data.scratch_out {
		sum += f64(val)
	}
	data.checksum = sum
}

// After profiling confirms transform_records_hotspot dominates both self_cycles
// and alloc_bytes, write the allocation-free replacement below:
// transform_records_optimized :: proc(data: ^Pipeline_Data)
// Guard if data == nil do return, add prof_zone(#procedure) at the top, compute
// n := min(len(data.records), len(data.scratch_out)), and use #no_bounds_check
// with plain stack locals (px, py, scale) to write the exact same formula into
// data.scratch_out[i] with zero heap allocations.
