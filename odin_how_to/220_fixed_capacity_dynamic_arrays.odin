// odin run 220_fixed_capacity_dynamic_arrays.odin -file

package main

import "core:container/small_array"
import "core:fmt"

/*
When you want append, pop, clear, ordered_remove, and unordered_remove with
zero heap allocations, Odin gives you a built-in fixed-capacity dynamic array:
[dynamic; N]T.

Every element plus the current length lives directly inline on the stack frame
or inside an enclosing struct—so you never call make or delete. Because cap(arr)
is fixed at N at compile time, there are no reallocations and no heap leaks.
Alongside this built-in type, core:container/small_array offers a standard
library struct Small_Array(N, T) with non-panicking bool-returning push_back.

This Primer is split into three focused sections called from main at the bottom.
*/

Packet_Batch :: struct {
	id:      int,
	samples: [dynamic; 8]int,
}

inline_dynamic_array_basics :: proc() {

	/*
	A zero-initialized stack variable buf: [dynamic; 4]string starts with
	len(buf) == 0 and cap(buf) == 4. Calling append(&buf, "hi") stores "hi" in
	the inline backing buffer and increments len to 1. Slicing buf[:] returns a
	standard []string view over the active 0..<len(buf) elements.

	    Suppose nums: [dynamic; 4]int:
	        append(&nums, 10, 20)   // len=2, cap=4, zero heap allocations
	        nums[:]                 // []int{10, 20}
	*/

	// Starter anchor: a stack-only [dynamic; 4]int ready for inline appends.
	starter_buf: [dynamic; 4]int
	append(&starter_buf, 10, 20)
	fmt.printfln("starter_buf: %v (len=%v, cap=%v, size_of=%v)", starter_buf[:], len(starter_buf), cap(starter_buf), size_of(starter_buf))

	// Declare recent_events: [dynamic; 4]string (no make or delete needed).
	// Append "login", "click_item", "add_to_cart", and "checkout" using
	// append(&recent_events, ...), then print recent_events[:], len, and cap.


	// Pop the last event with pop(&recent_events), test safe popping with
	// ev, ok := pop_safe(&recent_events), and loop over the remaining active
	// items with for ev_item, idx in recent_events[:] to print index and value.


	// Mutate active elements in place using for &ev_item in recent_events[:]
	// (or for &ev_item in recent_events), then append a slice splat
	// append(&recent_events, ..[]string{"retry"}) if space permits.


	// Compare ordered_remove(&recent_events, 0) vs unordered_remove(&recent_events, 0),
	// then call clear(&recent_events) and verify len is 0 while cap stays 4.


	// Try uncommenting the lines below to see the bounds-check panic when
	// appending past fixed capacity N:
	// overflow: [dynamic; 1]int
	// append(&overflow, 1, 2)
}

struct_embedded_fixed_dynamic :: proc() {

	/*
	Embedding [dynamic; N]T inside a struct is one of Odin's cleanest patterns
	for fixed-budget systems code (entity inventories, frame command queues,
	collision contact lists). Because the backing storage sits inside the struct
	itself rather than behind a heap pointer, copying the struct with b := a
	produces a completely independent copy with zero aliasing and zero cleanup:

	    Suppose batch := Packet_Batch{id = 1} with samples {42}:
	        batch_copy := batch
	        append(&batch_copy.samples, 99)   // batch.samples stays {42}

	Notice how much safer that is than embedding a []T or [dynamic]T field,
	where copying the struct would alias the heap buffer!
	*/

	// Starter anchor: a Packet_Batch struct carrying an inline [dynamic; 8]int.
	batch := Packet_Batch{id = 1}
	append(&batch.samples, 42)
	fmt.printfln("batch %v samples: %v (struct size_of=%v bytes)", batch.id, batch.samples[:], size_of(batch))

	// Assign batch_copy := batch, append 99 into batch_copy.samples, and mutate
	// batch_copy.samples in place with for &s in batch_copy.samples { s += 1 }.
	// Print both batch.samples[:] and batch_copy.samples[:] to confirm zero aliasing.


	// Define Inventory :: struct { owner: string, items: [dynamic; 6]string }
	// and a helper add_loot :: proc(inv: ^Inventory, item: string) -> bool that
	// checks len(inv.items) < cap(inv.items) before calling append(&inv.items, item).
	// Test add_loot on a local Inventory up to capacity 6 and verify the 7th
	// call returns false safely instead of panicking.
}

small_array_contrast :: proc() {

	/*
	How does built-in [dynamic; N]T compare to small_array.Small_Array(N, T)?
	Built-in [dynamic; N]T integrates with len, cap, append, and [:] slicing
	directly, and panics if you append past N. small_array.Small_Array(N, T)
	is a regular library struct whose push_back procedure returns a bool
	(false when full) instead of panicking, making overflow handling explicit.
	Both store N elements plus an integer length inline with identical stack
	footprint and zero heap allocations.
	*/

	// Starter anchor: a stack-allocated Small_Array from core:container/small_array.
	sa: small_array.Small_Array(4, int)
	small_array.push_back(&sa, 100)
	small_array.push_back(&sa, 200)
	fmt.printfln("Small_Array anchor: %v (len=%v)", small_array.slice(&sa), small_array.len(sa))

	// Compare size_of([dynamic; 4]int) against size_of(small_array.Small_Array(4, int))
	// and size_of([dynamic]int) (the 32-byte heap header) by printing all three.


	// Push 300, 400, and an overflow 500 into sa using small_array.push_back(&sa, ...),
	// capturing and printing the returned bool on each call to observe false
	// when capacity 4 is reached.


	// Pop with small_array.pop_back_safe(&sa), inspect slot 0 via
	// ptr := small_array.get_ptr(&sa, 0), remove slot 0 using
	// small_array.unordered_remove(&sa, 0), print small_array.slice(&sa), and
	// reset sa with small_array.clear(&sa).
}

main :: proc() {

	fmt.println("=== 1. Inline fixed-capacity dynamic arrays ===")
	inline_dynamic_array_basics()

	fmt.println("\n=== 2. Struct-embedded [dynamic; N]T ===")
	struct_embedded_fixed_dynamic()

	fmt.println("\n=== 3. Built-in [dynamic; N]T vs Small_Array ===")
	small_array_contrast()
}
