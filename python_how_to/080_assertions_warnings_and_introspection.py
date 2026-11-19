# python 080_assertions_warnings_and_introspection.py

import warnings


def assertions_vs_runtime_validation() -> None:

    # Critical safety rule: 'assert' is ONLY for internal developer invariants
    # (conditions that can only fail if your own code has a bug), NEVER for
    # validating user input, permissions, or network payloads!
    #
    # Python compiles assert condition, message into:
    #     if __debug__:
    #         if not condition:
    #             raise AssertionError(message)
    # When Python runs in optimized mode (python -O), __debug__ is False and
    # EVERY assert statement is stripped completely from bytecode! External
    # checks must always use explicit if ...: raise ValueError(...) statements.
    #
    # Watch out for the Assert Tuple Trap:
    # NEVER wrap the condition and message in parentheses like
    # assert(False, "msg")! In Python, (False, "msg") is a non-empty 2-tuple,
    # and EVERY non-empty tuple is truthy—so assert(False, "msg") silently
    # succeeds every time (emitting only a SyntaxWarning at compile time)!
    # Always write assert condition, "message" with zero outer parentheses.

    assert 2 + 2 == 4, "arithmetic invariant broke"
    print(f"Starter check: __debug__ is {__debug__}")

    # Define def withdraw(balance: int, amount: int) -> int: inside this
    # function. Enforce external inputs with explicit raises:
    # - if amount < 0: raise ValueError("amount must be >= 0")
    # - if amount > balance: raise ValueError("insufficient funds")
    # Compute remaining = balance - amount, verify the internal invariant with
    # assert remaining >= 0, "balance invariant broken", and return remaining.
    # Test withdraw(100, 40), withdraw(100, -5), and withdraw(100, 150)
    # (catching ValueError on the invalid calls) and print each outcome.


    # Observe AssertionError directly under normal execution vs. python -O:
    # Wrap assert 1 == 2, "expected mismatch" inside
    # try / except AssertionError as err: and print "Caught assertion:", err.
    # Then run python -O 080_assertions_warnings_and_introspection.py from your
    # shell to see __debug__ flip to False and notice the assertion skip
    # completely while withdraw()'s ValueError checks still enforce safety!


    # Prove why parenthesized assert tuples never trigger:
    # Print bool((False, "msg")) (expected: True!).
    #
    # Try uncommenting below to see Python emit a SyntaxWarning without raising AssertionError:
    # assert (False, "this non-empty tuple is always truthy!")


def warnings_and_warning_filters() -> None:

    # warnings.warn(message, category, stacklevel=...) emits a non-fatal
    # diagnostic message without aborting execution. Common categories are
    # UserWarning (default), DeprecationWarning, and RuntimeWarning.
    #
    # Two practical details explain most warning behavior:
    # - stacklevel=2 tells Python to point the warning's file and line number
    #   at the CALLER of your deprecated helper instead of the line inside the
    #   helper itself.
    # - warnings.catch_warnings(record=True) temporarily isolates warning
    #   filters (such as warnings.simplefilter("always") or "error") and
    #   collects emitted WarningMessage records into a list for inspection:
    #
    #     Suppose legacy_mode() calls warnings.warn("old", DeprecationWarning, stacklevel=2).
    #     Running with python -W error turns that warning into an exception!

    with warnings.catch_warnings(record=True) as starter_log:
        warnings.simplefilter("always")
        warnings.warn("starter diagnostic", UserWarning, stacklevel=1)
    print(f"Starter captured {len(starter_log)} warning(s)")

    # Define def legacy_mode(value: int) -> int: that calls
    # warnings.warn("legacy_mode is deprecated", DeprecationWarning, stacklevel=2)
    # and returns value * 2. Call legacy_mode(21) and print its return value.
    # (You can also test python -W default 080_assertions_warnings_and_introspection.py
    # and python -W error 080_assertions_warnings_and_introspection.py.)


    # Capture and inspect emitted WarningMessage fields programmatically:
    # Enter with warnings.catch_warnings(record=True) as caught:, call
    # warnings.simplefilter("always"), invoke legacy_mode(10), and print
    # caught[0].category.__name__, str(caught[0].message), and caught[0].lineno.


    # Escalate DeprecationWarning into a hard exception locally:
    # Wrap legacy_mode(5) inside with warnings.catch_warnings(): and
    # warnings.simplefilter("error", DeprecationWarning), catching
    # except DeprecationWarning as err: to print "Escalated to error:", err.


