# python 570_bytecode_disassembly_with_dis.py

import dis
import math


GLOBAL_SCALE = 3


def compute_poly(x: int) -> int:

    return x * x + 2 * x + 1


def code_object_and_stack_machine() -> None:

    # When CPython loads a .py file, it compiles every function once into an
    # immutable code object attached at fn.__code__. That code object holds the
    # compact bytecode stream executed by CPython's stack-based virtual machine.
    #
    # Unlike a register CPU, a stack VM pushes operands onto an evaluation stack
    # and pops them when running an operation:
    # - LOAD_FAST pushes a local variable or parameter onto the stack by direct
    #   integer index into the frame's C pointer array (O(1) array indexing).
    # - LOAD_CONST pushes a pre-compiled literal constant from co_consts.
    # - BINARY_OP pops two operands, computes the result, and pushes it back.
    # - RETURN_VALUE pops the top of the stack and returns it to the caller.
    #
    # Every code object exposes the tables those opcodes index into:
    # - co_varnames: tuple of parameter and local variable names
    # - co_consts: tuple of literal constants embedded at compile time
    # - co_names: tuple of global, built-in, and attribute names
    # - co_stacksize: maximum evaluation stack depth computed by the compiler
    #
    #     Suppose fn is def add_one(n: int) -> int: return n + 1.
    #     co_varnames is ("n",), co_consts contains 1, co_names is (), and the
    #     VM pushes n (LOAD_FAST), pushes 1 (LOAD_CONST), adds them (BINARY_OP),
    #     and returns the sum (RETURN_VALUE).

    code = compute_poly.__code__
    print("compute_poly co_varnames:", code.co_varnames)

    # Inspect the rest of compute_poly.__code__: print code.co_consts,
    # code.co_names, code.co_stacksize, and len(code.co_code) (the raw byte
    # length of the compiled bytecode instructions).


    # Disassemble compute_poly in two ways:
    # First build ops = [instr.opname for instr in dis.Bytecode(compute_poly)]
    # and print ops so you can see the flat list of instruction names.
    # Then call dis.dis(compute_poly) to view the full formatted bytecode listing
    # with line numbers, byte offsets, opnames, and operand annotations (argrepr).


    # Observe constant folding by the CPython bytecode compiler:
    # define a tiny helper def folded_seconds() -> int: return 60 * 60 * 24
    # and print folded_seconds.__code__.co_consts alongside
    # [instr.opname for instr in dis.Bytecode(folded_seconds)].
    # Notice 86400 appears directly in co_consts with zero BINARY_OP multiply!


def load_fast_vs_load_global_and_hoisting() -> None:

    # Why does moving a global or attribute lookup out of a tight pure-Python loop
    # make bytecode shorter and faster? Because local names live in co_varnames
    # (accessed by direct slot index via LOAD_FAST), while module globals,
    # built-ins, and dotted attributes like math.sin live in co_names and emit
    # LOAD_GLOBAL / LOAD_ATTR instructions that must look up dictionaries or
    # inline caches.
    #
    #     Suppose a loop runs 10_000 times:
    #         for x in xs: total += math.sin(x)
    #     Each iteration executes LOAD_GLOBAL (math) and LOAD_ATTR (sin).
    #     Binding sin = math.sin once BEFORE the loop turns both lookups inside
    #     the loop body into a single LOAD_FAST (sin) slot read!

    print("Module constant GLOBAL_SCALE:", GLOBAL_SCALE, "| math.sin(0.0):", math.sin(0.0))

    # Define def uses_global(x: int) -> int: return x * GLOBAL_SCALE
    # and def uses_local(x: int, scale: int = 3) -> int: return x * scale.
    # Print uses_global.__code__.co_names and
    # [instr.opname for instr in dis.Bytecode(uses_global)], then compare with
    # uses_local.__code__.co_names and its opnames to verify LOAD_GLOBAL vs LOAD_FAST.


    # Compare dotted attribute lookup inside a loop against a hoisted local:
    # define def sum_sin_global(xs: list[float]) -> float: calling math.sin(x)
    # inside a for loop, and def sum_sin_hoisted(xs: list[float]) -> float:
    # binding local_sin = math.sin before the loop.
    # Count how many LOAD_GLOBAL and LOAD_ATTR opcodes appear inside each
    # function's dis.Bytecode(...) stream and print both counts side by side.


    # Also check how built-ins like len() are fetched:
    # inspect [instr.opname for instr in dis.Bytecode(lambda s: len(s))] and
    # observe that Python built-ins are NOT keywords—they load via LOAD_GLOBAL!


def adaptive_specialization_and_construct_costs() -> None:

    # Starting in Python 3.11 (PEP 659), CPython includes an Adaptive Specializing
    # Interpreter. A freshly compiled function starts with generic instructions
    # such as BINARY_OP, LOAD_GLOBAL, or LOAD_ATTR because Python cannot know
    # argument types ahead of time.
    #
    # Once a function executes repeatedly (typically after roughly 8 to 16 calls),
    # CPython quickens hot opcodes in place into type-specialized instructions
    # such as BINARY_OP_MULTIPLY_INT or BINARY_OP_ADD_INT, guarded by fast type
    # checks. Passing adaptive=True to dis.Bytecode(fn, adaptive=True) or
    # dis.dis(fn, adaptive=True) reveals those live specialized opcodes; passing
    # show_caches=True even reveals the hidden inline CACHE entries reserved after
    # specializable instructions!
    #
    #     Suppose compute_poly(i) runs 20 times with ints.
    #     Before warmup: dis.Bytecode(compute_poly, adaptive=True) shows generic
    #     BINARY_OP instructions.
    #     After warmup: the same call shows specialized *_INT opcodes in place!

    cold_ops = [instr.opname for instr in dis.Bytecode(compute_poly, adaptive=True)]
    print("Cold compute_poly opnames:", cold_ops)

    # Warm up compute_poly by calling compute_poly(i) 25 times in a loop, then
    # capture warm_ops = [instr.opname for instr in dis.Bytecode(compute_poly, adaptive=True)].
    # Print warm_ops and print every (cold, warm) pair where the opname changed
    # so you can see exactly which opcodes CPython specialized in place!


    # Call dis.dis(compute_poly, adaptive=True, show_caches=True) and observe the
    # CACHE entries interleaved right after specializable instructions.
    # Then call compute_poly with floats (for i in range(25): compute_poly(float(i)))
    # and re-inspect [instr.opname for instr in dis.Bytecode(compute_poly, adaptive=True)]
    # to observe CPython de-specializing or re-specializing for float operands!


    # Compare bytecode structure between a manual list-append loop and a list
    # comprehension:
    # define def squares_loop(n: int) -> list[int]: using out = [] and out.append(i * i)
    # and def squares_comp(n: int) -> list[int]: returning [i * i for i in range(n)].
    # Print both opname lists and spot the dedicated LIST_APPEND opcode emitted
    # for the comprehension (avoiding repeated LOAD_ATTR append calls on every pass).


def main() -> None:

    print("=== 1. Code objects and the CPython stack machine ===")
    code_object_and_stack_machine()

    print("\n=== 2. LOAD_FAST vs LOAD_GLOBAL and loop hoisting ===")
    load_fast_vs_load_global_and_hoisting()

    print("\n=== 3. Adaptive specialization (PEP 659) and construct costs ===")
    adaptive_specialization_and_construct_costs()


if __name__ == "__main__":
    main()
