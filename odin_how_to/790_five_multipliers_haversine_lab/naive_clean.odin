// Five Multipliers Lab — Stage 0 baseline using heap nodes and vtable dispatch

package main

/*
This file models an idiomatic object-oriented baseline where each coordinate
record is allocated individually on the heap and dispatched through an enum
tag plus a procedure pointer ('eval').

Even before looking at instruction math, notice three hardware bottlenecks
baked into this layout:
First, 'build_naive_pairs' scatters each 'Naive_Pair' across separate heap
allocations inside '[]^Naive_Pair', forcing pointer-chasing cache misses on
every iteration instead of streaming contiguous memory.
Second, switching on 'Pair_Kind' and calling 'p->eval()' blocks inlining and
inserts an indirect branch per element.
Third, adding every result into a single serial 'total: f32' chains every
loop iteration behind the previous floating-point addition latency.
*/

DEG_TO_RAD :: f32(0.017453292519943295)

Pair_Kind :: enum u8 {
	Geodesic,
	Planar,
}

Naive_Pair :: struct {
	kind: Pair_Kind,
	x0:   f32,
	y0:   f32,
	x1:   f32,
	y1:   f32,
	eval: proc(self: ^Naive_Pair) -> f32,
}

// Polynomial Haversine chord kernel (3-term Taylor sin/cos, ~1e-5 accurate on [-40, 40] deg).
// Scalar and SIMD stages share this formula so outputs match within 1e-2 across all stages.
haversine_chord_scalar :: proc(x0, y0, x1, y1: f32) -> f32 {

	dlat_half := (y1 - y0) * (0.5 * DEG_TO_RAD)
	dlon_half := (x1 - x0) * (0.5 * DEG_TO_RAD)
	lat0 := y0 * DEG_TO_RAD
	lat1 := y1 * DEG_TO_RAD

	dl2 := dlat_half * dlat_half
	sin_dlat := dlat_half * (1.0 + dl2 * (-0.16666667 + dl2 * 0.008333333))

	dn2 := dlon_half * dlon_half
	sin_dlon := dlon_half * (1.0 + dn2 * (-0.16666667 + dn2 * 0.008333333))

	l0_2 := lat0 * lat0
	cos_lat0 := 1.0 + l0_2 * (-0.5 + l0_2 * 0.041666668)

	l1_2 := lat1 * lat1
	cos_lat1 := 1.0 + l1_2 * (-0.5 + l1_2 * 0.041666668)

	return sin_dlat * sin_dlat + cos_lat0 * cos_lat1 * (sin_dlon * sin_dlon)
}

eval_geodesic_vtable :: proc(self: ^Naive_Pair) -> f32 {

	return haversine_chord_scalar(self.x0, self.y0, self.x1, self.y1)
}

eval_planar_vtable :: proc(self: ^Naive_Pair) -> f32 {

	dx := self.x1 - self.x0
	dy := self.y1 - self.y0
	return dx * dx + dy * dy
}

build_naive_pairs :: proc(coords: []Coord_Pair, alloc := context.allocator) -> []^Naive_Pair {

	pairs := make([]^Naive_Pair, len(coords), alloc)
	for c, i in coords {
		node := new(Naive_Pair, alloc)
		node^ = Naive_Pair{
			kind = .Geodesic,
			x0   = c.x0,
			y0   = c.y0,
			x1   = c.x1,
			y1   = c.y1,
			eval = eval_geodesic_vtable,
		}
		pairs[i] = node
	}
	return pairs
}

destroy_naive_pairs :: proc(pairs: []^Naive_Pair, alloc := context.allocator) {

	for p in pairs {
		free(p, alloc)
	}
	delete(pairs, alloc)
}

// Baseline Stage 0 slow path used as the reference checksum and cycle ceiling:
compute_naive_wasted :: proc(pairs: []^Naive_Pair) -> f32 {

	total: f32 = 0.0
	for p in pairs {
		switch p.kind {
		case .Geodesic:
			total += p->eval()
		case .Planar:
			total += p->eval()
		}
	}
	return total
}

// Compute and compare the memory footprint per record for Naive_Pair
// (size_of(Naive_Pair) + size_of(^Naive_Pair) plus heap allocator overhead)
// against a contiguous Coord_Pair (16 bytes), and experiment with mixing
// .Planar nodes using eval_planar_vtable to observe branch misprediction cost.
