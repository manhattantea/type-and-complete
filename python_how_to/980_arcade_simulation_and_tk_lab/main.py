# python 980_arcade_simulation_and_tk_lab/main.py --headless

# 2D Arcade Simulation and Tkinter Lab Entry Point (main.py).
#
# Inspired by CodingTemplateExamples/examples/invaders and
# odin_how_to/980_raylib_arcade_lab, this capstone connects pure deterministic
# game simulation (game.py) with two interchangeable views (renderer.py):
# - Headless ASCII snapshots and deterministic frame stepping (--headless), ideal
#   for terminal verification and CI environments without a display server.
# - An interactive 800x600 60-FPS tkinter.Canvas window driven by root.after.

import sys

from game import GameState
from renderer import tk


def run_headless_simulation(state: GameState) -> None:

    # Print the baseline GameState contract before stepping simulation frames.
    print(f"Headless arcade scaffold ready (score={state.score}, invaders={len(state.invaders)}, player_x={state.player_x})")

    # Once game.py and renderer.py are implemented:
    # Align state.player_x underneath an invader if state.invaders is non-empty
    # (for example state.player_x = state.invaders[-1].x), then step 10
    # deterministic frames using dt = 0.1 (1.0 second total simulated time, giving
    # the bullet enough distance to travel from y=552 into the invader grid):
    # - On frame 0, pass InputState(fire=True) so update_game spawns a bullet.
    # - On frames 1..9, pass InputState() so the bullet travels upward and hits.
    # Print render_ascii_snapshot(state) and
    # f"Headless check: score={state.score}, invaders={len(state.invaders)}",
    # and assert state.score >= 100.


def main() -> None:

    print("=== 980: Arcade Simulation and Tkinter Lab ===")
    headless: bool = "--headless" in sys.argv[1:]
    state: GameState = GameState()
    print(f"Arcade setup: headless={headless}, tk_available={tk is not None}, player_x={state.player_x}")

    # Once game.py and renderer.py are implemented, expand the imports at the
    # top of this file to bring in InputState, init_game, and update_game from
    # game, plus render_ascii_snapshot and run_tk_window from renderer, and
    # replace GameState() above with state = init_game().

    # Dispatch cleanly between headless mode and the interactive Tkinter window:
    # - If headless is True, call run_headless_simulation(state) and return.
    # - Otherwise, if tk is None, fall back to run_headless_simulation(state).
    # - Else call run_tk_window(state) inside a try ... except tk.TclError:
    #   block and fall back to run_headless_simulation(state) when no graphical
    #   display is available.


if __name__ == "__main__":
    main()
