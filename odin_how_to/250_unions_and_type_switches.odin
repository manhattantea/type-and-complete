// odin run 250_unions_and_type_switches.odin -file

package main

import "core:fmt"

/*
Unlike C's untagged union (which forces you to track the active member by hand),
Odin's 'union { T1, T2, ... }' is a safe tagged (discriminated) union. It packs
a hidden integer tag alongside a buffer large enough for the largest variant,
preventing you from reading a Circle as a Rect by mistake.

Three union features shape everyday Odin code:
By default every union can be 'nil' (no active variant), unless you opt out
with '#no_nil'. Multiple error enums with a zero 'None' value combine cleanly
with '#shared_nil' so any '.None' equals 'nil'. And 'switch &v in u' hands you
a mutable pointer to the active payload in place.
*/

Circle :: struct {
	radius: f32,
}

Rect :: struct {
	w, h: f32,
}

Shape :: union {
	Circle,
	Rect,
}

tagged_unions_and_type_assertions :: proc() {

	/*
	A zero-initialized 's: Shape' starts as 'nil'. Assigning 's = Circle{radius = 5.0}'
	writes the Circle bytes into the union storage and flips the hidden tag.

	When you only expect one specific variant, a comma-ok type assertion checks
	the hidden tag safely at runtime:
	    Suppose unit_shape: Shape = Rect{w = 2.0, h = 3.0}
	    r, ok := unit_shape.(Rect)     // r is Rect{2.0, 3.0}, ok is true
	    c, ok2 := unit_shape.(Circle)  // c is zeroed Circle{}, ok2 is false

	Pairing a type assertion with 'or_else' supplies a default value in one
	expression ('s.(Rect) or_else Rect{w = 1, h = 1}'). By contrast, omitting
	', ok' and 'or_else' (writing 's.(Circle)' alone) panics if the active tag
	is anything else!
	*/

	// Starter tagged union holding a Rect variant and reporting size_of:
	unit_shape: Shape = Rect{w = 2.0, h = 3.0}
	fmt.printfln("Starter shape: %v (size_of(Shape)=%v bytes)", unit_shape, size_of(Shape))

	// Declare s: Shape = Circle{radius = 5.0} and a nil shape empty_shape: Shape.
	// Verify empty_shape == nil, extract c, ok := s.(Circle), and compute an
	// inline fallback using rect_val := s.(Rect) or_else Rect{w = 1, h = 1}.
	// Print c, ok, and rect_val.


	// Try uncommenting below to observe the single-value assertion runtime panic:
	// bad_circle := unit_shape.(Circle)
	// fmt.println(bad_circle)
}

type_switches_and_in_place_mutation :: proc() {

	/*
	When you need to handle every possible variant of a union, use a type switch
	('switch v in s'). Odin checks at compile time that you cover the variants
	(or add a default 'case:' or '#partial switch'). Because Shape is a normal
	nullable union, include 'case nil:' for the unset state.

	Notice the difference between by-value and by-reference binding:
	    Suppose s: Shape = Circle{radius = 4.0}:
	        switch v in s {
	        case Circle: // v is a read-only copy of Circle; cannot mutate s
	        }
	        switch &v in s {
	        case Circle: v.radius *= 2.0   // s now holds Circle{radius = 8.0}!
	        }
	Putting '&' in front of the bound variable 'v' gives you a pointer straight
	into the union's active payload so edits persist in 's'.
	*/

	// Declare a slice of shapes:
	// shapes := []Shape{Circle{radius = 3.0}, Rect{w = 4.0, h = 5.0}, nil}
	// Loop over shapes with: for &s in shapes
	// Inside a first 'switch &v in s', double v.radius for Circle and scale
	// v.w *= 2.0 for Rect (leaving case nil: empty).


	// Next, write a helper procedure at file scope:
	// shape_area :: proc(s: Shape) -> f32
	// returning 3.14159 * v.radius * v.radius for Circle, v.w * v.h for Rect, and
	// 0.0 for nil. Call shape_area on each element of shapes and print the areas.


	// Practice reassigning a union variable across types: start with
	// current: Shape = Circle{radius = 2.0}, overwrite it with
	// current = Rect{w = 6.0, h = 2.0}, then reset it to current = nil, checking
	// shape_area(current) after each step.
}

no_nil_ast_and_shared_nil_errors :: proc() {

	/*
	Two union directives tune how 'nil' behaves:

	When we put '#no_nil' on a union ('Expr :: union #no_nil { Int_Lit, Add_Expr }'),
	it removes the empty 'nil' state completely. A default-initialized Expr starts
	as the very first variant (Int_Lit{0}) instead of nil, and 'switch v in expr'
	never needs a 'case nil:' arm—ideal for AST nodes where every expression
	must always be a valid node! Because Add_Expr stores child pointers ('^Expr')
	rather than value-embedded Exprs, the recursive type has a fixed size.

	Conversely, when we put '#shared_nil' on a union of error enums:
	    Suppose Net_Error :: enum { None, Timeout }
	    and Disk_Error :: enum { None, Full }
	    and App_Error :: union #shared_nil { Net_Error, Disk_Error }
	In Odin, every error enum sets 'None = 0'. Without #shared_nil, assigning
	Net_Error.None to App_Error would make err != nil (it holds an active
	Net_Error variant whose value is .None)! With #shared_nil, every variant's
	zero value merges into the union's single 'nil' state so err == nil is true.
	*/

	// Build a #no_nil AST expression union at file scope:
	// Int_Lit  :: struct { value: int }
	// Add_Expr :: struct { left, right: ^Expr }
	// Mul_Expr :: struct { left, right: ^Expr }
	// Expr     :: union #no_nil { Int_Lit, Add_Expr, Mul_Expr }
	// Write a recursive evaluator at file scope:
	// eval_expr :: proc(e: Expr) -> int
	// Notice you do not need 'case nil:' inside eval_expr because Expr is #no_nil!


	// Construct the AST for (2 + 3) * 4 on the stack here:
	// e2: Expr = Int_Lit{2}, e3: Expr = Int_Lit{3}, e4: Expr = Int_Lit{4}
	// sum_node: Expr = Add_Expr{left = &e2, right = &e3}
	// root: Expr = Mul_Expr{left = &sum_node, right = &e4}
	// Print eval_expr(root) (expected: 20) and also declare zero_expr: Expr to
	// verify eval_expr(zero_expr) == 0 (first variant Int_Lit{0}, not nil!).


	// Define Net_Error :: enum { None, Timeout }, Disk_Error :: enum { None, Full },
	// and App_Error :: union #shared_nil { Net_Error, Disk_Error } at file scope.
	// Assign ok_err: App_Error = Net_Error.None and fail_err: App_Error = Disk_Error.Full.
	// Print ok_err == nil (expected: true thanks to #shared_nil) and fail_err != nil.
}

main :: proc() {

	fmt.println("=== 1. Tagged unions and type assertions ===")
	tagged_unions_and_type_assertions()

	fmt.println("\n=== 2. Type switches and in-place mutation ===")
	type_switches_and_in_place_mutation()

	fmt.println("\n=== 3. #no_nil AST unions and #shared_nil errors ===")
	no_nil_ast_and_shared_nil_errors()
}
