# Leaf submodule of geometry (400_modules_import_system_and_sys_path).

# Any folder containing an __init__.py file is a regular Python package. Inside
# that package, each .py file (shapes.py, transforms.py) is still an isolated
# submodule (geometry.shapes, geometry.transforms) rather than a merged scope.
#
# Notice how shapes.py sits at the bottom (leaf) of the dependency graph: it
# imports only from the standard library (math, and dataclasses once you add
# Circle) and knows nothing about transforms.py or main.py. Keeping data models
# in leaf submodules prevents circular imports as a package grows.
#
#     Suppose geometry/shapes.py defines PI = math.pi.
#     Any module that runs import geometry.shapes as shapes_mod reads the live
#     attribute shapes_mod.PI directly from this module's __dict__.

import math

# Minimal anchor constant shared across the geometry package.
PI: float = math.pi

# Add from dataclasses import dataclass near the top of this file, then define
# an immutable value record using @dataclass(slots=True, frozen=True):
# class Circle: with a single field radius: float.
# Using slots=True drops the per-instance __dict__, and frozen=True prevents
# callers from mutating radius in place.


# Define def circle_area(c: Circle) -> float: returning PI * c.radius * c.radius.


# Define def circle_circumference(c: Circle) -> float: returning
# 2.0 * PI * c.radius so callers can query both area and perimeter from this
# leaf submodule.
