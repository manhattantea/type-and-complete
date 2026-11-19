// 900_hotspot_hunt_five_multipliers_lab/simulation.odin
// Multi-system simulation contracts, cold systems, baseline bottlenecks, and optimization Drills.

package main

import "core:fmt"

/*
In real programs, roughly 95% of procedures are cold and take less than 1% of
total runtime. Optimizing a cold function wastes effort and hurts clarity, so
your job in this Lab is to measure all five simulation systems first and touch
only the two proven bottlenecks:

- load_world_config, build_spatial_tags, and audit_frame_checksum are cold
  verification and setup procedures. Leave all three untouched.
- step_entity_kinematics (Hotspot A) pairs Multiplier #1 (allocating a heap
  string inside the inner loop on every entity) with Multiplier #4 (a 128-byte
  Entity_AoS struct where 28 cold floats occupy most of every 64-byte cache
  line, forcing the CPU to fetch two cache lines per entity just to read x, y,
  vx, and vy).
- evaluate_sensor_polynomials (Hotspot B) pairs Multiplier #2 (one serial
  total += y floating-point dependency chain stalling CPU execution ports)
  with Multiplier #3 (scalar multiplies instead of Horner's Rule fused
  multiply-adds across 4-wide #simd[4]f32 lanes).

Notice what #soa[]Entity_SoA means when declared on Sim_World: Odin flips the
memory layout from [x,y,vx,vy, x,y,vx,vy, ...] to four separate contiguous
arrays [x0,x1,...], [y0,y1,...], [vx0,vx1,...], [vy0,vy1,...]. Suppose you
step 2,048 entities: each 64-byte cache line now carries 16 consecutive x
values with zero cold padding.
*/

ENTITY_COUNT :: 2048
SENSOR_COUNT :: 4096

Entity_AoS :: struct {
	x, y:       f32,
	vx, vy:     f32,
	tag_buffer: [28]f32,
}

Entity_SoA :: struct {
	x, y:   f32,
	vx, vy: f32,
}

Sim_World :: struct {
	aos_entities: []Entity_AoS,
	soa_entities: #soa[]Entity_SoA,
	sensor_x:     []f32,
	sensor_out:   []f32,
	config_scale: f32,
	tag_sum:      u64,
}