def type_checks_and_dynamic_attributes() -> None:

    # Runtime type checks inspect inheritance cleanly:
    # - isinstance(obj, ClsOrTuple) checks whether obj is an instance of a
    #   class or any subclass. Since Python 3.10 you can pass either a tuple
    #   (int, float) or a union type int | float.
    # - issubclass(Sub, BaseOrTuple) checks class inheritance directly. Remember
    #   that bool is a subclass of int, so isinstance(True, int) is True!
    #
    # Python also lets you inspect and modify attributes by string name:
    # - hasattr(obj, "name") checks existence (calls getattr and catches AttributeError).
    # - getattr(obj, "name", default) reads an attribute or returns default safely.
    # - setattr(obj, "name", value) sets or creates an attribute dynamically.
    # - delattr(obj, "name") removes an attribute from the object.
    #
    #     Suppose t = Task("ship") has no "owner" attribute yet.
    #     getattr(t, "owner", "unassigned") returns "unassigned"; after
    #     setattr(t, "owner", "ada"), hasattr(t, "owner") becomes True.

    print("Starter bool/int check:", isinstance(True, int), issubclass(bool, int))

    # Run runtime type and subclass checks and print all three booleans:
    # isinstance(3.5, int | float), isinstance(False, int), and
    # issubclass(KeyError, LookupError).


    # Define class Task: inside this function with
    # def __init__(self, title: str, done: bool = False) -> None: storing
    # self.title and self.done. Instantiate t = Task("ship primer"), then print:
    # hasattr(t, "title"), getattr(t, "owner", "unassigned"), set
    # setattr(t, "owner", "ada"), print hasattr(t, "owner") and t.owner, and
    # delete it with delattr(t, "owner") followed by hasattr(t, "owner").


    # Practice dynamic method lookup with getattr + callable:
    # Define class Calculator: with def add(self, a: int, b: int) -> int: and
    # def mul(self, a: int, b: int) -> int:. Create calc = Calculator(), look up
    # fn = getattr(calc, "mul", None), verify callable(fn), and print fn(6, 7).


def dir_vars_and_callable_introspection() -> None:

    # Two built-ins inspect what an object carries, and they answer very
    # different questions:
    # - dir(obj) returns a sorted list of ALL accessible attribute names on obj,
    #   including instance attributes, class methods, inherited object methods,
    #   and descriptors.
    # - vars(obj) returns obj.__dict__—ONLY the writable per-instance attribute
    #   dictionary! Built-ins like 42 or "hi" and classes defining __slots__
    #   have no __dict__, so vars() raises TypeError on them.
    # - callable(obj) returns True for functions, methods, classes (calling a
    #   class constructs an instance), and instances whose class defines __call__.
    #
    #     Suppose job = Job("index") sets self.name = "index".
    #     vars(job) is {"name": "index"} (1 key), whereas len(dir(job)) is ~27+
    #     because dir() includes every inherited dunder method from object!

    print("Starter callable checks:", callable(len), callable(42))

    # Define class Job: with def __init__(self, name: str) -> None: storing
    # self.name = name, create job = Job("index"), and print vars(job),
    # len(dir(job)), and [a for a in dir(job) if not a.startswith("__")].


    # Prove vars() raises TypeError on objects without __dict__:
    # Call vars(42) inside try / except TypeError as err: and print err.
    # Then define class SlottedPoint: with __slots__ = ("x", "y") and
    # def __init__(self, x: int, y: int) -> None: setting self.x and self.y.
    # Try vars(SlottedPoint(1, 2)) inside try / except TypeError as err: to see
    # slotted instances lack __dict__ too!


    # Test callable() across four distinct kinds of Python objects:
    # define def double(x: int) -> int: return x * 2 and
    # class Multiplier: with def __init__(self, factor: int) -> None: and
    # def __call__(self, x: int) -> int: return x * self.factor.
    # Print callable(double), callable(Multiplier), callable(Job("x")), and
    # callable(Multiplier(3)), plus Multiplier(3)(7) (expected: 21).


def main() -> None:

    print("=== 1. Assertions vs. runtime validation ===")
    assertions_vs_runtime_validation()

    print("\n=== 2. Warnings and warning filters ===")
    warnings_and_warning_filters()

    print("\n=== 3. Runtime type checks and dynamic attributes ===")
    type_checks_and_dynamic_attributes()

    print("\n=== 4. dir(), vars(), and callable() introspection ===")
    dir_vars_and_callable_introspection()


if __name__ == "__main__":
    main()
