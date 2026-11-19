# python 015_booleans_truthiness_and_short_circuit.py


def bool_as_int_subclass() -> None:

    # In Python, bool is a subclass of int: issubclass(bool, int) is True,
    # True == 1, and False == 0. Python originally lacked a separate bool type
    # and used 1 and 0 directly; inheriting from int kept older code working and
    # gives modern Python a clean idiom for counting matches in one pass.
    #
    # Suppose nums = [-2, 5, 9]:
    #     sum(n > 0 for n in nums) evaluates False + True + True and returns 2.
    # Notice that adding two bools produces a regular int, not a bool.

    print("issubclass(bool, int):", issubclass(bool, int), "| True == 1:", True == 1)

    # Print isinstance(True, int), True + True, False * 10, and
    # type(True + True).__name__.


    # Given nums = [-3, 0, 4, 7, -1, 9], compute
    # positive_count = sum(n > 0 for n in nums) and
    # even_count = sum(n % 2 == 0 for n in nums), then print both counts.


def truthiness_and_falsiness() -> None:

    # Every Python object can be tested in a boolean context (if x: or bool(x)).
    # Only a small, consistent set of built-in values are falsy:
    # - None and False
    # - numeric zero: 0, 0.0, 0j, Decimal(0), Fraction(0, 1)
    # - empty sequences, mappings, sets, and ranges: "", b"", (), [], {}, set(),
    #   and range(0)
    #
    # Every other built-in value is truthy. Watch out for two common traps:
    # - A non-empty container holding a falsy item is STILL truthy! bool([0])
    #   and bool([False]) are both True because the list has length 1.
    # - Any non-empty string is truthy -- even bool("False") and bool("0") are
    #   True!
    #
    # Custom classes are truthy by default unless they define __bool__ returning
    # False or __len__ returning 0.

    for sample in (0, 1, "", "False", [], [0]):
        print(f"bool({sample!r}) = {bool(sample)}")

    # Import Decimal from decimal and Fraction from fractions inside this
    # function, then check bool() across None, 0.0, 0j, Decimal(0),
    # Fraction(0, 1), b"", {}, set(), range(0), and range(1), printing each
    # value with !r and its bool(...) result.


    # Define a small class Bucket: inside this function with
    # def __init__(self, count: int) -> None: storing self.count = count and
    # def __bool__(self) -> bool: returning self.count > 0.
    # Print bool(Bucket(0)) (False) and bool(Bucket(3)) (True).


def value_returning_and_or_short_circuit() -> None:

    # Unlike C or Odin, Python's 'and' and 'or' operators do NOT convert their
    # result to True or False -- they return the ACTUAL operand object that
    # decided the expression, and they short-circuit (skipping the right operand
    # whenever the left operand already settles the outcome):
    # - a or b: returns a immediately if a is truthy (without evaluating b),
    #   otherwise evaluates and returns b.
    # - a and b: returns a immediately if a is falsy (without evaluating b),
    #   otherwise evaluates and returns b.
    # - Only 'not x' is guaranteed to return an actual bool (True or False).
    #
    # That value-returning rule creates the Falsy-Zero Trap:
    #     Suppose user_port: int | None = 0 (a valid request for an OS ephemeral
    #     port). Writing port = user_port or 8080 sees 0 as falsy and silently
    #     overwrites it with 8080!
    # Whenever 0, 0.0, or "" is a valid non-missing value, check None explicitly:
    #     port = 8080 if user_port is None else user_port

    print('"" or "fallback" ->', "" or "fallback")
    print('0 and "never" ->', 0 and "never")

    # Reproduce and fix the falsy-zero trap:
    # bind configured_timeout: int | None = 0.
    # Compute bad_timeout = configured_timeout or 30 (wrongly yields 30) and
    # good_timeout = 30 if configured_timeout is None else configured_timeout
    # (preserves 0). Print both, then set configured_timeout = None and re-check
    # good_timeout (30).


    # Prove short-circuiting skips side effects:
    # define def noisy_check(label: str, flag: bool) -> bool: that prints
    # f"evaluated {label}" and returns flag.
    # Run noisy_check("A", False) and noisy_check("B", True) followed by
    # noisy_check("C", True) or noisy_check("D", False) and verify neither B nor
    # D is ever printed.


    # Contrast not [] (True, type bool) against [] or "default" ("default", type
    # str) and "hi" and [1, 2] ([1, 2], type list), printing each value and its
    # type(...).__name__.


    # Practice safe guard short-circuiting with 'and':
    # bind empty_items: list[str] = [] and filled_items = ["alpha", "beta"].
    # Evaluate first_empty = empty_items and empty_items[0] (returns [] safely
    # without IndexError!) and first_filled = filled_items and filled_items[0]
    # (returns "alpha"), then print both results.


def chained_comparisons() -> None:

    # Python lets you chain comparison operators naturally, just like math:
    # low <= x < high means (low <= x) and (x < high), EXCEPT Python evaluates
    # the middle expression x only ONCE (even if x is a function call!).
    #
    # Suppose temperature = 22:
    #     0 <= temperature < 100 evaluates 0 <= 22 (True) and 22 < 100 (True)
    #     and returns True.
    #
    # You can chain any comparisons (a == b == c, 1 < 5 > 3), though keep chains
    # readable -- mixing != or 'in' in chains like a != b != c can surprise
    # readers because it does NOT check a != c!

    level = 5
    print("0 <= level <= 10:", 0 <= level <= 10)

    # Bind temperature = 22 and a = b = c = 5.
    # Print 0 <= temperature < 100, a == b == c, and 1 < 5 > 3 alongside
    # 1 != 2 != 1 (True, because Python checks 1 != 2 and 2 != 1, not 1 != 1!).


    # Prove the middle expression in a chain runs only once:
    # define def read_sensor() -> int: that prints "reading sensor" and returns
    # 42. Evaluate 0 <= read_sensor() < 100 and confirm "reading sensor" prints
    # exactly once.


def main() -> None:

    print("=== 1. bool as an int subclass ===")
    bool_as_int_subclass()

    print("\n=== 2. Truthiness and falsiness ===")
    truthiness_and_falsiness()

    print("\n=== 3. Value-returning and/or short-circuiting ===")
    value_returning_and_or_short_circuit()

    print("\n=== 4. Chained comparisons ===")
    chained_comparisons()


if __name__ == "__main__":
    main()
