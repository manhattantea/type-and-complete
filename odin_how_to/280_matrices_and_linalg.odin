// odin run 280_matrices_and_linalg.odin -file

package main

import "core:fmt"
import "core:math/linalg"

/*
For 2D and 3D graphics, physics, and simulation code, Odin builds matrices
directly into the type system as 'matrix[Rows, Cols]T' (supporting sizes 1..=4
in each dimension) alongside 'core:math/linalg':

    matrix[2, 2]f32            column-major in memory by default (OpenGL/GLSL)
    #row_major matrix[4, 4]f32  row-major in memory (Direct3D/HLSL)
    m[row, col]                 always indexed mathematically (row first, col second)
    m1 * m2, m * v              built-in matrix-matrix and matrix-vector multiplication
*/

Row_Mat2 :: #row_major matrix[2, 2]f32
Row_Mat4 :: #row_major matrix[4, 4]f32

built_in_matrices_and_memory_layout :: proc() {

	/*
	You always write matrix literals in natural mathematical row-by-row order:
	    Suppose mat := matrix[2, 2]f32{ 1, 2, 3, 4 }
	Row 0 is {1, 2} and row 1 is {3, 4}, so mat[0, 1] is 2 and mat[1, 0] is 3.

	In memory, however, Odin stores 'matrix[R, C]T' column-major by default to
	match OpenGL, Vulkan, and GLSL buffers: column 0 ({1, 3}) comes first in
	RAM, then column 1 ({2, 4}). Adding '#row_major' flips memory storage to
	row 0 ({1, 2}) followed by row 1 ({3, 4}) while keeping m[row, col] math
	identical!

	One handy shorthand: casting or assigning scalar '1' to any square matrix
	('id2: matrix[2, 2]f32 = 1' or 'matrix[4, 4]f32(1)') produces an identity
	matrix automatically.
	*/

	// Starter 2x2 identity matrix via scalar assignment + trace and determinant:
	id2: matrix[2, 2]f32 = 1
	fmt.printfln("2x2 Identity: %v (trace=%v, det=%v)", id2, linalg.trace(id2), linalg.determinant(id2))

	// Try uncommenting below to see Odin reject mismatched matrix-vector dimensions:
	// bad_mult := id2 * [3]f32{1, 2, 3}


	// Declare a 2x2 scaling matrix mat := matrix[2, 2]f32{ 2, 0, 0, 3 } and a 2D
	// point pt := [2]f32{4, 5}. Compute transformed := mat * pt and print mat,
	// transformed (expected: [8, 15]), and element mat[1, 1].


	// Inspect column-major vs #row_major memory order directly:
	// declare col_m := matrix[2, 2]f32{ 1, 2, 3, 4 } and row_m := Row_Mat2(col_m).
	// Print transmute([4]f32)col_m (expected: [1, 3, 2, 4]) alongside
	// transmute([4]f32)row_m (expected: [1, 2, 3, 4]) and confirm col_m[0, 1] == row_m[0, 1].
}

matrix_algebra_and_vectors :: proc() {

	/*
	Odin pairs built-in 'transpose(m)' with 'core:math/linalg' procedures for
	everyday linear algebra:

	    linalg.determinant(m)   signed area/volume scale factor
	    linalg.inverse(m)       multiplicative inverse when determinant != 0
	    linalg.adjugate(m)      transpose of the cofactor matrix
	    linalg.trace(m)         sum of main diagonal entries
	    linalg.dot(a, b)        vector dot product
	    linalg.cross(a, b)      3D vector cross product

	Suppose mat := matrix[2, 2]f32{ 2, 0, 0, 3 } and transformed := mat * pt:
	multiplying by linalg.inverse(mat) undoes the scale and recovers pt exactly.
	*/

	// Using shear := matrix[2, 2]f32{ 2, 1, 0, 3 } and pt := [2]f32{4, 5}:
	// compute transformed := shear * pt, det := linalg.determinant(shear),
	// inv := linalg.inverse(shear), adj := linalg.adjugate(shear), and
	// transp := transpose(shear). Print each and verify inv * transformed == pt!


	// Practice 3D vector algebra: declare a := [3]f32{1, 0, 0} and b := [3]f32{0, 1, 0},
	// compute linalg.dot(a, b) (expected: 0, perpendicular) and linalg.cross(a, b)
	// (expected: [0, 0, 1]), and also test a non-unit vector with linalg.normalize.


	// Practice matrix-matrix multiplication: declare rot90 := matrix[2, 2]f32{ 0, -1, 1, 0 }
	// and scale2 := matrix[2, 2]f32{ 2, 0, 0, 2 }. Multiply combined := rot90 * scale2
	// and apply combined * [2]f32{3, 1} (expected: [-2, 6]).


	// Practice non-square projection: declare proj := matrix[2, 3]f32{ 1, 0, 0, 0, 1, 0 }
	// and v3 := [3]f32{7, 8, 9}. Multiply flat := proj * v3 (produces [2]f32{7, 8})
	// and print flat alongside size_of(matrix[2, 3]f32) (24 bytes).
}

transforms_4x4_and_row_major_interop :: proc() {

	/*
	3D rendering pipelines compose translation, rotation, and scaling inside a
	'matrix[4, 4]f32' using 4D homogeneous points '{x, y, z, 1}'. In Odin's
	column-vector convention ('T * R * S * pt'), the rightmost matrix applies
	first (scale, then rotate, then translate).

	Look closely at how translation sits in memory:
	In default column-major 'matrix[4, 4]f32', the translation vector (tx, ty, tz)
	lives in column 3—slots 12, 13, 14 of the flat 16-float buffer. Converting to
	'Row_Mat4' (#row_major matrix[4, 4]f32) transposes the in-memory layout so
	(tx, ty, tz) moves to slots 3, 7, 11 instead, matching row-major shader APIs.
	*/

	// Build 4x4 transform matrices using core:math/linalg:
	// t_mat := linalg.matrix4_translate_f32([3]f32{10, 20, 30})
	// r_mat := linalg.matrix4_rotate_f32(1.5707963, [3]f32{0, 0, 1})
	// s_mat := linalg.matrix4_scale_f32([3]f32{2, 2, 2})
	// Compose model := t_mat * r_mat * s_mat and transform point
	// local_pt := [4]f32{1, 0, 0, 1} via world_pt := model * local_pt.
	// Print world_pt (scale [2, 0, 0], rotate +90 deg -> [0, 2, 0], translate -> [10, 22, 30, 1]).


	// Inspect 4x4 column-major vs #row_major memory layout on t_mat:
	// flat_col := transmute([16]f32)t_mat
	// row_t    := Row_Mat4(t_mat)
	// flat_row := transmute([16]f32)row_t
	// Print flat_col[12:15] vs flat_row[3], flat_row[7], flat_row[11] to verify
	// both store (10, 20, 30) in their respective memory conventions!


	// Compare element indexing on t_mat vs row_t: verify t_mat[0, 3] == row_t[0, 3]
	// (both 10) and t_mat[1, 3] == row_t[1, 3] (both 20) even though their flat
	// in-memory byte layouts differ!
}

main :: proc() {

	fmt.println("=== 1. Built-in matrices and memory layout ===")
	built_in_matrices_and_memory_layout()

	fmt.println("\n=== 2. Matrix algebra and vector operations ===")
	matrix_algebra_and_vectors()

	fmt.println("\n=== 3. 4x4 transforms and #row_major interop ===")
	transforms_4x4_and_row_major_interop()
}
