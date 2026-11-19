// odin run 225_maps.odin -file

package main

import "core:fmt"

/*
Odin includes a built-in hash table type: map[Key]Value. Any comparable type
(a type supporting ==) works directly as a key: strings, integers, enums,
pointers, fixed arrays like [2]int, and structs whose fields are all comparable.

Maps manage heap memory explicitly: allocate with make(map[K]V) and free with
defer delete(m). A zero-initialized map variable (m: map[K]V) also lazily
allocates on its first write, and still requires delete(m) once populated.
Reading a missing key never inserts a zero entry (unlike C++ std::map);
instead, Odin gives you comma-ok lookups, or_else fallbacks, and in/not_in
membership checks.

This Primer is split into three focused sections called from main at the bottom.
*/

Tile :: enum {
	Empty,
	Wall,
	Water,
	Goal,
}

Coord :: struct {
	x, y: int,
}

basic_operations_and_lookups :: proc() {

	/*
	To read safely from a map without guessing whether a key exists, use either
	val, ok := m[key] or an inline fallback val := m[key] or_else default_val.
	To test presence without extracting a value, write key in m or key not_in m.

	    Suppose scores holds {"alice": 10}:
	        v := scores["bob"] or_else -1   // v is -1; len(scores) stays 1!

	When updating values across every entry, for k, &v in m binds v directly
	as a mutable reference to the value slot inside the map bucket—allowing
	in-place updates without hashing the key a second time.
	*/

	// Starter anchor: a small string-to-int map with deferred cleanup.
	counts := make(map[string]int)
	defer delete(counts)
	counts["odin"] = 1
	fmt.printfln("Starter map: %v (len=%v)", counts, len(counts))

	// Create prices := make(map[string]int) with defer delete(prices).
	// Insert "apple" = 120, "banana" = 80, and "cherry" = 250, then print
	// prices and len(prices). Also test lazy allocation by declaring
	// lazy: map[string]int with defer delete(lazy) and writing lazy["first"] = 1.


	// Look up "banana" with comma-ok syntax (price, found := prices["banana"]),
	// test "mango" not_in prices, and read "mango" with fallback using
	// mango_price := prices["mango"] or_else 0. Print all results and verify
	// len(prices) did not grow after reading "mango".


	// Iterate over prices using for item, &cost in prices to apply a 10%
	// discount in place (cost = cost * 9 / 10), then delete "apple" with
	// delete_key(&prices, "apple") and print prices.


	// Build a word-frequency counter: declare words := []string{"go", "odin", "go", "zig", "odin"}
	// and freq := make(map[string]int) with defer delete(freq). Loop for w in words
	// and run freq[w] += 1 (unlike reading a missing key, compound assignment += 1
	// inserts 0 and increments to 1 cleanly on first sight!), then print freq.


	// Try uncommenting each line below one at a time to see the compiler reject
	// mutating a value copy without & and taking the address of a map lookup:
	// for k, v in counts { v += 1 }
	// bad_ptr := &counts["odin"]
}

clear_vs_delete_and_composite_keys :: proc() {

	/*
	Pay close attention to clear(&m) versus delete(m). Calling clear(&m) resets
	len(m) to 0 while keeping the underlying bucket allocation intact—ideal when
	you reuse a map every frame and want to avoid repeated heap allocations.
	Calling delete(m) frees the backing buffer completely (dropping cap to 0).

	Also notice how composite value types such as fixed arrays ([2]int) and
	comparable structs (Coord) work straight out of the box as map keys
	(map[[2]int]Tile or map[Coord]Tile) with zero custom hash boilerplate.
	*/

	// Starter anchor: a coordinate-keyed map storing Tile enum values.
	world := make(map[[2]int]Tile)
	defer delete(world)
	world[{0, 0}] = .Wall
	fmt.printfln("Origin tile: %v", world[{0, 0}])

	// Populate world with {1, 0} = .Empty, {2, 3} = .Water, and {5, 5} = .Goal.
	// Look up {2, 3} and missing {9, 9} using or_else .Empty, then iterate with
	// for coord, tile in world to print every stored coordinate.


	// Build a second map using the Coord struct key: grid_tags := make(map[Coord]string)
	// with defer delete(grid_tags), insert Coord{2, 4} = "Spawn", and print it.


	// Create scratch := make(map[string]int) and call reserve(&scratch, 32).
	// Insert two entries, print len(scratch) and cap(scratch), then call
	// clear(&scratch) and print len and cap again (len == 0, cap stays reserved).
	// Finally call delete(scratch) and print len and cap once more to see cap drop to 0.
}

nested_container_cleanup :: proc() {

	/*
	Maps only free their own outer table when you call delete(m). If the map's
	values are heap-allocated containers—such as map[string][dynamic]int—calling
	delete(groups) leaks every inner dynamic array! Always loop through the map
	and delete each inner [dynamic]int before calling delete(groups).

	    Suppose groups holds "evens" -> [dynamic]int{2, 4}:
	        for _, list in groups {
	            delete(list)   // frees each inner dynamic array first
	        }
	        delete(groups)     // now safe to free the outer map table

	One more Odin subtlety: indexing a map like &groups["evens"] is invalid
	because rehashing can move map buckets in memory. To append to an existing
	bucket list, either iterate with for name, &list in groups or pull the header
	out, append, and write it back: list := groups[k]; append(&list, x); groups[k] = list.
	*/

	// Create groups := make(map[string][dynamic]int), and define a helper proc
	// add_to_group :: proc(groups: ^map[string][dynamic]int, key: string, val: int)
	// that checks if key is in groups^, creates a [dynamic]int if missing, appends
	// val, and writes the updated header back into groups^[key].


	// Populate "primes" (2, 3, 5) and "squares" (1, 4, 9) using add_to_group,
	// then iterate with for _, &list in groups { append(&list, 0) } to append 0
	// directly to every bucket via reference iteration. Print groups, then clean
	// up every inner dynamic array before calling delete(groups).
}

main :: proc() {

	fmt.println("=== 1. Map basics, lookups, and in-place mutation ===")
	basic_operations_and_lookups()

	fmt.println("\n=== 2. clear vs delete and composite keys ===")
	clear_vs_delete_and_composite_keys()

	fmt.println("\n=== 3. Nested map[string][dynamic]int cleanup ===")
	nested_container_cleanup()
}
