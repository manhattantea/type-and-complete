// odin run 300_tracy_memory_allocator_and_arena_tracking.odin -file

package main

import "base:runtime"
import "core:fmt"
import "core:mem"

/*
Every time you call new, make, append, build a map, or call fmt.aprintf in Odin,
the runtime asks context.allocator for memory. That implicit parameter is a
profiling superpower: because every subsystem receives context.allocator without
changing a single line of application code, wrapping context.allocator in a
custom Tracy_Allocator lets you watch every allocation and free across an entire
system in real time.

When #config(TRACY_ENABLE, false) is evaluated at compile time, it creates a
compile-time boolean constant defaulting to false. Inside a when TRACY_ENABLE
block, Odin discards the enclosed foreign declarations and emit calls completely
before code generation when false, producing zero machine instructions and zero
dependency on TracyClient.lib. When enabled with -define:TRACY_ENABLE=true,
every allocation emits ___tracy_emit_memory_alloc_named and every free emits
___tracy_emit_memory_free_named so Tracy's Memory tab graphs live pool bytes and
flags leaks by call stack.

Watch out for one fatal trap when wrapping an allocator: Tracy_Allocator tracks
live pointers inside active_allocs: map[rawptr]int. Suppose active_allocs were
created with context.allocator after context.allocator already pointed to
&t_alloc. The first allocation inserts a key into active_allocs, which asks
context.allocator for map storage, which calls tracy_allocator_proc again, which
inserts into active_allocs again—recursing infinitely until the stack overflows.
Always pass t.backing explicitly when creating active_allocs so metadata
allocations bypass the wrapper.
*/

TRACY_ENABLE :: #config(TRACY_ENABLE, false)

when TRACY_ENABLE {
	when ODIN_OS == .Windows {
		foreign import tracy "TracyClient.lib"
	} else {
		foreign import tracy "system:TracyClient"
	}

	foreign tracy {
		___tracy_emit_memory_alloc_named :: proc "c" (ptr: rawptr, size: uint, secure: i32, name: cstring) ---
		___tracy_emit_memory_free_named  :: proc "c" (ptr: rawptr, secure: i32, name: cstring) ---
	}
}

Tracy_Allocator :: struct {
	backing:         runtime.Allocator,
	pool_name:       cstring,
	active_allocs:   map[rawptr]int,
	total_allocated: int,
	current_bytes:   int,
	peak_bytes:      int,
	alloc_calls:     int,
	free_calls:      int,
}

// Define tracy_allocator_init :: proc(t: ^Tracy_Allocator, backing: runtime.Allocator, pool_name: cstring = "Heap")
// Store t.backing = backing and t.pool_name = pool_name, and initialize
// t.active_allocs = make(map[rawptr]int, 64, backing) so map growth never recurses
// back through context.allocator.


// Define tracy_allocator_destroy :: proc(t: ^Tracy_Allocator)
// Call delete(t.active_allocs) so the map frees using its own stored backing
// allocator.


// Define tracy_allocator_proc with Odin's runtime.Allocator_Proc signature:
// proc(allocator_data: rawptr, mode: runtime.Allocator_Mode, size, alignment: int, old_memory: rawptr, old_size: int, location := #caller_location) -> (data: []byte, err: runtime.Allocator_Error)
// Cast t := (^Tracy_Allocator)(allocator_data) and switch mode:
// - .Alloc, .Alloc_Non_Zeroed: delegate to t.backing.procedure(...). When err == .None
//   and len(data) > 0, record ptr := rawptr(raw_data(data)) -> len(data) in
//   t.active_allocs, increment alloc_calls, add len(data) to total_allocated and
//   current_bytes, update peak_bytes = max(peak_bytes, current_bytes), and emit
//   ___tracy_emit_memory_alloc_named(ptr, uint(len(data)), 0, t.pool_name) inside when TRACY_ENABLE.
// - .Free: if old_memory != nil, look up sz, ok := t.active_allocs[old_memory],
//   subtract sz from t.current_bytes, call delete_key(&t.active_allocs, old_memory),
//   increment free_calls, emit ___tracy_emit_memory_free_named inside when TRACY_ENABLE,
//   and delegate .Free to t.backing.procedure(...).
// - .Free_All: when TRACY_ENABLE, loop over ptr, _ in t.active_allocs emitting
//   ___tracy_emit_memory_free_named(ptr, 0, t.pool_name); then call
//   clear(&t.active_allocs), set t.current_bytes = 0, and delegate .Free_All.
// - .Resize, .Resize_Non_Zeroed: remove old_memory from t.active_allocs and subtract
//   its recorded size from t.current_bytes (emitting a Tracy free when enabled),
//   delegate the resize, and on success record the returned pointer and len(data)
//   (emitting a Tracy alloc and updating peak_bytes).
// - .Query_Features, .Query_Info: delegate directly to t.backing.procedure(...).


