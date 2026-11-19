// odin run 780_concurrent_pipeline_lab

package main

import "core:fmt"
import "core:mem"
import "core:thread"

/*
Concurrent Pipeline Lab — Entry Point ('main.odin'):

This coordinator sets up leak detection before spawning OS worker threads,
feeds mixed valid and invalid Work_Item records into a shared Batch_Context,
runs 4 workers concurrently, and verifies zero memory leaks on shutdown.

Wrapping 'context.allocator' in a 'mem.Tracking_Allocator' BEFORE calling
'thread.create_and_start_with_poly_data' matters because each spawned thread
inherits a copy of the caller's 'context'. That lets the tracking allocator
observe allocations and frees made by every worker (such as growing
'ctx.errors') as well as main itself.
*/

main :: proc() {

	// Starter anchor verifying Batch_Context, worker_loop, and Tracking_Allocator sizing:
	anchor_items := make([]Work_Item, 2)
	defer delete(anchor_items)
	anchor_ctx := Batch_Context{items = anchor_items}
	defer delete(anchor_ctx.errors)
	worker_loop(&anchor_ctx)
	fmt.printfln("Starter pipeline ready: %s (Thread=%dB, Tracking=%dB)",
		format_batch_status(&anchor_ctx), size_of(thread.Thread), size_of(mem.Tracking_Allocator))
	free_all(context.temp_allocator)

	// Wrap context.allocator in a mem.Tracking_Allocator: declare
	// track: mem.Tracking_Allocator, call mem.tracking_allocator_init(&track, context.allocator),
	// register a defer block that prints any leaks in track.allocation_map and
	// any invalid frees in track.bad_free_array before calling
	// mem.tracking_allocator_destroy(&track), and set:
	// context.allocator = mem.tracking_allocator(&track)


	// Allocate work_items := make([]Work_Item, 16) with defer delete(work_items)
	// and populate each item i in 0..<16 with id = i + 1 and a mix of valid
	// and negative inputs (for example: -((i + 1) * 2) when i % 5 == 4, else
	// (i + 1) * 3) so items 5, 10, and 15 test error collection.


	// Declare batch_ctx := Batch_Context{items = work_items} with
	// defer delete(batch_ctx.errors), spawn 4 worker threads into
	// workers: [4]^thread.Thread using
	// thread.create_and_start_with_poly_data(&batch_ctx, worker_loop), and
	// join and destroy every thread once spawned.


	// Call print_batch_report(&batch_ctx), print format_batch_status(&batch_ctx),
	// release main's temp scratch with free_all(context.temp_allocator), and
	// verify completed_count + failed_count == 16 with zero leaks in track.
}
