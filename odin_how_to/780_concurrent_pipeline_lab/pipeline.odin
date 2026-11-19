// Concurrent Pipeline Lab — Worker pool state, atomic claiming, and error collection

package main

import "core:fmt"
import "core:sync"

/*
A parallel batch processor needs three mechanisms working cleanly together so
workers neither race on shared state nor leak temporary scratch memory:

First, lock-free slot claiming: 'idx := sync.atomic_add(&ctx.next_index, 1)'
returns the previous index before adding 1, handing each worker a unique
slot into 'ctx.items' until 'idx >= len(ctx.items)'. Because no two threads
receive the same idx, writing 'ctx.items[idx]' needs zero locks.

Second, per-item scratch cleanup: every thread created by 'core:thread' gets
its own thread-local 'context.temp_allocator'. When a worker formats a
temporary diagnostic string via 'fmt.tprintf', calling
'free_all(context.temp_allocator)' at the end of each iteration reclaims that
thread's scratch buffer in O(1) so memory never grows across thousands of jobs.

Third, guarded shared aggregation and error collection: updating shared
counters or appending a 'Batch_Error' into 'ctx.errors' touches shared state,
so those updates sit inside 'sync.guard(&ctx.mu)'.

    Suppose item 4 arrives with input_value = -10:
    The worker marks item.failed = true, takes sync.guard(&ctx.mu), increments
    ctx.failed_count, appends Batch_Error{item_id = item.id, input_value = -10,
    reason = "negative input rejected"} to ctx.errors, and skips squaring.
*/

Work_Item :: struct {
	id:               int,
	input_value:      int,
	processed_output: int,
	completed:        bool,
	failed:           bool,
}

Batch_Error :: struct {
	item_id:     int,
	input_value: int,
	reason:      string,
}

Batch_Context :: struct {
	items:           []Work_Item,
	errors:          [dynamic]Batch_Error,
	next_index:      int,
	completed_count: int,
	failed_count:    int,
	mu:              sync.Mutex,
}

format_batch_status :: proc(ctx: ^Batch_Context) -> string {

	if ctx == nil do return "nil batch"
	sync.guard(&ctx.mu)
	return fmt.tprintf("completed=%d/%d, failed=%d, errors=%d",
		ctx.completed_count, len(ctx.items), ctx.failed_count, len(ctx.errors))
}

worker_loop :: proc(ctx: ^Batch_Context) {

	if ctx == nil do return
	if sync.atomic_load(&ctx.next_index) >= len(ctx.items) do return

	// Replace the early return check above with the concurrent work-claiming
	// loop. Loop with 'for' and claim a unique slot each pass via:
	// idx := sync.atomic_add(&ctx.next_index, 1)
	// Break as soon as idx >= len(ctx.items).


	// Inside the loop, format a temporary scratch trace string using
	// fmt.tprintf("item-%d:%d", ctx.items[idx].id, ctx.items[idx].input_value)
	// and call free_all(context.temp_allocator) at the end of each pass (or
	// via loop-scoped defer free_all(context.temp_allocator)) so temp memory
	// never accumulates across iterations.


	// Validate ctx.items[idx].input_value >= 0. If negative, set
	// ctx.items[idx].failed = true, then inside a sync.guard(&ctx.mu) block
	// increment ctx.failed_count += 1 and append a Batch_Error to ctx.errors
	// with reason = "negative input rejected". Otherwise set
	// ctx.items[idx].processed_output = val * val + 1, set completed = true,
	// and increment ctx.completed_count += 1 inside sync.guard(&ctx.mu).
}

// Write a reporting helper at file scope with exact signature:
// print_batch_report :: proc(ctx: ^Batch_Context)
// Guard on ctx.mu with sync.guard(&ctx.mu), print completed_count,
// failed_count, and loop over ctx.errors printing each err.item_id,
// err.input_value, and err.reason.
