# python 130_lambda_and_late_binding_closures.py

from functools import partial


def lambdas_and_closure_cells() -> None:

    # A lambda expression (lambda params: expr) builds an ordinary Python
    # function object—compiling to the exact same bytecode as a one-line def,
    # except its __name__ is "<lambda>". The only limit is syntax: a lambda
    # body must be a single expression (no return, loops, try, or = assignment
    # statements). Use def whenever a function deserves a real name or multiple
    # steps.
    #
    # When an inner function (def or lambda) references a variable from an
    # enclosing function, Python cannot keep that variable solely on the outer
    # stack frame—the outer function may return long before the inner function
    # runs! Instead, Python promotes the variable into a heap-allocated Cell
    # object. Both the outer scope and the inner function's __closure__ tuple
    # hold a pointer to that same Cell, while __code__.co_freevars lists the
    # captured variable names:
    #
    #     Suppose def make_offset(base: int):
    #         def shift(x: int) -> int:
    #             return x + base
    #         return shift
    #     Calling add5 = make_offset(5) creates a Cell holding 5.
    #     add5.__code__.co_freevars is ('base',) and
    #     add5.__closure__[0].cell_contents is 5.

    triple = lambda x: x * 3
    print(f"Starter lambda: triple(4)={triple(4)}, name={triple.__name__!r}")

    # Compare a lambda against an equivalent one-line def:
    # Define def double_fn(x: int) -> int: return x * 2 and
    # double_lam = lambda x: x * 2.
    # Print type(double_fn) is type(double_lam), double_fn.__name__,
    # double_lam.__name__, and both __code__.co_varnames.


    # Build and inspect a heap closure cell:
    # Define make_offset(base: int) containing inner def shift(x: int) -> int:
    # returning x + base, and return shift.
    # Create add10 = make_offset(10), call add10(5) (expected: 15), and print
    # add10.__code__.co_freevars and add10.__closure__[0].cell_contents.


    # Observe a mutable closure cell using nonlocal:
    # Remember nonlocal tells Python to rebind a variable in the enclosing
    # function's Cell rather than creating a brand-new local variable.
    # Define make_counter(start: int = 0) setting count = start and returning
    # inner def tick() -> int: that declares nonlocal count, increments
    # count += 1, and returns count.
    # Create counter = make_counter(10), call counter() three times, and print
    # counter.__closure__[0].cell_contents afterward to watch the Cell update.


def late_binding_loop_trap() -> None:

    # Heap Cell sharing creates one of Python's classic bugs: the Late-Binding
    # Closure Trap. Consider building four multipliers in a comprehension:
    #
    #     buggy = [lambda x: x * i for i in range(4)]
    #
    # The comprehension runs inside ONE enclosing scope with ONE loop variable i,
    # which means ONE shared Cell object on the heap. Each loop iteration
    # overwrites that same Cell (0 -> 1 -> 2 -> 3). Because Python reads
    # cell.cell_contents LATE (when the lambda is called, NOT when it is
    # created), every lambda sees i == 3 after the loop finishes:
    #
    #     [fn(10) for fn in buggy] produces [30, 30, 30, 30] instead of [0, 10, 20, 30]!
    #
    # Notice this trap has nothing to do with lambda syntax—a plain def written
    # inside a for loop captures the exact same shared Cell.

    literal_funcs = [lambda x: x * 0, lambda x: x * 1]
    print(f"Starter literal functions (no loop cell): {[fn(10) for fn in literal_funcs]}")

    # Reproduce the late-binding loop trap:
    # Build buggy_multipliers = [lambda x: x * i for i in range(4)].
    # Evaluate buggy_results = [fn(10) for fn in buggy_multipliers] and print
    # buggy_results to observe [30, 30, 30, 30].


    # Inspect the shared heap Cell directly on buggy_multipliers:
    # - Print buggy_multipliers[0].__code__.co_freevars (expected: ('i',)).
    # - Print buggy_multipliers[0].__closure__[0].cell_contents (expected: 3).
    # - Print buggy_multipliers[0].__closure__[0] is buggy_multipliers[1].__closure__[0]
    #   (expected: True—every lambda points to the exact same Cell object!).


    # Prove plain def inside a for loop hits the exact same late-binding bug:
    # Create def_funcs = [] and loop for i in range(4): defining
    # def scale(x: int) -> int: return x * i and appending scale to def_funcs.
    # Print [fn(10) for fn in def_funcs] and verify it is also [30, 30, 30, 30].


def early_binding_fixes_defaults_factory_partial() -> None:

    # Three clean ways freeze each iteration's value early instead of sharing
    # one mutable loop Cell:
    #
    # - Default-argument capture: [lambda x, i=i: x * i for i in range(4)].
    #   Default values are evaluated ONCE when each function is created (Primer
    #   110), so each lambda freezes that iteration's int into its own
    #   __defaults__ tuple and needs no closure Cell at all (__closure__ is None).
    #   Small caveat: the extra parameter i=i is technically exposed if a caller
    #   accidentally passes two arguments.
    # - Factory function: calling make_multiplier(i) creates a brand-new stack
    #   frame on every iteration, allocating a separate Cell per returned
    #   function while keeping a clean 1-argument signature.
    # - functools.partial: partial(multiply_pair, i) freezes i eagerly inside a
    #   lightweight callable object without writing any nested function.

    def multiply_pair(factor: int, x: int) -> int:

        return x * factor

    times_two = partial(multiply_pair, 2)
    print(f"Starter partial(multiply_pair, 2)(10) = {times_two(10)}")

    # Apply Fix 1 (default-argument early binding):
    # Create fixed_multipliers = [lambda x, i=i: x * i for i in range(4)].
    # Compute fixed_results = [fn(10) for fn in fixed_multipliers], print it,
    # and assert fixed_results == [0, 10, 20, 30].
    # Inspect fixed_multipliers[0].__closure__ (None) alongside
    # fixed_multipliers[0].__defaults__ ((0,)).


    # Apply Fix 2 (factory function with distinct Cells):
    # Define make_multiplier(factor: int) returning nested
    # def multiply(x: int) -> int: return x * factor.
    # Build factory_multipliers = [make_multiplier(i) for i in range(4)],
    # assert [fn(10) for fn in factory_multipliers] == [0, 10, 20, 30], and
    # verify factory_multipliers[0].__closure__[0] is factory_multipliers[1].__closure__[0]
    # is False (distinct Cells!).


    # Apply Fix 3 (functools.partial eager binding):
    # Build partial_multipliers = [partial(multiply_pair, i) for i in range(4)].
    # Assert [fn(10) for fn in partial_multipliers] == [0, 10, 20, 30] and
    # print partial_multipliers[2].func.__name__ and partial_multipliers[2].args.


def main() -> None:

    print("=== 1. Lambdas and heap closure cells ===")
    lambdas_and_closure_cells()

    print("\n=== 2. The late-binding loop closure trap ===")
    late_binding_loop_trap()

    print("\n=== 3. Early-binding fixes: defaults, factories, and partial ===")
    early_binding_fixes_defaults_factory_partial()


if __name__ == "__main__":
    main()
