# python 235_comprehensions_and_generator_expressions.py

import sys


def conditional_output_vs_trailing_filter() -> None:

    # Comprehensions express map-and-filter pipelines declaratively without
    # initializing an empty list and calling .append() in a loop. Unlike a
    # regular for loop (whose loop variable leaks into the enclosing function),
    # a Python 3 comprehension isolates its loop variable so it does not
    # overwrite an outer variable of the same name.
    #
    # One syntax difference trips people up constantly: WHERE does "if" go?
    # - Trailing filter (AFTER the for clause): [n for n in nums if n % 2 == 0]
    #   DROPS items that fail the condition, producing a shorter list. Notice
    #   there is NO else here.
    # - Conditional output expression (BEFORE the for clause):
    #   ["even" if n % 2 == 0 else "odd" for n in nums] keeps EVERY item and
    #   chooses which value to emit for each one (else is REQUIRED).
    #
    #     Suppose nums = [1, 2, 3, 4].
    #     [n for n in nums if n % 2 == 0] produces [2, 4] (2 items).
    #     ["even" if n % 2 == 0 else "odd" for n in nums] produces
    #     ["odd", "even", "odd", "even"] (4 items).
    #
    # You can also use the walrus operator (:=) inside a trailing filter to
    # avoid computing a transformation twice:
    # [clean for raw in lines if (clean := raw.strip())] calls .strip() once
    # per element instead of twice. Keep in mind that a walrus target binds in
    # the ENCLOSING function scope (not the isolated comprehension scope).

    nums: list[int] = [1, 2, 3, 4, 5]
    doubled = [n * 2 for n in nums]
    print("Starter doubled list:", doubled)

    # Contrast trailing filter vs. conditional output expression on nums:
    # build evens: list[int] = [n for n in nums if n % 2 == 0] and
    # labels: list[str] = ["even" if n % 2 == 0 else "odd" for n in nums].
    # Print both, and also combine both in one comprehension that labels only
    # numbers > 1 as "big" if n >= 4 else "small".


    # Verify Python 3 comprehension scope isolation:
    # bind x = "outer" BEFORE running squares = [x * x for x in range(4)],
    # then print squares and x to confirm x is still "outer".


    # Use := inside a trailing filter so .strip() runs once per string:
    # given raw_inputs: list[str] = ["  42 ", "", "   ", " 100\n"],
    # build cleaned: list[str] = [clean for raw in raw_inputs if (clean := raw.strip())]
    # and print cleaned (plus note that clean is now bound in this function).


def nested_comprehensions_and_flattening() -> None:

    # When a comprehension contains multiple for clauses, they read strictly
    # LEFT TO RIGHT in the exact same nesting order as regular for loops:
    #
    #     [cell for row in matrix for cell in row]
    #     means:
    #         for row in matrix:       # outer loop first
    #             for cell in row:     # inner loop second
    #                 emit cell
    #
    # Contrast that with a NESTED comprehension (brackets inside brackets),
    # which builds a 2D list of lists instead of flattening into 1D:
    #
    #     Suppose table = [[r * c for c in range(1, 4)] for r in range(1, 4)].
    #     The outer comprehension runs r = 1, 2, 3 and builds one fresh inner
    #     row list per r, yielding [[1, 2, 3], [2, 4, 6], [3, 6, 9]].
    #
    # Readability guardrail: comprehensions shine at 1-2 clauses. The moment a
    # comprehension grows 3 nested loops, complex multi-branch conditions, or
    # side effects (never use [print(x) for x in items] just for side effects!),
    # switch back to a plain for loop or a small named helper function.

    grid: list[list[int]] = [[1, 2], [3, 4]]
    print("Starter flattened grid:", [cell for row in grid for cell in row])

    # Flatten a 2D matrix while filtering in one comprehension:
    # given matrix: list[list[int]] = [[1, 2, 3], [4, 5, 6]], build
    # evens: list[int] = [n for row in matrix for n in row if n % 2 == 0]
    # and print evens (expected: [2, 4, 6]).


    # Build a 2D multiplication table with a nested comprehension:
    # create mul_table: list[list[int]] = [[r * c for c in range(1, 5)] for r in range(1, 4)]
    # and print mul_table.


    # Rewrite a cramped multi-step transform cleanly as a plain for loop:
    # given words = ["  alpha ", "42", "beta ", "  "], collect uppercase
    # alphabetic words longer than 4 chars into result: list[str] = [] using a
    # clear multi-line for loop and print result (observing why a loop reads
    # far better than stuffing strip, isalpha, len, and upper into one line).


