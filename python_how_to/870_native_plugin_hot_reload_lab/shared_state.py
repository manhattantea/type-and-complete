# Persistent host state shared across plugin hot-reloads in 870_native_plugin_hot_reload_lab.

# When a dynamic plugin reloads inside a long-running host (such as a game loop,
# rule engine, or dev server), any state stored inside the plugin module itself
# gets wiped or orphaned on every reload. Keeping HostState in this standalone
# host-owned module guarantees that reloading plugins/rules_plugin.py preserves
# tick, player_x, and score seamlessly across versions.
#
# Using @dataclass(slots=True) also catches attribute typos immediately with
# AttributeError instead of silently attaching stray fields inside a plugin.

from dataclasses import dataclass


@dataclass(slots=True)
class HostState:
    tick: int = 0

    # Add the remaining three persistent state fields with defaults:
    # player_x: float = 0.0
    # score: int = 0
    # version_tag: str = "v1"
