# python 160_functools_lru_cache_partial_and_singledispatch.py

from functools import cache, lru_cache, partial, reduce, singledispatch


def memoization_cache_and_lru_traps() -> None:

    # The functools module ships two C-backed memoization decorators for pure
    # functions (functions whose return value depends solely on their inputs):
    # - @functools.cache is shorthand for @lru_cache(maxsize=None): an
    #   unbounded dict cache that is fast for finite dynamic programming, but
    #   can leak memory in a long-running server if distinct inputs grow forever.
    # - @functools.lru_cache(maxsize=128, typed=False) bounds memory by
    #   evicting least-recently-used entries in O(1) time via an internal
    #   dictionary plus doubly-linked list.
    #
    # Inspect hits, misses, and current entries via fn.cache_info(), and wipe
    # the table via fn.cache_clear(). Watch out for three classic cache traps:
    # - All arguments must be hashable: passing a list, dict, or set raises
    #   TypeError: unhashable type (convert to tuple or frozenset first).
    # - Call keys distinguish positional vs keyword args (fn(1) vs fn(x=1)),
    #   and setting typed=True caches int 3 and float 3.0 separately.
    # - Never mutate a cached return object! A cache hit returns the exact same
    #   PyObject reference:
    #
    #     Suppose @cache def get_roles() -> list[str]: return ["viewer"]
    #     a = get_roles(); a.append("admin")
    #     b = get_roles()  # returns ["viewer", "admin"]—every caller is corrupted!

    @cache
    def cached_square(n: int) -> int:

        return n * n

    first = cached_square(7)
    second = cached_square(7)
    print(f"Starter @cache: {first}, {second} | {cached_square.cache_info()}")

    # Write memoized dynamic programming with @lru_cache(maxsize=64):
    # Define count_ways(steps: int) -> int counting how many ways to climb
    # steps stairs taking 1 or 2 steps at a time:
    # - Raise ValueError("steps must be >= 0") if steps < 0.
    # - Return 1 if steps <= 1.
    # - Otherwise return count_ways(steps - 1) + count_ways(steps - 2).
    # Call ways = count_ways(30) (expected: 1346269), print ways and
    # count_ways.cache_info(), then call count_ways.cache_clear() and print
    # count_ways.cache_info() again to verify hits == 0 and currsize == 0.


    # Test the hashable-argument rule and typed=True key separation:
    # - Define @cache def sum_tuple(nums: tuple[int, ...]) -> int: return sum(nums)
    #   and print sum_tuple((1, 2, 3)) (6).
    # - Define @lru_cache(maxsize=8, typed=True) def echo(x: int | float) -> int | float:
    #   returning x. Call echo(3) and echo(3.0) and print echo.cache_info() to
    #   confirm typed=True stored them as two separate misses.
    #
    # Try uncommenting below after defining sum_tuple to observe TypeError:
    # print(sum_tuple([1, 2, 3]))


    # Reproduce the mutated-cached-return bug and fix it cleanly:
    # Define @cache def buggy_roles() -> list[str]: return ["viewer"].
    # Call r1 = buggy_roles(), call r1.append("admin"), then call r2 = buggy_roles()
    # and print r2 and r1 is r2 (True—the cache itself was mutated!).
    # Then write @cache def safe_roles() -> tuple[str, ...]: return ("viewer",)
    # so callers receive an immutable tuple that cannot poison the cache.


