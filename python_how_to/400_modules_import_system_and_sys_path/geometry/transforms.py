# Submodule of geometry (400_modules_import_system_and_sys_path).
# Run in module mode from the lab directory: python -m geometry.transforms

# Inside a package, neighbor submodules commonly use relative imports with
# leading dots:
#
#     from .shapes import PI        # single dot means current package (geometry)
#     from .. import sibling_helper # two dots mean the parent package if nested
#
# Python resolves those leading dots using the module's __package__ attribute.
# When you run a submodule file directly via:
#     python 400_modules_import_system_and_sys_path/geometry/transforms.py
# Python sets __name__ to "__main__" and leaves __package__ empty (None or ""),
# so executing from .shapes import PI immediately fails with:
#     ImportError: attempted relative import with no known parent package
#
# Running the exact same file in module mode from inside the lab directory via
# python -m geometry.transforms sets __package__ to "geometry", so relative
# imports resolve cleanly.

from .shapes import PI

# Minimal anchor constants proving relative import wiring works on first run.
DEFAULT_SCALE: float = 1.0
UNIT_CIRCLE_AREA: float = PI * DEFAULT_SCALE * DEFAULT_SCALE

# After defining Circle in geometry/shapes.py, extend the relative import above
# to import Circle alongside PI: from .shapes import Circle, PI


# Define def scale_circle(c: Circle, factor: float) -> Circle: returning a new
# Circle(radius=c.radius * factor) without mutating c (which is frozen).
# Raise ValueError("factor must be positive") if factor <= 0.0.


# Define def unit_circle() -> Circle: returning Circle(radius=DEFAULT_SCALE)
# as a convenience factory built on this submodule's anchor constant.


# Terminal experiment: try running this file directly with
# python 400_modules_import_system_and_sys_path/geometry/transforms.py
# to observe the relative-import ImportError first-hand, then change into
# 400_modules_import_system_and_sys_path and run python -m geometry.transforms.
