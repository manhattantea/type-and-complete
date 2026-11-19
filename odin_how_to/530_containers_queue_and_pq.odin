// odin run 530_containers_queue_and_pq.odin -file

package main

import "core:container/queue"
import pq "core:container/priority_queue"
import "core:fmt"

/*
Removing from index 0 of a plain '[dynamic]T' with 'ordered_remove(&arr, 0)'
shifts every remaining element left in O(N) time. When a worklist or scheduler
pushes and pops thousands of items, that linear shift turns into an O(N^2)
bottleneck.

Odin's standard library provides two array-backed containers for those jobs:
- 'core:container/queue' implements a circular ring buffer with O(1) amortized
  'push_front', 'push_back', 'pop_front', and 'pop_back'.
- 'core:container/priority_queue' implements a binary heap in a flat array
  with O(log N) 'push', 'pop', 'remove', and 'fix'.
*/

Task :: struct {
	priority: int,
	name:     string,
}

ring_buffer_queue_and_bfs :: proc() {

	/*
	A 'queue.Queue(T)' maintains a read offset and length inside a contiguous
	power-of-2 buffer. Wrapping indices with a bitmask lets the queue grow and
	drain from either end without sliding elements in memory.

	When we drain with 'queue.pop_front_safe(&q)', it returns '(val, ok)' so an
	empty queue returns 'false' cleanly instead of asserting like 'pop_front'.

	    Suppose 'q' starts empty:
	        queue.push_back(&q, "A")    // [A]
	        queue.push_back(&q, "B")    // [A, B]
	        queue.push_front(&q, "URG") // [URG, A, B]
	        first, ok := queue.pop_front_safe(&q)  // first = "URG", ok = true
	*/

	demo_q: queue.Queue(int)
	fmt.printfln("Starter empty queue len=%d", queue.len(demo_q))

	// Initialize q: queue.Queue(string) with queue.init(&q) and defer queue.destroy(&q).
	// Push "build" and "test" with queue.push_back, then push "hotfix" to the front
	// with queue.push_front. Drain and print all elements using:
	// for val, ok := queue.pop_front_safe(&q); ok; val, ok = queue.pop_front_safe(&q)


	// Practice ring-buffer wraparound:
	// initialize ring: queue.Queue(int) with capacity 4 via queue.init(&ring, 4)
	// and defer queue.destroy(&ring). Push 1, 2, 3, pop 2 items, push 4, 5, 6,
	// then drain all remaining items to confirm strict FIFO order across wraparound.


	// Implement a Breadth-First Search (BFS) worklist over a 5-node graph:
	// suppose node 0 connects to {1, 2}, 1 -> {3}, 2 -> {3, 4}, 3 -> {}, 4 -> {}.
	// Represent adjacency with fixed arrays or slices, declare visited: [5]bool,
	// push node 0 onto bfs_q: queue.Queue(int) (with visited[0] = true), and loop
	// while bfs_q is non-empty: pop curr, print curr, and push unvisited neighbors.
}

binary_heap_priority_queue :: proc() {

	/*
	A 'pq.Priority_Queue(T)' stores a binary heap inside 'p.queue: [dynamic]T',
	ordered by a 'less :: proc(a, b: T) -> bool' comparator passed to 'pq.init'.
	For a min-heap (smallest number popped first), write 'a.priority < b.priority';
	flip to '>' for a max-heap.

	Always pair 'pq.init(&p, less_proc, pq.default_swap_proc(T))' with
	'defer pq.destroy(&p)' so the backing dynamic array is freed on scope exit.
	*/

	demo_pq: pq.Priority_Queue(Task)
	sample_task := Task{priority = 1, name = "Bootstrap"}
	fmt.printfln("Starter task [%s] | empty pq len=%d", sample_task.name, pq.len(demo_pq))

	// Initialize task_heap: pq.Priority_Queue(Task) with a less proc where smaller
	// .priority values come first (a.priority < b.priority) and defer pq.destroy(&task_heap).
	// Push 4 Task values out of order (priorities 5, 1, 3, 2), inspect the top item
	// with pq.peek(task_heap), and pop all tasks in priority order using pq.pop.


	// Build a max-heap of integers (less proc: a > b) and drain it safely with
	// for top, ok := pq.pop_safe(&max_heap); ok; top, ok = pq.pop_safe(&max_heap)
	// printing each popped value from largest to smallest.
}

updating_and_removing_heap_items :: proc() {

	/*
	Schedulers often need to boost an existing job's priority or cancel a queued
	job before it reaches the top. Because 'pq.Priority_Queue(T)' exposes its
	backing slice as 'heap.queue', you can scan 'heap.queue[:]' for the target
	index 'idx':
	- After mutating 'heap.queue[idx]' in place, call 'pq.fix(&heap, idx)' to
	  restore the heap invariant in O(log N) without rebuilding the whole heap.
	- To cancel an item at 'idx', call 'removed := pq.remove(&heap, idx)' to swap
	  it out and repair the heap in O(log N).
	*/

	less_task :: proc(a, b: Task) -> bool {

		return a.priority < b.priority
	}

	preview: pq.Priority_Queue(Task)
	pq.init(&preview, less_task, pq.default_swap_proc(Task))
	defer pq.destroy(&preview)
	pq.push(&preview, Task{priority = 10, name = "Cleanup"})
	fmt.printfln("Starter top task: %s", pq.peek(preview).name)

	// Push 4 tasks into a fresh pq.Priority_Queue(Task): "Lint" (4), "Compile" (3),
	// "Upload" (5), and "Fetch" (2). Locate "Compile" in heap.queue[:] by index idx,
	// boost its priority to 0 (heap.queue[idx].priority = 0), call pq.fix(&heap, idx),
	// and verify pq.peek(heap).name is now "Compile".


	// Next, locate "Upload" in heap.queue[:], remove it directly using:
	// cancelled := pq.remove(&heap, cancel_idx)
	// Print cancelled.name, then drain the remaining heap with pq.pop_safe to verify
	// "Upload" is gone and the remaining tasks still pop in valid priority order.
}

main :: proc() {

	fmt.println("=== 1. Ring-buffer queue and BFS ===")
	ring_buffer_queue_and_bfs()

	fmt.println("\n=== 2. Binary heap priority queue ===")
	binary_heap_priority_queue()

	fmt.println("\n=== 3. Updating and removing heap items ===")
	updating_and_removing_heap_items()
}
