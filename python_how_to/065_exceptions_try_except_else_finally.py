# python 065_exceptions_try_except_else_finally.py


def four_clauses_try_except_else_finally() -> None:

    # Python prefers EAFP ("Easier to Ask for Forgiveness than Permission"):
    # wrap only the narrow operation that can fail inside try:, then handle
    # expected failure types explicitly. Putting extra unrelated lines inside
    # try: risks catching bugs from follow-up logic by mistake.
    #
    # Each of the four clauses has one exact job:
    # - try: holds ONLY the risky operation.
    # - except (ErrA, ErrB) as err: runs when try: raises a matching exception.
    # - else: runs ONLY when try: raised ZERO exceptions—and any exception
    #   raised inside else: is NOT caught by the except: clauses above it!
    # - finally: ALWAYS runs when leaving the try statement (normal completion,
    #   handled error, return, break, or unhandled exception).
    #
    #     Suppose raw = "3/4": try succeeds -> else returns 0.75 -> finally runs.
    #     Suppose raw = "5/0": try raises ZeroDivisionError -> except returns None
    #     -> finally still runs before leaving the function!

    try:
        starter_val = int("42")
    except ValueError as err:
        print("Starter parse error:", err)
    else:
        print("Starter parsed:", starter_val)
    finally:
        print("Starter finally ran")

    # Define def parse_ratio(raw: str) -> float | None: inside this function.
    # Put ONLY splitting, int conversion, and division inside try:
    # (num_text, den_text = raw.split("/"); quotient = int(num_text) / int(den_text)).
    # Catch except (ValueError, ZeroDivisionError) as err: printing the error
    # and returning None. In else:, print and return quotient. Add a finally:
    # block printing "parse_ratio finished".


    # Call parse_ratio("3/4"), parse_ratio("5/0"), and parse_ratio("bad"),
    # printing each returned value (0.75, None, None) while watching when else:
    # runs and confirming finally: runs every time.


    # Prove that exceptions raised in else: are NOT caught by the sibling
    # except: clause above it:
    # Wrap an inner try/except/else inside an outer try / except ValueError as outer_err:
    # In the inner try:, run n = int("10") (succeeds!). Catch ValueError in the
    # inner except (prints "inner caught"). In the inner else:, execute
    # raise ValueError("raised in else") and observe outer_err catch it instead!


def hierarchy_ordering_and_oserror() -> None:

    # Python tests except clauses top-to-bottom using issubclass(type(err), Target)
    # and enters ONLY the first matching clause. Because exceptions form an
    # inheritance hierarchy (for example, FileNotFoundError inherits from
    # OSError, which inherits from Exception), placing a broad parent class
    # ABOVE a specific child class makes the child branch completely unreachable:
    #
    #     Suppose you try to open a missing file:
    #         except OSError:           # catches FileNotFoundError first!
    #             print("generic os error")
    #         except FileNotFoundError: # dead code—never reached!
    #             print("missing file")
    #
    # Always order handlers from most specific subclass to broadest parent.

    print(
        "Starter hierarchy checks:",
        issubclass(FileNotFoundError, OSError),
        issubclass(ValueError, Exception),
    )

    # Reproduce the exception hierarchy ordering trap:
    # Wrap int("nope") in try: with except Exception: BEFORE except ValueError:
    # and print which handler ran (you will see Exception steal ValueError!).
    # Then repeat with except ValueError: BEFORE except Exception: so the
    # specific handler runs first.


    # Practice OSError vs. FileNotFoundError ordering on a real missing path:
    # Inside try:, attempt open("__missing_primer_065__.txt", encoding="utf-8").
    # Catch except FileNotFoundError as err: BEFORE except OSError as err:,
    # printing "missing file:", err.errno, and err.filename so you see
    # FileNotFoundError trigger first while still keeping OSError as a fallback.


    # Inspect the Method Resolution Order (__mro__) of exception classes:
    # print [cls.__name__ for cls in FileNotFoundError.__mro__] and
    # [cls.__name__ for cls in ZeroDivisionError.__mro__] to see their full
    # ancestor chains up to BaseException and object.


def base_exception_vs_exception_trap() -> None:

    # Never write a bare except: (or except BaseException:) for ordinary error
    # handling! In Python's exception hierarchy, BaseException is the root, and
    # three critical control-flow signals inherit from BaseException directly,
    # NOT from Exception:
    # - KeyboardInterrupt (Ctrl+C from the user)
    # - SystemExit (raised by sys.exit())
    # - GeneratorExit (raised when a generator is closed)
    #
    #     Suppose a loop wraps work in bare except:
    #     Pressing Ctrl+C raises KeyboardInterrupt, bare except: catches and
    #     swallows it, and the program refuses to stop!
    #
    # Always catch specific exception types, or at widest except Exception as err:.

    print(
        "SystemExit under Exception?",
        issubclass(SystemExit, Exception),
        "under BaseException?",
        issubclass(SystemExit, BaseException),
    )

    # Prove except Exception: lets Ctrl+C (KeyboardInterrupt) escape cleanly:
    # Inside an outer try / except KeyboardInterrupt as kb:, write an inner
    # try: raise KeyboardInterrupt("simulated Ctrl+C") followed by
    # except Exception: print("wrongly swallowed"). Confirm the outer handler
    # catches kb cleanly.


    # Repeat the exact check with SystemExit(2):
    # Raise SystemExit(2) inside an inner try / except Exception:, catch it in
    # an outer except SystemExit as exit_err:, and print exit_err.code.


def finally_return_swallowing_trap() -> None:

    # Never put 'return' (or 'break' / 'continue') inside a finally: block!
    # Because finally: always executes as the function frame exits, executing
    # return inside finally: overrides any return value from try: AND silently
    # discards any active unhandled exception that was propagating out:
    #
    #     Suppose you write:
    #         def broken() -> str:
    #             try:
    #                 raise RuntimeError("disk full")
    #             finally:
    #                 return "all good"
    #     Calling broken() returns "all good" and deletes the RuntimeError!
    #
    # Keep finally: strictly for cleanup (closing handles, releasing locks,
    # logging exit) and let return values and exceptions flow naturally.

    cleanup_done = False
    try:
        starter_ratio = 10 / 2
    finally:
        cleanup_done = True
    print(f"Starter clean finally: ratio={starter_ratio}, cleanup_done={cleanup_done}")

    # Reproduce the return-in-finally exception-swallowing trap:
    # Define def swallowed_error() -> str: that raises RuntimeError("disk full")
    # inside try: and executes return "silent fallback" inside finally:.
    # Call swallowed_error() and print its return value to watch the
    # RuntimeError disappear without crashing!


    # Also test return-value overriding in finally:
    # Define def overridden_value() -> str: that returns "from try" inside try:
    # and returns "from finally" inside finally:. Call it and print the result.


    # Write the clean version def safe_cleanup() -> str: where try: raises
    # RuntimeError("disk full") and finally: only prints "releasing resources"
    # without returning. Call safe_cleanup() inside try / except RuntimeError as err:
    # to confirm both cleanup AND error propagation happen as expected.


def main() -> None:

    print("=== 1. Four clauses: try, except, else, finally ===")
    four_clauses_try_except_else_finally()

    print("\n=== 2. Hierarchy ordering and OSError ===")
    hierarchy_ordering_and_oserror()

    print("\n=== 3. BaseException vs. Exception trap ===")
    base_exception_vs_exception_trap()

    print("\n=== 4. The return-in-finally swallowing trap ===")
    finally_return_swallowing_trap()


if __name__ == "__main__":
    main()
