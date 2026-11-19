// odin run 960_bytecode_vm_interpreter_lab

package main

import "core:fmt"

/*
This Lab connects all three VM layers across four package files:
- isa.odin defines Opcode, the 32-bit Instruction bit_field, and VM_Error.
- assembler.odin parses text assembly lines into packed Instruction words.
- vm.odin executes the instruction slice over 16 registers and a stack array.
- main.odin assembles SAMPLE_PROGRAM (summing 1 + 2 + ... + 10 = 55), runs it,
  and checks that malformed assembly returns .Unknown_Mnemonic cleanly.

The program buffer uses a heap-backed [dynamic]Instruction paired with
'defer delete(program)' right at declaration so its memory is guaranteed to
be freed regardless of which branch main exits through.
*/

SAMPLE_PROGRAM :: `
LOAD r0, 0
LOAD r1, 1
LOAD r2, 1
ADD r0, r1
ADD r1, r2
CMP_LT r3, r1, 11
JMP_IF_ZERO r3, 8
JMP 3
PRINT r0
HALT
`

main :: proc() {

	fmt.println("=== 1. Bytecode VM Baseline ===")
	program: [dynamic]Instruction
	defer delete(program)
	sample_inst := Instruction{op = .Load_Imm, dst = 0, imm16 = 42}
	fmt.printfln("Instruction size: %d bytes, sample op: %v, source length: %d bytes", size_of(Instruction), sample_inst.op, len(SAMPLE_PROGRAM))

	fmt.println("\n=== 2. Assemble and Execute Sample Program ===")

	// Assemble SAMPLE_PROGRAM into &program using assemble_program(SAMPLE_PROGRAM, &program).
	// Capture err := assemble_program(SAMPLE_PROGRAM, &program); if err != .None,
	// print the error with fmt.eprintfln and return early.
	// Otherwise print len(program) to verify how many 32-bit instructions were emitted.


	// Execute program[:] on the register VM via run_err := run_vm(program[:]).
	// Verify run_err == .None and confirm the VM outputs [vm] r0 = 55.


	fmt.println("\n=== 3. Error Propagation Check ===")

	// Call clear(&program) to reuse the existing capacity without reallocating,
	// then pass an invalid line such as "BAD_OP r0, 1" into assemble_program.
	// Print the returned VM_Error and assert it equals .Unknown_Mnemonic.
}