def partial_application_and_reduce() -> None:

    # functools.partial(fn, *bound_args, **bound_kwargs) freezes a subset of
    # positional and/or keyword arguments into a lightweight callable exposing
    # .func, .args, and .keywords. Unlike a loop lambda, partial captures its
    # arguments eagerly at creation time.
    #
    # functools.reduce(fn, iterable, initializer) folds an iterable left-to-right
    # into one accumulated value:
    #
    #     Suppose layers = [{"a": 1}, {"b": 2}].
    #     reduce(lambda acc, item: acc | item, layers, {}) evaluates
    #     (({} | {"a": 1}) | {"b": 2}) and returns {"a": 1, "b": 2}.
    #
    # Prefer dedicated built-ins (sum, min, max, any, all, math.prod) when they
    # fit; reach for reduce when folding custom merges or transform pipelines,
    # and pass an initializer so empty iterables do not raise TypeError.

    parse_hex = partial(int, base=16)
    print(f"Starter partial(int, base=16)('ff') = {parse_hex('ff')}")

    # Freeze options with functools.partial and inspect its attributes:
    # Define scale_and_offset(value: float, factor: float, offset: float = 0.0) -> float
    # returning value * factor + offset.
    # Create c_to_f = partial(scale_and_offset, factor=1.8, offset=32.0) and
    # double = partial(scale_and_offset, factor=2.0).
    # Print c_to_f(100.0) (212.0), double(7.5) (15.0), and inspect
    # c_to_f.func.__name__, c_to_f.args, and c_to_f.keywords.


    # Merge layered configuration dicts with functools.reduce:
    # Bind layers = [{"host": "localhost", "port": 8000}, {"port": 9000}, {"tls": True}].
    # Use reduce(lambda acc, layer: acc | layer, layers, {}) to fold them into
    # one merged dict and print the result (port should become 9000).
    # Also test the exact same reduce expression on [] to verify the {}
    # initializer prevents TypeError.


    # Apply a sequence of string transforms with reduce:
    # Create steps = [str.strip, str.lower, lambda s: s.replace(" ", "_")]
    # and run reduce(lambda val, fn: fn(val), steps, "  Hello World  ").
    # Print the result (expected: "hello_world").


def singledispatch_type_overloading() -> None:

    # Unlike C++ or Odin, Python does not support compile-time overloading by
    # parameter type in the same namespace—writing a second def serialize(...)
    # simply overwrites the first!
    #
    # @functools.singledispatch turns a function into a generic dispatcher that
    # routes calls based on the runtime type (MRO) of its FIRST positional
    # argument. Each @fn.register handler reads its target type straight from
    # the first parameter's type annotation (including int | float unions in
    # Python 3.11+!), and you can name every registered handler _ so you do not
    # clutter the module namespace:
    #
    #     @singledispatch
    #     def show(val: object) -> str:
    #         return f"fallback({val!r})"
    #     @show.register
    #     def _(val: int) -> str:
    #         return f"int:{val}"
    #     Calling show(5) dispatches to the int handler and returns "int:5".

    @singledispatch
    def describe(val: object) -> str:

        return f"generic:{type(val).__name__}"

    print(f"Starter @singledispatch fallback: {describe('hello')}")

    # Build a recursive @singledispatch serializer:
    # Define @singledispatch def serialize(val: object) -> str: returning
    # f"object({val!r})" as the fallback.
    # Register three handlers with @serialize.register:
    # - _ taking val: int -> return f"int:{val}"
    # - _ taking val: float -> return f"float:{val:.2f}"
    # - _ taking val: list -> recursively serialize every item and return
    #   "[" + ", ".join(serialize(item) for item in val) + "]"
    # Call and print serialize(42), serialize(3.14159), serialize([1, 2.5, "hi"]),
    # and serialize("raw").


    # Inspect MRO-based dispatch lookup:
    # Print serialize.dispatch(float) and serialize.dispatch(bool). Notice bool
    # is a subclass of int in Python, so serialize(True) routes to the int
    # handler unless you explicitly register a bool handler! Register a bool
    # handler returning "bool:true" / "bool:false" and re-test serialize(True).


    # Register a Python 3.11+ union type handler:
    # Add @serialize.register for _ taking val: tuple | set returning
    # f"seq({len(val)})". Test serialize((1, 2, 3)) and serialize({"a", "b"}).


def main() -> None:

    print("=== 1. Memoization with @cache and @lru_cache ===")
    memoization_cache_and_lru_traps()

    print("\n=== 2. functools.partial and functools.reduce ===")
    partial_application_and_reduce()

    print("\n=== 3. Type-based overloading with @singledispatch ===")
    singledispatch_type_overloading()


if __name__ == "__main__":
    main()
