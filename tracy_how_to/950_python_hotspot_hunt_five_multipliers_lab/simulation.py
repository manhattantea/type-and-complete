# 950_python_hotspot_hunt_five_multipliers_lab/simulation.py
# Multi-system simulation contracts, cold systems, baseline bottlenecks, and optimization Drills.
# Run this Lab from the workspace folder via: python 950_python_hotspot_hunt_five_multipliers_lab/main.py

from array import array
from dataclasses import dataclass


# In real Python services and tools, most functions take less than 1% of runtime.
# Leave the three cold functions untouched so your code stays clear and concise:
# - load_world_config(): cold startup config loader (< 1% of runtime).
# - build_tag_lookup(): cold startup tag table (< 1% of runtime).
# - audit_frame_checksum(): cold scalar verification helper (< 0.1% of runtime).
#
# Your profiler will flag only two true hotspots:
# - step_entity_kinematics() (Hotspot A): mixes Multiplier #1 (creating a new
#   temporary dict and a non-slotted EntityState object on every entity every
#   frame, triggering heap allocation churn and Gen-0 GC sweeps) with
#   Multiplier #4 (walking a list[EntityState] of scattered heap pointers).
# - compute_signal_energy() (Hotspot B): mixes Multiplier #1 (calling a Python
#   helper per entity and resolving getattr(entity, ...) dynamically) with
#   interpreter dispatch overhead on every iteration.
#
# When we store coordinates in array("d") instead of list[EntityState], Python
# packs raw 8-byte C doubles contiguously inside one flat memory block with zero
# per-element PyObject headers. Suppose you step 4,000 entities:
#
#     AoS baseline: 4,000 EntityState objects + 4,000 dicts = ~8,000 heap allocs/frame
#     SoA array("d"): mutating xs[i], ys[i], vxs[i], vys[i] in place = 0 B net allocs
#
# Pairing contiguous array("d") columns with math.sumprod(world.xs, world.vxs)
# lets CPython execute the dot-product accumulation loop directly in C without
# dispatching Python bytecode per element (see python_how_to/585 and 590 for
# standalone array("d") and SoA pool mechanics).


@dataclass
class EntityState:

    x: float
    y: float
    vx: float
    vy: float
    weight: float


@dataclass(slots=True)
class SimWorld:

    count: int
    entities: list[EntityState]
    xs: array
    ys: array
    vxs: array
    vys: array
    weights: array


def create_sim_world(entity_count: int = 4_000) -> SimWorld:

    entities: list[EntityState] = []
    xs = array("d")
    ys = array("d")
    vxs = array("d")
    vys = array("d")
    weights = array("d")
    for i in range(entity_count):
        x = (i % 101) * 0.125
        y = (i % 73) * 0.25
        vx = ((i % 19) - 9) * 0.05
        vy = ((i % 23) - 11) * 0.05
        weight = 1.0 + (i % 7) * 0.1
        entities.append(EntityState(x, y, vx, vy, weight))
        xs.append(x)
        ys.append(y)
        vxs.append(vx)
        vys.append(vy)
        weights.append(weight)
    return SimWorld(entity_count, entities, xs, ys, vxs, vys, weights)


# Cold system #1 (< 1% of runtime): keep readable, do not optimize.
def load_world_config() -> dict[str, float]:

    return {"dt": 0.016, "damping": 0.995}


# Cold system #2 (< 1% of runtime): keep readable, do not optimize.
def build_tag_lookup(count: int) -> dict[int, str]:

    return {i: f"ent-{i & 0xF:x}" for i in range(min(count, 32))}


def _entity_energy_slow(entity: EntityState) -> float:

    return getattr(entity, "x") * getattr(entity, "vx") + getattr(entity, "y") * getattr(entity, "vy")


# Baseline Hotspot A: AoS object + dict heap churn every frame.
def step_entity_kinematics(world: SimWorld, dt: float = 0.016) -> None:

    next_entities: list[EntityState] = []
    for e in world.entities:
        step = {
            "vx": e.vx * 0.995 + 0.01 * e.weight,
            "vy": e.vy * 0.995 - 0.005 * e.weight,
        }
        next_entities.append(
            EntityState(
                x=e.x + step["vx"] * dt,
                y=e.y + step["vy"] * dt,
                vx=step["vx"],
                vy=step["vy"],
                weight=e.weight,
            )
        )
    world.entities = next_entities


# Baseline Hotspot B: per-entity Python call + getattr bytecode dispatch waste.
def compute_signal_energy(world: SimWorld) -> float:

    total = 0.0
    for e in world.entities:
        total += _entity_energy_slow(e)
    return total


# Cold system #3 (< 0.1% of runtime): keep readable, do not optimize.
def audit_frame_checksum(energy: float, frame_idx: int) -> float:

    return round(energy, 9) + frame_idx * 0.0


# Define def step_entity_kinematics_fast(world: SimWorld, dt: float = 0.016) -> None:
# Hoist xs = world.xs, ys = world.ys, vxs = world.vxs, vys = world.vys,
# weights = world.weights, n = world.count into local variables so CPython
# uses fast LOAD_FAST slot reads instead of repeated attribute lookups.
# Loop for i in range(n): mutating vxs[i], vys[i], xs[i], and ys[i] in place
# with zero temporary dicts or objects using the exact baseline formulas:
# new_vx = vxs[i] * 0.995 + 0.01 * weights[i]
# new_vy = vys[i] * 0.995 - 0.005 * weights[i]
# vxs[i] = new_vx; vys[i] = new_vy; xs[i] += new_vx * dt; ys[i] += new_vy * dt.


# Define def compute_signal_energy_fast(world: SimWorld) -> float:
# Add import math at the top of simulation.py, hoist xs = world.xs, ys = world.ys,
# vxs = world.vxs, vys = world.vys to local LOAD_FAST variables, and return
# math.sumprod(xs, vxs) + math.sumprod(ys, vys) so CPython runs both dot
# reductions entirely in C with zero bytecode loop dispatch.
