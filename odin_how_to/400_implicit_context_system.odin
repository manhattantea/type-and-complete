// odin run 400_implicit_context_system.odin -file

package main

import "core:fmt"
import "core:mem"
import "base:runtime"

/*
In C or Rust, if a function five calls deep needs to allocate memory or emit a
log line, you either pass an allocator and logger down through every single
signature in the call chain, or you hide them in process-wide globals that break
thread isolation. Odin solves this with an implicit 'context' parameter.

Every standard Odin procedure secretly receives a hidden pointer to a
thread-local runtime.Context struct containing six cross-cutting fields:
  context.allocator              default heap or arena allocator (runtime.Allocator)
  context.temp_allocator         per-thread scratch allocator (runtime.Allocator)
  context.logger                 structured logger (runtime.Logger)
  context.assertion_failure_proc custom assertion failure handler
  context.user_ptr               arbitrary caller data pointer (rawptr)
  context.user_index             arbitrary caller integer tag (int)

When you assign to a field such as context.user_index = 42 inside a block, the
compiler copies runtime.Context onto that block's stack frame, modifies the
copy, and passes the copy to every call inside that scope. When execution exits
the closing brace, the caller's original context is back automatically.

This file is split into four sections called from main at the bottom so you can
read top to bottom and run the program at any point.
*/

build_numbered_batch :: proc(count: int) -> []int {

	batch := make([]int, count)
	for i in 0..<count {
		batch[i] = (i + 1) * 10
	}
	return batch
}

raw_add :: proc "contextless" (a, b: int) -> int {

	return a + b
}

inspecting_default_context :: proc() {

	/*
	Because context is a normal struct value of type runtime.Context, you can
	copy it into a local variable or inspect any of its six fields directly.
	By default, context.allocator points to Odin's heap allocator,
	context.temp_allocator points to a pre-initialized thread-local ring arena,
	context.user_index starts at 0, and context.user_ptr starts at nil.
	*/

	// Here is a quick look at the default runtime.Context values on entry:

	default_ctx: runtime.Context = context
	fmt.printfln("Default user_index: %d, user_ptr: %p", default_ctx.user_index, default_ctx.user_ptr)

	// Print the procedure pointers stored inside default_ctx.allocator.procedure,
	// default_ctx.temp_allocator.procedure, and default_ctx.logger.procedure
	// using fmt.printfln with %v so you can see the wired runtime callbacks.


	// Write a zero-parameter procedure print_current_user :: proc() above main
	// that reads context.user_index and context.user_ptr directly.
	// If context.user_ptr != nil, dereference (^string)(context.user_ptr)^ to
	// read the name; otherwise use "<none>". Print both values, then call
	// print_current_user() here to observe the untouched defaults.
}

scoped_user_data_overrides :: proc() {

	/*
	Modifying context never mutates a shared global variable. Suppose
	context.user_index starts at 0 before entering an inner block:

	    outer := context.user_index          // 0
	    {
	        context.user_index = 777
	        // any procedure called here sees context.user_index == 777
	    }
	    after := context.user_index          // back to 0 automatically!

	Nested blocks work the same way: an inner block copies the surrounding
	scope's already-modified context, overrides just one field, and leaves
	the rest inherited until the inner closing brace pops that frame copy.
	*/

	// Confirm the starting state before creating any scoped overrides:

	outer_id := context.user_index
	fmt.printfln("Before inner scope, context.user_index = %d", outer_id)

	// Open an inner block, declare secret_name := "Agent-42", assign
	// context.user_index = 777 and context.user_ptr = &secret_name, and call
	// print_current_user() inside the block.


	// Nest a second inner block inside the first where you override only
	// context.user_index = 999 while keeping user_ptr inherited, call
	// print_current_user(), then call print_current_user() after the inner
	// block closes and again after the outer block closes to verify step-by-step
	// restoration.


	// Write tag_with_user_index :: proc(label: string) that prints
	// "[worker %d] %s" using context.user_index and label. Call it inside a
	// loop: for worker_id in 1..=3 { context.user_index = worker_id; tag_with_user_index("job") }
	// Print context.user_index after the loop to confirm it reverted to 0.
}

injecting_context_allocator :: proc() {

	/*
	The real payoff of Odin's context system is implicit allocator injection.
	Procedures like make, new, and fmt.aprintf read context.allocator unless
	you pass an explicit allocator argument.

	Suppose build_numbered_batch :: proc(count: int) -> []int allocates its
	slice using make([]int, count). Called normally, that slice lands on the
	heap and needs delete(batch). If you wrap the exact same call inside a
	block where context.allocator = arena_alloc, build_numbered_batch puts its
	slice inside your arena without changing a single parameter or line inside
	build_numbered_batch!
	*/

	// Baseline call on the default heap allocator (must delete afterward):

	heap_batch := build_numbered_batch(3)
	defer delete(heap_batch)
	fmt.printfln("Heap batch: %v", heap_batch)

	// Backing buffer and arena ready for scoped allocator injection:

	backing: [256]byte
	arena: mem.Arena
	mem.arena_init(&arena, backing[:])
	arena_alloc := mem.arena_allocator(&arena)
	fmt.printfln("Arena ready (offset=%d, proc=%v)", arena.offset, arena_alloc.procedure)

	// Open a scoped block, assign context.allocator = arena_alloc, and call
	// arena_batch := build_numbered_batch(4) without changing its signature.
	// Notice you do not call delete(arena_batch); print arena_batch and
	// arena.offset to verify all 4 integers live inside backing.


	// Open a second scoped block with context.allocator = arena_alloc, create
	// notes := make([dynamic]string, 0, 4), append fmt.aprintf("note-%d", 1),
	// print notes and arena.offset, then wipe the entire arena at once with
	// free_all(arena_alloc) after the block exits.
}

contextless_and_restoration :: proc() {

	/*
	Procedures marked proc "contextless" () omit the hidden context pointer at
	the ABI boundary so they match C function pointers and OS callbacks.
	Because no context pointer arrives on entry, calling fmt.println or reading
	context.user_index inside a contextless procedure is a compile error until
	you explicitly initialize context = runtime.default_context().

	    Suppose a C library invokes callback :: proc "contextless" (code: int):
	        context = runtime.default_context()
	        fmt.printfln("Safe to log code=%d now", code)
	*/

	// Calling a pure contextless calculation that never touches context:

	fmt.printfln("Contextless raw_add(3, 4) = %d", raw_add(3, 4))

	// Write c_style_callback :: proc "contextless" (code: int) above main,
	// restore Odin's runtime context on its first line using:
	// context = runtime.default_context()
	// Then call fmt.printfln("Callback received code=%d", code) and invoke
	// c_style_callback(200) here.


	// Write a small local proc "contextless" () literal below and try
	// uncommenting a call to fmt.println("missing context") inside it before
	// assigning context = runtime.default_context() to see the compiler error.
}

main :: proc() {

	fmt.println("=== 1. Inspecting default context ===")
	inspecting_default_context()

	fmt.println("\n=== 2. Scoped user_index and user_ptr overrides ===")
	scoped_user_data_overrides()

	fmt.println("\n=== 3. Injecting context.allocator into an unchanged helper ===")
	injecting_context_allocator()

	fmt.println("\n=== 4. Contextless procedures and context restoration ===")
	contextless_and_restoration()
}
