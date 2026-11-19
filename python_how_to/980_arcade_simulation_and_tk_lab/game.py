# python 980_arcade_simulation_and_tk_lab/main.py --headless

# Pure Deterministic Arcade Simulation and Physics (game.py).
#
# Notice what is NOT imported in this file: tkinter!
# Keeping game.py 100% pure simulation state and math (Model-View separation)
# gives you two huge engineering advantages:
# - You can step 10, 1,000, or 100,000 frames headlessly at full CPU speed
#   without opening a window or needing a graphical display server.
# - Any collision bug can be reproduced deterministically by feeding a fixed
#   sequence of InputState frames and a fixed timestep dt into update_game(...).
#
# Why @dataclass(slots=True)? Adding slots=True tells Python to store fields in
# a fixed-size C-like slot array on each instance instead of allocating a
# per-object __dict__ hash table, which trims memory and speeds up attribute
# reads inside hot per-frame loops. Notice field(default_factory=list) on
# GameState: Python forbids mutable defaults like invaders: list = [] directly
# in a class body because every instance would share the exact same list!
#
# A classic game-loop Python pitfall when removing dead bullets or invaders:
# never delete elements from a list while iterating forward over it (such as
# for b in state.bullets: state.bullets.remove(b)), because removing index i
# shifts index i + 1 down into i, so the iterator moves to i + 1 and silently
# skips checking the element that just shifted into i!
#
# When entity order does not matter, O(1) swap-and-pop avoids both skipped
# items and middle-of-list O(n) shifts:
#
#     Suppose items = [b0, b1, b2, b3] and you scan with i = 0, while i < len(items):
#     - At i = 0, b0 is alive, so advance i += 1 (now i = 1).
#     - At i = 1, b1 is dead: overwrite items[1] = items[-1] (putting b3 at
#       index 1) and call items.pop() -> items becomes [b0, b3, b2].
#     - Do NOT increment i after a swap! On the next pass i is still 1, so the
#       loop checks the newly swapped b3 instead of skipping over it.

from dataclasses import dataclass, field

SCREEN_WIDTH: int = 800
SCREEN_HEIGHT: int = 600
PLAYER_WIDTH: int = 44
PLAYER_HEIGHT: int = 18
PLAYER_SPEED: float = 320.0
BULLET_SPEED: float = 520.0
INVADER_WIDTH: int = 28
INVADER_HEIGHT: int = 20
INVADER_SPEED: float = 90.0


@dataclass(slots=True)
class Bullet:
    x: float
    y: float
    vy: float = -BULLET_SPEED
    radius: float = 4.0
    active: bool = True


@dataclass(slots=True)
class Invader:
    x: float
    y: float
    width: float = INVADER_WIDTH
    height: float = INVADER_HEIGHT
    alive: bool = True


@dataclass(slots=True)
class InputState:
    move_left: bool = False
    move_right: bool = False
    fire: bool = False


@dataclass(slots=True)
class GameState:
    player_x: float = SCREEN_WIDTH / 2.0
    player_y: float = SCREEN_HEIGHT - 48.0
    invader_dir: float = 1.0
    score: int = 0
    fire_cooldown: float = 0.0
    frame_count: int = 0
    invaders: list[Invader] = field(default_factory=list)
    bullets: list[Bullet] = field(default_factory=list)


# Implement def init_game() -> GameState:
# Instantiate state = GameState(), then populate state.invaders with a 3-row
# by 6-column grid (18 invaders total), for example setting
# x = 180.0 + col * 72.0 and y = 80.0 + row * 48.0 for row in range(3) and
# col in range(6), and return state.


# Implement def spawn_bullet(state: GameState) -> None:
# Guard with if state.fire_cooldown > 0.0: return so rapid keypresses respect
# the weapon cooldown. Otherwise append
# Bullet(x=state.player_x, y=state.player_y - PLAYER_HEIGHT / 2.0) to
# state.bullets and set state.fire_cooldown = 0.25.


# Implement def update_game(state: GameState, inputs: InputState, dt: float) -> None:
# Advance player motion, bullets, invader formation, collisions, and compaction:
# - Increment state.frame_count += 1 and decrement
#   state.fire_cooldown = max(0.0, state.fire_cooldown - dt).
# - Move state.player_x left or right by PLAYER_SPEED * dt based on
#   inputs.move_left and inputs.move_right, clamping state.player_x inside
#   [PLAYER_WIDTH / 2.0, SCREEN_WIDTH - PLAYER_WIDTH / 2.0].
# - If inputs.fire is True, call spawn_bullet(state).
# - Advance each active bullet with b.y += b.vy * dt and set b.active = False
#   if b.y < 0.0.
# - Move alive invaders horizontally by state.invader_dir * INVADER_SPEED * dt.
#   If any alive invader crosses outside [24.0, SCREEN_WIDTH - 24.0], flip
#   state.invader_dir = -state.invader_dir and drop all alive invaders down by
#   16.0 pixels.
# - For each active bullet b and alive invader inv, check AABB overlap expanded
#   by b.radius:
#   abs(b.x - inv.x) <= inv.width / 2.0 + b.radius and abs(b.y - inv.y) <= inv.height / 2.0 + b.radius
#   On hit: set b.active = False, inv.alive = False, state.score += 100, and break.
# - Compact state.bullets in place keeping only b.active, and compact
#   state.invaders in place keeping only inv.alive using the while i < len(items):
#   swap-and-pop loop (remembering not to increment i on a swap).
