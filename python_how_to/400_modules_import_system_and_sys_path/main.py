# python 400_modules_import_system_and_sys_path/main.py

# Welcome to Python's module and import system lab. Unlike Odin or Go, where
# every source file in a folder shares a single package namespace automatically,
# every .py file in Python is an isolated module that must be imported by name.
#
# Suggested order across the 5 files in this lab:
# sibling_helper.py -> geometry/shapes.py -> geometry/transforms.py ->
# geometry/__init__.py -> the sections inside main.py below.

import sys

import geometry
import geometry.shapes as shapes_mod
import sibling_helper


def sibling_and_package_facade() -> None:

    # When you run python 400_modules_import_system_and_sys_path/main.py, Python
    # inserts the directory containing main.py at sys.path[0], followed by
    # PYTHONPATH, the standard library, and site-packages. That is why both
    # import sibling_helper and import geometry succeed regardless of your
    # current working directory (unless python -P or PYTHONSAFEPATH=1 disables
    # script-directory insertion to block accidental shadowing).
    #
    # Re-exporting symbols inside geometry/__init__.py gives callers a stable
    # package facade (geometry.PI) without coupling them to internal file names.

    print(
        f"Anchors -> sibling ready: {sibling_helper.SIBLING_READY}, "
        f"geometry.PI: {geometry.PI:.4f}, default scale: {geometry.DEFAULT_SCALE}"
    )

    # After defining MODULE_VERSION, format_banner, and module_identity in
    # sibling_helper.py, call sibling_helper.format_banner("Import System Lab")
    # and print the banner, sibling_helper.MODULE_VERSION, and
    # sibling_helper.module_identity().


    # After implementing Circle, circle_area, circle_circumference, and
    # scale_circle and re-exporting them in geometry/__init__.py, construct
    # unit = geometry.Circle(radius=2.5), compute its area with
    # geometry.circle_area(unit), scale it with bigger = geometry.scale_circle(unit, 2.0),
    # and print both areas to confirm unit remained unchanged.


def sys_modules_and_stale_binding_trap() -> None:

    # Every imported module is cached once in the global dict sys.modules.
    # Importing geometry ten times executes geometry/__init__.py only once and
    # returns the exact same module object (checked with 'is').
    #
    # That cache interacts with a classic Python binding trap when comparing
    # 'import pkg.mod' against 'from pkg.mod import value':
    #
    #     Suppose shapes_mod.PI starts at 3.14159... and you run:
    #         from geometry.shapes import PI as local_pi
    #     Python copies the current float reference into local_pi at import
    #     time. If another module later rebinds shapes_mod.PI = 3.0, reading
    #     shapes_mod.PI sees 3.0, while local_pi stays frozen at 3.14159...!
    #
    # Rebinding local_pi does not update shapes_mod.PI either. Always import
    # the module object when you need to observe live updates to a module-level
    # variable (or during monkeypatching in tests).

    print("geometry cached in sys.modules:", sys.modules["geometry"] is geometry)

    # Prove sys.modules returns a single shared module instance:
    # - Assert sys.modules["geometry.shapes"] is geometry.shapes
    # - Assert sys.modules["geometry.shapes"] is shapes_mod
    # - Run import geometry as geo_again inside this function and assert
    #   geo_again is geometry.


    # Demonstrate the stale local-binding trap hands-on:
    # - Bind a local copy with from geometry.shapes import PI as imported_pi
    # - Save original_pi = shapes_mod.PI, then rebind shapes_mod.PI = 3.0
    # - Print both shapes_mod.PI and imported_pi to observe the mismatch
    # - Restore shapes_mod.PI = original_pi so later code sees the true value.


def sys_path_and_export_inspection() -> None:

    # sys.path is just a regular Python list of directory strings searched from
    # index 0 onward whenever an import misses sys.modules. Inspecting
    # sys.path[0] immediately reveals where Python looks first for local files.

    print("First import search root (sys.path[0]):", sys.path[0])

    # Print the first three entries of sys.path (sys.path[:3]) and check which
    # loaded module names in sys.modules start with "geometry" using a list
    # comprehension: [name for name in sys.modules if name.startswith("geometry")].


    # Once you define __all__ in geometry/__init__.py, inspect and print
    # geometry.__all__ here, and verify that "PI" and "Circle" are listed while
    # submodule names like "shapes" are kept off the public wildcard list.


def main() -> None:

    print("=== 1. Sibling modules and package facade ===")
    sibling_and_package_facade()

    print("\n=== 2. sys.modules cache and stale-binding trap ===")
    sys_modules_and_stale_binding_trap()

    print("\n=== 3. sys.path search order and package exports ===")
    sys_path_and_export_inspection()


if __name__ == "__main__":
    main()