def set_and_dict_comprehensions_and_collisions() -> None:

    # Replacing [expr for x in it] with {expr for x in it} creates a set
    # comprehension (automatically deduplicating results), and writing
    # {k_expr: v_expr for x in it} creates a dict comprehension.
    #
    # Watch out for silent key collisions in dict comprehensions: if two items
    # produce the same key, Python does NOT raise an error—the LATER entry
    # quietly overwrites the earlier value!
    #
    #     Suppose pairs = [("a", 1), ("b", 2), ("a", 99)].
    #     {k: v for k, v in pairs} evaluates left-to-right and ends up as
    #     {"a": 99, "b": 2}, silently discarding 1!
    #
    # Inverting a dict with {v: k for k, v in d.items()} is therefore safe ONLY
    # when every value in d is unique (and hashable).

    words: list[str] = ["ant", "bear", "ape", "bat"]
    print("Starter unique word lengths:", {len(w) for w in words})

    # Build a set comprehension of remainders from a nested matrix:
    # given matrix: list[list[int]] = [[1, 2, 3], [4, 5, 6]], compute
    # remainders: set[int] = {n % 3 for row in matrix for n in row} and print it.


    # Invert a unique dictionary cleanly:
    # given role_ids: dict[str, int] = {"admin": 1, "editor": 2, "viewer": 3},
    # build id_to_role: dict[int, str] = {uid: role for role, uid in role_ids.items()}
    # and print id_to_role.


    # Observe silent dict-comprehension key-collision overwrites:
    # given animals = ["ant", "ape", "bear", "bat"], build
    # by_first_letter: dict[str, str] = {w[0]: w for w in animals} and print it
    # to verify "ape" overwrote "ant" and "bat" overwrote "bear" (last wins).


def generator_expressions_and_exhaustion() -> None:

    # Replacing [x * 2 for x in nums] with (x * 2 for x in nums) turns a list
    # comprehension into a GENERATOR EXPRESSION: instead of allocating a whole
    # list in RAM up front, Python builds a tiny lazy iterator object (~200
    # bytes regardless of length) that computes each item on demand as you pull
    # from it.
    #
    # Two essential generator rules:
    # - Sole-argument shortcut: when a generator expression is the only argument
    #   to a function like sum(), any(), all(), min(), or max(), you can drop
    #   the extra parentheses: sum(x * x for x in range(100)).
    # - Single-pass exhaustion trap: a generator computes values once and throws
    #   them away. Iterating it a second time yields ZERO items!
    #
    #     Suppose g = (x * x for x in range(1, 5)).
    #     First pass: sum(g) consumes 1, 4, 9, 16 and returns 30.
    #     Second pass: max(g) sees an empty iterator and crashes with
    #     ValueError: max() iterable argument is empty!

    list_mem = sys.getsizeof([x for x in range(10_000)])
    gen_mem = sys.getsizeof(x for x in range(10_000))
    print("Starter memory contrast (bytes) list vs. gen:", list_mem, gen_mem)

    # Compute a lazy sum without building an intermediate list:
    # compute total_squares = sum(x * x for x in range(1, 101)) and print it.


    # Observe single-pass exhaustion directly with list():
    # create lazy_gen = (x * 10 for x in range(3)).
    # Print list(lazy_gen) twice in a row so you see [0, 10, 20] followed by [].


    # Trigger and handle the two-pass generator exhaustion trap:
    # create stream = (x * 2 for x in range(1, 5)).
    # Compute first_sum = sum(stream) and print first_sum.
    # Next, wrap max(stream) inside try: / except ValueError as exc: and print
    # exc to see why two-pass reductions require materializing a tuple/list
    # first (or computing both in a single loop).


def main() -> None:

    print("=== 1. Conditional output vs. trailing filter ===")
    conditional_output_vs_trailing_filter()

    print("\n=== 2. Nested comprehensions and flattening ===")
    nested_comprehensions_and_flattening()

    print("\n=== 3. Set and dict comprehensions and collisions ===")
    set_and_dict_comprehensions_and_collisions()

    print("\n=== 4. Generator expressions and exhaustion ===")
    generator_expressions_and_exhaustion()


if __name__ == "__main__":
    main()
