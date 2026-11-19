// odin run 190_custom_iterators.odin -file

package main

import "core:fmt"

/*
Many languages require iterator traits, interfaces, or heap-allocated coroutine
state machines to plug a custom sequence into a 'for' loop.

Odin's 'for ... in' loop supports custom iterators with zero traits and zero
hidden allocations. Any procedure whose return signature ends with a 'bool' in
either of these two forms can sit directly on the right-hand side of 'for ... in':
- '(val: T, ok: bool)' for a 1-value loop: 'for val in next(&it)'
- '(val: T, idx: int, ok: bool)' for a 1- or 2-value loop: 'for val, idx in next(&it)'

On every pass, Odin calls the procedure once; if the trailing 'bool' is 'true',
the loop binds the yielded values and runs the body; when it returns 'false',
the loop ends. Because your iterator struct lives on your own stack frame,
iteration state stays completely transparent.
*/

Countdown_Iter :: struct {
	remaining: int,
}

countdown_next :: proc(it: ^Countdown_Iter) -> (val: int, ok: bool) {

	if it.remaining <= 0 do return 0, false
	val = it.remaining
	it.remaining -= 1
	return val, true
}

one_value_iterator_basics :: proc() {

	/*
	Suppose 'cd := Countdown_Iter{remaining = 3}'. Each call to 'countdown_next(&cd)'
	checks 'it.remaining > 0', yields the current number, decrements 'it.remaining',
	and returns 'true'. After yielding 3, 2, and 1, 'it.remaining' is 0, so the
	fourth call returns '0, false' and the 'for' loop exits cleanly.
	*/

	cd := Countdown_Iter{remaining = 3}
	for v in countdown_next(&cd) {
		fmt.printfln("countdown: %v", v)
	}

	// Define 'Fibonacci_Iter :: struct { a, b, limit: int }' and
	// 'fib_next :: proc(it: ^Fibonacci_Iter) -> (val: int, ok: bool)' at file scope.
	// Return '0, false' when 'it.a > it.limit'; otherwise save 'val = it.a',
	// advance 'it.a, it.b = it.b, it.a + it.b', and return 'val, true'.


	// Initialize 'fib := Fibonacci_Iter{a = 0, b = 1, limit = 50}' and print every
	// value with 'for val in fib_next(&fib)'. Then run a second identical loop on
	// '&fib' without resetting it to confirm an exhausted iterator yields 0 times.
}

two_value_step_iterators :: proc() {

	/*
	Returning three values '(val: T, idx: int, ok: bool)' lets callers ask for
	both the generated value and a step counter ('for val, idx in next(&it)'),
	or drop the index and write 'for val in next(&it)' using the exact same
	iterator procedure.

	    Suppose 'step_range_next(&it)' yields '(10, 0, true)', then '(20, 1, true)',
	    and finally '(0, 0, false)':
	    Under the hood, 'for val, idx in step_range_next(&it)' behaves like an
	    infinite loop that calls 'step_range_next(&it)' before every pass and
	    breaks the moment the trailing 'ok' is false.
	*/

	fmt.println("Three-return iterators support both 2-value and 1-value loops.")

	// Define 'Step_Range_Iter :: struct { current, stop, step, index: int }' at file scope.


	// Write 'step_range_next :: proc(it: ^Step_Range_Iter) -> (val: int, idx: int, ok: bool)'
	// at file scope. Guard against non-positive steps ('it.step <= 0') or reaching
	// the bound ('it.current >= it.stop') by returning '0, 0, false'; otherwise
	// capture 'val = it.current' and 'idx = it.index', advance 'it.current += it.step'
	// and 'it.index += 1', and return 'val, idx, true'.


	// Initialize 'it := Step_Range_Iter{current = 10, stop = 50, step = 10}' and
	// iterate with 'for val, idx in step_range_next(&it)' (expected: 0:10, 1:20,
	// 2:30, 3:40). Then drive 'it2 := Step_Range_Iter{current = 100, stop = 115, step = 5}'
	// with the 1-value loop 'for val in step_range_next(&it2)' (expected: 100, 105, 110).
}

stateful_collection_cursor :: proc() {

	/*
	Iterators are especially handy as zero-allocation cursors over existing
	slices or strings. Suppose you store 'items: []int' and 'cursor: int' inside
	a struct. Instead of allocating a filtered '[dynamic]int' copy, your step
	procedure advances 'it.cursor' until it finds a matching element and yields
	'(val, original_index, true)'.

	Even better, because 'cursor' lives inside the struct on the caller's stack,
	breaking out of the loop early leaves 'cursor' right after the item that
	stopped you—a second 'for' loop on the same cursor resumes seamlessly from
	where the first loop left off.
	*/

	fmt.println("Stateful cursors filter or tokenize slices with zero heap allocation.")

	// Define 'Positive_Cursor :: struct { items: []int, cursor: int }' at file scope,
	// and write 'positive_next :: proc(it: ^Positive_Cursor) -> (val: int, src_idx: int, ok: bool)'
	// that loops while 'it.cursor < len(it.items)', saves 'src_idx = it.cursor' and
	// 'val = it.items[it.cursor]', increments 'it.cursor += 1', skips values
	// 'val <= 0' with 'continue', and returns 'val, src_idx, true' on positive items.


	// Create 'cur := Positive_Cursor{items = []int{-4, 7, 0, 12, -1, 5, 9}}'.
	// First, loop with 'for val, idx in positive_next(&cur)', print each match,
	// and 'break' as soon as 'val > 10' (stops after idx 3, val 12).
	// Second, run another 'for val, idx in positive_next(&cur)' on the exact same
	// 'cur' and confirm it resumes at idx 5 (val 5) and idx 6 (val 9).


	// Write a zero-allocation word splitter: define
	// 'Word_Cursor :: struct { text: string, pos: int }' and
	// 'word_next :: proc(it: ^Word_Cursor) -> (word: string, ok: bool)' that skips
	// spaces (' '), slices from 'start' up to the next space or end of string,
	// and returns 'it.text[start:end], true'. Test it on "  odin   custom  iterators ".
}

main :: proc() {

	fmt.println("=== 1. One-value custom iterators ===")
	one_value_iterator_basics()

	fmt.println("\n=== 2. Two-value step iterators ===")
	two_value_step_iterators()

	fmt.println("\n=== 3. Stateful collection and string cursors ===")
	stateful_collection_cursor()
}
