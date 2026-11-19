# python 140_decorators_and_functools_wraps.py

from collections.abc import Callable
from functools import wraps
from typing import Any


def compute_tax(amount: float, rate: float = 0.08) -> float:
    """Return total amount with tax applied."""

    return round(amount * (1.0 + rate), 2)


def decorator_desugaring_and_metadata_loss() -> None:

    # A Python decorator is pure syntactic sugar executed ONCE at function
    # definition time (typically when a module is imported), NOT magic that
    # rewrites calls later:
    #
    #     @trace_calls
    #     def price(amount: float) -> float:
    #         return amount * 1.08
    #
    # is 100% identical to:
    #
    #     def price(amount: float) -> float:
    #         return amount * 1.08
    #     price = trace_calls(price)
    #
    # Whatever object trace_calls(price) returns replaces the name price in the
    # enclosing scope. That creates the #1 decorator trap: when a naive
    # decorator defines an inner def wrapper(*args, **kwargs): and returns
    # wrapper directly, wrapper silently overwrites the original function's
    # identity!
    #
    #     Suppose broken_tax = broken_trace(compute_tax).
    #     broken_tax.__name__ becomes "wrapper" instead of "compute_tax",
    #     broken_tax.__doc__ becomes None instead of compute_tax's docstring,
    #     broken_tax.__annotations__ becomes wrapper's annotations, and tools
    #     like help(), inspect.signature(), debuggers, and test runners lose
    #     track of the real function.

    print(
        f"Baseline compute_tax(100.0)={compute_tax(100.0)} | "
        f"name={compute_tax.__name__!r} | doc={compute_tax.__doc__!r}"
    )

    # Write a deliberately broken decorator WITHOUT @wraps to see the bug live:
    # Define broken_trace(fn: Callable[..., Any]) -> Callable[..., Any] with an
    # inner def wrapper(*args: Any, **kwargs: Any) -> Any: that prints
    # f"[broken] calling {fn.__name__}" and returns fn(*args, **kwargs).
    # Apply it to compute_tax manually: broken_tax = broken_trace(compute_tax)
    # and call broken_tax(100.0, rate=0.10).


    # Inspect the metadata damage side-by-side:
    # Print compute_tax.__name__, compute_tax.__doc__, and
    # hasattr(compute_tax, "__wrapped__") right next to broken_tax.__name__,
    # broken_tax.__doc__, and hasattr(broken_tax, "__wrapped__")—notice
    # broken_tax now reports "wrapper", None, and False!


    # Import inspect inside this function (import inspect) and compare
    # inspect.signature(compute_tax) against inspect.signature(broken_tax) to
    # watch the real (amount: float, rate: float = 0.08) -> float signature
    # collapse into (*args: Any, **kwargs: Any) -> Any.


