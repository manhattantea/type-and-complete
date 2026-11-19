# Public API surface for vault (410_visibility_all_and_circular_imports).

# Look at how public_api.py collaborates with both models.py and _internal.py
# without creating a runtime circular import:
#
# - VaultSession only needs VaultAccount inside type annotations
#   (account: VaultAccount | None). Because from __future__ import annotations
#   postpones annotation evaluation and if TYPE_CHECKING: is always False at
#   runtime, static checkers (mypy, pyright) validate the bidirectional link
#   between VaultAccount and VaultSession while Python never runs a cycle.
# - When a function genuinely needs another module at runtime—for instance to
#   call a helper only along one code path or to break an unavoidable runtime
#   loop—putting the import statement inside the function body defers it until
#   every top-level module has finished initializing.
#
#     Suppose def verify_pin(pin: int) -> bool: runs
#         from ._internal import _hash_pin
#     inside its body. Python loads vault._internal on the first call, caches
#     it in sys.modules, and subsequent calls are a fast dictionary lookup.

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import models

# Minimal anchor constant re-exported by vault/__init__.py on first run.
DEFAULT_SESSION_PREFIX: str = "sess"

# Once you define VaultAccount in vault/models.py, update the TYPE_CHECKING
# block above to: from .models import VaultAccount


# Define class VaultSession: right below with two methods:
# - def __init__(self, session_id: str, account: VaultAccount | None = None) -> None:
#   storing self.session_id = session_id and self.account = account.
# - def owner_label(self) -> str: returning self.account.owner when
#   self.account is not None, or "anonymous" otherwise.


# Define def verify_pin(pin: int) -> bool: using a deferred local import
# from ._internal import _hash_pin inside the function body, returning
# _hash_pin(pin) == _hash_pin(1234).
