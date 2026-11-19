# Shared data models for vault (410_visibility_all_and_circular_imports).

# Circular imports (ImportError: cannot import name 'X' from partially
# initialized module 'Y') happen when Module A imports Module B at top level
# while Module B is still midway through importing Module A:
#
#     Suppose vault/models.py ran from .public_api import VaultSession at
#     module top level while vault/public_api.py ran
#     from .models import VaultAccount at top level.
#     When Python starts loading models.py, it inserts an empty module entry
#     in sys.modules["vault.models"], pauses at the import of public_api, and
#     runs public_api.py. When public_api.py asks for VaultAccount, models.py
#     has not reached class VaultAccount yet, so Python raises ImportError!
#
# Python gives you three clean ways to break cycles:
# - Type-only cycles: enable from __future__ import annotations (which turns
#   annotations into lazy strings so Python does not evaluate them at import
#   time) and guard the cross-module import under if TYPE_CHECKING: (a constant
#   that is False at runtime and True only for static type checkers).
# - Leaf extraction: keep shared data types in a leaf module that never imports
#   higher-level modules at runtime.
# - Deferred local import: place an unavoidable runtime import inside the
#   function body that needs it (practiced in public_api.py).
#
# Inside VaultAccount below, you will also practice double-underscore class
# attribute name mangling (__attr). At compile time, Python rewrites
# self.__master_key inside class VaultAccount into
# self._VaultAccount__master_key. That does not encrypt or hide the value; it
# prevents subclasses from accidentally overwriting a base class attribute of
# the same name.

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import public_api

# Minimal anchor constant re-exported by vault/__init__.py on first run.
DEFAULT_OWNER: str = "guest"

# Once you define VaultSession in vault/public_api.py, update the TYPE_CHECKING
# block above to: from .public_api import VaultSession


# Define class VaultAccount: right below with two methods:
# - def __init__(self, owner: str, master_key: str, active_session: VaultSession | None = None) -> None:
#   assigning self.owner = owner, self.__master_key = master_key (mangled!),
#   and self.active_session = active_session.
# - def masked_summary(self) -> str: returning
#   f"VaultAccount(owner={self.owner!r}, key_len={len(self.__master_key)})"
#   so logs never reveal the raw master key.


# Circular-import experiment: after both VaultAccount and VaultSession exist,
# try temporarily moving from .public_api import VaultSession ABOVE the
# if TYPE_CHECKING: guard while placing a top-level from .models import VaultAccount
# inside public_api.py to observe the partially initialized module ImportError.
