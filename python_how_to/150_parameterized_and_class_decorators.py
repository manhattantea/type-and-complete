# python 150_parameterized_and_class_decorators.py

from collections.abc import Callable
from functools import partial, update_wrapper, wraps
from typing import Any

COMMAND_REGISTRY: dict[str, type[Any]] = {}


def three_layer_decorator_factories() -> None:

    # Once you read @deco as fn = deco(fn), parameterized decorators like
    # @retry(max_attempts=3) explain themselves—and show why they need three
    # nested function layers:
    #
    # Python evaluates the expression after @ BEFORE touching the target def.
    # Writing @retry(max_attempts=3) first calls retry(max_attempts=3). That
    # call must return a single-argument decorator function, which Python
    # immediately calls with your target fn, which in turn returns wrapper:
    #
    #     def retry(max_attempts: int = 3):        # layer 1: config factory
    #         def decorator(fn):                   # layer 2: actual decorator
    #             @wraps(fn)
    #             def wrapper(*args, **kwargs):    # layer 3: call-time wrapper
    #                 return fn(*args, **kwargs)
    #             return wrapper
    #         return decorator
    #
    # Validate configuration eagerly in layer 1 (for example, checking
    # if max_attempts < 1: raise ValueError(...)) so bad arguments fail right
    # when the function is decorated rather than silently waiting for a call!

    def prefix_output(prefix: str) -> Callable[[Callable[..., str]], Callable[..., str]]:

        def decorator(fn: Callable[..., str]) -> Callable[..., str]:

            @wraps(fn)
            def wrapper(*args: Any, **kwargs: Any) -> str:

                return f"{prefix}{fn(*args, **kwargs)}"

            return wrapper

        return decorator

    @prefix_output("[ok] ")
    def starter_status() -> str:

        return "ready"

    print(f"Starter 3-layer factory: {starter_status()} (name={starter_status.__name__!r})")

    # Write a 3-layer retry decorator factory:
    # Define retry(max_attempts: int = 3) -> Callable[[Callable[..., Any]], Callable[..., Any]].
    # Immediately raise ValueError("max_attempts must be >= 1") if max_attempts < 1.
    # Inside decorator(fn), define @wraps(fn) wrapper(*args, **kwargs) that
    # loops up to max_attempts times trying fn(*args, **kwargs), catching
    # ValueError on failed attempts and re-raising on the final attempt.


    # Test @retry(max_attempts=3) on a flaky function:
    # Track attempts = 0 in this scope and decorate flaky_parse() -> str with
    # @retry(max_attempts=3). Inside flaky_parse, use nonlocal attempts to
    # increment attempts by 1, raise ValueError("transient error") while
    # attempts < 3, and return "parsed ok" on attempt 3.
    # Print flaky_parse() and verify it succeeds on the third attempt; also
    # test a second flaky function decorated with @retry(max_attempts=2) inside
    # try / except ValueError: to prove the final error propagates!


    # Prove fail-fast validation in layer 1:
    # Wrap retry(max_attempts=0) inside try / except ValueError as exc: and
    # print exc to confirm invalid configuration fails immediately at
    # decoration time before any target function is even passed in.


