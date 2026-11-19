# python 460_code_quality_typecheck_and_linter_hygiene.py

from enum import Enum, auto
from typing import Never, assert_never, assert_type


def assert_type_and_never_paths() -> None:

    # Running python -m py_compile (or ast.parse) only checks grammar and
    # indentation. It will happily accept mismatched return types, unhandled
    # enum cases, or dead code paths. Static analyzers (mypy --strict, pyright,
    # ty) paired with fast linters (ruff) catch those bugs before runtime, and
    # Python 3.11+ ships three typing primitives built directly for them:
    #
    # - typing.assert_type(val, ExpectedType): asks the static type checker to
    #   verify that val's inferred type is EXACTLY ExpectedType. At runtime it
    #   simply returns val unchanged with virtually zero cost.
    # - typing.Never (the bottom type, equivalent to NoReturn for return
    #   annotations): marks a function that never returns normally because it
    #   always raises an exception or loops forever. After a call returning
    #   Never, type checkers know subsequent lines are unreachable.
    #
    #     Suppose def fail(msg: str) -> Never: raises ValueError(msg).
    #     In def parse_positive(n: int) -> int:
    #         if n <= 0:
    #             fail("must be positive")
    #         return n
    #     Static checkers prove every normal exit returns int with no missing
    #     return warning.

    sample_id: int = 42
    verified_id = assert_type(sample_id, int)
    print(f"assert_type runtime pass-through -> {verified_id}")

    # Define def abort_invalid(reason: str) -> Never: that unconditionally
    # raises ValueError(reason). Then define
    # def require_positive(n: int) -> int: calling abort_invalid("n must be > 0")
    # when n <= 0 and returning n otherwise. Test it on 7 and catch ValueError
    # on -1.


    # Practice type narrowing paired with assert_type:
    # declare raw: int | str = "ready"
    # Check if isinstance(raw, str):, verify assert_type(raw, str), and print
    # raw.upper() to see how isinstance() narrows a union for static checkers.


def exhaustive_match_with_assert_never() -> None:

    # One of the highest-value static guarantees in systems languages like Odin
    # is an exhaustive switch over an enum: add a new variant and the compiler
    # immediately flags every switch you forgot to update.
    #
    # In Python, pairing match/case with typing.assert_never(arg: Never) -> Never
    # achieves the exact same safety net:
    #
    #     Suppose TrafficLight has RED, YELLOW, GREEN and match light handles
    #     all three, ending with:
    #         case _ as unreachable:
    #             assert_never(unreachable)
    #     Because all three members are matched, the checker narrows unreachable
    #     to Never and stays quiet. The moment someone adds FLASHING = auto() to
    #     TrafficLight without updating match, unreachable narrows to
    #     Literal[TrafficLight.FLASHING] instead of Never, and mypy/pyright
    #     immediately rejects assert_never(unreachable)!
    #
    # At runtime, if bad data ever reaches assert_never(...), it raises
    # AssertionError immediately instead of silently returning None.

    print("Enum exhaustiveness helpers ready:", Enum.__name__, auto.__name__, assert_never.__name__)

    # Define class TrafficLight(Enum): with RED = auto(), YELLOW = auto(), and
    # GREEN = auto().
    # Then define def next_light(light: TrafficLight) -> TrafficLight: using
    # match light: mapping RED -> GREEN, GREEN -> YELLOW, YELLOW -> RED, and
    # ending with case _ as unreachable: assert_never(unreachable).


    # Step current = TrafficLight.RED through one complete 3-step cycle
    # (RED -> GREEN -> YELLOW -> RED), calling
    # current = assert_type(next_light(current), TrafficLight) on each step and
    # printing current.name.


    # Verify the runtime safety net of assert_never:
    # call assert_never("INVALID") inside try ... except AssertionError as err:
    # and print err (add # type: ignore[arg-type] if running mypy --strict).


    # Static-check experiment: after implementing TrafficLight and next_light,
    # try adding FLASHING = auto() to TrafficLight without adding a case branch
    # in next_light, then run mypy --strict or pyright to see the exhaustiveness
    # error fire immediately.


def main() -> None:

    print("=== 1. assert_type and Never control-flow paths ===")
    assert_type_and_never_paths()

    print("\n=== 2. Exhaustive match/case with assert_never ===")
    exhaustive_match_with_assert_never()


if __name__ == "__main__":
    main()
