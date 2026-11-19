# python 950_ecs_entity_simulation_lab/main.py

# Data-Oriented ECS Entity Simulation Lab (main.py).
#
# This multi-file Lab parallels odin_how_to/950_ecs_entity_simulation_lab and
# wires together three layers:
# - world.py: flat Structure-of-Arrays array.array("f") component columns,
#   ComponentFlag bitmasks, and generational EntityHandle(idx, gen) handles.
# - systems.py: stateless movement_system and damage_system loops filtering
#   slots with full bitmask subset tests.
# - main.py: spawning mixed entity archetypes, stepping fixed-dt simulation
#   ticks, and proving that recycled slots reject stale handles.

from systems import HEALTH_MASK, MOVE_MASK
from world import MAX_ENTITIES, World


def run_ecs_simulation() -> None:

    # Allocate the fixed-capacity SoA World and confirm its baseline storage
    # layout before implementing the methods in world.py and systems.py.
    world = World()
    print(
        f"World ready: capacity={MAX_ENTITIES}, free_slots={len(world.free_slots)}, "
        f"float_bytes={world.x.itemsize}, move_mask={int(MOVE_MASK)}, health_mask={int(HEALTH_MASK)}"
    )

    # Once world.py and systems.py are implemented, expand the imports at the
    # top of this file to bring in movement_system and damage_system from
    # systems, plus ComponentFlag and EntityHandle from world.

    # Spawn 16 entities into handles: list[EntityHandle] = [] across three
    # distinct component archetypes so bitmask filtering actually matters:
    # - Indices 0..5: ComponentFlag.POSITION | ComponentFlag.VELOCITY | ComponentFlag.HEALTH
    #   with position (i * 5.0, i * 3.0), velocity (20.0, 15.0), and staggered
    #   health = 40.0 + i * 20.0 so the earliest slots die mid-simulation.
    # - Indices 6..10: ComponentFlag.POSITION | ComponentFlag.VELOCITY
    #   with position (i * 5.0, i * 3.0) and velocity (20.0, 15.0) (immortal
    #   movers that damage_system must ignore).
    # - Indices 11..15: ComponentFlag.POSITION | ComponentFlag.HEALTH
    #   with position (i * 5.0, i * 3.0) and health = 150.0 (stationary targets
    #   that movement_system must ignore).


    # Step 10 deterministic simulation ticks at dt = 0.1 with poison_dmg = 12.0:
    # Track dead_handles: list[EntityHandle] = [] across the loop.
    # On each tick call movement_system(world, dt=0.1) and extend dead_handles
    # with damage_system(world, poison_dmg=12.0).
    # After 10 ticks (120.0 total poison damage), verify every handle h in
    # dead_handles reports world.is_alive(h) is False, and assert that a
    # stationary target (for example handles[11]) still sits at its original
    # (11 * 5.0, 11 * 3.0) coordinates.


    # Prove generational slot recycling prevents use-after-free aliasing:
    # When dead_handles is non-empty, spawn a new entity into a recycled slot:
    #     reborn = world.spawn_entity(ComponentFlag.POSITION | ComponentFlag.HEALTH, x=50.0, y=50.0, health=200.0)
    # Locate the matching stale handle from dead_handles whose idx == reborn.idx.
    # Verify reborn.gen > stale.gen, assert world.is_alive(reborn) is True,
    # assert world.is_alive(stale) is False, and verify a second call to
    # world.despawn_entity(stale) returns False without harming reborn.
    # Finally, print each surviving live slot's idx, gen, (x, y), and health.


def main() -> None:

    print("=== 950: Data-Oriented ECS Entity Simulation Lab ===")
    run_ecs_simulation()


if __name__ == "__main__":
    main()