def dual_mode_decorators_with_partial() -> None:

    # Standard-library and framework decorators often work in BOTH forms:
    # bare (@tag) AND configured with options (@tag(category="math")).
    # Look at the difference in what Python passes to tag:
    # - @tag calls tag(target_fn), so the first argument is a callable.
    # - @tag(category="math") calls tag(category="math"), so fn stays None!
    #
    # By giving fn a default of None and forcing all configuration parameters
    # after * (keyword-only), one guard handles both modes cleanly:
    #
    #     def tag(fn: Callable[..., Any] | None = None, *, category: str = "general") -> Any:
    #         if fn is None:
    #             return partial(tag, category=category)
    #         @wraps(fn)
    #         def wrapper(*args: Any, **kwargs: Any) -> Any:
    #             return fn(*args, **kwargs)
    #         return wrapper
    #
    # Notice what functools.partial(tag, category=category) does: it returns a
    # new 1-argument callable with category already frozen, which Python then
    # calls with the decorated function—entering tag a second time with fn set!

    round_two = partial(round, ndigits=2)
    print(f"Starter partial freeze: round_two(3.14159) = {round_two(3.14159)}")

    # Implement the dual-mode @tag decorator:
    # Define tag(fn: Callable[..., Any] | None = None, *, category: str = "general") -> Any.
    # When fn is None, return partial(tag, category=category).
    # Otherwise define @wraps(fn) wrapper(*args: Any, **kwargs: Any) -> Any
    # returning fn(*args, **kwargs), set wrapper.category = category (functions
    # have a __dict__ so custom attributes attach directly), and return wrapper.


    # Test both bare and configured forms side by side:
    # - Decorate def ping() -> str: return "pong" with bare @tag.
    # - Decorate def cube(x: int) -> int: return x ** 3 with @tag(category="math").
    # Call both and print (ping.__name__, ping.category) alongside
    # (cube.__name__, cube.category) to confirm metadata and categories work
    # identically in both modes.


    # Verify the empty-parentheses edge case:
    # Decorate def health() -> str: return "ok" with @tag() (no keyword args)
    # and assert health.category == "general" and health.__name__ == "health".


def stateful_class_decorators_and_class_registries() -> None:

    # The phrase "class decorator" covers two distinct patterns in Python:
    #
    # - Callable class AS a decorator: when a decorator tracks mutable state
    #   (call counts, rate limits, metrics), a class implementing __init__ and
    #   __call__ is often cleaner than nested nonlocal variables. Because a
    #   class instance does not automatically copy __name__ or __doc__ from fn,
    #   call functools.update_wrapper(self, fn) inside __init__ to copy
    #   metadata and set self.__wrapped__ = fn.
    # - Decorator applied TO a class: @register_command above class PingCommand:
    #   desugars to PingCommand = register_command(PingCommand). The decorator
    #   receives the newly created type object at class-definition time, can
    #   record it in a registry dict or attach attributes, and returns the class.
    #
    #     Suppose COMMAND_REGISTRY = {} and @register_command decorates PingCommand.
    #     COMMAND_REGISTRY["PingCommand"] immediately holds PingCommand before
    #     a single instance is ever created!

    print(f"Starter COMMAND_REGISTRY before registration: {COMMAND_REGISTRY}")

    # Build a stateful callable class decorator:
    # Define class CallCounter: with:
    # - __init__(self, fn: Callable[..., Any]) -> None saving self.fn = fn,
    #   self.calls: int = 0, and calling update_wrapper(self, fn).
    # - __call__(self, *args: Any, **kwargs: Any) -> Any incrementing
    #   self.calls += 1 and returning self.fn(*args, **kwargs).
    # Decorate def add_one(x: int) -> int: return x + 1 with @CallCounter, call
    # it three times, and print add_one.__name__, add_one.calls (3), and
    # add_one.__wrapped__(10) (11 without incrementing add_one.calls).


    # Build a class-level registry decorator:
    # Define register_command(cls: type[Any]) -> type[Any] storing
    # COMMAND_REGISTRY[cls.__name__] = cls and returning cls.
    # Decorate two tiny classes PingCommand and StatusCommand (each with a
    # simple method like run(self) -> str) with @register_command, then print
    # COMMAND_REGISTRY to see both registered at class-definition time.


    # Combine a parameterized factory with a class decorator:
    # Write register_as(alias: str) -> Callable[[type[Any]], type[Any]] that
    # stores COMMAND_REGISTRY[alias] = cls, sets cls.command_alias = alias, and
    # returns cls. Decorate a small HealthCommand class with @register_as("health"),
    # look it up via COMMAND_REGISTRY["health"], instantiate it, and print its
    # command_alias.


def main() -> None:

    print("=== 1. Three-layer parameterized decorator factories ===")
    three_layer_decorator_factories()

    print("\n=== 2. Dual-mode decorators with functools.partial ===")
    dual_mode_decorators_with_partial()

    print("\n=== 3. Stateful class decorators and class registries ===")
    stateful_class_decorators_and_class_registries()


if __name__ == "__main__":
    main()
