# python 230_hashability_and_equality_contracts.py


def hash_table_lookup_and_numeric_collision() -> None:

    # When you insert or look up a key in a Python dict or set, CPython runs a
    # strict two-step lookup protocol:
    # - First, compute h = hash(key) and probe bucket slot h & mask (perturbing
    #   to another slot whenever a different key already occupies that bucket).
    # - Second, compare the candidate entry against key using an identity
    #   shortcut (existing is key) or value equality (existing == key).
    #
    # One ironclad invariant follows directly from that two-step protocol:
    # whenever a == b is True, hash(a) == hash(b) MUST also be True!
    # If two equal objects returned different hashes, a lookup for b would land
    # in the wrong bucket and miss a completely. (The reverse is NOT required:
    # two unequal objects are allowed to share a hash—that is just a normal
    # hash collision resolved by ==.)
    #
    # Because bool is a subclass of int and Python compares numbers by numeric
    # value across types, 1 == True == 1.0 is True, so Python guarantees
    # hash(1) == hash(True) == hash(1.0) == 1. That causes one of Python's
    # most famous dictionary puzzles:
    #
    #     Suppose d = {1: "int", True: "bool", 1.0: "float"}.
    #     Python inserts key 1 with value "int". When True arrives, hash(True)
    #     matches and True == 1 is True, so Python KEEPS the original key 1 and
    #     overwrites its value with "bool". Then 1.0 overwrites it with "float",
    #     leaving {1: "float"} with len(d) == 1!

    print("Starter numeric hashes:", hash(1), hash(True), hash(1.0))

    # Reproduce the numeric key-collision puzzle directly:
    # construct weird_dict: dict[object, str] = {1: "int", True: "bool", 1.0: "float"}.
    # Print weird_dict, len(weird_dict), and the type of the single stored key
    # type(next(iter(weird_dict))) to prove the FIRST inserted key object won.


    # Repeat the puzzle with 0, False, and 0.0 inside a set:
    # create weird_set: set[object] = {False, 0, 0.0} and print weird_set and
    # len(weird_set) to verify only the first inserted representative stays.


def hashable_vs_unhashable_builtins() -> None:

    # An object is hashable in Python if it has a hash value that never changes
    # during its lifetime (__hash__) and can be compared for equality (__eq__).
    # - Immutable built-ins (int, float, str, bytes, frozenset, None) are
    #   hashable.
    # - Mutable built-in containers (list, dict, set, bytearray) set
    #   __hash__ = None so hash(x) raises TypeError immediately.
    # - A tuple is hashable if and only if ALL of its elements are hashable.
    #
    #     Suppose key_ok = (1, "a", frozenset({2})) -> hash(key_ok) succeeds.
    #     Suppose key_bad = (1, [2, 3]) -> hash(key_bad) raises TypeError.

    print("Starter immutable tuple hash:", hash((1, "a", frozenset({2}))))

    # Probe hashability across several built-in containers:
    # loop over candidates: list[object] = [42, "hi", (1, 2), frozenset({1}), [1, 2], {"a": 1}, (1, [2])].
    # Inside a try: / except TypeError: block, attempt hash(item) and print
    # whether each item is hashable or unhashable.


def custom_eq_and_hash_contract() -> None:

    # By default, a user-defined class inherits object.__eq__ (identity: is)
    # and object.__hash__ (derived from object identity), so fresh instances
    # are hashable by identity.
    #
    # The moment you define a custom __eq__ method on your class WITHOUT also
    # defining __hash__, Python automatically sets __hash__ = None! Why?
    # Because two distinct instances with equal fields would have a == b True
    # while inheriting identity-based hashes would give hash(a) != hash(b),
    # silently breaking every dict and set!
    #
    # To make a value-equality class safely hashable:
    # - Implement __eq__(self, other: object) -> bool returning NotImplemented
    #   when isinstance(other, MyClass) is False.
    # - Implement __hash__(self) -> int returning hash((self.x, self.y)) over
    #   the exact same fields compared in __eq__.
    # - Keep those fields immutable (for example via read-only properties or
    #   @dataclass(frozen=True), covered in Primer 360).

    class EqOnlyPoint:
        def __init__(self, x: int) -> None:

            self.x = x

        def __eq__(self, other: object) -> bool:

            if not isinstance(other, EqOnlyPoint):
                return NotImplemented
            return self.x == other.x

    print("Starter EqOnlyPoint.__hash__ is disabled:", EqOnlyPoint.__hash__)

    # Confirm that defining __eq__ without __hash__ prevents set/dict insertion:
    # create p = EqOnlyPoint(5), wrap {p} inside try: / except TypeError as exc:,
    # and print exc to observe TypeError: unhashable type: 'EqOnlyPoint'.


    # Build a properly hashable GridCoord class right here:
    # define class GridCoord: with:
    # - __init__(self, x: int, y: int) -> None storing self.x and self.y
    # - __eq__(self, other: object) -> bool returning NotImplemented if not
    #   isinstance(other, GridCoord), otherwise (self.x, self.y) == (other.x, other.y)
    # - __hash__(self) -> int returning hash((self.x, self.y))
    # - __repr__(self) -> str returning f"GridCoord({self.x}, {self.y})"
    # Instantiate origin = GridCoord(0, 0) and same_origin = GridCoord(0, 0),
    # verify origin is not same_origin and origin == same_origin, put origin
    # into visited: set[GridCoord] = {origin} and labels: dict[GridCoord, str] = {origin: "start"},
    # and verify same_origin in visited (True) and labels[same_origin] ("start").


def mutable_key_corruption_trap() -> None:

    # What actually goes wrong if you DO implement __hash__ on a class whose
    # fields can still be mutated after insertion?
    #
    #     Suppose origin = GridCoord(0, 0) is placed in visited = {origin}.
    #     Python stores origin in the bucket for hash((0, 0)).
    #     Now suppose you mutate origin.x = 99!
    #     origin is STILL sitting in the old bucket for hash((0, 0)), while
    #     checking origin in visited probes the NEW bucket for hash((99, 0))!
    #     So origin in visited returns False EVEN THOUGH origin is visibly
    #     inside list(visited)!
    #
    # Never mutate attributes that participate in __hash__ after an object has
    # been placed in a dict or set. In real code, lock fields with
    # @dataclass(frozen=True) or store them behind read-only @property getters.

    print("Ready to prove why mutable hash keys strand objects in old buckets.")

    # Reproduce the stranded-key corruption bug using a small MutableCoord
    # class (with mutable self.x, self.y, __eq__, __hash__, and __repr__):
    # create c = MutableCoord(1, 2) and put it in bag: set[MutableCoord] = {c}.
    # Print c in bag BEFORE mutation (True).
    # Now mutate c.x = 99 and print list(bag), c in bag (False!), and
    # MutableCoord(99, 2) in bag (False!) to see the corrupted hash bucket live.


def main() -> None:

    print("=== 1. Hash table lookup and numeric collision ===")
    hash_table_lookup_and_numeric_collision()

    print("\n=== 2. Hashable vs. unhashable built-ins ===")
    hashable_vs_unhashable_builtins()

    print("\n=== 3. Custom __eq__ and __hash__ contract ===")
    custom_eq_and_hash_contract()

    print("\n=== 4. Mutable key corruption trap ===")
    mutable_key_corruption_trap()


if __name__ == "__main__":
    main()
