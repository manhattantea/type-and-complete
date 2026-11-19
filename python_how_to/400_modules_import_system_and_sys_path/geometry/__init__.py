# Package marker and public re-export surface for geometry (400_modules_import_system_and_sys_path).

# When a folder contains __init__.py, Python treats it as a regular package.
# The first time any file executes import geometry, Python runs this file once,
# binds the resulting module object to the name geometry, and caches it at
# sys.modules["geometry"].
#
# Keep two subtle rules in mind when designing __init__.py:
# - Importing geometry does NOT automatically load child files like shapes.py
#   or transforms.py unless __init__.py explicitly imports them (or a caller
#   runs import geometry.shapes directly).
# - Re-exporting key symbols here (for example, from .shapes import Circle)
#   gives callers a clean facade like geometry.Circle so you can reorganize
#   internal files later without breaking external imports.
#
#     Suppose geometry/__init__.py runs from .shapes import PI.
#     Callers can write geometry.PI directly, while sys.modules now holds both
#     "geometry" and "geometry.shapes" as separate cached module objects.

# Minimal anchor re-exports keep import geometry working out of the box.
from .shapes import PI
from .transforms import DEFAULT_SCALE

# After defining Circle and circle_area in geometry/shapes.py and scale_circle
# in geometry/transforms.py, re-export them right here:
# from .shapes import PI, Circle, circle_area
# from .transforms import DEFAULT_SCALE, scale_circle


# Define __all__: list[str] listing every public symbol you want exposed on the
# geometry facade: ["PI", "DEFAULT_SCALE", "Circle", "circle_area", "scale_circle"].
# Static type checkers and from geometry import * both treat __all__ as the
# package's explicit export contract.
