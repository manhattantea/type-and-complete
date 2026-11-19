# python 770_import_hooks_and_custom_loaders.py

from collections.abc import Sequence
import importlib
from importlib.abc import Loader, MetaPathFinder
from importlib.machinery import ModuleSpec
import sys
from types import ModuleType


def meta_path_and_two_phase_import_protocol() -> None:

    # Every import statement in Python walks the list of finder objects stored
    # in sys.meta_path. Normally you see BuiltinImporter (C built-ins like sys),
    # FrozenImporter (frozen stdlib modules), and PathFinder (.py files on
    # sys.path).
    #
    # You can insert your own MetaPathFinder + Loader into sys.meta_path to
    # synthesize virtual modules in memory or transform source code at import
    # time. Python splits importing into a strict 2-phase protocol:
    # - Finding (MetaPathFinder.find_spec(fullname, path, target=None)):
    #   Python calls find_spec on each finder in sys.meta_path in order.
    #   Return None immediately for any module name you do not own so Python
    #   continues to the next finder. When you own the name, return
    #   ModuleSpec(fullname, loader).
    # - Loading (Loader.create_module + Loader.exec_module):
    #   - create_module(self, spec) usually returns None, telling importlib to
    #     allocate a standard empty ModuleType(spec.name) with __name__,
    #     __spec__, __loader__, and __package__ pre-wired.
    #   - importlib inserts that module into sys.modules[fullname] BEFORE
    #     running exec_module (which is why circular imports resolve cleanly).
    #   - exec_module(self, module) populates module.__dict__ (or runs
    #     exec(code, module.__dict__)) and returns None.
    #
    #     Suppose your finder owns "virtual_cfg_alpha":
    #     find_spec returns ModuleSpec("virtual_cfg_alpha", self), importlib
    #     registers the empty ModuleType in sys.modules["virtual_cfg_alpha"],
    #     and then exec_module fills in ENV, MODULE_NAME, and describe().

    print("Starter meta_path finders:", [type(f).__name__ for f in sys.meta_path])

    # Write class VirtualConfigFinder(MetaPathFinder, Loader): with three methods:
    # - def find_spec(self, fullname: str, path: Sequence[str] | None, target: ModuleType | None = None) -> ModuleSpec | None:
    #   Return ModuleSpec(fullname, self) when fullname.startswith("virtual_cfg_"),
    #   and return None for every other module name.
    # - def create_module(self, spec: ModuleSpec) -> ModuleType | None:
    #   Return None so importlib allocates a standard ModuleType.
    # - def exec_module(self, module: ModuleType) -> None:
    #   Set module.__dict__["ENV"] = "test",
    #   module.__dict__["MODULE_NAME"] = module.__name__, and
    #   module.__dict__["describe"] = lambda: f"{module.__name__} ({module.__dict__['ENV']})".


    # Write a second tiny loader class InMemorySourceLoader(MetaPathFinder, Loader):
    # backed by a dict[str, str] mapping module names to Python source strings.
    # In exec_module(self, module: ModuleType) -> None:, compile the source
    # with compile(src, module.__name__, "exec") and run exec(code, module.__dict__).


def virtual_module_loader_and_sys_modules_cleanup() -> None:

    # Remember one major caching rule: sys.modules caches every imported module
    # globally by name.
    #
    #     Suppose you import "virtual_cfg_alpha" once:
    #     Python stores the ModuleType object in sys.modules["virtual_cfg_alpha"].
    #     A second importlib.import_module("virtual_cfg_alpha") returns that
    #     cached object immediately WITHOUT calling sys.meta_path again—even if
    #     you already removed your custom finder!
    #
    # Always remove both your finder from sys.meta_path and any synthetic keys
    # from sys.modules inside a finally block so global interpreter state stays
    # clean between tests.

    print("Starter cached sys.modules count =", len(sys.modules))

    # Instantiate VirtualConfigFinder() (move the class to module scope or define
    # a shared helper if needed) and insert it at sys.meta_path.insert(0, finder)
    # inside a try block:
    # - Call mod = importlib.import_module("virtual_cfg_alpha").
    # - Print mod.ENV, mod.MODULE_NAME, and mod.describe().
    # - Assert sys.modules["virtual_cfg_alpha"] is mod.
    # - Verify non-matching names fall through cleanly by importing "json" and
    #   confirming json.__loader__ is not finder.
    # - In finally:, remove finder from sys.meta_path and call
    #   sys.modules.pop("virtual_cfg_alpha", None).


    # Prove sys.modules caching behavior explicitly:
    # Import "virtual_cfg_beta" while the finder is installed, remove the finder
    # from sys.meta_path, and call importlib.import_module("virtual_cfg_beta")
    # again to see it still resolve from sys.modules until you pop it.


    # Test InMemorySourceLoader with a tiny module dictionary such as
    # {"mem_greeter": "GREETING = 'hello from memory'\ndef greet(n: str) -> str: return f'{GREETING}, {n}'"}
    # inside try / finally:, calling importlib.import_module("mem_greeter") and
    # cleaning up both sys.meta_path and sys.modules afterward.


def main() -> None:

    print("=== 1. sys.meta_path and the 2-phase import protocol ===")
    meta_path_and_two_phase_import_protocol()

    print("\n=== 2. Virtual module loading and sys.modules cleanup ===")
    virtual_module_loader_and_sys_modules_cleanup()


if __name__ == "__main__":
    main()
