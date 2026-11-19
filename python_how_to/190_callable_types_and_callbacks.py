# python 190_callable_types_and_callbacks.py

from collections.abc import Callable
from typing import Literal, Protocol, overload


def callable_type_annotations() -> None:

    # Python's type system starts with collections.abc.Callable for describing
    # simple callback parameters (always import Callable from collections.abc
    # rather than the legacy typing.Callable alias):
    # - Callable[[Param1, Param2], ReturnType] specifies exact positional
    #   parameter types and a return type.
    # - Callable[[], ReturnType] describes a zero-argument factory callback.
    # - Callable[..., ReturnType] uses Python's Ellipsis literal (...) to mean
    #   "accepts any parameter signature and returns ReturnType", which disables
    #   argument type checking at call sites—so prefer exact parameter lists
    #   whenever you know them.
    #
    #     Suppose def apply_transform(items: list[str], fn: Callable[[str], str]) -> list[str]:
    #     Passing str.strip works cleanly because str.strip(" hi ") takes one
    #     str and returns one str ("hi").

    def run_once(fn: Callable[[int], int], value: int) -> int:

        return fn(value)

    print(f"Starter Callable[[int], int]: run_once(abs, -7) = {run_once(abs, -7)}")

    # Write apply_transform(items: list[str], fn: Callable[[str], str]) -> list[str]
    # returning [fn(item) for item in items].
    # Test it with str.strip, str.upper, and a custom local helper
    # def slugify(text: str) -> str: return text.strip().lower().replace(" ", "-")
    # over [" Ada Lovelace ", " Grace Hopper "], printing each transformed list.


    # Practice a two-argument callback annotation Callable[[int, int], int]:
    # Define combine_pairs(left: list[int], right: list[int], op: Callable[[int, int], int]) -> list[int]
    # returning [op(a, b) for a, b in zip(left, right, strict=True)].
    # Define def add_ints(a: int, b: int) -> int: return a + b and call
    # combine_pairs([1, 2, 3], [10, 20, 30], add_ints) plus
    # combine_pairs([5, 1, 9], [2, 8, 4], max).


    # Practice a zero-argument factory callback Callable[[], list[int]]:
    # Define make_rows(count: int, row_factory: Callable[[], list[int]]) -> list[list[int]]
    # returning [row_factory() for _ in range(count)].
    # Call grid = make_rows(3, lambda: [0, 0]), mutate grid[0][0] = 9, and
    # print grid to verify every row is an independent list!


def callback_protocols_for_rich_signatures() -> None:

    # Callable[[...], ...] hits a hard limit as soon as a callback uses
    # keyword-only parameters (*, strict: bool), optional default values, or
    # meaningful parameter names—Callable has no syntax to express any of those.
    #
    # That is where typing.Protocol shines: define a Protocol class with a
    # single def __call__(self, ...): ... method (here Python's ... Ellipsis
    # body marks a type-level interface stub with no runtime body). Because
    # Protocol uses structural subtyping (static duck typing), ANY plain def
    # function OR callable class with a matching signature satisfies the
    # Protocol automatically—without ever inheriting from it!
    #
    #     class ValidatorProtocol(Protocol):
    #         def __call__(self, value: str, *, strict: bool = False) -> bool: ...
    #
    #     def is_non_empty(value: str, *, strict: bool = False) -> bool:
    #         return bool(value.strip()) if strict else bool(value)
    #     is_non_empty satisfies ValidatorProtocol structurally with zero inheritance!

    print(f"Starter check: callable(str.strip)={callable(str.strip)}, callable(42)={callable(42)}")

    # Define a callback Protocol and a consumer function:
    # Define class ValidatorProtocol(Protocol): with
    # def __call__(self, value: str, *, strict: bool = False) -> bool: ...
    # Then write run_validation(items: list[str], validator: ValidatorProtocol, *, strict: bool = False) -> list[bool]
    # returning [validator(item, strict=strict) for item in items].


    # Satisfy ValidatorProtocol with a plain function (no inheritance):
    # Define is_non_empty(value: str, *, strict: bool = False) -> bool returning
    # bool(value.strip()) when strict is True, else bool(value).
    # Create samples = ["ok", "   ", ""] and print both
    # run_validation(samples, is_non_empty, strict=False) ([True, True, False])
    # and run_validation(samples, is_non_empty, strict=True) ([True, False, False]).


    # Satisfy the exact same ValidatorProtocol with a stateful callable class:
    # Define class MinLengthValidator: with __init__(self, min_len: int) -> None
    # and __call__(self, value: str, *, strict: bool = False) -> bool checking
    # len(value.strip() if strict else value) >= self.min_len.
    # Pass MinLengthValidator(3) into
    # run_validation(["hi", "   ", "odin"], MinLengthValidator(3), strict=True)
    # and print the result ([False, False, True]).


def typing_overload_and_literal_discrimination() -> None:

    # Sometimes a function's return type depends directly on an input flag or
    # argument type. Suppose parse_data(raw, as_bytes=False) returns str, while
    # parse_data(raw, as_bytes=True) returns bytes. Annotating -> str | bytes
    # forces every caller to write isinstance narrowing checks even when
    # passing a literal True or False!
    #
    # @typing.overload solves this by letting you place multiple type-checker
    # signatures above ONE real runtime implementation:
    # - Each @overload stub uses Literal[False] / Literal[True] (or distinct
    #   input types) and ends with ... as its body.
    # - The final def MUST NOT carry @overload! At runtime, Python executes
    #   each def in order so the final real implementation overwrites the
    #   earlier stubs in the namespace. Putting @overload on the real body
    #   causes calling the function to fail with NotImplementedError!

    mode: Literal["text", "bytes"] = "text"
    print(f"Starter Literal mode={mode!r}")

    # Write @overload declarations discriminated by Literal[False] / Literal[True]:
    # - @overload def parse_data(raw: str, *, as_bytes: Literal[False] = False) -> str: ...
    # - @overload def parse_data(raw: str, *, as_bytes: Literal[True]) -> bytes: ...
    # - Real runtime implementation (NO @overload decorator!):
    #   def parse_data(raw: str, *, as_bytes: bool = False) -> str | bytes:
    #   returning raw.encode("utf-8") when as_bytes is True, else raw.strip().


    # Call both @overload variants and inspect their runtime types:
    # Bind text_out = parse_data("  hello  ") (statically narrowed to str) and
    # byte_out = parse_data("hello", as_bytes=True) (statically narrowed to bytes).
    # Print text_out, type(text_out).__name__, byte_out, and type(byte_out).__name__.


    # Practice input-type @overload discrimination without a boolean flag:
    # Declare @overload def double_item(x: int) -> int: ... and
    # @overload def double_item(x: str) -> str: ... above ONE runtime function
    # def double_item(x: int | str) -> int | str: return x * 2.
    # Test double_item(21) (42) and double_item("ha") ("haha") and print both.


def main() -> None:

    print("=== 1. collections.abc.Callable annotations ===")
    callable_type_annotations()

    print("\n=== 2. Callback Protocols for keyword and default signatures ===")
    callback_protocols_for_rich_signatures()

    print("\n=== 3. @typing.overload and Literal return narrowing ===")
    typing_overload_and_literal_discrimination()


if __name__ == "__main__":
    main()
