# python 035_scopes_legb_and_closures_preview.py

GLOBAL_LIMIT = 500
GLOBAL_COUNTER = 0


def read_global_limit() -> int:

    limit = GLOBAL_LIMIT
    # Try uncommenting the assignment below to trigger UnboundLocalError --
    # even though the assignment appears AFTER the read on the line above!
    # GLOBAL_LIMIT = 100
    return limit


def legb_lookup_and_builtin_shadowing() -> None:

    # Whenever Python reads a bare name, it searches scopes in strict LEGB order:
    # Local (current def or lambda) -> Enclosing (any outer defs) -> Global
    # (current module) -> Built-in (the builtins module: len, sum, max, list).
    #
    # The first scope containing that name wins. That creates a classic beginner
    # trap called built-in shadowing:
    #
    #     Suppose inside a function you write:
    #         sum = 0
    #         total = sum([1, 2, 3])   # TypeError: 'int' object is not callable!
    #
    # Because Local beats Built-in, binding a variable named sum, list, dict,
    # str, or id hides the built-in function of the same name for the rest of
    # that scope. Pick descriptive names like total, items, or user_id instead.

    local_label = "local"
    print("L:", local_label, "| G:", GLOBAL_LIMIT, "| B:", len([1, 2, 3]))

    # Build a full 4-tier LEGB lookup check:
    # bind enclosing_tag = "enclosing" right here, define an inner helper
    # def show_legb() -> None: with local_tag = "local" that prints local_tag
    # (Local), enclosing_tag (Enclosing), GLOBAL_LIMIT (Global), and max(3, 9)
    # (Built-in), then call show_legb().


    # Demonstrate the built-in shadowing trap safely inside a nested helper
    # def shadow_demo() -> None: so the outer scope stays clean:
    # bind sum = 0, print sum, import builtins and call builtins.sum([1, 2, 3])
    # to reach the shadowed built-in, then run del sum and call sum([1, 2, 3])
    # to confirm built-in lookup resumes.
    #
    # Try uncommenting before del sum inside shadow_demo() to hit TypeError:
    # print(sum([1, 2, 3]))


def why_blocks_do_not_scope() -> None:

    # A major surprise for anyone coming from C, Go, Rust, or Odin: compound
    # blocks (if, for, while, with, try) do NOT create their own scope! Every
    # variable assigned inside those blocks lives in the enclosing function's
    # scope and stays alive after the block exits:
    #
    #     Suppose you write:
    #         if True:
    #             chosen = "fast"
    #         print(chosen)   # prints "fast" -- chosen escaped the if block!
    #
    # (Watch out: if the condition were False with no else branch, reading
    # chosen afterward would raise UnboundLocalError.)
    #
    # The deliberate exception is comprehensions and generator expressions:
    # [x * x for x in items] runs in its own isolated scope so loop variable x
    # never leaks into or overwrites variables in the enclosing function.

    if True:
        from_if = "escaped if block"
    print("After if block:", from_if)

    # Confirm for-loop leaking:
    # run a loop for last_seen in [10, 20, 30]: tracking total = last_seen,
    # then print last_seen AFTER the loop ends (expected: 30).


    # Confirm with-block and try-block non-scoping:
    # import contextlib inside this function (import contextlib), enter
    # with contextlib.nullcontext("session-ok") as ctx_val: printing ctx_val
    # inside, then print ctx_val again AFTER the with block exits.
    # Next run try: parsed = int("42") with except ValueError: parsed = 0, and
    # print parsed AFTER the try/except block.


    # Contrast with comprehension isolation:
    # build squares = [comp_var * comp_var for comp_var in [1, 2, 3]] and print
    # squares alongside "comp_var" in locals() (False).


def compile_time_locals_and_unbound_local() -> None:

    # CPython decides which names are local at COMPILE time, not line-by-line
    # at runtime! If an assignment (name = ..., name += ..., for name in ...,
    # or name := ...) appears ANYWHERE inside a def body, CPython compiles name
    # into a fast local slot (LOAD_FAST) for the ENTIRE function.
    #
    # Reading that name before the assignment executes raises UnboundLocalError
    # -- even when a module global with the exact same name exists!
    #
    #     Suppose module global GLOBAL_LIMIT = 500 and a function contains:
    #         limit = GLOBAL_LIMIT   # crashes here with UnboundLocalError!
    #         GLOBAL_LIMIT = 100     # forces GLOBAL_LIMIT to be local everywhere
    #
    # If a function truly needs to rebind a module-level global variable, you
    # must declare global NAME inside that function (though passing parameters
    # and returning new values is almost always cleaner than mutating globals).

    print("read_global_limit():", read_global_limit())

    # Uncomment # GLOBAL_LIMIT = 100 inside read_global_limit() at the top of
    # this file, run this script to observe UnboundLocalError, then comment it
    # back out so the script runs cleanly again.


    # Practice explicit global rebinding:
    # define def bump_global_counter(delta: int) -> int: inside this function
    # that declares global GLOBAL_COUNTER, runs GLOBAL_COUNTER += delta, and
    # returns GLOBAL_COUNTER. Call it with 5 and then 10, printing both results
    # and GLOBAL_COUNTER.


def closures_and_nonlocal_preview() -> None:

    # An inner function can always READ variables from an enclosing function
    # without any extra keyword (that is the E in LEGB). Even after the outer
    # function returns, Python keeps those captured variables alive inside cell
    # objects attached to the inner function -- this pair of function + captured
    # state is called a closure.
    #
    # However, if the inner function wants to REBIND an enclosing variable
    # (like count += 1), the compile-time local rule would make count a fresh
    # local and trigger UnboundLocalError unless you declare nonlocal count:
    #
    #     Suppose make_counter(10) sets count = 10 and returns inner step()
    #     which declares nonlocal count, runs count += 1, and returns count.
    #     Three calls to counter() return 11, 12, and 13 because step() updates
    #     the enclosed cell on every call.

    def make_adder(offset: int):

        def add(x: int) -> int:

            return x + offset

        return add

    add_five = make_adder(5)
    print("Read-only closure add_five(10):", add_five(10))

    # Define def make_counter(start: int): containing count = start and an inner
    # def step() -> int: that declares nonlocal count, increments count += 1,
    # and returns count. Return step from make_counter.
    # Create counter = make_counter(10), call counter() three times, and print
    # each returned value (11, 12, 13).


    # Prove every closure gets its own independent cell:
    # create other = make_counter(100), call counter() (14) and other() (101),
    # and print counter.__closure__[0].cell_contents next to
    # other.__closure__[0].cell_contents.


def main() -> None:

    print("=== 1. LEGB lookup and built-in shadowing ===")
    legb_lookup_and_builtin_shadowing()

    print("\n=== 2. Why blocks do not create scope ===")
    why_blocks_do_not_scope()

    print("\n=== 3. Compile-time locals, UnboundLocalError, and global ===")
    compile_time_locals_and_unbound_local()

    print("\n=== 4. Closures and nonlocal preview ===")
    closures_and_nonlocal_preview()


if __name__ == "__main__":
    main()
