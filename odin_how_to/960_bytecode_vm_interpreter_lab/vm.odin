// Register-based bytecode VM interpreter for 960_bytecode_vm_interpreter_lab.

package main

/*
A register-based VM keeps a fixed array of virtual registers right on the call
stack ('regs: [16]i64') and steps an instruction pointer 'ip' through the
packed Instruction slice.

Notice also how Odin handles fixed-capacity stacks without heap allocation:
when we declare 'call_stack: [dynamic; 64]u32', it behaves like a normal
dynamic array (supporting append, pop, and len), except its 64-element buffer
lives inline on the stack instead of asking context.allocator for memory.

Dispatching on 'switch inst.op' in Odin is exhaustive by default: if you later
add a Call or Ret variant to Opcode in isa.odin, the compiler flags run_vm
immediately until every new opcode branch is handled.

Suppose code[3] holds Instruction{op = .Add, dst = 0, src_a = 1} while regs[0]
is 3 and regs[1] is 3. Executing that instruction sets regs[0] = 6 and moves
ip from 3 to 4. If code[7] is Instruction{op = .Jmp, imm16 = 3}, next_ip is
overwritten to 3 so execution jumps back to the loop body.
*/

// Add 'import "core:fmt"' at the top of this file when implementing run_vm below.

// Write run_vm :: proc(code: []Instruction) -> (err: VM_Error)
// Declare regs: [16]i64, call_stack: [dynamic; 64]u32, and ip := 0.
// Loop while ip >= 0 && ip < len(code):
// Fetch inst := code[ip] and set next_ip := ip + 1.
// Dispatch with an exhaustive switch inst.op over all Opcode variants:
// - .Load_Imm: assign regs[inst.dst] = i64(inst.imm16).
// - .Add: regs[inst.dst] += regs[inst.src_a].
// - .Sub: regs[inst.dst] -= regs[inst.src_a].
// - .Mul: regs[inst.dst] *= regs[inst.src_a].
// - .Cmp_Lt: assign regs[inst.dst] = 1 if regs[inst.src_a] < i64(inst.imm16) else 0.
// - .Jmp: guard that int(inst.imm16) is within 0..<len(code) (else return .Invalid_Opcode) and set next_ip = int(inst.imm16).
// - .Jmp_If_Zero: when regs[inst.dst] == 0, guard bounds and set next_ip = int(inst.imm16).
// - .Print: print the register value with fmt.printfln("[vm] r%d = %d", inst.dst, regs[inst.dst]).
// - .Halt: return .None immediately.
// Advance ip = next_ip at the end of each cycle. If the loop exits past the end
// of code without hitting .Halt, return .None (or extend with Call/Ret using
// call_stack and return .Stack_Overflow if len(call_stack) == cap(call_stack)).
