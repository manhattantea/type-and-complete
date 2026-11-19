# python 575_interpreter_waste_and_bytecode_cost.py

import dis
import sys
import time


def add_loop_python(values: list[int]) -> int:

    total = 0
    for b in values:
        total += b
    return total


def boxed_objects_and_heap_footprint() -> None:

    # In a compiled language like C or Odin, adding two 64-bit integers held in
    # CPU registers compiles to a single machine instruction (add rax, rbx) that
    # retires in about 1 clock cycle and touches zero heap memory.
    #
    # In CPython, every number is a heap-allocated PyObject struct carrying an
    # object header (reference count ob_refcnt and type pointer ob_type) plus its
    # payload. A Python int is an immutable, arbitrary-precision PyLongObject
    # (typically 28 bytes for small nonzero values on 64-bit CPython), and a
    # Python float is a 24-byte PyFloatObject.
    #
    # Because PyLongObject is immutable, executing total += b cannot overwrite
    # total's digits in place. Whenever the result falls outside CPython's tiny
    # [-5, 256] small-integer cache, every single addition must:
    # - allocate a fresh 28-byte PyLongObject (or pull from a small-object pool),
    # - write the new digit value,
    # - increment the new reference count (Py_INCREF), and
    # - decrement and free the previous total object (Py_DECREF).
    #
    #     Suppose total = 1_000 and b = 7.
    #     id(total) before total += b points to one 28-byte PyLongObject holding 1000.
    #     After total += b, total is rebound to a DIFFERENT 28-byte PyLongObject
    #     holding 1007 while the old 1000 object's refcount drops to 0 and frees!

    print(
        "Boxed sizes -> int(0):",
        sys.getsizeof(0),
        "B | int(10_000):",
        sys.getsizeof(10_000),
        "B | float(1.0):",
        sys.getsizeof(1.0),
        "B",
    )

    # Prove that integer addition allocates new objects outside [-5, 256]:
    # bind total = 1_000, capture before_id = id(total), execute total += 1,
    # and print before_id == id(total) (expected: False).
    # Also check sys.getsizeof(1 << 100) and sys.getsizeof(1 << 1000) to see how
    # PyLongObject grows in 30-bit digit limbs as integers get huge.


    # Measure the hidden allocation cost of boxing a list of integers:
    # build nums = list(range(1_000)), compute pointer_table = sys.getsizeof(nums),
    # and compute boxed_ints = sum(sys.getsizeof(x) for x in nums).
    # Print pointer_table, boxed_ints, and total bytes versus the 8_000 raw bytes
    # that 1,000 unboxed 64-bit C integers would occupy.


def eval_loop_dispatch_and_adaptive_guards() -> None:

    # Beyond object boxing, a pure-Python 'for b in values: total += b' loop pays
    # interpreter dispatch overhead on every single iteration inside CPython's
    # _PyEval_EvalFrameDefault loop:
    # - FOR_ITER advances the list iterator and checks for exhaustion,
    # - STORE_FAST binds b,
    # - LOAD_FAST pushes total and b onto the evaluation stack,
    # - BINARY_OP (or specialized BINARY_OP_ADD_INT) runs type guards verifying
    #   both operands are compact PyLongObjects before performing the C addition,
    # - STORE_FAST rebinds total, and
    # - JUMP_BACKWARD loops back and checks eval-breaker flags (signals, GIL
    #   switch interval, pending callbacks).
    #
    # That turns 1 hardware integer addition into roughly 50 to 150+ CPU
    # instructions of interpreter dispatch, guard checks, and refcount traffic!

    cold_count = len(list(dis.Bytecode(add_loop_python)))
    print(f"add_loop_python static bytecode instruction count: {cold_count}")

    # Warm up add_loop_python by calling add_loop_python([10, 20, 30]) 25 times
    # so CPython's Python 3.11+ adaptive interpreter quickens the loop instructions.
    # Collect instructions = list(dis.Bytecode(add_loop_python, adaptive=True))
    # and print each instruction's offset and opname (or call
    # dis.dis(add_loop_python, adaptive=True)).


    # Count the exact number of VM opcodes executed inside the hot loop body:
    # slice instructions from the index of FOR_ITER through JUMP_BACKWARD
    # inclusive (or JUMP_BACKWARD_NO_INTERRUPT), print loop_ops_per_iter, and
    # multiply by N = 10_000 to report total VM bytecode dispatches for one call
    # to add_loop_python(list(range(10_000))).


    # Compare what happens when operand types change mid-flight:
    # call add_loop_python([1.5, 2.5, 3.5]) once and inspect
    # [instr.opname for instr in dis.Bytecode(add_loop_python, adaptive=True)].
    # Notice that adaptive specialization must guard types on every pass because
    # Python functions remain dynamically typed even after quickening.


def pushing_hot_loops_into_c_builtins() -> None:

    # How do you eliminate interpreter waste on a hot loop without leaving Python?
    # Push the loop itself out of Python's bytecode interpreter into a C-level
    # loop inside CPython's standard library:
    # - Built-in bulk reductions: sum(), min(), max(), any(), all().
    # - Standard-library C engines: itertools, operator, math.sumprod, bytes.translate,
    #   and array.array.
    #
    # Inside CPython's C implementation of sum(values), the loop increments a C
    # pointer across the list array and accumulates into a C int64 / long fast
    # path without dispatching a single Python bytecode instruction per element!
    # Keep normal cold code clean and idiomatic; apply this push-to-C discipline
    # only on hot loops proven by profiling (Primers 560, 565, and 592).

    t0 = time.perf_counter_ns()
    sample_sum = sum(range(100))
    t1 = time.perf_counter_ns()
    print(f"Starter C-loop sum(range(100)) = {sample_sum} in {t1 - t0} ns")

    # Build values = list(range(10_000)) and write a small timing helper
    # def best_ns(fn: Callable[[], int], trials: int = 5) -> int:
    # (import Callable from collections.abc) that returns min elapsed
    # time.perf_counter_ns() across trials to filter OS scheduling jitter.
    # Benchmark add_loop_python(values) versus sum(values), assert both return
    # 49_995_000, and print both timings in microseconds, nanoseconds per element
    # (elapsed_ns / len(values)), and the speedup factor (py_ns / c_ns).


    # Test a second C-level engine comparison using string/bytes transformation or
    # dot products:
    # build xs = [float(i) for i in range(10_000)] and ys = [0.5] * 10_000.
    # Compare a pure-Python zip loop accumulating total += x * y against
    # math.sumprod(xs, ys) (import math; Python 3.12+ C-level sum of products).
    # Assert both match within 1e-6 and print the speedup factor.


    # Test bytes.translate as a C-level bulk byte transform:
    # build raw = b"aBcDeFgH" * 2_000 and table = bytes.maketrans(b"abcdefgh", b"ABCDEFGH").
    # Compare bytes(b - 32 if 97 <= b <= 104 else b for b in raw) against
    # raw.translate(table), verify exact equality, and print the speedup ratio.


def main() -> None:

    print("=== 1. Boxed objects and heap footprint ===")
    boxed_objects_and_heap_footprint()

    print("\n=== 2. Eval loop dispatch and adaptive guards ===")
    eval_loop_dispatch_and_adaptive_guards()

    print("\n=== 3. Pushing hot loops into C builtins ===")
    pushing_hot_loops_into_c_builtins()


if __name__ == "__main__":
    main()
