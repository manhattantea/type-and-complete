// odin run 520_slice_and_sort_algorithms.odin -file

package main

import "core:fmt"
import "core:slice"

/*
An Odin slice '[]T' is a lightweight {data, len} view over contiguous memory.
Because it is just a view, 'core:slice' provides generic algorithms that sort,
deduplicate, search, reverse, and compare elements right inside the caller's
existing buffer without hidden heap allocations.

Only helpers that explicitly create a copy—such as 'slice.clone'—touch
'context.allocator' and return memory you must free with 'defer delete(...)'.
*/

Score_Entry :: struct {
	name:   string,
	points: int,
}

sorting_dedup_and_binary_search :: proc() {

	/*
	'slice.sort(s)' sorts any ordered slice ascending in place. Once sorted,
	'slice.binary_search(s, target)' finds a value in O(log N) steps and
	returns '(index: int, found: bool)'.

	When we call 'slice.unique(s)' on a sorted slice, it compacts adjacent
	equal elements toward the front in place and returns a shortened sub-slice
	's[:unique_count]' with zero heap allocations:

	    Suppose sorted := [5]int{1, 1, 2, 3, 3}:
	        uniq := slice.unique(sorted[:])
	        // uniq is {1, 2, 3} (len 3); sorted's backing array still holds 5 slots

	Always sort before calling 'slice.unique' or 'slice.binary_search', because
	both assume equal items sit together and elements increase monotonically.
	*/

	sample_ranks := [3]int{1, 2, 3}
	fmt.printfln("Starter ranks sorted: %v", slice.is_sorted(sample_ranks[:]))

	// Sort nums := [6]int{50, 10, 42, 5, 99, 12} ascending using slice.sort(nums[:]).
	// Verify with slice.is_sorted(nums[:]), then search for 42 and missing 77 via:
	// idx, found := slice.binary_search(nums[:], 42)
	// Print the sorted slice, both search results, and also see what binary_search
	// returns on an unsorted slice so you never forget the sorted precondition.


	// Clone, sort, and deduplicate without mutating the original array:
	// declare raw := [8]int{4, 1, 4, 2, 1, 3, 2, 4}
	// Make a heap copy with: cloned := slice.clone(raw[:])
	// Register defer delete(cloned) immediately, sort cloned with slice.sort(cloned),
	// deduplicate in place via uniq := slice.unique(cloned), and print both raw and uniq.
}

custom_comparators_and_keys :: proc() {

	/*
	For structs or custom orderings, 'core:slice' gives you two options:
	- 'slice.sort_by(s, less_proc)' takes a comparator 'proc(a, b: E) -> bool'
	  returning true when 'a' must come before 'b' (great for multi-field tie-breaking).
	- 'slice.sort_by_key(s, key_proc)' takes a single-field extractor
	  'proc(e: E) -> K' and sorts ascending by that extracted key.
	*/

	top_entry := Score_Entry{name = "Ada", points = 900}
	fmt.printfln("Starter top entry: %s (%d pts)", top_entry.name, top_entry.points)

	// Declare entries := [4]Score_Entry with two players tied on points
	// (for example Ada=900, Ben=1200, Cy=900, Dee=450).
	// Sort entries[:] descending by .points using slice.sort_by, breaking ties
	// alphabetically by a.name < b.name when a.points == b.points, and print entries.


	// Re-sort entries[:] by name ascending using slice.sort_by_key:
	// slice.sort_by_key(entries[:], proc(e: Score_Entry) -> string { return e.name })
	// Print entries, then sort by numeric key (-e.points) to order high-to-low.


	// Test descending primitive sorting with slice.reverse_sort on [5]int{3, 9, 1, 7, 4}
	// and print the sorted array.
}

mutation_cloning_and_reinterpretation :: proc() {

	/*
	When you need to inspect raw bytes inside a typed buffer (for hashing,
	checksums, or binary network packets), 'slice.reinterpret([]Dst, src)' creates
	a new slice view over the exact same memory without copying a single byte.

	    Suppose pair := [2]u16{0x0102, 0x0304}:
	        bytes := slice.reinterpret([]u8, pair[:])
	        // len(bytes) is 4 (automatically scaled by size_of(u16) / size_of(u8))

	Because 'slice.reinterpret' shares memory, mutating 'bytes[0]' directly
	alters 'pair[0]'.
	*/

	pair := [2]u16{0x0102, 0x0304}
	pair_bytes := slice.reinterpret([]u8, pair[:])
	fmt.printfln("Starter reinterpret: %d u16s -> %d bytes", len(pair), len(pair_bytes))

	// Practice slice.reverse, slice.equal, and slice.fill:
	// declare items := [5]int{1, 2, 3, 4, 5}
	// Reverse items[:] in place with slice.reverse(items[:]), check equality against
	// [5]int{5, 4, 3, 2, 1} using slice.equal, then overwrite all slots with
	// slice.fill(items[:], -1) and print items.


	// Inspect host endianness with slice.reinterpret:
	// declare words := [2]u32{0xAABBCCDD, 0x11223344}
	// Reinterpret as bytes via raw_bytes := slice.reinterpret([]u8, words[:])
	// Print len(raw_bytes) and loop over raw_bytes printing each byte as %02x
	// to observe little-endian byte order in memory.
}

main :: proc() {

	fmt.println("=== 1. Sorting, dedup, and binary search ===")
	sorting_dedup_and_binary_search()

	fmt.println("\n=== 2. Custom comparators and keys ===")
	custom_comparators_and_keys()

	fmt.println("\n=== 3. Mutation, cloning, and reinterpretation ===")
	mutation_cloning_and_reinterpretation()
}
