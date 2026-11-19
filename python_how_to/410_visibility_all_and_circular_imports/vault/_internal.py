# Internal helper module for vault (410_visibility_all_and_circular_imports).

# Python has no private or internal access-modifier keyword. Instead, module
# and attribute visibility rests on naming conventions paired with __all__:
#
# - A single leading underscore (_internal.py, _SECRET_SALT, _hash_pin) tells
#   callers, linters, and documentation tools that a symbol is an internal
#   implementation detail rather than part of the stable public API.
# - Wildcard imports (from vault._internal import *) skip every name starting
#   with a leading underscore.
# - Explicit imports (from vault._internal import _INTERNAL_TAG) still succeed
#   at runtime because Python follows the "consenting adults" philosophy:
#   conventions discourage accidental coupling without locking out debugging
#   tools or tests.
#
# Notice also where _internal.py sits in the dependency graph: it imports
# neither models.py nor public_api.py. Keeping low-level helpers at the bottom
# (leaf) layer eliminates circular imports by construction.

# Minimal anchor constant skipped by wildcard imports.
_INTERNAL_TAG: str = "vault-internal-v1"

# Define an internal integer constant _SECRET_SALT: int = 0x9E3779B9 right below.


# Define def _hash_pin(pin: int) -> int: that computes and returns a simple
# deterministic 32-bit integer mix:
# ((pin ^ _SECRET_SALT) * 0x45D9F3B) & 0xFFFFFFFF
# Notice the leading underscore marks this helper as package-internal so only
# trusted vault submodules call it.
