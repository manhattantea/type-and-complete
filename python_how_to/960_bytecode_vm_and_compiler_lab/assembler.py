# Module for 960_bytecode_vm_and_compiler_lab (run via: python 960_bytecode_vm_and_compiler_lab/main.py)

# Two-Pass Symbolic Assembler (assembler.py).
#
# Why does an assembler scan the source text twice instead of emitting 32-bit
# machine words in a single pass? Forward jumps!
#
#     Suppose a loop looks like this (with instruction indices on the left):
#         4: loop_start: LOAD_IMM r4, 0
#         7:             JMP_IF_ZERO r4, done
#         10:            JMP loop_start
#         11: done:      PRINT r0
#
# When the assembler reads line 7 (JMP_IF_ZERO r4, done), it has not reached
# the done: label at index 11 yet. A single-pass encoder cannot know the jump
# distance yet without patching emitted words later.
#
# Splitting assembly into two clean passes solves both forward and backward
# jumps with one formula:
# - Pass 1 strips comments (anything after ; or #), records every label: name
#   and its instruction index in labels: dict[str, int], and collects clean
#   (pc, instruction_text) pairs without encoding any bits yet.
# - Pass 2 knows every label address already, so any branch at pc computes its
#   signed relative offset as:
#       offset = labels[target_label] - (pc + 1)
#
# Why pc + 1 instead of pc? When the VM fetches instruction pc, it immediately
# advances ip to pc + 1 before executing the jump.
# - Forward jump at pc = 7 to done (11): 11 - (7 + 1) = +3, so ip moves 8 + 3 = 11.
# - Backward jump at pc = 10 to loop_start (4): 4 - (10 + 1) = -7, so ip moves 11 - 7 = 4.


class AssemblerError(Exception):
    # Raised when assembly source contains invalid syntax, duplicate or missing
    # labels, unknown mnemonics, or out-of-range register and immediate operands.
    stage: str = "assemble"


# Add from isa import Instruction, Opcode near the top of this module before
# implementing the parser and two-pass assembler below.


# Implement register operand parsing:
# define def _parse_register(token: str) -> int:
# Normalize with clean = token.strip().rstrip(",").lower().
# Verify clean.startswith("r") and that clean[1:] parses as an integer in
# 0 <= reg <= 15, raising AssemblerError with the offending token otherwise.


# Implement the two-pass symbolic assembler:
# define def assemble_program(source: str) -> list[int]:
#
# Pass 1 (collect labels and clean instruction lines):
# - Initialize labels: dict[str, int] = {} and instructions: list[tuple[int, str]] = [].
# - Walk source.splitlines() with for line_no, raw_line in enumerate(source.splitlines(), start=1):
#   so error messages can report exact line numbers.
# - Strip comments after ";" or "#":
#   line = raw_line.split(";", 1)[0].split("#", 1)[0].strip()
# - Skip blank lines with if not line: continue.
# - Handle "label:" declarations (either alone on a line or prefixed before an
#   instruction): if ":" in line, split label_part, rest = line.split(":", 1),
#   strip label_name = label_part.strip(), reject empty or duplicate label names
#   with AssemblerError, store labels[label_name] = len(instructions), and set
#   line = rest.strip(). If not line remains, continue.
# - Append (len(instructions), line) to instructions.
#
# Pass 2 (encode 32-bit machine words and resolve relative branch offsets):
# - Initialize program: list[int] = [].
# - For each (pc, line) in instructions:
#   split tokens with parts = line.replace(",", " ").split() and look up
#   op = Opcode[parts[0].upper()] (catching KeyError and raising AssemblerError).
# - Validate operand counts and encode per opcode:
#   - LOAD_IMM: dst = _parse_register(parts[1]) and imm16 = int(parts[2], 0)
#     (passing base 0 to int lets decimal 11 and hex 0x10 both parse cleanly).
#   - ADD, SUB, MUL, CMP_LT: dst = _parse_register(parts[1]) and src = _parse_register(parts[2]).
#   - JMP: look up target = parts[1] in labels (raising AssemblerError if missing)
#     and compute imm16 = labels[target] - (pc + 1).
#   - JMP_IF_ZERO: dst = _parse_register(parts[1]), look up target = parts[2] in
#     labels, and compute imm16 = labels[target] - (pc + 1).
#   - PRINT: dst = _parse_register(parts[1]).
#   - HALT: requires zero operands.
# - Wrap Instruction.encode(...) in try ... except ValueError as exc: raising
#   AssemblerError from exc, append the encoded word to program, and return program.
