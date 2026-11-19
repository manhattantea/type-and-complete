// SOA and SIMD entity simulation systems for 950_ecs_entity_simulation_lab.

package main

/*
Because World.positions and World.velocities are declared as #soa[MAX_ENTITIES]Vec2,
reading w.positions.x[base:base + 4] gives a slice of four back-to-back f32
values sitting next to each other in L1 cache.

When we declare a '#simd[4]f32' vector, Odin maps it onto a 128-bit hardware
SIMD register (SSE on x86_64 or NEON on ARM64) so a single instruction adds or
multiplies four entities at once. Using 'core:simd', two idioms keep the hot
loop branchless across 4-entity chunks:

    dt_vec := #simd[4]f32{dt, dt, dt, dt}
    next_x := simd.fma(vel_x, dt_vec, pos_x)

'simd.fma' (fused multiply-add) computes vel_x * dt_vec + pos_x in one step.
Not every slot in a 4-entity chunk is guaranteed to be alive with both Position
and Velocity, so instead of branching per entity we build a '#simd[4]u32' mask
where active moving lanes hold ~u32(0) (all bits 1) and skipped lanes hold 0.

Suppose chunk 0..=3 has alive moving entities in lanes 0 and 1, a stationary
entity (no .Velocity) in lane 2, and a dead slot in lane 3. Calling:

    blended_x := simd.select(active_mask, next_x, pos_x)

picks next_x for lanes 0 and 1 and keeps the original pos_x untouched for lanes
2 and 3 in a single branchless register operation before writing the 4 floats
back to w.positions.x[base:base + 4].
*/

// Add 'import "core:simd"' at the top of this file when implementing movement_system below.
//
// Write movement_system :: proc(w: ^World, dt: f32)
// Broadcast dt into dt_vec := #simd[4]f32{dt, dt, dt, dt}.
// Step across MAX_ENTITIES in 4-entity chunks using: for base := 0; base < MAX_ENTITIES; base += 4
// Inside each chunk, build lane_mask: [4]u32 where lane_mask[lane] = ~u32(0) if
// w.alive[base + lane] && ({.Position, .Velocity} <= w.masks[base + lane]), else 0.
// Load pos_x := simd.from_slice(#simd[4]f32, w.positions.x[base:base + 4]) and
// vel_x := simd.from_slice(#simd[4]f32, w.velocities.x[base:base + 4]) (and same for y).
// Compute next_x := simd.fma(vel_x, dt_vec, pos_x) and next_y := simd.fma(vel_y, dt_vec, pos_y),
// blend with mask_vec := simd.from_array(lane_mask), calling
// simd.select(mask_vec, next_x, pos_x) and simd.select(mask_vec, next_y, pos_y),
// and copy simd.to_array(...) back into w.positions.x[base:base + 4] and w.positions.y[base:base + 4].
// Note why base += 4 is safe without a tail loop here: MAX_ENTITIES :: 64 is divisible by 4.


// Write damage_system :: proc(w: ^World)
// Loop i over 0..<MAX_ENTITIES. Whenever w.alive[i] is true, .Health in w.masks[i]
// is set, and w.health[i] <= 0, build the current handle with
// h := Entity_Handle{idx = u32(i), gen = w.generations[i]} and recycle the slot
// by calling despawn_entity(w, h).
