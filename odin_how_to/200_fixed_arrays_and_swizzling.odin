// odin run 200_fixed_arrays_and_swizzling.odin -file

package main

import "core:fmt"

/*
Fixed arrays in Odin are declared as [N]T, where N is a compile-time constant
length. Unlike C arrays (which silently decay into raw pointers whenever you
pass them around or assign them), an Odin fixed array is a genuine value type:
all N elements sit inline on the stack or inside a struct, and assigning b := a
copies every element cleanly.

Because fixed arrays know their exact length at compile time, Odin also equips
them with built-in element-wise vector math, direct == comparison, shader-style
swizzling up to 4 components, and contiguous multi-dimensional grids.

This Primer is split into three focused sections called from main at the bottom.
*/

value_arrays_and_literals :: proc() {

	/*
	You can declare a fixed array with an explicit count like [3]f32{1, 2, 3},
	or write [?]T{...} to let the compiler count the elements for you. When you
	only want to populate specific slots or spans in a larger table, ranged
	compound literals let you write index ranges directly inside the braces:

	    Suppose you initialize a 6-slot lookup table:
	        table := [6]int{0..=2 = 10, 4 = 99}
	    Slots 0, 1, 2 become 10; slot 4 becomes 99; slots 3 and 5 stay 0.

	Because [N]T is a true value type, assigning copy := original duplicates the
	backing elements in place—mutating copy[0] never touches original[0]. You can
	also compare any two fixed arrays of the same length and comparable element
	type directly using == and !=.
	*/

	// Starter anchor: a 3D float vector ready for value checks and vector math.
	v1 := [3]f32{1.0, 2.0, 3.0}
	fmt.printfln("Starter v1: %v (len=%v, size_of=%v bytes)", v1, len(v1), size_of(v1))

	// Copy v1 into a new variable named v_copy := v1, verify v_copy == v1 is true,
	// then mutate v_copy[0] = 99.0. Print both v1 and v_copy plus v_copy == v1
	// to verify that fixed arrays copy by value and compare element-by-element.


	// Declare an inferred-length array named tags using [?]string{"alpha", "beta", "gamma"}
	// and print tags, len(tags), and size_of(tags).


	// Initialize an [8]int lookup table named buckets using ranged compound
	// literal syntax: buckets := [8]int{0..=3 = 10, 4 = 99}
	// Print buckets to confirm indices 5 through 7 are zero-initialized.
}

vector_arithmetic_and_swizzling :: proc() {

	/*
	In C++ or Python, adding two 3D vectors requires writing a Vec3 class with
	overloaded operators. In Odin, any numeric fixed array [N]T supports
	element-wise +, -, *, and / plus scalar multiplication (v * 10.0) directly.

	When working with 1 to 4 components, Odin also supports shader-style
	swizzling. When we write v.zyx or color.bgra, it means "build a new fixed
	array by picking and reordering components from v using xyzw or rgba names"
	(even repeating a slot like v.xxx). You can also swizzle on the left-hand
	side of an assignment to update multiple distinct slots at once:

	    Suppose pos := [3]f32{1.0, 2.0, 3.0}:
	        pair := pos.xy         // [2]f32{1.0, 2.0}
	        pos.xz = {99.0, 88.0}  // pos becomes [3]f32{99.0, 2.0, 88.0}

	For arbitrary index lists (or more than 4 components), the built-in
	swizzle(v, 2, 1, 0) call achieves the same reordering by integer index.
	*/

	// Starter anchor: a base vector to combine with your own vectors below.
	base := [3]f32{1.0, 2.0, 3.0}
	fmt.printfln("Base vector: %v", base)

	// Declare delta := [3]f32{4.0, 5.0, 6.0}, then compute element-wise
	// sum_vec := base + delta, diff_vec := delta - base, and scaled := base * 10.0.
	// Also compute the squared components prod := base * delta and dot product
	// dot := prod.x + prod.y + prod.z, printing all results with fmt.printfln.


	// Extract xy_pair := base.xy ([2]f32), reversed := base.zyx, and a broadcast
	// vector same_x := base.xxx. Next, mutate base in place with lvalue swizzling:
	// base.xz = {99.0, 88.0}
	// Also test reordered := swizzle(base, 2, 1, 0) and print all results.


	// Declare color_rgba := [4]u8{255, 128, 64, 255}, reorder it into BGRA
	// byte order in a single expression using color_bgra := color_rgba.bgra,
	// halve its RGB brightness with color_rgba.rgb /= 2, and print both arrays.


	// Try uncommenting each line below one at a time to see the compiler catch
	// out-of-range component names and duplicate lvalue swizzle targets:
	// bad_component := base.w
	// base.xx = {1.0, 2.0}
}

multidimensional_grids :: proc() {

	/*
	A 2D fixed array is written [Rows][Cols]T—for example, [3][4]int represents
	3 rows of 4 integers laid out back-to-back in row-major order inside one
	contiguous block of memory (size_of([3][4]int) is 12 * size_of(int)).

	    Suppose tile_map := [2][3]int{{1, 2, 3}, {4, 5, 6}}:
	        tile_map[1][0]       // reads row 1, col 0 -> 4
	        tile_map[0] * 2      // row 0 arithmetic -> [3]int{2, 4, 6}

	Because each row grid[r] is itself a [Cols]T fixed array, you can index a
	single cell with grid[r][c], loop row-by-row with for row in grid, swap two
	rows in one line (grid[0], grid[1] = grid[1], grid[0]), or apply array
	arithmetic to entire rows at once.
	*/

	// Starter anchor: a 2x2 identity matrix stored flat on the stack.
	identity := [2][2]int{{1, 0}, {0, 1}}
	fmt.printfln("2x2 identity: %v (size_of=%v bytes)", identity, size_of(identity))

	// Declare grid: [3][3]int, assign grid[1][1] = 5 and grid[0][2] = 9,
	// then print grid, len(grid) (notice len is 3 rows, not 9 cells!), and
	// size_of(grid) (9 * size_of(int)).


	// Walk grid with nested coordinate loops (for row_vals, y in grid and
	// for cell, x in row_vals) to find and print the (y, x) coordinates of any
	// non-zero cell.


	// Build a [3][4]int table named matrix_2d and fill every cell using nested
	// range loops: for row in 0..<3 and for col in 0..<4
	// Set matrix_2d[row][col] = row * 4 + col, then iterate row-by-row using
	// for row_vals, y in matrix_2d to print each row index and row on its own line.


	// Combine two rows of matrix_2d using fixed-array arithmetic:
	// combined_row := matrix_2d[0] + matrix_2d[2]
	// Swap row 0 and row 2 with matrix_2d[0], matrix_2d[2] = matrix_2d[2], matrix_2d[0]
	// and print combined_row plus the updated matrix_2d.


	// Define a helper procedure grid_sum :: proc(g: [3][3]int) -> int
	// using nested collection loops (for row in g { for cell in row { ... } })
	// and call grid_sum(grid) to print the total across all 9 cells.
}

main :: proc() {

	fmt.println("=== 1. Value arrays and compound literals ===")
	value_arrays_and_literals()

	fmt.println("\n=== 2. Vector arithmetic and swizzling ===")
	vector_arithmetic_and_swizzling()

	fmt.println("\n=== 3. Multidimensional grids ===")
	multidimensional_grids()
}
