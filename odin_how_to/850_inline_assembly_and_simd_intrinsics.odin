// odin run 850_inline_assembly_and_simd_intrinsics.odin -file

package main

import "base:intrinsics"
import "core:fmt"

/*
Sometimes a hot path needs a specific CPU instruction that ordinary arithmetic
cannot express cleanly: reading the hardware cycle counter, counting set bits,
reversing bit order, swapping byte endianness, or checking integer overflow
from the CPU carry flag without a branch.

Odin exposes those capabilities at two levels:
First, "base:intrinsics" provides portable compiler intrinsics that LLVM
lowers straight to single machine instructions across x86_64, ARM64, and
RISC-V. For example, intrinsics.count_ones emits POPCNT on x86_64 or CNT on
ARM64, and intrinsics.read_cycle_counter emits RDTSC or CNTVCT_EL0.

Second, Odin provides native inline assembly blocks written as:
    asm(params) -> (results) [ register_bindings ] { instructions }(args)
Because inline assembly targets a single CPU ISA, wrap asm procedures inside
'when ODIN_ARCH == .amd64' (or .arm64) compile-time guards so the file still
compiles cleanly on other architectures.
*/

when ODIN_ARCH == .amd64 {
	asm_add :: proc "contextless" (a, b: u32) -> u32 {

		return asm(a, b: u32) -> (res: u32) [
			a -> res = %eax,
			b = %ecx,
		] {
			add b, res
		}(a, b)
	}
}

cycle_and_bit_intrinsics :: proc() {

	/*
	Hardware bit intrinsics replace slow 32-step loops with one CPU cycle:
	- intrinsics.read_cycle_counter() reads the core timestamp counter.
	- intrinsics.count_ones(x) counts set 1-bits (population count).
	- intrinsics.count_leading_zeros(x) counts 0-bits down from the MSB.
	- intrinsics.count_trailing_zeros(x) counts 0-bits up from the LSB.
	- intrinsics.reverse_bits(x) mirrors all bits end-to-end (bit 0 <-> bit N-1).

	Suppose mask: u8 = 0b0000_1101 (decimal 13). Then count_ones(mask) is 3,
	count_trailing_zeros(mask) is 0, count_leading_zeros(mask) is 4, and
	reverse_bits(mask) is 0b1011_0000 (0xB0).
	*/

	initial_cycles := intrinsics.read_cycle_counter()
	fmt.printfln("Initial CPU cycle counter: %d", initial_cycles)

	// Measure elapsed CPU cycles across a tiny loop:
	// Capture t0 := intrinsics.read_cycle_counter(), sum i in 0..<1000 into
	// acc, capture t1 := intrinsics.read_cycle_counter(), and print acc and
	// elapsed := t1 - t0 with fmt.printfln.


	// Declare bitmask: u32 = 0b1011_0001_1110_0000.
	// Compute ones := intrinsics.count_ones(bitmask),
	// tz := intrinsics.count_trailing_zeros(bitmask), and
	// lz := intrinsics.count_leading_zeros(bitmask), then print all three.


	// Reverse bit order using intrinsics.reverse_bits:
	// Declare nibble_pattern: u8 = 0b1101_0010, compute
	// mirrored := intrinsics.reverse_bits(nibble_pattern), and print both in
	// 8-bit binary (%#08b) using fmt.printfln (expected: 0b01001011).
}

endian_and_overflow_intrinsics :: proc() {

	/*
	Network protocols and binary file formats often store multi-byte integers in
	big-endian order while x86_64 and ARM64 CPUs operate in little-endian order.
	Calling intrinsics.byte_swap(x) emits a single BSWAP (or REV) instruction to
	flip byte order in place.

	Meanwhile, intrinsics.overflow_add(a, b) performs an unsigned or signed
	addition and returns (result, did_overflow) by reading the CPU carry or
	overflow flag directly without branching. Suppose you add u8(250) + u8(20):
	270 wraps modulo 256 to 14, and did_overflow is true.
	*/

	// Declare packet_magic: u32 = 0x12345678, compute
	// swapped := intrinsics.byte_swap(packet_magic), and print both in
	// 8-digit hex (%#08X) using fmt.printfln (expected: 0x78563412).


	// Call wrapped, overflowed := intrinsics.overflow_add(u8(250), u8(20))
	// and print both wrapped (14) and overflowed (true) with fmt.printfln.
	// Also test intrinsics.overflow_add(u8(100), u8(20)) to confirm overflowed
	// stays false when the sum fits inside u8.


	// Test underflow detection with intrinsics.overflow_sub(u16(5), u16(12)):
	// capture diff, underflowed := intrinsics.overflow_sub(u16(5), u16(12))
	// and print both values with fmt.printfln.


	// Compare byte_swap on a 64-bit network value:
	// net_id: u64 = 0x0102_0304_0506_0708
	// Swap it with intrinsics.byte_swap(net_id) and print in hex (%#016X).
}

inline_asm_and_clobbers :: proc() {

	/*
	In Odin's inline asm expression:
	    asm(a, b: u32) -> (res: u32) [ a -> res = %eax, b = %ecx ] { add b, res }(a, b)
	the bracketed register bindings map Odin parameters and return values onto
	concrete CPU registers ('a -> res = %eax' ties input 'a' and output 'res'
	to '%eax', while 'b = %ecx' places 'b' in '%ecx').
	*/

	when ODIN_ARCH == .amd64 {
		sum := asm_add(40, 2)
		fmt.printfln("AMD64 inline asm_add(40, 2) = %d", sum)
	} else {
		fmt.println("Skipping AMD64 inline asm on non-amd64 target")
	}

	// Inside a 'when ODIN_ARCH == .amd64' block, write a second inline asm
	// helper outside this procedure:
	// asm_sub :: proc "contextless" (a, b: u32) -> u32
	// using asm(a, b: u32) -> (res: u32) [ a -> res = %eax, b = %ecx ] { sub b, res }(a, b)
	// Call asm_sub(100, 58) inside 'when ODIN_ARCH == .amd64' and print 42.


	// Write a third 'when ODIN_ARCH == .amd64' helper demonstrating a no-op
	// memory barrier pattern:
	// asm_fence_nop :: proc "contextless" ()
	// using asm() [] { nop }()
	// Call asm_fence_nop() and explain in a short comment why register bindings
	// and clobber awareness matter under optimization.
}

main :: proc() {

	fmt.println("=== 1. Cycle and bit intrinsics ===")
	cycle_and_bit_intrinsics()

	fmt.println("\n=== 2. Byte swap and overflow intrinsics ===")
	endian_and_overflow_intrinsics()

	fmt.println("\n=== 3. Inline assembly and clobbers ===")
	inline_asm_and_clobbers()
}
