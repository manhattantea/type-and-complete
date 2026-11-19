# Module for 960_bytecode_vm_and_compiler_lab (run via: python 960_bytecode_vm_and_compiler_lab/main.py)

# Register-Based Virtual Machine Execution Loop (vm.py).
#
# A register virtual machine holds a small fixed bank of general-purpose slots
# (16 integers in regs), an instruction pointer (ip) indexing into the bytecode
# program, an output buffer for PRINT, and a halted flag.
#
# Two Python 3.12+ practices make the fetch-decode-execute loop much safer:
# - Structural match inst.op: paired with typing.assert_never. Calling
#   assert_never(unreachable) in a final case _ as unreachable: branch tells
#   static type checkers that every member of the closed Opcode IntEnum must be
#   handled; if a future Opcode is added and forgotten here, type checking fails
#   immediately instead of silently ignoring the instruction.
# - Explicit watchdog bounds (max_steps) and VMError. Without a step budget, a
#   buggy backward jump that forgets to increment its loop counter hangs forever:
#
#       Suppose a program has 2 words: [LOAD_IMM r0, 1, JMP -1].
#       At ip = 1, the VM fetches JMP -1, advances ip to 2, and adds -1 back to
#       ip = 1 forever. Checking if steps >= max_steps: raise VMError(...)
#       converts an infinite loop into a clean, inspectable exception.
#
# Notice the fetch order inside run(): increment self.ip += 1 immediately after
# fetching word = code[self.ip] and BEFORE calling self.step(word). That keeps
# relative branch offsets anchored to the next instruction, matching the
# labels[target] - (pc + 1) math in assembler.py.

from dataclasses import dataclass, field


class VMError(Exception):
    # Raised on illegal opcodes, out-of-bounds jumps, or step-budget exhaustion.
    stage: str = "execute"


@dataclass(slots=True)
class VirtualMachine:
    regs: list[int] = field(default_factory=lambda: [0] * 16)
    ip: int = 0
    output: list[int] = field(default_factory=list)
    halted: bool = False

    # Add these imports at the top of vm.py when implementing the methods below:
    #     from collections.abc import Sequence
    #     from typing import assert_never
    #     from isa import Instruction, Opcode

    # Implement single-instruction decode and dispatch on VirtualMachine:
    # define def step(self, word: int) -> None:
    # Decode with inst = Instruction.decode(word) inside try ... except ValueError as exc:
    # raising VMError(f"Illegal instruction word {word:#010x}: {exc}") from exc.
    # Then dispatch with match inst.op: across every Opcode variant:
    # - case Opcode.LOAD_IMM: self.regs[inst.dst] = inst.imm16
    # - case Opcode.ADD: self.regs[inst.dst] += self.regs[inst.src]
    # - case Opcode.SUB: self.regs[inst.dst] -= self.regs[inst.src]
    # - case Opcode.MUL: self.regs[inst.dst] *= self.regs[inst.src]
    # - case Opcode.CMP_LT: self.regs[inst.dst] = 1 if self.regs[inst.dst] < self.regs[inst.src] else 0
    # - case Opcode.JMP: self.ip += inst.imm16
    # - case Opcode.JMP_IF_ZERO: if self.regs[inst.dst] == 0: self.ip += inst.imm16
    # - case Opcode.PRINT: self.output.append(self.regs[inst.dst])
    # - case Opcode.HALT: self.halted = True
    # - case _ as unreachable: assert_never(unreachable)


    # Implement the bounded fetch-decode-execute loop on VirtualMachine:
    # define def run(self, code: Sequence[int], max_steps: int = 10_000) -> list[int]:
    # Reset self.regs = [0] * 16, self.ip = 0, self.output = [], and self.halted = False.
    # Track steps = 0 and loop with while not self.halted:
    # - If not (0 <= self.ip < len(code)): raise VMError(f"IP out of bounds: {self.ip}")
    # - If steps >= max_steps: raise VMError(f"Step budget exceeded ({max_steps})")
    # - Fetch word = code[self.ip], immediately advance self.ip += 1, call
    #   self.step(word), and increment steps += 1.
    # Return list(self.output).


# Implement the module-level convenience entry point below VirtualMachine:
# define def run_vm(code: Sequence[int], max_steps: int = 10_000) -> list[int]:
# Instantiate vm = VirtualMachine() and return vm.run(code, max_steps=max_steps).
