// odin run 205_slices_and_views.odin -file

package main

import "base:runtime"
import "core:fmt"

/*
A slice []T in Odin is a lightweight 16-byte non-owning view into contiguous
memory. Inside the runtime, every slice is just two fields (runtime.Raw_Slice):
a data pointer (rawptr) and an element count (len: int).

Unlike Go slices (which carry a 24-byte header with capacity and silently
allocate when appended to), Odin slices never store capacity and never allocate
behind your back. Resizable buffers have their own dedicated type, [dynamic]T.
Because a slice only borrows someone else's memory, mutating slice[i] mutates
the original array, and holding a slice past a reallocation turns it dangling.

This Primer is split into three focused sections called from main at the bottom.
*/

slice_header_and_views :: proc() {

	/*
	Slicing an array with arr[start:end] builds a new 16-byte header pointing
	at &arr[start] with length (end - start). Zero elements are copied:

	    Suppose backing := [4]int{10, 20, 30, 40}:
	        mid := backing[1:3]   // views {20, 30}
	        mid[0] = 999          // backing becomes {10, 999, 30, 40}

	You can omit either bound: arr[:end] starts at 0, arr[start:] runs to the
	end, and arr[:] creates a view over the entire array. You can also slice a
	slice again (sub := mid[1:2]) to narrow the window further without copying.
	*/

	// Starter anchor: inspect a slice view's 16-byte header (data + len).
	sample := [3]int{1, 2, 3}
	sample_view := sample[:]
	raw_sample := transmute(runtime.Raw_Slice)sample_view
	fmt.printfln("sample_view: %v (len=%v, data=%v)", sample_view, raw_sample.len, raw_sample.data)

	// Declare backing := [6]int{10, 20, 30, 40, 50, 60}, then take three slices:
	// middle := backing[1:5], head := backing[:3], and tail := backing[4:].
	// Also sub-slice middle with inner := middle[1:3] and print all four slices
	// alongside their len(...) values.


	// Mutate middle[0] = 999 and print backing, head, and middle to verify that
	// all three share the same underlying stack array (backing[1] and head[1]
	// both become 999).


	// Inspect middle's raw header using transmute(runtime.Raw_Slice)middle, and
	// check raw_data(middle) == &backing[1] to verify where data points.
	// Also iterate over middle using for val, idx in middle to confirm idx
	// starts at 0 relative to the slice, not 1 from backing.
}

copy_and_nil_vs_empty :: proc() {

	/*
	Because slices only alias memory, you need the built-in copy(dst, src)
	procedure whenever you want an independent duplicate of the elements.
	When we call copy(dst, src), Odin copies min(len(dst), len(src)) elements
	and returns the count copied—and it handles overlapping sub-slices safely
	just like C's memmove:

	    Suppose src := [4]int{1, 2, 3, 4} and dst: [2]int:
	        n := copy(dst[:], src[1:4])   // n == 2, dst becomes {2, 3}

	Also pay attention to zero-length slices: an uninitialized slice s: []int
	has data == nil and len == 0 (so s == nil is true). By contrast, slicing
	arr[0:0] produces len == 0 with a non-nil data pointer (&arr[0]), so
	raw_data(arr[0:0]) != nil even though len is 0.
	*/

	// Starter anchor: compare a nil slice's nil check and length.
	empty_default: []int
	fmt.printfln("empty_default == nil: %v, len=%v", empty_default == nil, len(empty_default))

	// Declare src := [5]int{10, 20, 30, 40, 50} and dst: [3]int.
	// Copy elements with copied := copy(dst[:], src[1:4]), mutate dst[0] = -1,
	// and print copied, dst, and src to verify src stayed untouched.


	// Allocate a heap slice clone := make([]int, len(src)) with defer delete(clone),
	// copy src[:] into clone with copy(clone, src[:]), and print clone.


	// Test truncating copy and overlapping copy: declare short: [2]int and
	// run n := copy(short[:], src[:]) (prints 2 elements), then shift elements
	// inside src with copy(src[1:4], src[0:3]) and print src.


	// Compare uninit_slice: []int with zero_view := src[0:0] by printing
	// == nil, len(...), and raw_data(...) != nil for both.
}

dangling_view_and_bounds_traps :: proc() {

	/*
	A slice never owns the buffer it points to. Two lifetime bugs catch people
	off guard when slicing:

	First, if you take a slice view into a growable [dynamic]T array and then
	append enough items to trigger a heap reallocation, the dynamic array moves
	to a brand-new buffer and frees the old one—leaving your earlier slice
	pointing at freed memory:

	    Suppose buf has cap 2 and holds {10, 20}:
	        stale := buf[:]               // points to old buffer A
	        append(&buf, 30, 40, 50)      // buf moves to new buffer B; A is freed!
	        // reading stale[0] now reads freed memory (dangling slice view)

	Second, writing local := []int{10, 20, 30} allocates the 3 ints on the
	current procedure's stack frame—so returning local from a procedure returns
	a dangling slice pointing into a dead stack frame!
	*/

	// Starter anchor: create a tiny dynamic array near its capacity limit.
	buf := make([dynamic]int, 0, 2)
	defer delete(buf)
	append(&buf, 10, 20)
	fmt.printfln("buf before growth: %v (cap=%v, data=%v)", buf, cap(buf), raw_data(buf))

	// Capture stale_view := buf[:] and print raw_data(stale_view).
	// Next, trigger reallocation by calling append(&buf, 30, 40, 50).
	// Print raw_data(buf) alongside raw_data(stale_view) to prove the buffer
	// moved to a new address (do not read elements from stale_view afterward!).


	// Define a helper double_all :: proc(nums: []int) that scales every element
	// in place with for &n in nums { n *= 2 }. Pass both a fresh dynamic slice
	// buf[:] and a stack slice literal []int{3, 6, 9} into double_all, then
	// define sum_slice :: proc(s: []int) -> int and print the summed totals.


	// Try uncommenting the line below to observe Odin's runtime slice bounds check:
	// bad := buf[1:10]
}

main :: proc() {

	fmt.println("=== 1. Slice headers and shared views ===")
	slice_header_and_views()

	fmt.println("\n=== 2. Copying slices and nil vs empty ===")
	copy_and_nil_vs_empty()

	fmt.println("\n=== 3. Dangling view and bounds traps ===")
	dangling_view_and_bounds_traps()
}
