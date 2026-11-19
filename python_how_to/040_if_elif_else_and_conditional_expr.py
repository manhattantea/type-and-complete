# python 040_if_elif_else_and_conditional_expr.py


def if_elif_else_and_explicit_none() -> None:

    # Python structures conditional branches with colons and indentation rather
    # than curly braces, omits parentheses around conditions, and spells "else
    # if" as elif. Branches are tested top-to-bottom and ONLY the first true
    # branch executes.
    #
    # Always guard optional numbers with an explicit 'is None' or 'is not None'
    # check BEFORE numeric comparisons! Never test 'if not latency:' when 0.0 is
    # a valid measurement:
    #
    #     Suppose ms: float | None = 0.0 (instant loopback response).
    #     if not ms: wrongly treats 0.0 as missing/offline!
    #     if ms is None: lets 0.0 fall cleanly into elif ms < 20.0: ("fast").

    ping_ms: float | None = 12.5
    if ping_ms is None:
        print("Starter status: offline")
    else:
        print(f"Starter status: online ({ping_ms} ms)")

    # Define def classify_latency(ms: float | None) -> str: inside this function.
    # Check if ms is None: return "offline" first (so 0.0 is never mistaken for
    # missing), then elif ms < 20.0: return "fast",
    # elif ms < 100.0: return "normal", and else: return "slow".
    # Call and print classify_latency on 0.0, 19.9, 45.0, 250.0, and None.


    # Define def clamp_score(score: int) -> int: using if / elif / else that
    # returns 0 when score < 0, 100 when score > 100, and score otherwise.
    # Test it on -5, 42, and 150.


def conditional_expressions_and_laziness() -> None:

    # When a two-way branch simply chooses between two values, Python provides
    # an inline conditional (ternary) expression:
    #
    #     result = truthy_expr if condition else falsy_expr
    #
    # Pay close attention to evaluation order: Python evaluates condition FIRST,
    # then evaluates ONLY the chosen branch -- the unchosen branch is skipped
    # completely! Avoid nesting conditional expressions; once you have three or
    # more branches, plain if / elif / else is much easier to read.
    #
    #     Suppose divisor = 0:
    #         ratio = 0.0 if divisor == 0 else 100 / divisor
    #     Because divisor == 0 is True, Python returns 0.0 and never executes
    #     100 / divisor (so no ZeroDivisionError happens).

    count = 1
    label = "singular" if count == 1 else "plural"
    print(f"{count} item ({label})")

    # Set retries = 3, compute suffix = "retry" if retries == 1 else "retries"
    # with an inline conditional expression, and print f"{retries} {suffix}".


    # Prove lazy branch evaluation:
    # bind divisor = 0 and compute
    # safe_quotient = 0.0 if divisor == 0 else 100 / divisor, printing it to
    # confirm no ZeroDivisionError occurs. Repeat with divisor = 4 (25.0).


def pass_vs_ellipsis_idioms() -> None:

    # Two tiny placeholders often show up in Python codebases: the pass
    # statement and the ... (Ellipsis) literal. Keep their difference clear:
    # - The pass keyword is a no-op STATEMENT used only when Python syntax
    #   demands an indented block (for instance an empty custom exception class
    #   like class ConfigError(Exception):). It produces no value and cannot be
    #   assigned to a variable.
    # - '...' is a real runtime EXPRESSION evaluating to the built-in singleton
    #   object Ellipsis. Besides acting as a placeholder body in stub files
    #   (.pyi), '...' is a real value used in type hints (tuple[int, ...]) and
    #   multidimensional slicing (such as NumPy arrays).

    print("... is Ellipsis:", ... is Ellipsis, "| type:", type(...).__name__)

    # Verify Ellipsis is a real runtime value:
    # bind marker = ... and print marker is Ellipsis (True), bool(marker)
    # (True), and marker == Ellipsis (True).


    # Combine explicit is not None with an inline conditional expression:
    # bind raw_limit: int | None = 0. Write if raw_limit is not None: to compute
    # clamped = raw_limit if raw_limit >= 0 else 0 and print clamped, with an
    # else: branch printing "no limit". Repeat with raw_limit = None.


def main() -> None:

    print("=== 1. if / elif / else and explicit None checks ===")
    if_elif_else_and_explicit_none()

    print("\n=== 2. Conditional expressions and lazy branches ===")
    conditional_expressions_and_laziness()

    print("\n=== 3. pass vs Ellipsis idioms ===")
    pass_vs_ellipsis_idioms()


if __name__ == "__main__":
    main()
