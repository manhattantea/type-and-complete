# python 720_typeddict_literal_newtype_and_typeguard.py

import sys
from typing import Literal, NewType, NotRequired, Required, TypedDict, TypeGuard

if sys.version_info >= (3, 13):
    from typing import ReadOnly, TypeIs


def newtype_and_literal_primitives() -> None:

    # Passing bare int IDs and open str statuses across function boundaries is
    # a quiet bug factory: swap user_id and order_id in a call and neither
    # Python nor a static checker notices until production data gets corrupted.
    #
    # Two lightweight tools from typing close those holes with zero runtime
    # wrapper cost:
    # - NewType("OrderId", int): Python's nominal distinct type (like Odin's
    #   distinct int). A static checker refuses to mix UserId, OrderId, and
    #   plain int. At runtime, NewType returns a tiny identity callable
    #   (essentially def new_type(x): return x), so OrderId(101) hands back the
    #   bare int 101 with zero extra object allocation. Because NewType is NOT
    #   a real class, calling isinstance(x, OrderId) raises TypeError!
    # - Literal["pending", "paid", "cancelled"]: locks a parameter or alias to
    #   a closed set of exact constant values instead of accepting any str.
    #
    #     Suppose UserId = NewType("UserId", int) and OrderId = NewType("OrderId", int).
    #     Calling OrderId(101) produces the plain int 101 (type is int), while
    #     passing UserId(42) where OrderId is expected fails static type checks.

    DemoTag = NewType("DemoTag", int)
    tag = DemoTag(1)
    print(f"Starter NewType tag = {tag!r} (runtime type: {type(tag).__name__})")

    # Define two nominal ID types:
    # UserId = NewType("UserId", int)
    # OrderId = NewType("OrderId", int)
    # Also define a closed status alias:
    # type OrderStatus = Literal["pending", "paid", "cancelled"]
    # Verify at runtime that OrderId(101) == 101 and type(OrderId(101)) is int.


    # Write def format_dispatch(order_id: OrderId, user_id: UserId, status: OrderStatus) -> str:
    # returning f"order={order_id} user={user_id} status={status}".
    # Call it with OrderId(101), UserId(42), and "paid", and print the string.


    # Confirm that NewType is a callable identity helper rather than a class:
    # Try uncommenting below to observe TypeError at runtime:
    # print(isinstance(OrderId(101), OrderId))
    # Try uncommenting below under a static checker to catch both swapped IDs
    # and an invalid Literal value:
    # format_dispatch(UserId(42), OrderId(101), "unknown")


def typeddict_required_notrequired_and_readonly() -> None:

    # When Python talks to JSON APIs or SQLite rows, data arrives as plain
    # dictionaries whose keys map to different value types. Wrapping every row
    # in a @dataclass can add allocation overhead, yet typing it as
    # dict[str, Any] throws away all key and type safety.
    #
    # TypedDict describes the exact key/value shape of an ordinary dict: at
    # runtime it creates a plain dict with zero wrapper class overhead. Use
    # TypedDict for JSON/wire shapes at system boundaries, and @dataclass for
    # internal domain entities that carry methods and invariants.
    #
    # Three modifiers let TypedDict express real-world schemas cleanly:
    # - NotRequired[T]: marks a key optional inside a default total=True
    #   TypedDict (where every other key is mandatory).
    # - total=False with Required[T]: flips the default so every key is
    #   optional EXCEPT keys wrapped in Required[T]—ideal for partial PATCH
    #   update payloads.
    # - ReadOnly[T] (PEP 705, added in Python 3.13 typing): prevents static
    #   code from reassigning that key (payload["order_id"] = ...) and makes
    #   read-only fields safe to read covariantly across narrower dicts.
    #
    #     Suppose class Patch(TypedDict, total=False):
    #         order_id: Required[int]
    #         coupon: str
    #     {"order_id": 101} is valid because coupon is optional, whereas
    #     {"coupon": "SAVE10"} fails static checks because order_id is Required.

    class BaseHeader(TypedDict):
        version: int
        source: NotRequired[str]

    sample_header: BaseHeader = {"version": 1}
    print("Starter TypedDict is plain dict:", type(sample_header) is dict, sample_header)

    # Define OrderId = NewType("OrderId", int) and
    # type OrderStatus = Literal["pending", "paid", "cancelled"].
    # Define class OrderPayload(TypedDict): with fields:
    # - order_id: ReadOnly[OrderId] (on Python 3.13+; use plain OrderId on 3.12)
    # - customer: str
    # - status: OrderStatus
    # - coupon: NotRequired[str]
    # Write def summarize_order(payload: OrderPayload) -> str: reading
    # payload.get("coupon", "none") safely, and test it on an order without a
    # coupon and an order with coupon="SPRING15".


    # Define a partial update shape using total=False plus Required:
    # class OrderPatch(TypedDict, total=False):
    # with order_id: Required[OrderId], status: OrderStatus, and coupon: str.
    # Write def apply_patch(order: OrderPayload, patch: OrderPatch) -> OrderPayload:
    # that copies dict(order), updates it with patch, and returns the updated
    # mapping. Test patching only status="cancelled" on an existing order.


    # Remember that ReadOnly is enforced statically while Python's runtime dict
    # stays mutable. Try uncommenting an assignment like
    # order["order_id"] = OrderId(999) under mypy or pyright to see ReadOnly
    # block accidental key mutation.


