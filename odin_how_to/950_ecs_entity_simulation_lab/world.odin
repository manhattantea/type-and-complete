// Generational entity registry and SOA world layout for 950_ecs_entity_simulation_lab.

package main

/*
An Entity Component System (ECS) separates identity, component membership, and
raw component arrays so simulation loops touch only the memory they need. This
file defines the shared World contract combining three idiomatic Odin patterns:

Generational handles (Entity_Handle with idx and gen):
Reusing freed integer indices without a generation counter causes silent
dangling-reference bugs. Suppose entity #4 is an enemy goblin at slot 4 with
generation 0, and a turret stores handle {idx = 4, gen = 0}. When the goblin
dies and a health potion later spawns into recycled slot 4, the world bumps
generations[4] from 0 to 1. Any system still holding {idx = 4, gen = 0} checks
is_alive(&w, old_handle) and sees generations[4] (1) != old_handle.gen (0), so
the turret drops the stale target immediately instead of shooting the potion.

Bit-set component masks (bit_set[Component_Flag; u8]):
When we write bit_set[Component_Flag; u8], it means Odin packs every flag in
Component_Flag into one bit of a single byte. Testing whether an entity has both
Position and Velocity uses the subset operator '{.Position, .Velocity} <= w.masks[i]',
which compiles down to a single bitwise AND and compare rather than chasing booleans.

Structure of Arrays (#soa[MAX_ENTITIES]Vec2):
In a normal array of structs ([64]Vec2), x and y floats alternate in memory as
x0, y0, x1, y1. Putting '#soa' in front of [MAX_ENTITIES]Vec2 tells Odin to
lay out positions.x as a contiguous [64]f32 array followed by positions.y as a
separate contiguous [64]f32 array, which lets SIMD systems load 4 x coordinates
straight into a hardware register without shuffling around y values.
*/

MAX_ENTITIES :: 64

Vec2 :: struct {
	x, y: f32,
}

Entity_Handle :: struct {
	idx: u32,
	gen: u32,
}

Component_Flag :: enum {
	Position,
	Velocity,
	Health,
	AI,
}

Component_Mask :: bit_set[Component_Flag; u8]

World :: struct {
	positions:    #soa[MAX_ENTITIES]Vec2,
	velocities:   #soa[MAX_ENTITIES]Vec2,
	health:       [MAX_ENTITIES]i32,
	masks:        [MAX_ENTITIES]Component_Mask,
	generations:  [MAX_ENTITIES]u32,
	alive:        [MAX_ENTITIES]bool,
	active_count: int,
}

/*
is_alive guards against out-of-range indices first, then confirms both that the
slot is currently occupied and that its generation counter still matches the
handle. That single equality check is what catches stale handles after a slot
has been recycled.
*/

is_alive :: proc(w: ^World, h: Entity_Handle) -> bool {

	if int(h.idx) >= MAX_ENTITIES {
		return false
	}
	return w.alive[h.idx] && w.generations[h.idx] == h.gen
}

// Write spawn_entity :: proc(w: ^World, mask: Component_Mask) -> (handle: Entity_Handle, ok: bool)
// Scan i across 0..<MAX_ENTITIES looking for the first slot where !w.alive[i].
// When a free slot is found, mark w.alive[i] = true, store w.masks[i] = mask,
// zero-initialize w.positions[i] = {} and w.velocities[i] = {}, set
// w.health[i] = 100 when .Health in mask (else 0), increment w.active_count += 1,
// and return Entity_Handle{idx = u32(i), gen = w.generations[i]}, true.
// If every slot up to MAX_ENTITIES is occupied, return Entity_Handle{}, false.


// Write despawn_entity :: proc(w: ^World, h: Entity_Handle) -> bool
// First guard against stale or invalid handles with if !is_alive(w, h) do return false.
// Otherwise mark w.alive[h.idx] = false, clear w.masks[h.idx] = {}, bump
// w.generations[h.idx] += 1 so any surviving copy of h fails future is_alive
// checks, decrement w.active_count -= 1, and return true.
