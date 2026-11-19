# python 420_dynamic_imports_and_importlib.py

import importlib
import importlib.metadata
import importlib.resources
import importlib.util
from pathlib import Path
import sys
import tempfile


def dynamic_imports_and_find_spec() -> None:

    # Normally Python resolves imports statically at write time (import json).
    # When a module name comes from a config file, CLI flag, or plugin registry
    # at runtime, use the importlib standard library instead of legacy
    # __import__():
    #
    # - importlib.import_module("os.path") returns the os.path submodule you
    #   asked for (and accepts package="my_pkg" for relative names).
    # - Legacy __import__("os.path") surprisingly returns the top-level os
    #   package unless you pass a non-empty fromlist argument!
    #
    # When you only want to check whether an optional dependency is installed
    # without executing its top-level code or populating sys.modules, use
    # importlib.util.find_spec(name). It walks sys.meta_path and sys.path and
    # returns a ModuleSpec (describing where the module lives and which loader
    # handles it) or None if missing:
    #
    #     Suppose you call spec = importlib.util.find_spec("sqlite3").
    #     spec is a ModuleSpec pointing to sqlite3/__init__.py, yet
    #     "sqlite3" in sys.modules stays False until you actually import it.

    json_mod = importlib.import_module("json")
    print(f"Dynamically loaded {json_mod.__name__!r}; dumps([1, 2]) -> {json_mod.dumps([1, 2])}")

    # Dynamically import "math" and "statistics" via importlib.import_module.
    # Look up factorial_fn = getattr(math_mod, "factorial") and
    # median_fn = getattr(stats_mod, "median"), call them on 5 and
    # [10, 30, 20], and print both results (expected: 120 and 20).


    # Contrast importlib.import_module("os.path") against __import__("os.path")
    # by printing both returned modules' __name__ attributes so you see why
    # importlib.import_module is the clean API for dotted submodule names.


    # Probe module availability without executing any module code:
    # - Bind sqlite_spec = importlib.util.find_spec("sqlite3")
    # - Bind missing_spec = importlib.util.find_spec("definitely_missing_plugin_xyz")
    # Assert sqlite_spec is not None and missing_spec is None, print
    # sqlite_spec.origin, and confirm "sqlite3" in sys.modules is still False.


def loading_plugins_from_disk_and_reload() -> None:

    # Sometimes a user drops a standalone .py plugin file into a folder that is
    # NOT on sys.path. importlib.util lets you load that file explicitly in
    # four steps:
    # - spec = importlib.util.spec_from_file_location("my_plugin", path)
    # - mod = importlib.util.module_from_spec(spec)
    # - sys.modules["my_plugin"] = mod
    # - spec.loader.exec_module(mod)
    #
    # Registering sys.modules[name] = mod BEFORE calling exec_module(mod) is a
    # subtle requirement: decorators like @dataclass and typing.get_type_hints
    # look up the module in sys.modules while the class body is executing!
    #
    # Once a module is loaded, importlib.reload(mod) re-executes its source
    # inside the SAME existing module object (mod.__dict__). Watch the trap:
    #
    #     Suppose mod.py defines VERSION = 1 and another file already ran
    #     from mod import VERSION.
    #     After mod.py is edited to VERSION = 2 and importlib.reload(mod) runs,
    #     mod.VERSION updates to 2, but any earlier 'from mod import VERSION'
    #     local binding stays stuck at 1, and existing class instances still
    #     point to the old class object created before reload().

    starter_plugin_src = '"""Temporary dynamic plugin."""\n\ndef ping() -> str:\n    return "pong"\n'
    with tempfile.TemporaryDirectory() as tmp_dir:
        starter_path = Path(tmp_dir) / "starter_plugin.py"
        starter_path.write_text(starter_plugin_src, encoding="utf-8")
        starter_spec = importlib.util.spec_from_file_location("starter_plugin", starter_path)
        print("Starter plugin spec prepared:", starter_spec.name if starter_spec is not None else None)

    # Load a custom plugin file from an isolated TemporaryDirectory:
    # - Write plugin_path = Path(tmp_dir) / "sample_plugin.py" containing a
    #   1-line module docstring and def run_hook(x: int) -> int: return x * 10.
    # - Build spec = importlib.util.spec_from_file_location("sample_plugin", plugin_path).
    # - Guard if spec is not None and spec.loader is not None:, create
    #   plugin_mod = importlib.util.module_from_spec(spec), register
    #   sys.modules["sample_plugin"] = plugin_mod, run
    #   spec.loader.exec_module(plugin_mod), and print plugin_mod.__doc__ and
    #   plugin_mod.run_hook(7) (expected: 70).
    # - Clean up sys.modules.pop("sample_plugin", None) in a finally: block so
    #   the deleted temp module does not linger in sys.modules.


    # Test importlib.reload(plugin_mod) while the temporary file still exists:
    # - Save old_hook = plugin_mod.run_hook before editing the file.
    # - Overwrite plugin_path so run_hook returns x * 100, then call
    #   reloaded = importlib.reload(plugin_mod).
    # - Assert reloaded is plugin_mod, and print both plugin_mod.run_hook(7)
    #   (expected: 700) and old_hook(7) (still 70!) to observe the stale
    #   reference catch first-hand.


