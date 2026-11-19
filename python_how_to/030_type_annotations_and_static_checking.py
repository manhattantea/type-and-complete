# python 030_type_annotations_and_static_checking.py

import inspect
from typing import Any, Final, Literal


def runtime_non_enforcement_and_metadata() -> None:

    # Critical Python mental model: Python remains dynamically typed at runtime!
    # Adding type annotations such as count: int = "oops" does NOT make the
    # Python interpreter raise a TypeError when the script runs.
    #
    # Instead, CPython compiles annotations into runtime metadata dictionaries
    # stored in __annotations__ on modules, classes, and functions. Ahead-of-time
    # static type checkers (mypy, pyright) inspect those hints before you ship
    # code, while runtime libraries (dataclasses, pydantic, fastapi) read them
    # using inspect.get_annotations().
    #
    # Suppose you write:
    #     def double(n: int) -> int:
    #         return n * 2
    # Calling double("ha") still returns "haha" at runtime because Python
    # dispatches * on str dynamically -- a static checker catches the mismatch
    # ahead of time!

    def double(n: int) -> int:

        return n * 2

    print("double.__annotations__:", double.__annotations__)
    print("inspect.get_annotations:", inspect.get_annotations(double))

    # Prove runtime non-enforcement directly:
    # bind mismatched: int = "still runs at runtime" and call double("ha"),
    # printing mismatched and the call result to see CPython execute both
    # without raising TypeError.


    # Define def parse_port(raw: str) -> int | None: inside this function that
    # returns int(raw) if raw.isdigit() else None. Call it on "8080" and "abc",
    # then print inspect.get_annotations(parse_port).


def modern_containers_and_type_aliases() -> None:

    # Since Python 3.9+, built-in collection types accept generic type arguments
    # directly (no legacy typing.List or typing.Dict imports needed):
    # - list[int]          a list whose elements are ints
    # - dict[str, float]   a dict mapping str keys to float values
    # - tuple[int, str]    a fixed 2-tuple: index 0 is int, index 1 is str
    # - tuple[int, ...]    a variable-length tuple of any number of ints
    #
    # Since Python 3.12 (PEP 695), the 'type' statement defines a clean, lazy
    # type alias object:
    #     type ScoreBoard = dict[str, float]
    # Reading ScoreBoard.__value__ reveals the underlying aliased type at
    # runtime while keeping signatures readable across your codebase.

    type ScoreBoard = dict[str, float]
    board: ScoreBoard = {"ada": 98.5, "linus": 94.0}
    print("Type alias:", ScoreBoard, "| board:", board)

    # Write two container-annotated helpers inside this function:
    # - def sum_scores(values: list[int]) -> int: returning sum(values)
    # - def average_board(scores: ScoreBoard) -> float: returning 0.0 when
    #   scores is empty, otherwise sum(scores.values()) / len(scores)
    # Call both on sample data and print their outputs plus .__annotations__.


    # Contrast fixed vs variadic tuple annotations:
    # - Define def format_record(record: tuple[int, str]) -> str: returning
    #   f"#{record[0]} {record[1]}".
    # - Define def sum_variadic(nums: tuple[int, ...]) -> int: returning
    #   sum(nums).
    # Test format_record((7, "ada")), sum_variadic((1, 2)), and
    # sum_variadic((1, 2, 3, 4)).


    # Define two PEP 695 aliases: type Coord = tuple[float, float] and
    # type Route = list[Coord]. Build a 2-point route:
    # path: Route = [(0.0, 0.0), (3.0, 4.0)]
    # and print path alongside Coord.__value__.


def unions_final_and_literal() -> None:

    # Modern Python 3.10+ writes union types with the pipe operator (int | str,
    # int | None) instead of legacy typing.Union or typing.Optional.
    #
    # Two typing helpers tighten contracts without runtime overhead:
    # - Final[T] marks a name as constant so static checkers reject rebinding it
    #   (for example MAX_CONNECTIONS: Final[int] = 100).
    # - Literal["USR", "ORD"] restricts a parameter to an exact fixed set of
    #   literal values instead of accepting any arbitrary string.
    #
    # Static checkers also understand type narrowing: inside an
    # if isinstance(raw_id, int): branch, the checker narrows raw_id from
    # int | str down to int, and narrows the else branch down to str!
    #
    # Suppose raw_id: int | str = 42:
    #     if isinstance(raw_id, int):
    #         return f"USR-{raw_id:04d}"   # static checker knows raw_id is int
    #     return f"USR-{raw_id.upper()}"   # static checker knows raw_id is str

    MAX_RETRIES: Final[int] = 3
    mode: Literal["fast", "safe"] = "safe"
    print(f"Starter hints: MAX_RETRIES={MAX_RETRIES}, mode={mode}")

    # Define MAX_CONNECTIONS: Final[int] = 100 and
    # def format_id(raw_id: int | str, prefix: Literal["USR", "ORD"] = "USR") -> str:
    # Use isinstance(raw_id, int) to return f"{prefix}-{raw_id:04d}" for int or
    # f"{prefix}-{raw_id.upper()}" for str. Call format_id(42) and
    # format_id("abc", prefix="ORD"), printing both plus
    # format_id.__annotations__.


    # Static-checking experiment:
    # Try running mypy or pyright (if installed) on a call like:
    # format_id(42, prefix="BAD")
    # Notice plain python runs it without complaint, while a static checker
    # rejects "BAD" because it is not in Literal["USR", "ORD"].


def any_vs_object_and_narrowing() -> None:

    # Do NOT confuse typing.Any with object -- they mean opposite things to a
    # static type checker!
    # - Any is an escape hatch that DISABLES static type checking completely:
    #   every attribute access or method call on Any is silently permitted.
    # - object is the type-safe top type (every Python value is an object): a
    #   static checker rejects val.upper() or val + 1 on object until you prove
    #   its concrete type with isinstance() or an explicit is not None check.
    #
    # Suppose val: object = "hello":
    #     val.upper() fails static checking, while
    #     if isinstance(val, str): return val.upper() passes cleanly!

    dynamic_box: Any = "hello"
    safe_box: object = "hello"
    print("Same runtime value:", dynamic_box == safe_box)

    # Define def describe_value(val: object) -> str: that narrows val with
    # isinstance(val, str) (returning val.upper()), isinstance(val, int)
    # (returning f"int:{val}"), and falls back to str(val).
    # Call describe_value on "hello", 7, and [1, 2] and print each result.


    # Define a companion def unsafe_peek(val: Any) -> str: returning str(val),
    # call it on "hello", and note in a short comment why
    # val.nonexistent_method() would pass a static checker on Any yet crash
    # with AttributeError at runtime (whereas object catches it statically).


def main() -> None:

    print("=== 1. Runtime non-enforcement and metadata ===")
    runtime_non_enforcement_and_metadata()

    print("\n=== 2. Modern containers and type aliases ===")
    modern_containers_and_type_aliases()

    print("\n=== 3. Unions, Final, and Literal ===")
    unions_final_and_literal()

    print("\n=== 4. Any vs object and type narrowing ===")
    any_vs_object_and_narrowing()


if __name__ == "__main__":
    main()
