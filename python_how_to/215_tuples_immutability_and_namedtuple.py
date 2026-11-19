# python 215_tuples_immutability_and_namedtuple.py

from typing import NamedTuple


class Point(NamedTuple):
    x: int
    y: int


def tuple_syntax_and_unpacking() -> None:

    # Python lists are usually homogeneous sequences of changing length, while
    # tuples are fixed-length heterogeneous records whose positions carry
    # meaning (like (host, port) or (x, y)). Because a tuple never grows,
    # CPython allocates one compact fixed-size block without over-allocation
    # headroom.
    #
    # One classic syntax surprise catches almost everyone once: parentheses
    # alone only group expressions, so (42) evaluates to the plain int 42, NOT
    # a tuple! It is the COMMA that builds a tuple:
    # - () is an empty tuple (the one special case without a comma).
    # - (42,) or 42, is a 1-element tuple.
    # - (1, 2) or 1, 2 is a 2-element tuple.
    #
    #     Suppose you write port = (8080) by mistake.
    #     type(port) is int, so iterating over port raises TypeError.
    #     Writing port = (8080,) makes type(port) tuple with len(port) == 1.

    pair: tuple[str, int] = ("localhost", 8080)
    host, port = pair
    print("Starter unpacked record:", host, port)

    # Test the 1-element tuple comma rule directly:
    # bind not_a_tuple = (42), single_tuple = (42,), and empty_tuple: tuple[()] = ().
    # Print each value alongside type(not_a_tuple), type(single_tuple), and
    # len(empty_tuple).


    # Practice tuple packing, unpacking, and starred catch-all unpacking:
    # create response: tuple[int, str, str, str] = (200, "OK", "text/plain", "hello").
    # Unpack status, reason, *body_parts = response and print status, reason,
    # and body_parts (notice *body_parts always produces a list!).


    # Swap two variables without a temporary variable using tuple packing:
    # bind left = "first" and right = "second", execute left, right = right, left,
    # and print left and right.


def shallow_immutability_and_iadd_puzzle() -> None:

    # What does "tuple immutability" actually freeze in memory?
    # A tuple locks its fixed C array of PyObject pointers so NO slot can ever
    # be rebound to a different object (t[0] = 99 always raises TypeError).
    # It does NOT recursively freeze the objects those pointers refer to!
    #
    # If a tuple holds a mutable list, calling t[1].append(30) mutates the list
    # object on the heap without touching the tuple's pointer array, so it
    # succeeds silently.
    #
    # Even stranger is Python's most famous bytecode puzzle: t[1] += [30].
    # Python executes augmented assignment in three steps:
    # - Step A: load the list reference from t[1].
    # - Step B: call list.__iadd__([30]), which mutates the list IN PLACE and
    #   returns that same list object.
    # - Step C: attempt to store the result back into t[1] = result, which
    #   raises TypeError because tuple does not support item assignment!
    #
    #     Suppose t = (1, [10, 20]) and you run t[1] += [30].
    #     The statement raises TypeError, YET t is now (1, [10, 20, 30])!
    #     Rule of thumb: avoid putting mutable containers inside tuples unless
    #     you explicitly need a fixed wrapper around live state.

    boxed: tuple[str, list[int]] = ("scores", [10, 20])
    boxed[1].append(30)
    print("Starter mutated list inside tuple:", boxed)

    # Reproduce the famous tuple += bytecode puzzle:
    # create record: tuple[str, list[str]] = ("user_1", ["read", "write"]).
    # Wrap record[1] += ["admin"] inside try: / except TypeError as exc:
    # printing the caught error message, then print record afterward to prove
    # "admin" was appended even though TypeError was raised!


    # Confirm that rebinding a tuple slot directly fails before any mutation:
    # try uncommenting the line below to observe TypeError:
    # record[0] = "user_2"


def hashability_of_tuples() -> None:

    # A tuple is hashable (valid as a dict key or set member) ONLY when every
    # element inside it is also hashable.
    # - (10, 20) contains two ints, so hash((10, 20)) succeeds and (10, 20) can
    #   key a grid dictionary.
    # - (10, [20, 30]) contains a mutable list, so hash((10, [20, 30])) raises
    #   TypeError: unhashable type: 'list'.
    #
    #     Suppose coords = {(0, 0): "origin", (1, 2): "camp"}.
    #     Looking up coords[(1, 2)] hashes the tuple in O(1) and finds "camp".

    grid: dict[tuple[int, int], str] = {(0, 0): "origin"}
    print("Starter tuple key lookup:", grid[(0, 0)], "hash:", hash((0, 0)))

    # Use tuples as composite dictionary keys:
    # create routes: dict[tuple[str, int], str] mapping ("127.0.0.1", 80) to
    # "http" and ("127.0.0.1", 443) to "https". Look up ("127.0.0.1", 443) and
    # print the result alongside hash(("127.0.0.1", 443)).


    # Prove that a tuple containing a mutable list is NOT hashable:
    # bind unhashable_pair = ("key", [1, 2]), wrap hash(unhashable_pair) inside
    # try: / except TypeError as exc:, and print exc.


def namedtuple_records() -> None:

    # Positional tuples like color[2] get cryptic fast when a record grows past
    # two or three fields. typing.NamedTuple subclasses tuple directly so you
    # keep positional indexing, unpacking, hashability, and zero per-instance
    # __dict__ memory overhead while gaining named attributes, type annotations,
    # default values, and handy immutable record helpers:
    # - instance._fields returns a tuple of field names.
    # - instance._replace(field=value) returns a brand-new NamedTuple copy with
    #   only the specified fields changed (the leading underscore avoids
    #   colliding with user field names like replace or fields).
    # - instance._asdict() returns a plain dict mapping field names to values.
    #
    #     Suppose p = Point(3, 4).
    #     p.x is 3, p[0] is also 3, and p._replace(y=10) returns Point(x=3, y=10)
    #     without mutating p.

    origin = Point(3, 4)
    print("Starter NamedTuple:", origin, "moved:", origin._replace(y=10))

    # Define class Color(NamedTuple): (right here or at module scope) with
    # fields r: int, g: int, b: int, and a: int = 255.
    # Instantiate sky = Color(135, 206, 235), unpack r, g, b, a = sky, build a
    # translucent variant faded = sky._replace(a=128), and print sky,
    # (r, g, b, a), faded, faded._asdict(), and Color._fields.


    # Verify that Color truly inherits tuple behavior:
    # check isinstance(sky, tuple) (True), place sky and faded into a
    # palette: set[Color] = {sky, faded}, and print palette and sky[0] == sky.r.
    #
    # Try uncommenting below to confirm NamedTuple fields are read-only:
    # sky.a = 0


def main() -> None:

    print("=== 1. Tuple syntax and unpacking ===")
    tuple_syntax_and_unpacking()

    print("\n=== 2. Shallow immutability and the += puzzle ===")
    shallow_immutability_and_iadd_puzzle()

    print("\n=== 3. Hashability of tuples ===")
    hashability_of_tuples()

    print("\n=== 4. Typed immutable records with NamedTuple ===")
    namedtuple_records()


if __name__ == "__main__":
    main()
