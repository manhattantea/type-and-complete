# python 590_arena_and_object_pool_patterns.py

from array import array
from typing import NamedTuple


class Handle(NamedTuple):

    index: int
    generation: int


def soa_contiguous_storage_and_handles() -> None:

    # Creating and destroying millions of tiny objects like Particle(x, y, vx, vy)
    # inside a hot simulation or request loop hammers Python's heap allocator
    # and garbage collector. Each normal class instance allocates a PyObject
    # header, type pointer, refcount, dynamic __dict__ hash table, plus separate
    # boxed PyFloatObject instances for each coordinate.
    #
    # Two systems patterns eliminate that churn:
    # 1. Fixed Object Pool: pre-allocate __slots__ objects once and recycle them
    #    with acquire() and release() (explored in Lab 595).
    # 2. Structure of Arrays (SoA) + Generational Handles: instead of N Particle
    #    objects, store parallel C-backed array("f") columns (x, y, vx, vy) of
    #    unboxed 4-byte IEEE-754 floats indexed by an integer slot index.
    #
    # Why pair slot index with a generation counter in Handle(index, generation)
    # instead of passing raw integer indices around?
    #
    #     Suppose slot 0 holds "Goblin" at generation 0.
    #     You despawn "Goblin", and slot 0 is immediately recycled for "Dragon".
    #     A stale reference holding raw index 0 would silently mutate or kill
    #     "Dragon"! Incrementing generations[0] from 0 to 1 on despawn lets
    #     handle.generation == pool.generations[handle.index] reject the stale
    #     "Goblin" handle in O(1) time. (Compare odin_how_to/490_pool_and_handle_allocations.odin!)

    positions = array("f", [0.0] * 4)
    starter_handle = Handle(index=0, generation=0)
    print(
        "4 unboxed C floats occupy",
        positions.buffer_info()[1] * positions.itemsize,
        "bytes | starter handle:",
        starter_handle,
    )

    # Verify the memory layout of array("f") vs a boxed list[float]:
    # create n = 1_000 floats in col = array("f", [0.0] * n) and boxed = [0.0] * n,
    # and print col.buffer_info()[1] * col.itemsize (4,000 bytes) alongside
    # sys.getsizeof(boxed) (import sys inside this function).


def generational_pool_lifecycle() -> None:

    # A fixed-capacity ParticleSoAPool manages parallel columns and a free-slot
    # stack. Initializing self.free_slots: list[int] = list(reversed(range(capacity)))
    # lets self.free_slots.pop() hand out slots 0, 1, 2, ... in O(1) time, and
    # self.alive = bytearray(capacity) tracks 1 (live) or 0 (free) in 1 byte per
    # slot without boxing booleans.
    #
    #     Suppose capacity = 4:
    #     - spawn("Goblin", ...) pops slot 0 -> returns Handle(0, 0).
    #     - despawn(Handle(0, 0)) sets alive[0] = 0, bumps generations[0] = 1,
    #       and pushes 0 back onto free_slots.
    #     - spawn("Dragon", ...) pops slot 0 -> returns Handle(0, 1).
    #     - is_alive(Handle(0, 0)) sees 0 != generations[0] and returns False!

    alive_flags = bytearray(4)
    generations = array("I", [0] * 4)
    print("Starter pool state -> alive:", list(alive_flags), "| generations:", list(generations))

    # Define class ParticleSoAPool: (either here or at module level above main)
    # with these exact methods:
    # - def __init__(self, capacity: int) -> None:
    #   store self.capacity = capacity, parallel array("f", [0.0] * capacity)
    #   columns (self.x, self.y, self.vx, self.vy), self.names: list[str] = [""] * capacity,
    #   self.generations = array("I", [0] * capacity), self.alive = bytearray(capacity),
    #   and self.free_slots: list[int] = list(reversed(range(capacity))).
    # - def spawn(self, name: str, x: float, y: float, vx: float, vy: float) -> Handle:
    #   raise RuntimeError("Pool exhausted") if not self.free_slots; otherwise
    #   pop idx = self.free_slots.pop(), fill columns, set self.alive[idx] = 1,
    #   and return Handle(idx, self.generations[idx]).
    # - def is_alive(self, handle: Handle) -> bool:
    #   return True only when 0 <= handle.index < self.capacity,
    #   self.alive[handle.index] == 1, and self.generations[handle.index] == handle.generation.
    # - def despawn(self, handle: Handle) -> bool:
    #   if not self.is_alive(handle): return False; otherwise set
    #   self.alive[handle.index] = 0, self.names[handle.index] = "",
    #   self.generations[handle.index] += 1, append handle.index to self.free_slots,
    #   and return True.


    # Instantiate pool = ParticleSoAPool(capacity=4) and test slot reuse:
    # spawn goblin = pool.spawn("Goblin", 1.0, 2.0, 0.5, 0.0), assert
    # pool.is_alive(goblin), then assert pool.despawn(goblin).
    # Next spawn dragon = pool.spawn("Dragon", 10.0, 20.0, -1.0, 0.0) and print
    # both handles to observe dragon.index == goblin.index == 0 while
    # dragon.generation == goblin.generation + 1.


    # Verify stale-handle safety and exhaustion:
    # assert not pool.is_alive(goblin), assert not pool.despawn(goblin), and
    # assert pool.is_alive(dragon). Then fill the remaining 3 slots and confirm
    # a 5th spawn raises RuntimeError inside try / except RuntimeError:.


def main() -> None:

    print("=== 1. SoA Contiguous Storage and Handles ===")
    soa_contiguous_storage_and_handles()
    print("=== 2. Generational Pool Lifecycle ===")
    generational_pool_lifecycle()


if __name__ == "__main__":
    main()
