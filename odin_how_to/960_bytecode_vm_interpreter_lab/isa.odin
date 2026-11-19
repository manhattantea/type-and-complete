// Instruction set architecture and packed bit-field encoding for 960_bytecode_vm_interpreter_lab.

package main

/*
A bytecode VM stays fast when every instruction fits into a tiny, fixed-width
word so the fetch loop reads contiguous bytes straight from L1 cache.

When we define 'Instruction :: bit_field u32 { ... }', Odin packs every field
into exact bit slices of one 32-bit unsigned integer without manual shift-and-mask
macros. The bit widths add up to 32 bits:
- op: 8-bit Opcode selecting the operation
- dst: 4-bit destination register index (0..=15)
- src_a: 4-bit source register index (0..=15)
- imm16: signed 16-bit immediate constant or jump target (-32768..=32767)

Suppose you construct inst := Instruction{op = .Load_Imm, dst = 1, imm16 = -5}.
Odin packs those fields into 4 bytes (size_of(Instruction) == 4) and automatically
sign-extends inst.imm16 back to -5 when the VM reads it as an i16.

Notice also why VM_Error puts '.None' first (underlying value 0). Odin's
'or_return' operator inspects the final return value of a call: 0 means success,
and any non-zero enum value immediately returns that error to the caller.
*/

Opcode :: enum u8 {
	Load_Imm,
	Add,
	Sub,
	Mul,
	Cmp_Lt,
	Jmp,
	Jmp_If_Zero,
	Print,
	Halt,
}

Instruction :: bit_field u32 {
	op:    Opcode | 8,
	dst:   u8     | 4,
	src_a: u8     | 4,
	imm16: i16    | 16,
}

#assert(size_of(Instruction) == 4)

VM_Error :: enum {
	None,
	Stack_Overflow,
	Invalid_Opcode,
	Unknown_Mnemonic,
}