def narrowing_with_typeguard_and_typeis() -> None:

    # Built-in isinstance(x, str) narrows types automatically, but it cannot
    # inspect every element inside a container like list[object]. Writing a
    # boolean helper annotated with TypeGuard[T] or Python 3.13's TypeIs[T]
    # (PEP 742) teaches static checkers how your predicate narrows a value.
    #
    # Watch the crucial difference between TypeGuard[T] and TypeIs[T]:
    #
    #     Suppose token: int | str and you check if pred(token): ... else: ...
    #     - With -> TypeGuard[str]: the static checker narrows the if branch to
    #       str, but leaves the else branch un-narrowed as int | str! That is
    #       intentional when False does not exclude T (for instance, an empty
    #       list[str] fails is_non_empty_str_list yet is still a list[str]).
    #     - With -> TypeIs[str] (Python 3.13+): behaves like isinstance(),
    #       narrowing BOTH the if branch (to str) AND the else branch (by
    #       subtracting str, leaving strictly int)!
    #
    # Always remember: static checkers trust your predicate's return annotation
    # blindly—writing the real runtime checks inside the body is up to you.

    print("Starter check: Python 3.13+ TypeIs available =", sys.version_info >= (3, 13))

    # Write def is_non_empty_str_list(val: list[object]) -> TypeGuard[list[str]]:
    # returning bool(val) and all(isinstance(item, str) for item in val).
    # Test it on mixed_a: list[object] = ["alpha", "beta"],
    # mixed_b: list[object] = ["alpha", 99], and empty: list[object] = [].
    # Inside if is_non_empty_str_list(items): print [s.upper() for s in items].


    # Practice Python 3.13 TypeIs narrowing (using TypeIs[str] on 3.13+ or
    # TypeGuard[str] on 3.12):
    # Write def is_str_token(val: int | str) -> TypeIs[str]: returning
    # isinstance(val, str). Loop over tokens: list[int | str] = ["ok", 42]:
    # in the if branch print token.upper(); in the else branch print token + 1.
    # Notice why TypeIs[str] lets the else branch treat token as int cleanly,
    # whereas TypeGuard[str] would leave token as int | str in else.


    # Write def is_score_map(raw: object) -> TypeGuard[dict[str, int]]:
    # verifying isinstance(raw, dict) and that every key is str and every value
    # satisfies type(v) is int (excluding bool, which subclasses int).
    # Test it on {"a": 1, "b": 2} and {"a": True} and print which passes.


def main() -> None:

    print("=== 1. NewType and Literal primitives ===")
    newtype_and_literal_primitives()

    print("\n=== 2. TypedDict with Required, NotRequired, and ReadOnly ===")
    typeddict_required_notrequired_and_readonly()

    print("\n=== 3. Narrowing with TypeGuard and TypeIs ===")
    narrowing_with_typeguard_and_typeis()


if __name__ == "__main__":
    main()
