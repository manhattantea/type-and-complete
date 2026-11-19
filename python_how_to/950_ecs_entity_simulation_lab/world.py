# Module for 950_ecs_entity_simulation_lab (run via: python 950_ecs_entity_simulation_lab/main.py)

# Data-Oriented ECS World and Generational Handles (world.py).
#
# In classic object-oriented Python, representing 1,000 game entities as
# class Entity instances allocates 1,000 PyObject headers, 1,000 per-instance
# __dict__ hash tables, and thousands of boxed float objects scattered across
# the heap. Every update loop has to chase pointers from object to dict to
# float, thrashing the CPU cache.
#
# Structure-of-Arrays (SoA) flips that memory layout on its side. Instead of a
# list of entity objects, World stores one flat array.array("f") column per
# numeric component (x, y, vx, vy, health). Each array.array("f") packs raw
# 32-bit C floats back to back at 4 bytes per slot with zero per-element
# PyObject header overhead.
#
# Three standard-library tools shape the shared contracts below:
# - enum.IntFlag defines bit flags that combine with bitwise OR (|), such as
#   ComponentFlag.POSITION | ComponentFlag.VELOCITY, so one integer bitmask
#   tracks every component active on a slot.
# - @dataclass(slots=True, frozen=True) removes __dict__ from EntityHandle and
#   makes handles immutable so a caller cannot accidentally rewrite idx or gen.
# - field(default_factory=...) creates a fresh list or array for every World
#   instance instead of sharing one mutable container across all instances.
#
# Why generational handles prevent silent use-after-free bugs:
#
#     Suppose entity slot 3 starts with generations[3] == 1 and receives
#     old_handle = EntityHandle(idx=3, gen=1).
#     When slot 3 dies, despawn_entity clears masks[3] = ComponentFlag.NONE,
#     bumps generations[3] from 1 to 2, and pushes 3 back onto free_slots.
#     Next, a brand-new projectile calls spawn_entity and recycles slot 3,
#     receiving new_handle = EntityHandle(idx=3, gen=2).
#     If a homing missile still held old_handle, checking is_alive(old_handle)
#     sees old_handle.gen (1) != generations[3] (2) and rejects it in O(1)
#     instead of damaging the newly spawned projectile.

import array
from dataclasses import dataclass, field
from enum import IntFlag

MAX_ENTITIES: int = 64


class ComponentFlag(IntFlag):
    NONE = 0
    POSITION = 1 << 0
    VELOCITY = 1 << 1
    HEALTH = 1 << 2


@dataclass(slots=True, frozen=True)
class EntityHandle:
    idx: int
    gen: int


@dataclass(slots=True)
class World:
    masks: list[ComponentFlag] = field(
        default_factory=lambda: [ComponentFlag.NONE] * MAX_ENTITIES
    )
    generations: list[int] = field(
        default_factory=lambda: [1] * MAX_ENTITIES
    )
    # Filling free_slots in reverse order means free_slots.pop() hands out
    # indices 0, 1, 2, ... in ascending order in O(1) time from the tail.
    free_slots: list[int] = field(
        default_factory=lambda: list(range(MAX_ENTITIES - 1, -1, -1))
    )
    x: array.array = field(default_factory=lambda: array.array("f", [0.0]) * MAX_ENTITIES)
    y: array.array = field(default_factory=lambda: array.array("f", [0.0]) * MAX_ENTITIES)
    vx: array.array = field(default_factory=lambda: array.array("f", [0.0]) * MAX_ENTITIES)
    vy: array.array = field(default_factory=lambda: array.array("f", [0.0]) * MAX_ENTITIES)
    health: array.array = field(default_factory=lambda: array.array("f", [0.0]) * MAX_ENTITIES)

    # Implement entity allocation right here on World:
    # define def spawn_entity(self, mask: ComponentFlag, x: float = 0.0, y: float = 0.0, vx: float = 0.0, vy: float = 0.0, health: float = 100.0) -> EntityHandle:
    # Guard against exhaustion with if not self.free_slots: raise RuntimeError("World capacity exceeded")
    # and reject empty masks with if mask == ComponentFlag.NONE: raise ValueError("Entity mask cannot be NONE").
    # Pop idx = self.free_slots.pop(), write self.masks[idx] = mask, populate
    # self.x[idx], self.y[idx], self.vx[idx], self.vy[idx], and self.health[idx],
    # and return EntityHandle(idx=idx, gen=self.generations[idx]).


    # Implement O(1) liveness validation on World:
    # define def is_alive(self, handle: EntityHandle) -> bool:
    # Return True only when all three checks hold:
    # - handle.idx is inside bounds: 0 <= handle.idx < MAX_ENTITIES
    # - the slot has active components: self.masks[handle.idx] != ComponentFlag.NONE
    # - the slot generation matches: self.generations[handle.idx] == handle.gen


    # Implement generational despawning and slot recycling on World:
    # define def despawn_entity(self, handle: EntityHandle) -> bool:
    # Start with if not self.is_alive(handle): return False so stale or
    # already-despawned handles can never corrupt generations or push duplicate
    # indices onto free_slots.
    # Otherwise clear self.masks[handle.idx] = ComponentFlag.NONE, increment
    # self.generations[handle.idx] += 1 to invalidate every existing handle to
    # that slot, push handle.idx onto self.free_slots with append, and return True.
