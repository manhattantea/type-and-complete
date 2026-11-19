// odin run 720_threads_basics.odin -file

package main

import "core:fmt"
import "core:thread"

/*
In C, spawning an OS thread forces you to pack arguments into an untyped void*
and cast it back manually inside the worker. Odin's 'core:thread' package keeps
worker arguments strongly typed from the call site all the way into the worker
procedure:

    thread.create_and_start_with_poly_data(arg, worker_proc)
    thread.create_and_start_with_poly_data2(arg1, arg2, worker_proc)

Under the hood, Odin also gives every spawned thread its own fresh 'context'
(including a thread-local 'context.temp_allocator') and cleans up that scratch
arena automatically when the thread exits. Once a thread starts, the parent
thread must wait for it with 'thread.join(t)' or 'thread.join_multiple(..threads)'
and release its OS handle with 'thread.destroy(t)'.

This file is split into three sections called from main at the bottom so you
can read top to bottom and run the program at any point.
*/

Worker_Range :: struct {
	data:        []int,
	partial_sum: int,
}

spawning_with_poly_data :: proc() {

	/*
	When you pass '&r1' (type '^Worker_Range') into
	'thread.create_and_start_with_poly_data(&r1, sum_worker)', Odin verifies at
	compile time that 'sum_worker' expects a single '^Worker_Range' parameter.
	Because each worker writes only into its own distinct struct ('r1.partial_sum'
	vs 'r2.partial_sum') and only reads disjoint slices of 'nums', no mutex is
	required for independent work partitioning.
	*/

	// Here is a starter Worker_Range and thread.Thread descriptor size check:

	anchor_range := Worker_Range{data = []int{1, 2, 3}}
	fmt.printfln("anchor range len=%d | size_of(thread.Thread)=%dB", len(anchor_range.data), size_of(thread.Thread))

	// Write a typed worker procedure at file scope:
	// sum_worker :: proc(r: ^Worker_Range)
	// Iterate over r.data and accumulate the total into r.partial_sum.


	// Declare nums := [8]int{10, 20, 30, 40, 50, 60, 70, 80}, build r1 for
	// nums[0:4] and r2 for nums[4:8], and start t1 and t2 with
	// thread.create_and_start_with_poly_data(&r1, sum_worker) and &r2.
	// Wait with thread.join(t1) and thread.join(t2), free both handles with
	// thread.destroy(t1) and thread.destroy(t2), and print r1.partial_sum + r2.partial_sum
	// (expected: 360).


	// Scale up to 4 worker structs in an array: declare big_nums: [64]int filled
	// with 1..=64, ranges: [4]Worker_Range, and handles: [4]^thread.Thread.
	// Partition big_nums into 16-element slices across a loop, spawn all 4
	// workers, join and destroy every handle, and verify the sum equals 2080.
}

poly_data2_and_join_multiple :: proc() {

	/*
	Suppose a worker only needs a slice and a scalar multiplier — inventing a
	one-off struct just to pass two values adds clutter. Calling
	'thread.create_and_start_with_poly_data2(arg1, arg2, worker_proc)' forwards
	two typed arguments straight into your worker!

	When launching a batch of threads stored in an array 'threads: [3]^thread.Thread',
	calling 'thread.join_multiple(..threads[:])' waits for all of them in one
	statement using Odin's '..' slice-to-variadic expansion operator before you
	loop to call 'thread.destroy(t)' on each handle.
	*/

	// Write a 2-argument worker procedure at file scope:
	// scale_slice_worker :: proc(chunk: []int, factor: int)
	// Loop for &val in chunk and multiply val *= factor in place.


	// Declare values := [12]int{1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12} and
	// threads: [3]^thread.Thread. Partition values into three 4-element slices
	// (values[0:4], values[4:8], values[8:12]) and spawn 3 threads using
	// thread.create_and_start_with_poly_data2(chunk, 10, scale_slice_worker).
	// Wait with thread.join_multiple(..threads[:]), destroy every handle in a
	// loop, and print values (expected: [10, 20, ..., 120]).


	// Write fill_sequence_worker :: proc(dst: []int, start_value: int) at file scope
	// that writes dst[i] = start_value + i. Spawn 4 threads via
	// thread.create_and_start_with_poly_data2 over a [16]int array, wait with
	// thread.join_multiple, destroy handles, and confirm values read 0..=15.
}

thread_local_temp_allocator :: proc() {

	/*
	Because each thread receives its own 'context.temp_allocator', workers can
	format strings with 'fmt.tprintf' or allocate scratch slices without locking
	or colliding with other threads. Watch the lifetime boundary, though:

	    Suppose a worker runs msg := fmt.tprintf("worker %d", id) and stores msg
	    into a shared struct before returning. As soon as the worker exits, Odin
	    destroys that thread's temp_allocator, leaving 'msg' as a dangling
	    pointer when main reads it after thread.join!

	To return formatted text out of a worker safely without heap allocations,
	write into a fixed byte buffer owned by the caller or worker slot.
	*/

	// Define a fixed-buffer output slot struct at file scope:
	// Worker_Label :: struct { buf: [64]u8, length: int }
	// Write a 2-argument worker procedure at file scope:
	// format_worker :: proc(worker_id: int, out: ^Worker_Label)
	// Inside format_worker, format text := fmt.tprintf("worker-%d-done", worker_id)
	// using the thread's local temp_allocator, copy min(len(text), len(out.buf))
	// bytes into out.buf[:], and record out.length = n.


	// Spawn 2 threads with thread.create_and_start_with_poly_data2 passing
	// worker IDs 1 and 2 and &labels[0] / &labels[1]. Join with
	// thread.join_multiple, destroy handles, and print string(labels[i].buf[:labels[i].length]).
}

main :: proc() {

	fmt.println("=== 1. Spawning typed workers with poly_data ===")
	spawning_with_poly_data()

	fmt.println("\n=== 2. Passing two args (poly_data2) and join_multiple ===")
	poly_data2_and_join_multiple()

	fmt.println("\n=== 3. Thread-local context.temp_allocator lifetime ===")
	thread_local_temp_allocator()
}