// Define tracy_allocator :: proc(t: ^Tracy_Allocator) -> runtime.Allocator
// Return runtime.Allocator{procedure = tracy_allocator_proc, data = t}.


tracy_allocator_and_recursion_guard :: proc() {

	/*
	Before allocating real pools, note that Odin also provides mem.nil_allocator(),
	a built-in sentinel allocator that rejects every allocation with .Out_Of_Memory.
	Pairing a scoped { context.allocator = tracy_allocator(&t_alloc); ... } block
	with defer frees lets every allocation inside that scope report cleanly under
	one named pool without leaking past the closing brace.
	*/

	_, nil_err := make([]u8, 32, mem.nil_allocator())
	fmt.printfln("Nil allocator probe: err=%v | Tracy_Allocator=%v B", nil_err, size_of(Tracy_Allocator))

	// Initialize t_alloc: Tracy_Allocator using tracy_allocator_init(&t_alloc, context.allocator, "SimHeap")
	// and defer tracy_allocator_destroy(&t_alloc). Open a scoped block setting
	// context.allocator = tracy_allocator(&t_alloc), then:
	// - Allocate floats := make([]f32, 256) with defer delete(floats).
	// - Allocate ids := make([dynamic]int, 0, 8) with defer delete(ids) and append 20
	//   integers so dynamic growth exercises .Resize.
	// - Allocate msg := fmt.aprintf("items=%v", len(ids)) with defer delete(msg).
	// Print t_alloc.alloc_calls, t_alloc.free_calls, t_alloc.total_allocated, and
	// t_alloc.peak_bytes after the block closes, and assert(t_alloc.current_bytes == 0).


	// Verify the recursion guard directly: temporarily omit the backing argument
	// inside tracy_allocator_init (or inspect t_alloc.active_allocs.allocator) and
	// confirm that active_allocs.allocator.procedure != tracy_allocator_proc so map
	// resizes inside tracy_allocator_proc never re-enter tracy_allocator_proc.
}

