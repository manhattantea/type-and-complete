// odin run 760_thread_pool_tasks.odin -file

package main

import "core:fmt"
import "core:thread"

/*
Spawning a fresh OS thread for every tiny unit of work wastes tens of
microseconds per job on kernel thread creation, stack allocation, and teardown.
When you have dozens or thousands of small independent jobs, a fixed worker
pool ('thread.Pool') spawns N worker threads once and lets them pull tasks
from a shared queue.

Every job submitted to 'thread.Pool' is represented by a 'thread.Task' struct
carrying three main fields: 'procedure' (the callback), 'data' (an untyped
rawptr to shared or per-job input/output structs), and 'user_index' (an int
tag identifying which slot or item index this task owns).

This file is split into three sections called from main at the bottom so you
can practice basic pool execution, polling completed tasks with
'thread.pool_pop_done', and parallel slice chunking.
*/

Job_Output :: struct {
	results: [8]int,
}

Chunk_Sum_Job :: struct {
	slice:       []int,
	partial_sum: int,
}

pool_lifecycle_and_tasks :: proc() {

	/*
	A 'thread.Pool' follows a clear four-step lifecycle:
	First, 'thread.pool_init(&pool, context.allocator, thread_count)' creates
	internal queues and allocates thread objects (pair with
	'defer thread.pool_destroy(&pool)').
	Second, 'thread.pool_add_task(&pool, context.allocator, task_proc, data_ptr, user_index)'
	queues work items; note that 'pool_add_task' allocates a queue node on the
	allocator you pass in, so keep that allocator consistent with 'pool_destroy'.
	Third, 'thread.pool_start(&pool)' launches the worker threads.
	Fourth, 'thread.pool_finish(&pool)' blocks until every queued task completes
	and shuts down the pool workers cleanly.

	    Suppose output: Job_Output has [8]int slots:
	    Enqueuing 8 tasks with data = &output and user_index = 0..<8 lets task i
	    write straight into output.results[i] with zero mutexes, because no two
	    tasks share the same user_index.
	*/

	// Starter anchor showing Job_Output and thread.Pool sizing:

	output: Job_Output
	fmt.printfln("Starter Job_Output (%d slots, Pool=%dB)",
		len(output.results), size_of(thread.Pool))

	// Write a task callback at file scope with exact signature:
	// square_task :: proc(task: thread.Task)
	// Inside it, cast out := (^Job_Output)(task.data) and store
	// task.user_index * task.user_index into out.results[task.user_index].


	// Initialize a 2-thread pool: pool: thread.Pool, call
	// thread.pool_init(&pool, context.allocator, 2) with defer thread.pool_destroy(&pool),
	// enqueue 8 tasks for i in 0..<8 calling thread.pool_add_task(&pool, context.allocator, square_task, &output, i),
	// call thread.pool_start(&pool) and thread.pool_finish(&pool), and print
	// output.results (expected: [0, 1, 4, 9, 16, 25, 36, 49]).


	// Guard against out-of-bounds tasks by checking task.data != nil and
	// task.user_index >= 0 && task.user_index < len(out.results) inside
	// square_task, then test enqueueing tasks BEFORE vs AFTER pool_start.
}

polling_done_tasks_with_pop_done :: proc() {

	/*
	'thread.pool_finish(&pool)' blocks until every single task is complete.
	What if your main thread wants to report progress, stream partial results,
	or launch follow-up work as individual tasks finish?

	When we call 'completed_task, ok := thread.pool_pop_done(&pool)', it means
	"check the pool's completed-task queue without blocking: if a finished task
	is waiting, pop its thread.Task record and return ok == true; otherwise
	return ok == false immediately".

	    Suppose 6 tasks run on 2 workers:
	        done_count := 0
	        for done_count < 6 {
	            if finished, ok := thread.pool_pop_done(&pool); ok {
	                done_count += 1
	                // inspect finished.user_index immediately
	            } else {
	                thread.yield()
	            }
	        }
	    After collecting all 6 done records, still call 'thread.pool_finish(&pool)'
	    before 'pool_destroy' so the worker threads join cleanly.
	*/

	// Write a task callback at file scope with exact signature:
	// weighted_work_task :: proc(task: thread.Task)
	// Have it cast out := (^Job_Output)(task.data) and write
	// (task.user_index + 1) * 100 into out.results[task.user_index].


	// Declare batch_out: Job_Output and a 2-thread pool: thread.Pool (with
	// pool_init + defer pool_destroy). Enqueue 6 weighted_work_task jobs
	// (user_index 0..<6), call thread.pool_start(&pool), and loop until
	// done_count == 6 calling thread.pool_pop_done(&pool) (yielding with
	// thread.yield() when ok is false) and printing each completed user_index.


	// Call thread.pool_finish(&pool) after the polling loop and verify
	// batch_out.results[:6] equals [100, 200, 300, 400, 500, 600].
}

parallel_slice_chunking :: proc() {

	/*
	Submitting 10,000 tiny 1-element tasks to a thread pool creates severe
	queue contention: threads spend more time locking the task queue than doing
	useful math. Instead, partition a large slice into a small number of
	coarse chunks (one chunk per worker or 2x-4x worker count) so each task
	iterates over a contiguous slice in L1 cache.

	    Suppose values has 1000 integers split across 4 Chunk_Sum_Job structs:
	    Chunk 0 owns values[0:250], Chunk 1 owns values[250:500], Chunk 2 owns
	    values[500:750], and Chunk 3 owns values[750:1000]. Each task writes only
	    to its own job.partial_sum field, and the main thread adds the 4 partial
	    sums after pool_finish.
	*/

	// Starter anchor confirming Chunk_Sum_Job layout:

	fmt.printfln("Starter Chunk_Sum_Job size: %dB", size_of(Chunk_Sum_Job))

	// Write a chunk-summing task at file scope with exact signature:
	// sum_chunk_task :: proc(task: thread.Task)
	// Cast job := (^Chunk_Sum_Job)(task.data), loop over job.slice, and store
	// the total into job.partial_sum.


	// Allocate values := make([]int, 1000) with defer delete(values) and fill
	// values[i] = i + 1. Partition values into jobs: [4]Chunk_Sum_Job where
	// chunk_len := len(values) / len(jobs) and the final chunk takes any
	// remainder up to len(values).


	// Dispatch all 4 &jobs[c] pointers to a 4-thread pool using
	// thread.pool_add_task, run pool_start and pool_finish, sum each
	// jobs[c].partial_sum into grand_total, and assert grand_total == 500_500.
}

main :: proc() {

	fmt.println("=== 1. Thread pool lifecycle and Task callbacks ===")
	pool_lifecycle_and_tasks()

	fmt.println("\n=== 2. Polling completed tasks with pool_pop_done ===")
	polling_done_tasks_with_pop_done()

	fmt.println("\n=== 3. Parallel slice chunking ===")
	parallel_slice_chunking()
}
