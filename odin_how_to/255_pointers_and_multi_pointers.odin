// odin run 255_pointers_and_multi_pointers.odin -file

package main

import "core:fmt"
import "core:mem"

/*
In C, one syntax ('int *p') blurs two distinct ideas: "a pointer to one int"
and "a pointer to a contiguous array of many ints." Odin separates them cleanly
at the type level so pointer bugs cannot hide behind implicit decay:

    ^T       pointer to at most ONE value of T (no pointer arithmetic!)
    [^]T     multi-pointer to 0 or more contiguous T values (indexable/sliceable)
    rawptr   untyped memory address (like C's void*)
    uintptr  pointer-sized unsigned integer for address and alignment math
*/

Node :: struct {
	val:  int,
	next: ^Node,
}

Packet :: struct {
	tag:    u16,
	flags:  u16,
	length: u32,
}

single_pointers_and_auto_deref :: proc() {

	/*
	A single pointer '^T' holds the address of one T (or nil). Take an address
	with '&x' and read or write the target value with postfix 'p^'. Postfix '^'
	chains naturally left-to-right ('head.next^.val' instead of C's awkward
	'(*head.next).val'). Better yet, accessing fields ('p.val') or indexing a
	pointer to an array ('arr_ptr[i]') automatically dereferences one level so
	Odin needs no '->' arrow operator.

	Because '^T' points to a single item, pointer arithmetic like 'head_ptr + 1'
	is a compile-time error.
	*/

	// Starter ^Node demonstrating both auto-dereference (head_ptr.val) and postfix ^:
	head := Node{val = 1, next = nil}
	head_ptr: ^Node = &head
	fmt.printfln("Head node via pointer: val=%v, explicit deref=%v", head_ptr.val, head_ptr^)

	// Try uncommenting below to see Odin reject arithmetic on a single pointer ^T:
	// bad_ptr := head_ptr + 1


	// Build a 3-node stack linked list:
	// n3 := Node{val = 30, next = nil}
	// n2 := Node{val = 20, next = &n3}
	// n1 := Node{val = 10, next = &n2}
	// Walk the list with curr: ^Node = &n1 in a 'for curr != nil' loop, printing
	// curr.val and advancing curr = curr.next.


	// Write a small mutating helper at file scope:
	// swap_ints :: proc(a, b: ^int)
	// using a temporary variable (tmp := a^; a^ = b^; b^ = tmp). Call it on two
	// local ints x := 5 and y := 99 and print x and y before and after.


	// Test pointer-to-fixed-array auto-indexing: declare nums := [3]int{7, 8, 9}
	// and arr_ptr: ^[3]int = &nums. Read arr_ptr[1] directly without writing
	// arr_ptr^[1], then assign arr_ptr[2] = 90 and print nums.
}

multi_pointers_and_slicing :: proc() {

	/*
	When talking to C buffers or walking raw backing memory without a stored
	slice length, use a multi-pointer '[^]T'. You obtain one from a slice or
	array view via 'raw_data(slice)' (which hands back the raw data pointer).

	Suppose scores := [4]int{100, 200, 300, 400} and mp: [^]int = raw_data(scores[:]):
	'mp[2]' reads 300, 'mp[1:]' returns a shifted '[^]int' pointing at 200, and
	'mp[0:4]' re-attaches a length to form a bounds-checked '[]int' slice!
	Because '[^]T' carries no length of its own, calling 'len(mp)' is rejected
	at compile time—only slice it back into '[]T' once you know the element count.
	*/

	// Declare scores := [4]int{100, 200, 300, 400} and obtain
	// mp: [^]int = raw_data(scores[:]).
	// Print mp[0] and mp[2], then advance the multi-pointer by 1 element with
	// mp_shifted := mp[1:] and print mp_shifted[0] (expected: 200).


	// Convert mp back into a safe bounded slice using bounded: []int = mp[0:4]
	// and iterate 'for v in bounded' to print every element.


	// Demonstrate mutation through a multi-pointer: set mp_shifted[1] = 999
	// and print scores afterward to prove mp_shifted aliases scores[2] directly.
}

rawptr_ptr_to_bytes_and_alignment :: proc() {

	/*
	When you inspect arbitrary memory, compute buffer offsets, or write a custom
	allocator, three tools bridge typed pointers and raw bytes:

	'rawptr' holds an untyped address (convert '^T' or '[^]T' with 'rawptr(p)',
	and convert back with '(^T)(rp)'). 'mem.ptr_to_bytes(&val)' returns a safe
	'[]u8' slice covering the exact 'size_of(T)' bytes of any variable so you can
	hash, serialize, or hex-dump structs cleanly.

	For alignment math, convert 'rawptr' to 'uintptr' (an unsigned integer wide
	enough to hold an address). Suppose you need to round an address 'addr' up
	to a power-of-2 boundary 'align := uintptr(16)':
	    aligned := (addr + align - 1) &~ (align - 1)
	Adding 'align - 1' pushes any unaligned address into the next block, and
	'&~' (bit clear) masks off the low bits so 'aligned' is an exact multiple
	of 16. Suppose addr is 103 and align is 16: (103 + 15) &~ 15 = 118 &~ 15 = 112.
	*/

	// Starter mem.ptr_to_bytes view over a Packet struct:
	pkt := Packet{tag = 0xCAFE, flags = 1, length = 64}
	pkt_bytes := mem.ptr_to_bytes(&pkt)
	fmt.printfln("Starter ptr_to_bytes: len=%v, first two bytes=0x%02x 0x%02x", len(pkt_bytes), pkt_bytes[0], pkt_bytes[1])

	// Print every byte of pkt_bytes in hex (%02x) on one line, then also view an
	// array of 2 Packets with mem.ptr_to_bytes(&pkts[0], 2) and verify its byte
	// length equals 2 * size_of(Packet) (16 bytes).


	// Cast &pkt to rawptr and then to uintptr, print the numeric address in hex
	// (%#x), and round it back to a ^Packet via (^Packet)(rawptr(addr)) to read
	// restored.tag.


	// Practice uintptr alignment arithmetic: declare buffer: [64]u8, take an
	// unaligned interior address unaligned_addr := uintptr(&buffer[3]), and
	// compute aligned_16 := (unaligned_addr + 16 - 1) &~ uintptr(16 - 1).
	// Print unaligned_addr % 16 vs aligned_16 % 16 (expected: 0) and the byte
	// delta aligned_16 - unaligned_addr.


	// Write a reusable helper at file scope:
	// align_forward_uintptr :: proc(addr, align: uintptr) -> uintptr
	// asserting that align is a power of two (align > 0 && (align & (align - 1)) == 0)
	// and returning (addr + align - 1) &~ (align - 1). Test it on 103 with
	// align = 16 (expected: 112) and align = 64 (expected: 128).
}

main :: proc() {

	fmt.println("=== 1. Single pointers (^T) and auto-deref ===")
	single_pointers_and_auto_deref()

	fmt.println("\n=== 2. Multi-pointers ([^]T) and slicing ===")
	multi_pointers_and_slicing()

	fmt.println("\n=== 3. rawptr, mem.ptr_to_bytes, and uintptr alignment ===")
	rawptr_ptr_to_bytes_and_alignment()
}
