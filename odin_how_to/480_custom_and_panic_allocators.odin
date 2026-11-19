// odin run 480_custom_and_panic_allocators.odin -file

package main

import "core:fmt"
import "core:mem"
import "base:runtime"

/*
Odin's allocator abstraction is intentionally tiny: every allocator in the
entire language is a 16-byte runtime.Allocator{procedure, data} struct. Because
there are no virtual base classes or heap interfaces, swapping allocators for
profiling, leak detection, arena scoping, or strict zero-allocation enforcement
costs a single assignment to context.allocator.

In this file you will inspect built-in sentinel allocators (nil_allocator and
panic_allocator), build your own wrapping Allocator_Proc, and test
mem.Rollback_Stack for LIFO and rollback stack lifetimes.
*/

// Define Counting_Allocator_Data :: struct at file scope with fields:
// backing: runtime.Allocator, alloc_calls: int, bytes_allocated: int, free_calls: int


// Define counting_allocator_proc with the exact runtime.Allocator_Proc signature on one line:
// counting_allocator_proc :: proc(allocator_data: rawptr, mode: runtime.Allocator_Mode, size, alignment: int, old_memory: rawptr, old_size: int, location := #caller_location) -> ([]byte, runtime.Allocator_Error)
// Cast allocator_data to ^Counting_Allocator_Data. When mode is .Alloc or
// .Alloc_Non_Zeroed, increment data.alloc_calls += 1 and data.bytes_allocated += size.
// When mode is .Free, increment data.free_calls += 1. Delegate every mode to:
// return data.backing.procedure(data.backing.data, mode, size, alignment, old_memory, old_size, location)

allocator_interface_and_panic_sentinel :: proc() {

	/*
	Two built-in allocators act as compile-free safety nets:
	    mem.nil_allocator()     always returns .Out_Of_Memory without crashing
	    mem.panic_allocator()   panics immediately on any allocation attempt

	Using mem.panic_allocator() inside an inner { ... } scope on context.allocator
	proves that a real-time audio callback, render loop, or stack-buffer helper
	performs zero hidden heap allocations.
	*/

	nil_alloc: runtime.Allocator = mem.nil_allocator()
	nil_buf, nil_err := make([]byte, 64, nil_alloc)
	fmt.printfln("nil_allocator returned len=%d, err=%v", len(nil_buf), nil_err)

	// Open an inner { ... } block, assign context.allocator = mem.panic_allocator(),
	// compute the sum of 0..<100 in a loop, and format the result into a stack
	// stack_buf: [64]byte buffer using fmt.bprintf to prove stack formatting
	// allocates zero heap bytes.
	//
	// Try uncommenting a heap allocation inside that block to see panic_allocator fire:
	// bad := make([]int, 4); fmt.println(len(bad))
}

building_a_counting_allocator :: proc() {

	/*
	Wrapping an existing allocator is how Odin implements Tracking_Allocator,
	mutex-guarded allocators, and budget enforcers. Suppose c_data holds
	backing = context.allocator: when a caller invokes make([]int, 16, c_alloc),
	Odin calls counting_allocator_proc(&c_data, .Alloc, 128, 8, nil, 0, loc), your
	procedure updates its counters, and then forwards the exact arguments to
	c_data.backing.procedure so the real allocator serves the bytes.
	*/

	fmt.println("Implement Counting_Allocator_Data and counting_allocator_proc above, then test below.")

	// After implementing Counting_Allocator_Data and counting_allocator_proc above,
	// initialize c_data := Counting_Allocator_Data{backing = context.allocator} and
	// c_alloc := runtime.Allocator{procedure = counting_allocator_proc, data = &c_data}.


	// Perform three allocations using c_alloc:
	// nums := make([]int, 16, c_alloc) with defer delete(nums, c_alloc)
	// raw := make([]byte, 128, c_alloc) with defer delete(raw, c_alloc)
	// scalar := new(f64, c_alloc) with defer free(scalar, c_alloc)
	// Print c_data.alloc_calls and c_data.bytes_allocated right after allocating,
	// then open an inner block so the defers run and print c_data.free_calls.


	// Bonus check: add an optional max_bytes: int budget field to
	// Counting_Allocator_Data and return nil, .Out_Of_Memory before delegating
	// when max_bytes > 0 && data.bytes_allocated + size > data.max_bytes.
}

rollback_stack_allocator_lifo :: proc() {

	/*
	A fixed-buffer mem.Arena ignores individual free or delete calls. When you
	need stack-shaped lifetimes inside a fixed buffer where freeing an allocation
	immediately reclaims space for the next one, Odin provides
	mem.Rollback_Stack.

	Each allocation stores a small header recording the stack offset before it.
	Freeing the newest allocation pops a single LIFO frame, and freeing an older
	allocation rolls the stack all the way back past it (reclaiming both that
	allocation and anything allocated after it in O(1) time).

	    Suppose rs_buf has 512 bytes:
	        a := make([]u8, 200, rs_alloc)
	        b := make([]u8, 200, rs_alloc)
	        c, err := make([]u8, 200, rs_alloc)   // fails: .Out_Of_Memory
	        delete(a, rs_alloc)                   // rolls back both a and b!
	        d, ok_err := make([]u8, 400, rs_alloc) // succeeds!
	*/

	rs_buf: [512]byte
	rs: mem.Rollback_Stack
	mem.rollback_stack_init(&rs, rs_buf[:])
	rs_alloc := mem.rollback_stack_allocator(&rs)

	seed := new_clone(u32(0x1234_5678), rs_alloc)
	fmt.printfln("Rollback stack seed: 0x%X", seed^)
	free(seed, rs_alloc)

	// Allocate first := make([]u8, 200, rs_alloc) and second := make([]u8, 200, rs_alloc),
	// setting first[0] = 1 and second[0] = 2.


	// Attempt third, err := make([]u8, 200, rs_alloc) and print err to verify
	// it returns .Out_Of_Memory inside the 512-byte backing buffer.


	// Roll back both allocations in one call with delete(first, rs_alloc), then
	// allocate big, big_err := make([]u8, 400, rs_alloc) and print big_err and
	// len(big) to verify the space was reclaimed. Finish with free_all(rs_alloc).
}

main :: proc() {

	fmt.println("=== 1. Allocator interface, nil, and panic_allocator ===")
	allocator_interface_and_panic_sentinel()

	fmt.println("\n=== 2. Building a custom counting allocator ===")
	building_a_counting_allocator()

	fmt.println("\n=== 3. Rollback_Stack_Allocator LIFO rollbacks ===")
	rollback_stack_allocator_lifo()
}
