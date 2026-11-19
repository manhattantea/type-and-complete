# Package export boundary for vault (410_visibility_all_and_circular_imports).

# __all__ is a module-level list of string names declaring the explicit public
# interface of a module or package. It steers three distinct tools at once:
#
# - Wildcard imports (from vault import *): Python binds ONLY the names listed
#   in __all__. Without __all__, wildcard imports bind every global name in
#   this file that does not start with an underscore, which would accidentally
#   leak imported submodule names like models and public_api!
# - Static type checkers (mypy --strict, pyright): treat __all__ as the
#   canonical re-export list so callers can run from vault import VaultAccount
#   without triggering implicit-reexport errors.
# - help(vault) and documentation builders: present only the public surface
#   listed in __all__.
#
# Notice that _internal is intentionally kept out of __all__ and not imported
# here at top level.

from .models import DEFAULT_OWNER
from .public_api import DEFAULT_SESSION_PREFIX

# Minimal anchor export list working out of the box before classes are added.
__all__: list[str] = ["DEFAULT_OWNER", "DEFAULT_SESSION_PREFIX"]

# Once you define VaultAccount in vault/models.py and VaultSession plus
# verify_pin in vault/public_api.py, re-export them here:
# from .models import DEFAULT_OWNER, VaultAccount
# from .public_api import DEFAULT_SESSION_PREFIX, VaultSession, verify_pin
# and extend __all__ to include "VaultAccount", "VaultSession", and "verify_pin".


# Try adding a convenience factory def open_demo_session(owner: str, pin: int) -> VaultSession | None:
# that returns a VaultSession linked to a VaultAccount only when verify_pin(pin)
# is True (returning None otherwise), and experiment with omitting a name from
# __all__ to see how wildcard imports skip unlisted symbols.