def package_resources_and_metadata() -> None:

    # Packages often ship non-code data files (SQL schemas, templates, JSON
    # lookup tables). Reaching for Path(__file__).parent / "data/banner.txt"
    # breaks the moment your package runs from inside a zipapp bundle or custom
    # loader where __file__ is not a normal directory on disk.
    #
    # importlib.resources solves this cleanly:
    # - importlib.resources.files(pkg) returns a Traversable object rooted at
    #   the package. You navigate with .joinpath("data", "banner.txt") and read
    #   directly with .read_text(encoding="utf-8") or .read_bytes().
    # - If a C library requires a real OS filesystem path, wrap the resource in
    #   with importlib.resources.as_file(res) as disk_path: so Python yields
    #   the path directly (or extracts a temporary file when zipped) and cleans
    #   it up automatically on exit.
    #
    # For inspecting installed distributions (version numbers, CLI entry
    # points, plugin groups) without importing their code, use
    # importlib.metadata. Always guard version() lookups with
    # importlib.metadata.PackageNotFoundError because minimal environments may
    # not have optional packages like pip installed.

    json_root = importlib.resources.files("json")
    print(f"importlib.resources root for stdlib json package: {json_root.name!r}")

    # Build a tiny temporary package on sys.path and read bundled data with
    # importlib.resources:
    # - Inside with tempfile.TemporaryDirectory() as tmp_dir:, create
    #   pkg_dir = Path(tmp_dir) / "demo_res_pkg" with an empty __init__.py and
    #   a nested file pkg_dir / "data" / "banner.txt" containing
    #   "Hello from importlib.resources!".
    # - Temporarily insert tmp_dir at sys.path[0] inside try ... finally:
    #   (removing tmp_dir from sys.path and calling
    #   sys.modules.pop("demo_res_pkg", None) in finally:).
    # - Call importlib.invalidate_caches(), then read the banner using
    #   banner_res = importlib.resources.files("demo_res_pkg").joinpath("data", "banner.txt")
    #   and print banner_res.read_text(encoding="utf-8").


    # Materialize banner_res onto a concrete Path using
    # with importlib.resources.as_file(banner_res) as disk_path:
    # Print disk_path.name and disk_path.stat().st_size to practice the pattern
    # required when handing a packaged data file to external tools or C APIs.


    # Query distribution metadata safely with importlib.metadata:
    # - Call importlib.metadata.version("pip") inside
    #   try ... except importlib.metadata.PackageNotFoundError:
    #   printing either the version string or "pip not installed in this env".
    # - Inspect console_scripts = importlib.metadata.entry_points(group="console_scripts")
    #   and print len(console_scripts) along with the first three entry point
    #   names ([ep.name for ep in list(console_scripts)[:3]]).


def main() -> None:

    print("=== 1. Dynamic imports and find_spec probing ===")
    dynamic_imports_and_find_spec()

    print("\n=== 2. Loading disk plugins and importlib.reload ===")
    loading_plugins_from_disk_and_reload()

    print("\n=== 3. Bundled package resources and distribution metadata ===")
    package_resources_and_metadata()


if __name__ == "__main__":
    main()