def functools_wraps_and_unwrapped_calls() -> None:

    # Decorating the inner wrapper with @functools.wraps(fn) fixes every
    # metadata problem in one line:
    # - It copies __module__, __name__, __qualname__, __doc__, __annotations__,
    #   and __type_params__ from fn onto wrapper.
    # - It merges fn.__dict__ into wrapper.__dict__.
    # - Most importantly, it sets wrapper.__wrapped__ = fn, which lets
    #   inspect.signature() follow the chain back to fn's real parameters AND
    #   lets unit tests bypass the decorator completely by calling
    #   wrapped_fn.__wrapped__(...)!
    #
    #     Suppose traced_tax = trace_calls(compute_tax) using @wraps(fn).
    #     Calling traced_tax(100.0, rate=0.10) prints trace logs and returns 110.0.
    #     Calling traced_tax.__wrapped__(100.0, 0.08) skips tracing and returns 108.0.

    def passthrough(fn: Callable[..., Any]) -> Callable[..., Any]:

        @wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:

            return fn(*args, **kwargs)

        return wrapper

    sample_wrapped = passthrough(compute_tax)
    print(
        f"Starter @wraps check: name={sample_wrapped.__name__!r}, "
        f"unwrapped_same={sample_wrapped.__wrapped__ is compute_tax}"
    )

    # Write a proper metadata-preserving decorator:
    # Define trace_calls(fn: Callable[..., Any]) -> Callable[..., Any] with an
    # inner @wraps(fn) def wrapper(*args: Any, **kwargs: Any) -> Any: that:
    # - Prints f"[trace] calling {fn.__name__} args={args} kwargs={kwargs}"
    # - Calls result = fn(*args, **kwargs)
    # - Prints f"[trace] {fn.__name__} returned {result!r}"
    # - Returns result
    # Apply it to compute_tax via traced_tax = trace_calls(compute_tax) and
    # call traced_tax(100.0, rate=0.10).


    # Put the broken decorator and the fixed @wraps decorator side-by-side:
    # Write a quick broken_wrap(fn) without @wraps right alongside trace_calls,
    # wrap compute_tax with both, and print a side-by-side comparison of
    # __name__, __doc__, __annotations__, and inspect.signature(...) for
    # broken_tax vs traced_tax!


    # Bypass the decorator using __wrapped__:
    # Call raw_total = traced_tax.__wrapped__(100.0, 0.08) and print raw_total
    # (expected: 108.0 with zero [trace] lines printed).


def stacking_order_and_definition_timing() -> None:

    # When you stack two decorators on one function:
    #
    #     @outer_tag
    #     @inner_tag
    #     def greet(name: str) -> str:
    #         return f"Hello, {name}!"
    #
    # Python desugars that to greet = outer_tag(inner_tag(greet)).
    # That produces two opposite directions to keep straight:
    # - At DEFINITION time, decorators apply bottom-up: inner_tag wraps greet
    #   first, then outer_tag wraps inner_tag's wrapper.
    # - At CALL time, wrappers execute top-down: calling greet("Ada") enters
    #   outer_tag's wrapper first, which calls inner_tag's wrapper, which calls
    #   greet, and then returns unwind back through inner_tag and outer_tag.

    print("Starter: stacked decorators apply bottom-up and run top-down.")

    # Observe both definition-time and call-time ordering:
    # Define outer_tag(fn: Callable[..., Any]) -> Callable[..., Any] and
    # inner_tag(fn: Callable[..., Any]) -> Callable[..., Any], both using
    # @wraps(fn). Print "applying outer_tag" / "applying inner_tag" in the
    # decorator body (definition time), and print "enter outer_tag" /
    # "enter inner_tag" before calling fn and "exit outer_tag" / "exit inner_tag"
    # after calling fn inside each wrapper.
    # Stack @outer_tag above @inner_tag on def greet(name: str) -> str:
    # returning f"Hello, {name}!", then call print(greet("Ada")).


    # Follow a multi-layer __wrapped__ chain:
    # Import inspect and call inspect.unwrap(greet)("Grace") alongside
    # greet.__wrapped__.__wrapped__("Grace") to prove @wraps preserves the
    # full chain all the way down to the raw greet function.


    # Combine a validation decorator with logging:
    # Write require_positive(fn: Callable[[float], float]) -> Callable[[float], float]
    # using @wraps(fn) that raises ValueError("value must be > 0") when x <= 0
    # before calling fn(x). Decorate def half(x: float) -> float: return x / 2.0
    # with @require_positive and test half(10.0) (5.0) plus half(-2.0) inside
    # try / except ValueError:.


def main() -> None:

    print("=== 1. Decorator desugaring and metadata loss ===")
    decorator_desugaring_and_metadata_loss()

    print("\n=== 2. Preserving identity with @functools.wraps ===")
    functools_wraps_and_unwrapped_calls()

    print("\n=== 3. Decorator stacking order and definition timing ===")
    stacking_order_and_definition_timing()


if __name__ == "__main__":
    main()
