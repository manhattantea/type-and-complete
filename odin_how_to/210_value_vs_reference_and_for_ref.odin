// odin run 210_value_vs_reference_and_for_ref.odin -file

package main

import "core:fmt"

/*
Understanding value copies versus reference views—and when to reach for
for &v—prevents several subtle bugs when moving to Odin from C, Python, or JS.

Fixed arrays ([N]T) and structs are pure value types: passing them to a
procedure or assigning b := a copies every byte. Slices ([]T) are 16-byte
headers pointing to shared memory, so copying a slice—or copying a struct that
holds a slice—copies only the header, leaving both copies pointing at the
same backing array.

Meanwhile, in collection loops, for v in items binds v as a read-only copy,
whereas for &v in items binds v directly as a mutable reference of type T
(not ^T) aliased to each slot in memory.

This Primer is split into three focused sections called from main at the bottom.
*/

Item :: struct {
	id: int,
	hp: int,
}

Packet :: struct {
	id:      int,
	payload: []int,
}

value_copies_and_proc_params :: proc() {

	/*
	Because [N]T and struct values copy all of their data on assignment and
	procedure calls, mutating a parameter copy inside a procedure never affects
	the caller's variable:

	    Suppose nums := [3]int{11, 22, 33}:
	        try_zero_array(nums)   // receives a copy; caller's nums stays {11, 22, 33}
	        zero_slice(nums[:])    // receives 16-byte view; caller's nums becomes {0, 0, 0}

	When you want a procedure to modify the caller's elements, accept either a
	pointer ^[N]T (which locks the length to N) or a slice []T (which works on
	any length).
	*/

	// Starter anchor: assigning a struct duplicates all of its fields by value.
	starter := Item{id = 0, hp = 100}
	copy_item := starter
	copy_item.hp = 50
	fmt.printfln("starter=%v, copy_item=%v", starter, copy_item)

	// Define a helper procedure try_zero_array :: proc(a: [3]int) that copies
	// a into a local temp := a, sets temp[0] = 0, and prints temp.


	// Define two mutating helpers:
	// zero_fixed_ptr :: proc(a: ^[3]int) setting a[0] = 0 via auto-dereference
	// zero_slice :: proc(s: []int) using for &val in s { val = 0 }


	// Define heal_item_ptr :: proc(it: ^Item, bonus: int) that adds bonus to
	// it.hp via pointer auto-dereference. Declare nums := [3]int{11, 22, 33},
	// call try_zero_array(nums) and print nums, then call zero_fixed_ptr(&nums)
	// and zero_slice(nums[:]), and test heal_item_ptr(&copy_item, 25).
}

for_ref_across_collections :: proc() {

	/*
	When we write for &val in items, Odin does NOT bind val as a pointer ^T;
	instead, val has type T directly, bound as a mutable reference straight to
	that slot inside items! That means you write val += 1 or item.hp += 25
	directly—never val^ += 1—while &val gives the exact memory address of the
	slot.

	    Suppose party := [2]Item{{1, 50}, {2, 60}}:
	        for &member in party {
	            member.hp += 25   // mutates party directly -> hp becomes 75, 85
	        }

	The exact same &val syntax works across fixed arrays [N]T, slices []T,
	dynamic arrays [dynamic]T, maps (for k, &v in m), and nested 2D grids.
	*/

	// Starter anchor: mutate a fixed array in place using for &n in sample_arr.
	sample_arr := [2]int{5, 10}
	for &n in sample_arr {
		n *= 2
	}
	fmt.printfln("Doubled sample_arr: %v", sample_arr)

	// Declare party := [3]Item{{1, 50}, {2, 60}, {3, 70}}. Run a loop using
	// for &member, idx in party to add 25 to member.hp in place. Print %T of
	// member (confirms Item, not ^Item!) and compare &member against &party[idx]
	// to verify they share the exact same address, then print party.


	// Take a slice view mid_party := party[1:] and run for &m in mid_party to
	// subtract 5 from m.hp, printing party afterward to confirm slice reference
	// iteration updates the backing array.


	// Create roster := make([dynamic]Item) with defer delete(roster), append two
	// Item values, and heal every unit in place with for &unit in roster.


	// Create scores := make(map[string]int) with defer delete(scores), insert
	// "alice" = 10 and "bob" = 20, and double all values in place using
	// for _, &score in scores { score *= 2 }


	// Declare a 2D grid := [2][2]int{{1, 2}, {3, 4}} and add 10 to every cell in
	// place using nested reference loops: for &row in grid and for &cell in row.


	// Try uncommenting the line below to see the compiler reject mutating a
	// read-only by-value loop copy:
	// for x in [2]int{1, 2} { x += 10 }
}

struct_slice_aliasing_trap :: proc() {

	/*
	Watch out when a struct contains a slice field (such as Packet.payload: []int).
	Assigning p2 := p1 copies the Packet struct by value—which duplicates p1.id
	independently, but only copies the 16-byte slice header for payload! Both
	p1.payload and p2.payload still point at the exact same backing array.

	    Suppose raw := [3]int{1, 2, 3} and p1 := Packet{1, raw[:]}:
	        p2 := p1
	        p2.id = 2              // p1.id remains 1
	        p2.payload[0] = 999    // p1.payload[0] ALSO becomes 999!

	If a copied struct needs its own independent slice data, allocate a new
	buffer with make and copy(dst, src) into it.
	*/

	// Starter anchor: a Packet holding a view into a local stack array.
	raw := [3]int{1, 2, 3}
	p1 := Packet{id = 1, payload = raw[:]}
	fmt.printfln("p1 before copy: %v", p1)

	// Assign p2 := p1, then set p2.id = 2 and p2.payload[0] = 999.
	// Print both p1 and p2 to observe that p1.id stayed 1 while p1.payload[0]
	// changed alongside p2.payload[0].


	// Break the aliasing cleanly: allocate buf2 := make([]int, len(p1.payload))
	// with defer delete(buf2), call copy(buf2, p1.payload), assign
	// p2.payload = buf2, mutate p2.payload[1] = 888, and print both p1 and p2
	// to verify p1.payload is now isolated.
}

main :: proc() {

	fmt.println("=== 1. Value copies and procedure parameters ===")
	value_copies_and_proc_params()

	fmt.println("\n=== 2. Reference loops across collections ===")
	for_ref_across_collections()

	fmt.println("\n=== 3. Struct-containing-slice aliasing trap ===")
	struct_slice_aliasing_trap()
}
