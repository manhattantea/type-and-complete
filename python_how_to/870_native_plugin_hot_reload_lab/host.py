# python 870_native_plugin_hot_reload_lab/host.py

# Calling importlib.reload(existing_module) executes the updated file directly
# into the existing module's __dict__ in place. If the developer saves a file
# containing a SyntaxError or mid-file NameError, reload() leaves the live
# module half-mutated and crashes the running host!
#
# Instead, a resilient plugin host loads every candidate file into a fresh,
# uniquely named temporary module before touching the active callback:
#
#     Suppose generation starts at 0 and increments on each load attempt:
#         spec = importlib.util.spec_from_file_location(f"_rules_plugin_gen_{gen}", path)
#         candidate = importlib.util.module_from_spec(spec)
#         spec.loader.exec_module(candidate)   # wrapped in try ... except Exception:
#     Only after getattr(candidate, "step_simulation", None) passes callable()
#     do we swap self.active_step = step_fn. If anything fails, the previous
#     working active_step keeps running uninterrupted!

from collections.abc import Callable
import importlib.util
from pathlib import Path
import tempfile

from shared_state import HostState


# Define class PluginLoader: to load candidate plugin files safely and preserve
# the last good callback across broken reloads:
# - __init__(self) -> None: sets self._generation: int = 0,
#   self.active_step: Callable[[HostState], None] | None = None, and
#   self.active_version: str = "none".
# - load(self, plugin_path: Path) -> bool: increments self._generation += 1,
#   builds mod_name = f"_rules_plugin_gen_{self._generation}", and inside
#   try ... except Exception as exc: calls
#   spec = importlib.util.spec_from_file_location(mod_name, plugin_path), verifies
#   spec is not None and spec.loader is not None, creates
#   candidate = importlib.util.module_from_spec(spec), and runs
#   spec.loader.exec_module(candidate).
#   Validate step_fn = getattr(candidate, "step_simulation", None) with
#   callable(step_fn) (raising TypeError("missing callable step_simulation") if
#   missing), then atomically update self.active_step = step_fn and
#   self.active_version = str(getattr(candidate, "PLUGIN_VERSION", "unknown")),
#   returning True. In except Exception as exc:, print a warning noting that
#   self.active_version remains active and return False.


# Define class PluginHost: to drive persistent HostState across live reloads:
# - __init__(self, loader: PluginLoader) -> None: stores self.loader = loader and
#   self.state = HostState().
# - run_ticks(self, count: int) -> None: verifies self.loader.active_step is
#   not None, invokes it count times passing self.state, and prints self.state
#   after each tick.


def main() -> None:

    print("=== 870 Native Plugin Hot-Reload Lab ===")
    plugin_path = Path(__file__).resolve().parent / "plugins" / "rules_plugin.py"
    starter_state = HostState()
    print(f"Starter plugin path: {plugin_path} (exists={plugin_path.exists()})")
    print(f"Starter host state: {starter_state}")

    # Run a self-contained 3-phase hot-reload verification after implementing
    # HostState, rules_plugin.py, PluginLoader, and PluginHost:
    # - Phase 1 (v1): instantiate loader = PluginLoader() and host = PluginHost(loader),
    #   assert loader.load(plugin_path), and run 3 ticks (ticks 1..3).
    # - Phase 2 (hot-reload v2 in tempfile.TemporaryDirectory() so we never
    #   clobber the repo file): write rules_plugin_v2.py defining
    #   PLUGIN_VERSION = "v2" and def step_simulation(state): setting
    #   state.version_tag = PLUGIN_VERSION, state.tick += 1,
    #   state.player_x += 3.0, and state.score += 25. Call assert loader.load(v2_path),
    #   run 3 more ticks (4..6), and assert host.state.tick == 6 and score kept
    #   accumulating from v1.
    # - Phase 3 (broken plugin fallback): write rules_plugin_broken.py with
    #   invalid syntax ("def step_simulation(:"), call ok = loader.load(broken_path),
    #   assert not ok and loader.active_version == "v2", and run 1 more tick
    #   (tick == 7) proving the host survived the broken reload!


if __name__ == "__main__":
    main()
