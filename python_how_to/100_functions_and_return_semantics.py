# python 100_functions_and_return_semantics.py

from collections.abc import Callable


def square(x: int) -> int:
    """Return the square of an integer."""

    return x * x


def call_by_sharing_and_nested_mutation() -> None:

    # Unlike C++ reference parameters (&) or Odin pointers (^T), Python has no
    # syntax to pass a variable slot by reference, nor does it copy whole
    # containers onto the stack when calling a function. Every argument uses
    # pass-by-object-reference (also called call-by-sharing):
    #
    # - Every value in Python is a heap-allocated PyObject. Variable names are
    #   labels pointing to those heap objects.
    # - Calling fn(x) creates a brand-new local parameter label inside the
    #   function's stack frame and binds it to the exact same PyObject as x.
    # - Mutating that shared object in place (data.append(99), data[0] = 0)
    #   changes the heap object itself, so the caller sees the change.
    # - Rebinding the local parameter name (data = data + [99] or data = [])
    #   only moves the local label to a new object; the caller's label still
    #   points to the original list untouched.
    #
    # Watch out for nested mutable containers as well! Even if you make a
    # shallow copy of the outer list (outer_copy = matrix[:]), the outer list
    # still holds pointers to the exact same inner list objects:
    #
    #     Suppose nested = [[1], [2]].
    #     If a helper runs nested[0].append(9), the caller's nested becomes
    #     [[1, 9], [2]].
    #     If a helper instead runs nested = nested + [[99]], only the local
    #     parameter label moves; the caller's nested stays [[1, 9], [2]].

    starter = [10, 20]
    before_id = id(starter)
    starter.append(30)
    print(f"After in-place append: {starter} (same object={id(starter) == before_id})")

    # Define two local helpers to contrast in-place mutation against rebinding:
    # - mutate_in_place(data: list[int]) -> None calling data.append(99) and
    #   falling off the end (implicitly returning None).
    # - rebind_local(data: list[int]) -> list[int] assigning data = data + [99]
    #   and returning data.
    # Test both on original: list[int] = [1, 2, 3]. Print original and
    # res is None after mutate_in_place(original), then print original,
    # updated, and original is updated after rebind_local(original).


    # Test nested mutable arguments vs shallow rebinding:
    # - Define append_inner(matrix: list[list[int]]) -> None that appends 9 to
    #   matrix[0] (mutating the shared inner list).
    # - Define rebind_outer(matrix: list[list[int]]) -> list[list[int]] that
    #   rebinds matrix = matrix + [[99]] and returns matrix.
    # Start with nested: list[list[int]] = [[1], [2]]. Call append_inner(nested)
    # and verify nested became [[1, 9], [2]]. Then call extended = rebind_outer(nested)
    # and confirm nested stayed [[1, 9], [2]] while extended has 3 rows.
    # Finally, make a shallow slice copy shallow = nested[:], run
    # shallow[1].append(7), and print nested to prove inner lists are still shared!


    # Contrast with an immutable int argument:
    # Define bump(n: int) -> int that executes n += 1 and returns n.
    # Bind count = 10, call bumped = bump(count), and print count, bumped, and
    # id(count) == id(bumped) to confirm count stays 10 because int cannot be
    # mutated in place.


