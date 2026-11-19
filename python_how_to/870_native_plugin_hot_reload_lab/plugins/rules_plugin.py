# plugins/rules_plugin.py — hot-reloadable rules plugin for 870_native_plugin_hot_reload_lab.

# A hot-reloadable plugin stays stateless by exporting a stable contract
# (PLUGIN_VERSION and step_simulation(state)) and mutating only the host-owned
# HostState argument passed in by host.py.
#
# Guarding type-only host imports under if TYPE_CHECKING: (combined with
# from __future__ import annotations) gives the plugin full IDE type checking on
# HostState without depending on sys.path when parsed standalone.

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from shared_state import HostState

PLUGIN_VERSION = "v1"


def step_simulation(state: HostState) -> None:

    state.tick += 1

    # Complete the remaining v1 tick updates once HostState defines those fields:
    # set state.version_tag = PLUGIN_VERSION, advance state.player_x += 1.5, and
    # increase state.score += 10.
