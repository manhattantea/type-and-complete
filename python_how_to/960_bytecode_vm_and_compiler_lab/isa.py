# Module for 960_bytecode_vm_and_compiler_lab (run via: python 960_bytecode_vm_and_compiler_lab/main.py)

# 32-Bit Fixed-Width Bytecode ISA and Bit-Packing (isa.py).
#
# Our virtual machine executes fixed-width 32-bit instruction words packed into
# a single integer with four bit fields:
#     bits 31..24 -> op    (8 bits, Opcode value)
#     bits 23..20 -> dst   (4 bits, destination register 0..15)
#     bits 19..16 -> src   (4 bits, source register 0..15)
#     bits 15..0  -> imm16 (signed 16-bit two's-complement immediate -32768..32767)
#
# Opcode inherits from enum.IntEnum, which means each member behaves as both a
# readable enum constant (Opcode.JMP) and a real integer so bit shifts like
# int(op) << 24 work cleanly. Starting Opcode values at 1 instead of 0 is a
# deliberate safety choice: an accidental all-zero word (0x00000000) fails fast
# when Opcode(0) raises ValueError instead of silently running a real opcode.
#
# Why bit-packing exposes an important Python integer trap:
# Unlike C or Odin integers, Python int has arbitrary precision with no fixed
# 16-bit or 32-bit wraparound. That matters the moment you encode a negative
# branch offset:
#
#     Suppose we encode a backward jump with imm16 = -7.
#     Masking (-7) & 0xFFFF produces the unsigned 16-bit pattern 0xFFF9 (65529).
#     If decode() only extracts raw_imm = word & 0xFFFF, Python keeps 0xFFF9 as
#     positive +65529 instead of -7, sending the instruction pointer off a cliff!
#
# Branchless two's-complement 16-bit sign extension fixes it in two operations:
#     imm16 = (raw_imm ^ 0x8000) - 0x8000
#
# Flipping bit 15 (^ 0x8000, which is 32768) and subtracting 0x8000 maps both
# positive and negative halves with zero if-branches:
#     Suppose raw_imm = 0x0005 (5):     (5 ^ 32768) - 32768 == 32773 - 32768 == 5
#     Suppose raw_imm = 0xFFF9 (65529): (65529 ^ 32768) - 32768 == 32761 - 32768 == -7

from dataclasses import dataclass
from enum import IntEnum


class Opcode(IntEnum):
    LOAD_IMM = 1     # regs[dst] = imm16
    ADD = 2          # regs[dst] += regs[src]
    SUB = 3          # regs[dst] -= regs[src]
    MUL = 4          # regs[dst] *= regs[src]
    CMP_LT = 5       # regs[dst] = 1 if regs[dst] < regs[src] else 0
    JMP = 6          # ip += imm16 (relative to next instruction)
    JMP_IF_ZERO = 7  # if regs[dst] == 0: ip += imm16
    PRINT = 8        # append regs[dst] to VM output buffer
    HALT = 9         # stop VM execution cleanly


@dataclass(slots=True, frozen=True)
class Instruction:
    op: Opcode
    dst: int = 0
    src: int = 0
    imm16: int = 0

    # Implement 32-bit instruction packing as a @staticmethod on Instruction:
    # define def encode(op: Opcode, dst: int = 0, src: int = 0, imm16: int = 0) -> int:
    # Validate register bounds (0 <= dst <= 15 and 0 <= src <= 15) and signed
    # 16-bit immediate bounds (-32768 <= imm16 <= 32767), raising ValueError if
    # any operand overflows its bit field.
    # Return (int(op) << 24) | ((dst & 0xF) << 20) | ((src & 0xF) << 16) | (imm16 & 0xFFFF).


    # Implement 32-bit instruction unpacking as a @staticmethod on Instruction:
    # define def decode(word: int) -> "Instruction":
    # Extract op = Opcode((word >> 24) & 0xFF) so unknown opcodes like 0 raise
    # ValueError immediately. Then extract dst = (word >> 20) & 0xF,
    # src = (word >> 16) & 0xF, and raw_imm = word & 0xFFFF.
    # Apply sign extension imm16 = (raw_imm ^ 0x8000) - 0x8000 and return
    # Instruction(op=op, dst=dst, src=src, imm16=imm16).


    # Quick sanity check once both static methods exist:
    # verify Instruction.decode(Instruction.encode(Opcode.JMP, imm16=-7)).imm16 == -7
    # and confirm Instruction.decode(0) raises ValueError.