def return_values_none_and_tuple_unpacking() -> None:

    # Every Python function returns an object. If execution reaches the end of
    # the body without hitting return, or hits a bare return statement, Python
    # implicitly returns the singleton None.
    #
    # Returning multiple comma-separated values (return lo, hi, total) does NOT
    # return three separate stack slots—Python packs them into a single tuple
    # object, which the caller can unpack in one statement:
    #
    #     Suppose calc() returns (1, 16, 44).
    #     Writing lo, hi, total = calc() binds lo=1, hi=16, total=44.
    #     Writing packed = calc() binds packed to the tuple (1, 16, 44).
    #
    # At call sites, Python lets you pass arguments positionally (by slot order)
    # or by keyword (by parameter name). Mixing both improves readability for
    # boolean flags and numbers—for instance format_endpoint("api.local", 443, use_tls=True)
    # makes the third argument self-explanatory—as long as all positional
    # arguments appear before any keyword arguments.

    print(f"square(5) positional = {square(5)}, keyword = {square(x=5)}")

    # Define min_max_sum(nums: list[int]) -> tuple[int, int, int] that raises
    # ValueError("nums must not be empty") when not nums, and otherwise returns
    # min(nums), max(nums), sum(nums).
    # Call it on [4, 8, 1, 15, 16] and unpack directly into lo, hi, total
    # (expected: 1, 16, 44). Also capture packed = min_max_sum([4, 8, 1, 15, 16])
    # and print type(packed) to confirm multiple returns are a real tuple.


    # Practice early return combined with implicit None fallback:
    # Define find_first_even(nums: list[int]) -> int | None that loops over nums,
    # immediately returns n when n % 2 == 0, and falls off the end when no even
    # number exists. Call it on [1, 3, 4, 6] (expected: 4) and [1, 3, 5]
    # (verify result is None).


    # Practice positional vs keyword call ergonomics:
    # Define format_endpoint(host: str, port: int, use_tls: bool) -> str
    # returning f"{'https' if use_tls else 'http'}://{host}:{port}".
    # Call and print it three ways:
    # - All positional: format_endpoint("localhost", 8080, False)
    # - Mixed positional and keyword: format_endpoint("api.local", 443, use_tls=True)
    # - All keyword in a different order: format_endpoint(use_tls=True, port=8443, host="edge.local")
    #
    # Try uncommenting below to observe Python's SyntaxError when a positional
    # argument follows a keyword argument:
    # print(format_endpoint(host="localhost", 8080, False))


def first_class_functions_and_dispatch() -> None:

    # In Python, def is an executable statement, not a compile-time-only
    # declaration. When execution reaches def, Python wraps the compiled code
    # object (__code__), annotations (__annotations__), and docstring (__doc__)
    # into a heap function object and binds it to the function's name.
    #
    # Because functions are ordinary first-class objects, you can store them in
    # dictionaries, pass them into other functions, return them from functions,
    # and inspect their live metadata attributes at runtime:
    #
    #     Suppose ops = {"sq": square}.
    #     Calling ops["sq"](6) looks up the function object and invokes it,
    #     returning 36 while preserving ops["sq"].__name__ == "square".

    print(
        f"square metadata: name={square.__name__!r}, "
        f"doc={square.__doc__!r}, vars={square.__code__.co_varnames}"
    )

    # Define two integer math functions add(a: int, b: int) -> int and
    # mul(a: int, b: int) -> int (give add a short 1-line docstring so you can
    # inspect its __doc__ attribute at runtime).
    # Build a dispatch table:
    # ops: dict[str, Callable[[int, int], int]] = {"add": add, "mul": mul}
    # Invoke ops["add"](6, 7) (13) and ops["mul"](6, 7) (42), then print
    # ops["add"].__qualname__, ops["add"].__doc__, and ops["add"].__annotations__.


    # Pass a function object as an argument to another function:
    # Define apply_twice(fn: Callable[[int], int], value: int) -> int returning
    # fn(fn(value)). Call apply_twice(square, 3) and print the result (81).


    # Prove that def executes at runtime like any other statement:
    # Set use_double = True and write an if/else block that defines
    # def transform(n: int) -> int: returning n * 2 in the if branch and
    # def transform(n: int) -> int: returning n + 10 in the else branch.
    # Call transform(5) and inspect transform.__name__ and transform.__code__.co_firstlineno.


def main() -> None:

    print("=== 1. Call-by-sharing and nested mutable arguments ===")
    call_by_sharing_and_nested_mutation()

    print("\n=== 2. Return values, implicit None, and tuple unpacking ===")
    return_values_none_and_tuple_unpacking()

    print("\n=== 3. First-class functions and dispatch tables ===")
    first_class_functions_and_dispatch()


if __name__ == "__main__":
    main()
