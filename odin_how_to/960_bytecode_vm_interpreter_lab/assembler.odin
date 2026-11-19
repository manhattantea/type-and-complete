// Zero-allocation text assembly parser for 960_bytecode_vm_interpreter_lab.

package main

/*
An assembler turns human-readable text lines into packed Instruction words.
Instead of calling strings.split (which allocates a heap slice for every line
and token), Odin offers 'strings.split_iterator(&rem, "\n")'. When we call
strings.split_iterator, it slices off the next substring before "\n" and
advances 'rem' in place, returning ok == false once 'rem' is empty, with zero
heap allocations.

Suppose an input line is "CMP_LT r3, r1, 11". Trimming whitespace and walking
tokens with split_iterator yields "CMP_LT", "r3,", "r1,", and "11". Stripping
trailing commas and parsing register indices and integers produces one packed
word: Instruction{op = .Cmp_Lt, dst = 3, src_a = 1, imm16 = 11}.

Using 'or_return' on parse_reg calls keeps error propagation flat: if any
register token fails validation, assemble_program immediately returns
.Unknown_Mnemonic without deeply nested 'if err != .None' pyramids.
*/

// Add 'import "core:strconv"' and 'import "core:strings"' at the top of this
// file when implementing parse_reg and assemble_program below.

// Write parse_reg :: proc(tok: string) -> (reg: u8, err: VM_Error)
// Trim whitespace and any trailing comma using:
// clean := strings.trim_right(strings.trim_space(tok), ",")
// Verify len(clean) >= 2 and that clean[0] == 'r' || clean[0] == 'R'.
// Parse clean[1:] with idx, ok := strconv.parse_int(clean[1:]).
// Check ok && idx >= 0 && idx <= 15; on success return u8(idx), .None, and on
// any failure return 0, .Unknown_Mnemonic.


// Write assemble_program :: proc(source: string, out_code: ^[dynamic]Instruction) -> (err: VM_Error)
// Keep a mutable cursor rem := source and walk lines with:
// for line in strings.split_iterator(&rem, "\n")
// Inside the loop, call trimmed := strings.trim_space(line) and skip empty lines
// or comment lines starting with ';' or '#'.
// Pull the mnemonic token via strings.split_iterator(&trimmed, " ") (skipping
// extra spaces when consecutive spaces appear).
// Switch on the mnemonic string ("LOAD", "ADD", "SUB", "MUL", "CMP_LT", "JMP",
// "JMP_IF_ZERO", "PRINT", "HALT"):
// - "LOAD": parse dst := parse_reg(tok1) or_return and imm := strconv.parse_int(tok2), emit Instruction{op = .Load_Imm, dst = dst, imm16 = i16(imm)}.
// - "ADD", "SUB", "MUL": parse dst and src_a with parse_reg(...) or_return.
// - "CMP_LT": parse dst, src_a with parse_reg(...) or_return and imm16 with strconv.parse_int.
// - "JMP": parse target := strconv.parse_int(...) into imm16.
// - "JMP_IF_ZERO": parse dst with parse_reg(...) or_return and target into imm16.
// - "PRINT": parse dst with parse_reg(...) or_return.
// - "HALT": emit Instruction{op = .Halt}.
// Return .Unknown_Mnemonic if a mnemonic is unrecognized or an operand fails
// to parse, and append each valid Instruction to out_code before returning .None.