init_sim_world :: proc(w: ^Sim_World) {

	w.aos_entities = make([]Entity_AoS, ENTITY_COUNT)
	w.soa_entities = make(#soa[]Entity_SoA, ENTITY_COUNT)
	w.sensor_x = make([]f32, SENSOR_COUNT)
	w.sensor_out = make([]f32, SENSOR_COUNT)
	reset_sim_world(w)
}

reset_sim_world :: proc(w: ^Sim_World) {

	w.config_scale = 1.0
	w.tag_sum = 0
	for i in 0..<ENTITY_COUNT {
		px := f32((i % 97) + 1) * 0.25
		py := f32((i % 53) + 1) * 0.5
		vx := f32((i % 17) - 8) * 0.75
		vy := f32((i % 13) - 6) * 0.5
		w.aos_entities[i] = Entity_AoS{x = px, y = py, vx = vx, vy = vy}
		w.soa_entities[i] = Entity_SoA{x = px, y = py, vx = vx, vy = vy}
	}
	for i in 0..<SENSOR_COUNT {
		w.sensor_x[i] = f32(i % 256) * 0.01
		w.sensor_out[i] = 0.0
	}
}

destroy_sim_world :: proc(w: ^Sim_World) {

	delete(w.aos_entities)
	delete_soa(w.soa_entities)
	delete(w.sensor_x)
	delete(w.sensor_out)
}

// Cold system #1 (<1% of frame cycles) — leave untouched.
load_world_config :: proc(w: ^Sim_World) {

	w.config_scale = 1.025
}

// Cold system #2 (<1% of frame cycles) — leave untouched.
build_spatial_tags :: proc(w: ^Sim_World) {

	acc: u64 = 0
	for i in 0..<16 {
		acc += u64(i * 7 + 3)
	}
	w.tag_sum = acc
}

// Baseline Hotspot A: Multiplier #1 (per-entity heap alloc waste) + Multiplier #4 (128-byte AoS cache waste).
step_entity_kinematics :: proc(w: ^Sim_World, dt: f32) {

	scale := w.config_scale
	for i in 0..<len(w.aos_entities) {
		e := &w.aos_entities[i]
		label := fmt.aprintf("e_%d", i)
		if len(label) > 0 {
			e.x += e.vx * dt * scale
			e.y += e.vy * dt * scale
		}
		delete(label)
	}
}

// Baseline Hotspot B: Multiplier #2 (serial total dependency chain) + Multiplier #3 (scalar polynomial).
evaluate_sensor_polynomials :: proc(w: ^Sim_World) -> f32 {

	c0: f32 = 1.25
	c1: f32 = 0.50
	c2: f32 = -0.125
	c3: f32 = 0.0625

	total: f32 = 0.0
	for i in 0..<len(w.sensor_x) {
		x := w.sensor_x[i]
		x2 := x * x
		x3 := x2 * x
		y := c0 + c1 * x + c2 * x2 + c3 * x3
		w.sensor_out[i] = y
		total += y
	}
	return total
}

// Cold system #3 (<1% of frame cycles) — full-state parity checksum across every entity and sensor output.
audit_frame_checksum :: proc(w: ^Sim_World, use_soa: bool, sensor_sum: f32) -> f32 {

	pos_sum: f32 = 0.0
	if use_soa {
		for i in 0..<ENTITY_COUNT {
			pos_sum += w.soa_entities.x[i] + w.soa_entities.y[i] + w.soa_entities.vx[i] + w.soa_entities.vy[i]
		}
	} else {
		for i in 0..<ENTITY_COUNT {
			e := &w.aos_entities[i]
			pos_sum += e.x + e.y + e.vx + e.vy
		}
	}
	out_sum: f32 = 0.0
	for i in 0..<SENSOR_COUNT {
		out_sum += w.sensor_out[i]
	}
	return pos_sum + out_sum + sensor_sum + f32(w.tag_sum) + w.config_scale
}

/*
Once your Profiler in profiler.odin implements zone_enter and zone_exit, wire
prof: ^Profiler into all five simulation procedures above by adding
zone_enter(prof, "<proc_name>", <item_count>) at the top of each body.
Calling zone_enter without assigning its result triggers @(deferred_out = zone_exit)
automatically at scope exit with zero _ = silencers.

Then implement the two optimized hotspot replacements below without modifying
load_world_config, build_spatial_tags, or audit_frame_checksum.

When writing the fast sensor pass, #no_bounds_check removes per-iteration array
bounds branches inside a verified loop, #simd[4]f32 packs four 32-bit floats
into one 128-bit vector register, and simd.fma(x, acc, c) computes (x * acc) + c
in one instruction (see odin_how_to/700 and 710 for raw #soa/#simd mechanics).
*/

// Define step_entity_kinematics_fast :: proc(prof: ^Profiler, w: ^Sim_World, dt: f32)
// Start with zone_enter(prof, "step_entity_kinematics_fast", ENTITY_COUNT),
// compute dt_scale := dt * w.config_scale, and loop over 0..<ENTITY_COUNT with
// #no_bounds_check updating w.soa_entities.x[i] += w.soa_entities.vx[i] * dt_scale
// and w.soa_entities.y[i] += w.soa_entities.vy[i] * dt_scale with 0 heap allocations.


// Define evaluate_sensor_polynomials_fast :: proc(prof: ^Profiler, w: ^Sim_World) -> f32
// Add import "core:simd" at the top of simulation.odin and start with
// zone_enter(prof, "evaluate_sensor_polynomials_fast", SENSOR_COUNT).
// Rewrite c0 + c1*x + c2*x^2 + c3*x^3 via Horner's Rule c0 + x*(c1 + x*(c2 + x*c3))
// using three simd.fma calls on #simd[4]f32 vector loads, unroll across two
// independent vector accumulators acc0, acc1: #simd[4]f32 stepping i += 8 under
// #no_bounds_check to break the serial dependency chain, store each vector back
// into w.sensor_out[i:], handle any tail elements, and return
// simd.reduce_add_ordered(acc0 + acc1).
