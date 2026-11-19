# Module for 950_ecs_entity_simulation_lab (run via: python 950_ecs_entity_simulation_lab/main.py)

# ECS Simulation Systems (systems.py).
#
# In an Entity-Component-System architecture, data lives in World and behavior
# lives in stateless system functions. Each system scans the flat component
# columns from 0 to MAX_ENTITIES - 1 and touches only slots whose bitmask
# contains every required ComponentFlag bit.
#
# Watch out for the classic bitmask subset bug when filtering slots:
#
#     Suppose MOVE_MASK = ComponentFlag.POSITION | ComponentFlag.VELOCITY (0b011).
#     Suppose slot 11 is a stationary turret with masks[11] = ComponentFlag.POSITION (0b001)
#     and leftover velocity vx[11] = 20.0 from a previously recycled entity.
#     Writing if world.masks[11] & MOVE_MASK: computes 0b001 & 0b011 == 0b001,
#     which is truthy because ANY overlapping bit matched! The stationary turret
#     would falsely start moving across the map.
#     Always test full subset inclusion explicitly:
#         if (world.masks[11] & MOVE_MASK) == MOVE_MASK:
#     Now 0b001 == 0b011 evaluates to False and the turret stays put.

from world import ComponentFlag

MOVE_MASK: ComponentFlag = ComponentFlag.POSITION | ComponentFlag.VELOCITY
HEALTH_MASK: ComponentFlag = ComponentFlag.HEALTH

# Expand the import above to from world import ComponentFlag, EntityHandle, MAX_ENTITIES, World
# as you implement the two systems below.


# Implement the movement and wall-bounce system:
# define def movement_system(world: World, dt: float, bounds: tuple[float, float] = (100.0, 100.0)) -> None:
# Unpack max_x, max_y = bounds and loop with for i in range(MAX_ENTITIES):
# Skip any slot where (world.masks[i] & MOVE_MASK) != MOVE_MASK.
# Integrate position by velocity:
#     world.x[i] += world.vx[i] * dt
#     world.y[i] += world.vy[i] * dt
# Bounce cleanly off the arena walls:
# - If world.x[i] < 0.0, clamp world.x[i] = 0.0 and flip world.vx[i] = -world.vx[i].
# - If world.x[i] > max_x, clamp world.x[i] = max_x and flip world.vx[i] = -world.vx[i].
# - Apply the same clamp-and-flip check to world.y[i] and world.vy[i] against [0.0, max_y].


# Implement the periodic poison damage and despawn system:
# define def damage_system(world: World, poison_dmg: float) -> list[EntityHandle]:
# Initialize despawned: list[EntityHandle] = [] and loop with for i in range(MAX_ENTITIES):
# Skip any slot where (world.masks[i] & HEALTH_MASK) != HEALTH_MASK.
# Subtract world.health[i] -= poison_dmg.
# Whenever world.health[i] <= 0.0:
# - Capture the live handle BEFORE despawning:
#   handle = EntityHandle(idx=i, gen=world.generations[i])
# - Call world.despawn_entity(handle) and append handle to despawned.
# Think about what breaks if you build EntityHandle after calling despawn_entity:
# world.generations[i] has already incremented, so your returned handle would
# carry the next generation instead of the dead entity's generation!
# Return despawned at the end of the pass.
