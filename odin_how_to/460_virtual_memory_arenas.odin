// odin run 460_virtual_memory_arenas.odin -file

package main

import "core:fmt"
import "core:mem/virtual"

/*
A fixed-buffer mem.Arena requires guessing an upper byte limit before you start
allocating. When a workload's size varies wildly (loading a scene, parsing a
source file, building an AST), guessing too low triggers Out_Of_Memory and
guessing too high wastes real RAM.

Odin's core:mem/virtual package solves this by talking straight to the OS
virtual memory manager (VirtualAlloc on Windows, mmap on POSIX). Virtual
address space is cheap on 64-bit CPUs, while physical RAM pages are only
committed by the kernel as you actually touch them. A virtual.Arena gives you
bump-pointer allocation with dynamic capacity, and virtual.arena_destroy(&arena)
hands all pages back to the OS when the arena's lifetime ends.
*/

Graph_Node :: struct {
	label:     string,
	neighbors: [dynamic]^Graph_Node,
}

growing_virtual_arenas :: proc() {

	/*
	When we call virtual.arena_init_growing(&v_arena), the arena starts with an
	OS-backed memory block and automatically chains additional blocks whenever an
	allocation outgrows the current one. Notice that virtual.arena_init_growing
	is marked @(require_results) and returns an Allocator_Error, so Odin forces
	you to inspect init_err rather than silently ignoring out-of-memory startup
	failures.

	Two fields summarize the arena's footprint at any moment:
	    v_arena.total_used       bytes actually handed out to callers
	    v_arena.total_reserved   bytes reserved from the OS virtual address space

	Calling virtual.arena_free_all(&v_arena) resets the arena's offset back to
	zero in one bulk operation without releasing the underlying blocks, while
	defer virtual.arena_destroy(&v_arena) returns everything to the OS on exit.
	*/

	v_arena: virtual.Arena
	init_err := virtual.arena_init_growing(&v_arena)
	if init_err != nil {
		fmt.printfln("Failed to initialize virtual arena: %v", init_err)
		return
	}
	defer virtual.arena_destroy(&v_arena)

	v_alloc := virtual.arena_allocator(&v_arena)
	tag := new_clone(1001, v_alloc)
	fmt.printfln("Virtual arena tag=%d (used=%d, reserved=%d)", tag^, v_arena.total_used, v_arena.total_reserved)

	// Open an inner { ... } scope, assign context.allocator = v_alloc, and
	// allocate a [dynamic]int named numbers (appending 0..<1000 in a loop) plus
	// a map[string]int named scores with two entries ("alice" and "bob") —
	// without calling delete on either collection.


	// Print v_arena.total_used and v_arena.total_reserved after populating
	// numbers and scores.


	// Call virtual.arena_free_all(&v_arena) to wipe both collections in one bulk
	// call, then print v_arena.total_used to confirm it returned to 0.
}

messy_graphs_without_per_node_free :: proc() {

	/*
	Pointer-heavy graphs, cyclic meshes, and compiler ASTs are notoriously painful
	to tear down with individual free calls. Suppose node A points to B, B points
	to C, and C points back to A: a naive recursive destructor loops forever, and
	a shared child node risks double-free corruption unless you maintain a visited
	set just for cleanup.

	When every Graph_Node and every node's neighbors [dynamic]^Graph_Node array
	live inside one virtual.Arena, cleanup becomes trivial. You allocate freely,
	wire arbitrary cycles, and erase the entire graph in one bulk
	virtual.arena_free_all(&graph_arena) call with zero traversal and zero leaks.
	*/

	graph_arena: virtual.Arena
	init_err := virtual.arena_init_growing(&graph_arena)
	if init_err != nil {
		fmt.printfln("Failed to initialize graph arena: %v", init_err)
		return
	}
	defer virtual.arena_destroy(&graph_arena)

	g_alloc := virtual.arena_allocator(&graph_arena)
	root := new_clone(Graph_Node{label = "Root", neighbors = make([dynamic]^Graph_Node, g_alloc)}, g_alloc)
	fmt.printfln("Root node=%q | used=%d bytes", root.label, graph_arena.total_used)

	// Build a 4-node cyclic graph inside g_alloc using new_clone and
	// make([dynamic]^Graph_Node, g_alloc): allocate hub ("Hub"), leaf_a ("LeafA"),
	// and leaf_b ("LeafB"). Append hub and leaf_a to root.neighbors, append
	// leaf_b and root (creating a cycle!) to hub.neighbors, and append leaf_a to
	// leaf_b.neighbors.


	// Print each node's label and len(node.neighbors), print graph_arena.total_used,
	// and then wipe the entire cyclic graph in one bulk call with
	// virtual.arena_free_all(&graph_arena). Print graph_arena.total_used afterward
	// to verify it is 0.
}

static_reserved_virtual_arenas :: proc() {

	/*
	A growing arena allocates chained blocks whose base addresses sit wherever
	the OS places them. Sometimes you need one contiguous virtual address region
	so pointers never span disconnected blocks, or you want a hard ceiling.

	When we call virtual.arena_init_static(&static_arena, reserved, commit_size),
	it asks the OS to reserve a contiguous range of 'reserved' bytes of virtual
	addresses while committing only 'commit_size' bytes of physical RAM at a time
	as the bump pointer advances. On Windows or Linux, reserving 16 MB or even
	1 GB costs virtually zero physical memory until pages are actually written.
	*/

	reserved_bytes :: uint(16 * 1024 * 1024)
	commit_bytes   :: uint(64 * 1024)
	fmt.printfln("Static arena plan: reserve=%d bytes, commit_step=%d bytes", reserved_bytes, commit_bytes)

	// Initialize static_arena: virtual.Arena using:
	// static_err := virtual.arena_init_static(&static_arena, reserved_bytes, commit_bytes)
	// Handle static_err != nil explicitly (print and return), and register
	// defer virtual.arena_destroy(&static_arena).


	// Print static_arena.total_reserved and static_arena.total_used right after
	// init, then allocate a 128 KB slice from virtual.arena_allocator(&static_arena),
	// write a sentinel byte, and print static_arena.total_used again to see
	// usage grow inside the single 16 MB reservation.
}

main :: proc() {

	fmt.println("=== 1. Growing virtual arenas ===")
	growing_virtual_arenas()

	fmt.println("\n=== 2. Messy graphs freed in one bulk call ===")
	messy_graphs_without_per_node_free()

	fmt.println("\n=== 3. Static reserved virtual arenas ===")
	static_reserved_virtual_arenas()
}
