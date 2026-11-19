# python 450_warnings_deprecation_and_future_flags.py

from __future__ import annotations

import warnings


def future_annotations_mechanics() -> None:

    # Python evolves language syntax carefully across versions using
    # compile-time __future__ directives. Enabling
    # from __future__ import annotations (PEP 563) changes how the compiler
    # handles type annotations on functions and classes: instead of evaluating
    # every annotation object eagerly at import time, Python stores them as
    # plain strings inside __annotations__.
    #
    # Two practical consequences follow immediately:
    # - Forward references (such as a Node class referencing Node | None in its
    #   own __init__ before the class body finishes) and if TYPE_CHECKING:
    #   imports work cleanly with zero runtime import cost.
    # - Because __future__ flags alter compilation of the entire file, they
    #   MUST appear before every normal import or statement (only # comments
    #   and a module docstring may come earlier; anything else raises
    #   SyntaxError). Note that Python 3.14+ (PEP 649) replaces stringification
    #   with lazy descriptor evaluation.
    #
    #     Suppose this file defines def greet(name: str) -> None:.
    #     With from __future__ import annotations active at the top, reading
    #     greet.__annotations__ returns {'name': 'str', 'return': 'None'}
    #     rather than {'name': <class 'str'>, 'return': None}.

    print(f"Starter __annotations__ with future flag: {future_annotations_mechanics.__annotations__!r}")

    # Define a self-referential class Node: right here with
    # def __init__(self, value: int, next_node: Node | None = None) -> None:
    # storing self.value and self.next_node. Notice you do NOT need quotes
    # around Node! Print Node.__init__.__annotations__ to verify Python stored
    # 'Node | None' as a string.


    # SyntaxError experiment: try temporarily moving import warnings ABOVE
    # from __future__ import annotations at the top of this file and running it
    # to observe:
    # SyntaxError: from __future__ imports must occur at the beginning of the file


def warnings_stacklevel_and_filtering() -> None:

    # Removing a public function overnight breaks downstream users. Python's
    # warnings module lets you deprecate APIs gradually by emitting
    # DeprecationWarning while keeping the old function working.
    #
    # Two subtle rules make warnings genuinely useful:
    # - Visibility defaults: outside __main__, CPython suppresses
    #   DeprecationWarning inside imported libraries so end users are not
    #   spammed, whereas test runners (unittest, pytest) and python -Wd reveal
    #   them.
    # - stacklevel=2: with the default stacklevel=1, Python points the warning
    #   line number INSIDE your deprecated helper at the warnings.warn(...)
    #   line itself, hiding who called it! Setting stacklevel=2 walks one frame
    #   up the call stack to report the caller's line:
    #
    #     Suppose line 90 calls legacy_connect("localhost") and line 72 inside
    #     legacy_connect calls warnings.warn(..., DeprecationWarning, stacklevel=2).
    #     recorded[0].lineno reports line 90 (the caller), not line 72!
    #
    # Python 3.12 also adds skip_file_prefixes=(...) for wrapper packages, and
    # Python 3.13 adds the @warnings.deprecated("...") decorator.

    print("Active CPython warning filter rules:", len(warnings.filters))

    # Define two helpers (either here or at module scope above main):
    # - def connect(host: str, port: int = 5432) -> str: returning
    #   f"connected://{host}:{port}".
    # - def legacy_connect(host: str) -> str: calling
    #   warnings.warn("legacy_connect is deprecated; use connect()", DeprecationWarning, stacklevel=2)
    #   and returning connect(host).


    # Capture and inspect the deprecation warning cleanly:
    # - Open with warnings.catch_warnings(record=True) as recorded:
    # - Call warnings.simplefilter("always", DeprecationWarning) inside the block.
    # - Call endpoint = legacy_connect("localhost") and note its line number.
    # - Outside the with block, assert len(recorded) == 1 and
    #   issubclass(recorded[0].category, DeprecationWarning), then print
    #   endpoint, recorded[0].lineno, and recorded[0].message.
    # - Temporarily change stacklevel=2 to stacklevel=1 to watch lineno jump
    #   into legacy_connect instead of the call site, then restore stacklevel=2.


    # Escalate deprecation warnings into hard exceptions (like python -W error):
    # - Open with warnings.catch_warnings():
    # - Set warnings.simplefilter("error", DeprecationWarning)
    # - Call legacy_connect("localhost") inside
    #   try ... except DeprecationWarning as err: and print err.


    # Add a thin wrapper def old_alias(host: str) -> str: that calls
    # legacy_connect(host). Capture a warning from old_alias("db.local") to
    # observe that stacklevel=2 now points inside old_alias rather than its
    # caller, illustrating why multi-layer wrappers need a higher stacklevel or
    # skip_file_prefixes.


def main() -> None:

    print("=== 1. Compile-time __future__ annotations ===")
    future_annotations_mechanics()

    print("\n=== 2. Deprecation warnings, stacklevel, and filters ===")
    warnings_stacklevel_and_filtering()


if __name__ == "__main__":
    main()
