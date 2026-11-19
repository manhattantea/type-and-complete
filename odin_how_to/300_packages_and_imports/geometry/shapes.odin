package geometry

/*
Every .odin file inside the geometry/ subdirectory declares package geometry.
Because geometry/ is a separate folder, Odin treats it as its own package
that callers pull in via import "geometry" (relative to the importing package).

By default, every top-level constant, struct, and procedure in a package is
exported to callers that import it. Any type you define here (such as Point2D,
Circle, or Rectangle) becomes part of package geometry's public interface.
*/

// Minimal anchor constant read directly by main.odin:

PI :: 3.141592653589793

// Define a struct Point2D :: struct { x, y: f32 } to represent a 2D point
// shared across shapes in package geometry.


// Define a struct Circle :: struct { center: Point2D, radius: f32 } (or start
// with radius: f32 if you prefer) and a procedure circle_area :: proc(c: Circle) -> f32
// that computes and returns PI * c.radius * c.radius.


// Define a struct Rectangle :: struct { width, height: f32 } along with two
// procedures: rectangle_area :: proc(r: Rectangle) -> f32 (r.width * r.height)
// and rect_perimeter :: proc(r: Rectangle) -> f32 (2 * (r.width + r.height)).