heap_churn_vs_arena_reuse :: proc() {

	/*
	Allocating and freeing buffers every frame on the general-purpose heap is classic
	Multiplier #1 (Waste): each call searches free lists, updates allocator metadata,
	and fragments cache lines. An arena allocator (mem.Arena) takes one contiguous
	byte buffer up front via mem.arena_init(&arena, buf) and hands out slices by
	bumping a single offset integer forward. When the frame finishes, calling
	free_all(context.allocator) resets that offset back to zero in one write—reusing
	the exact same hot L1/L2 memory on the next frame with zero backing-heap calls.

	    Suppose a frame allocates three 512-byte scratch buffers over 10 frames.
	    On the heap: 30 allocs + 30 frees (15,360 B of allocator traffic).
	    With mem.Arena + free_all: 1 backing setup alloc, then 0 backing allocs and
	    0 backing frees across all 10 frames!

	Odin's context.temp_allocator works the same way out of the box—every call to
	fmt.tprintf or make(..., context.temp_allocator) bumps a per-thread scratch arena
	until you reset it at the end of each frame with free_all(context.temp_allocator).
	*/

	scratch_buf: [4096]byte
	arena: mem.Arena
	mem.arena_init(&arena, scratch_buf[:])
	fmt.printfln("Starter stack arena ready: capacity=%v B", len(scratch_buf))

	// Measure per-frame heap churn across 10 simulated frames:
	// Wrap context.allocator with heap_ta: Tracy_Allocator ("FrameHeap") and inside
	// each frame i in 0..<10 allocate items := make([dynamic]f32, 0, 64), append 128
	// floats, build label := fmt.aprintf("frame=%v", i), and free both before the
	// next frame. Print heap_ta.alloc_calls, heap_ta.free_calls, and total_allocated.


	// Post-fix trace validation using mem.Arena + free_all:
	// Wrap the OS heap in backing_ta: Tracy_Allocator ("ArenaBacking"), allocate one
	// 16 KB backing slice arena_mem := make([]byte, 16 * 1024, tracy_allocator(&backing_ta))
	// (with defer delete(arena_mem, tracy_allocator(&backing_ta))), initialize
	// frame_arena: mem.Arena with arena_mem, and run the same 10-frame loop using
	// context.allocator = mem.arena_allocator(&frame_arena) plus free_all(context.allocator)
	// at the end of every frame. Print backing_ta.alloc_calls and assert that
	// backing_ta.alloc_calls == 1 (zero heap allocations during all 10 steady-state frames!).


	// Also test context.temp_allocator in a 5-frame loop: allocate a slice via
	// make([]u64, 64, context.temp_allocator), compute a small sum, call
	// free_all(context.temp_allocator) at frame end, and confirm temp usage resets.
}

leak_diagnosis_and_resize :: proc() {

	/*
	Memory profilers shine when a subsystem forgets to free one allocation on an
	uncommon branch. Because active_allocs holds every pointer whose .Free has not
	arrived yet, any leak leaves current_bytes > 0 after the frame or shutdown scope
	exits—pointing straight to the exact unfreed pointer and byte count.

	Similarly, if .Resize forgets to remove old_memory from active_allocs before
	inserting the new pointer, or if .Free_All forgets to clear active_allocs, your
	tracker reports phantom live bytes even when the underlying arena is empty.
	*/

	probe_sizes := [3]int{64, 128, 128}
	fmt.printfln("Leak probe check: unfreed [64, 128, 128] slice bytes=%v B", probe_sizes[0] + probe_sizes[1] + probe_sizes[2])

	// Run an intentional leak-diagnosis test:
	// Initialize leak_ta: Tracy_Allocator ("LeakHunt") and run 5 frames inside a
	// scoped block using tracy_allocator(&leak_ta). On frames 0, 1, 3, and 4 free
	// the frame's []u64 buffer with delete(buf), but on frame 2 allocate
	// leaked := make([]u64, 64) and skip delete(leaked). After the loop, assert
	// leak_ta.current_bytes == 64 * size_of(u64) (512 B), loop over ptr, sz in
	// leak_ta.active_allocs to print the leaked pointer and byte size, then free it
	// explicitly and assert leak_ta.current_bytes == 0.


	// Verify .Resize and .Free_All together on a tracked arena:
	// Initialize arena_buf: [8192]byte and sub_arena: mem.Arena, wrap
	// mem.arena_allocator(&sub_arena) inside arena_ta: Tracy_Allocator ("TrackedArena"),
	// allocate 3 slices, grow a [dynamic]u32 past its initial capacity so .Resize runs,
	// assert arena_ta.current_bytes > 0, then call free_all(tracy_allocator(&arena_ta))
	// and assert both arena_ta.current_bytes == 0 and len(arena_ta.active_allocs) == 0.
}

main :: proc() {

	fmt.println("=== 1. Tracy_Allocator and recursion guard ===")
	tracy_allocator_and_recursion_guard()

	fmt.println("\n=== 2. Heap churn vs. mem.Arena and temp_allocator reuse ===")
	heap_churn_vs_arena_reuse()

	fmt.println("\n=== 3. Leak diagnosis, .Resize, and .Free_All verification ===")
	leak_diagnosis_and_resize()
}
