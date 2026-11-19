// odin run 030_operators_and_precedence.odin -file

package main

import "core:fmt"

/*
Odin keeps C's familiar arithmetic operators (+, -, *, /) while fixing several
classic C traps around modulo, bitwise operators, and operator precedence.

Knowing these differences upfront saves hours of subtle bitmask and wrap-around
debugging when porting algorithms from C, C++, or Python.

This file is split into three small sections called from main at the bottom so
you can read top to bottom and run the program at any point.
*/

remainder_vs_floored_modulo :: proc() {

	/*
	Odin gives you two distinct modulo operators:
	'a % b' is truncated remainder toward zero, so the sign follows the dividend
	(-7 % 3 == -1).
	'a %% b' is mathematical floored modulo, so the sign follows the divisor
	(-7 %% 3 == 2).

	Suppose a 4-slot ring buffer sits at slot := 0 and steps backward by 1 to
	-1. Using -1 % 4 produces -1 (an out-of-bounds negative index!), whereas
	-1 %% 4 produces 3 (wrapping cleanly to the final slot without needing C's
	((i % n) + n) % n workaround).
	*/

	// Contrasting truncated '%' with floored '%%' on -7:

	cursor := -7
	fmt.printfln("-7 %% 3 = %v | -7 %%%% 3 = %v", cursor % 3, cursor %% 3)

	// Compute wrapped_slot := (0 - 1) %% 4 and print wrapped_slot (expected: 3).


	// Write a reusable helper procedure at file scope named:
	// wrap_ring_index :: proc(idx, size: int) -> int
	// Inside it, return idx %% size. Call wrap_ring_index from here with inputs
	// (-1, 4), (-5, 4), and (9, 4) and print all three wrapped indices (3, 3, 1).
}

bitwise_ops_packing_and_precedence :: proc() {

	/*
	Because Odin reserves '^' exclusively for pointers (^T and ptr^), bitwise
	XOR uses '~' (a ~ b), and unary bitwise NOT also uses '~' (~a). Bit-clear
	(AND-NOT) gets its own dedicated operator: 'a &~ mask' clears every bit
	set in mask without writing 'a & (~mask)'.

	Watch the C-vs-Odin operator precedence difference carefully. In C, '=='
	and '!=' bind tighter than '&', so 'flags & MASK != 0' silently parses as
	'flags & (MASK != 0)' (a notorious C bug!). In Odin, bitwise '&', '&~',
	'<<', and '>>' sit at multiplicative precedence above '+', '-', '|', '~',
	and all of them bind tighter than comparisons ('==', '!=', '<', '>').
	As a flip side, '1 << 4 + 1' in Odin is (1 << 4) + 1 = 17 whereas in C it is
	1 << 5 = 32, so explicit parentheses around bit math keep intent obvious.
	*/

	// Checking a flag bit with explicit grouping:

	demo_mask: u8 = 0b1010_0001
	fmt.printfln("demo_mask = %08b | bit 0 set? %v", demo_mask, (demo_mask & 0b0000_0001) != 0)

	// Declare flags: u8 = 0b0000_0101 (bits 0 and 2 set). Apply compound bitwise
	// assignments in order: set bit 1 with '|= 0b0000_0010', toggle bit 0 with
	// '~= 0b0000_0001', and clear bit 2 with '&~= 0b0000_0100'.
	// Print flags and ~flags in 8-bit binary using "%08b" (00000010 and 11111101).


	// Test binary XOR directly on two masks: compute diff := u8(0b1100_1010) ~ u8(0b1010_1100)
	// and print diff in "%08b" (expected: 01100110, marking every differing bit).


	// Verify Odin's precedence rules: evaluate 'flags & 0b0000_0010 != 0' and
	// '(flags & 0b0000_0010) != 0' to confirm both yield true, then print
	// '1 << 4 + 1' alongside '1 << (4 + 1)' (17 vs 32) to lock in the shift vs
	// addition rule.


	// Bit-pack four u8 channels (r: u8 = 0xAA, g: u8 = 0xBB, b: u8 = 0xCC,
	// a: u8 = 0xFF) into packed_rgba: u32 using shifts ('<<') and '|':
	// packed_rgba := (u32(r) << 24) | (u32(g) << 16) | (u32(b) << 8) | u32(a)
	// Print packed_rgba with "0x%08X" (expected: 0xAABBCCFF).


	// Unpack all four channels back out from packed_rgba using right-shifts and
	// '& 0xFF' (for example, unpacked_g := u8((packed_rgba >> 16) & 0xFF)) and
	// print each unpacked channel with "0x%02X".
}

ternary_expressions_and_no_increment :: proc() {

	/*
	Odin supports two inline ternary conditional forms so you can pick the one
	that reads clearest in context:
	C-style:      cond ? when_true : when_false
	Python-style: when_true if cond else when_false

	Odin deliberately has no '++' or '--' operators. Incrementing or
	decrementing is always a statement (i += 1 or i -= 1), never an expression
	nested inside another line like C's undefined 'a[i++] = i'.
	*/

	// Inline ternary starter:

	base_temp := 24
	fmt.printfln("Weather: %v", base_temp > 20 ? "Warm" : "Cool")

	// Declare score := 75. Compute status_label using a C-style ternary
	// (score >= 50 ? "Pass" : "Fail") and clamped_score using an Odin-style
	// ternary (100 if score > 100 else score). Print both values.


	// Declare latency_ms := 45 and classify tier_label into "fast", "ok", or
	// "slow" using chained 'a if cond else b' expressions. Increment latency_ms
	// by 1 with '+= 1' and print both.
	// Try uncommenting below to confirm Odin rejects C's postfix '++':
	// latency_ms++
}

main :: proc() {

	fmt.println("=== 1. Remainder vs floored modulo ===")
	remainder_vs_floored_modulo()

	fmt.println("\n=== 2. Bitwise ops, packing, and precedence ===")
	bitwise_ops_packing_and_precedence()

	fmt.println("\n=== 3. Ternary expressions and no increment ===")
	ternary_expressions_and_no_increment()
}
