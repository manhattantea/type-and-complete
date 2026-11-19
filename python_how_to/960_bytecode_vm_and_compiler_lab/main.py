# python 960_bytecode_vm_and_compiler_lab/main.py

# Bytecode VM and Two-Pass Assembler Lab (main.py).
#
# This multi-file Lab parallels odin_how_to/960_bytecode_vm_interpreter_lab and
# connects three focused modules into a working toolchain:
# - isa.py: 32-bit fixed-width instruction packing and signed 16-bit decoding.
# - assembler.py: two-pass symbolic label resolution into 32-bit machine words.
# - vm.py: 16-register fetch-decode-execute loop with match + assert_never and
#   step-budget watchdog errors.

from assembler import AssemblerError
from isa import Instruction, Opcode
from vm import VMError, VirtualMachine

SUM_PROGRAM: str = "\n".join([
    "; Compute 1 + 2 + ... + 10 = 55 using symbolic labels and a negative jump offset.",
    "    LOAD_IMM r0, 0      ; accumulator sum = 0",
    "    LOAD_IMM r1, 1      ; counter i = 1",
    "    LOAD_IMM r2, 1      ; increment step = 1",
    "    LOAD_IMM r3, 11     ; loop bound (stop when i == 11)",
    "loop_start:",
    "    LOAD_IMM r4, 0      ; scratch r4 = i",
    "    ADD r4, r1",
    "    CMP_LT r4, r3       ; r4 = 1 if i < 11 else 0",
    "    JMP_IF_ZERO r4, done",
    "    ADD r0, r1          ; sum += i",
    "    ADD r1, r2          ; i += 1",
    "    JMP loop_start",
    "done:",
    "    PRINT r0",
    "    HALT",
])


def run_vm_pipeline() -> None:

    # Inspect the baseline VM contract before assembling and running SUM_PROGRAM.
    vm = VirtualMachine()
    sentinel_inst = Instruction(op=Opcode.HALT)
    print(
        f"VM ready: opcodes={len(Opcode)}, regs={len(vm.regs)}, "
        f"program_lines={len(SUM_PROGRAM.splitlines())}, sentinel={sentinel_inst.op.name}, "
        f"errors=({AssemblerError.__name__}, {VMError.__name__})"
    )

    # Once isa.py, assembler.py, and vm.py are implemented, expand the imports
    # at the top of this file to bring in assemble_program from assembler and
    # run_vm from vm.

    # Assemble SUM_PROGRAM into code: list[int] = assemble_program(SUM_PROGRAM)
    # and disassemble every instruction word with for pc, word in enumerate(code):
    # Decode inst = Instruction.decode(word) and print the address, raw hex word
    # formatted as 0x{word:08x}, and decoded Instruction. Confirm that JMP
    # loop_start decoded with a negative imm16 offset!


    # Execute output = run_vm(code), print output, and assert output == [55].


    # Synthesize a second assembly program and verify both error paths:
    # - Write a short factorial assembly program using MUL and SUB to compute
    #   5! = 120, assemble it, run it on run_vm(...), and assert [120].
    # - Confirm assemble_program("JMP missing_label") raises AssemblerError.
    # - Confirm run_vm([0x00000000]) raises VMError for an illegal opcode, and
    #   confirm an intentional infinite loop (loop:\n JMP loop) raises VMError
    #   when called with max_steps=50.


def main() -> None:

    print("=== 960: Bytecode VM and Two-Pass Assembler Lab ===")
    run_vm_pipeline()


if __name__ == "__main__":
    main()
