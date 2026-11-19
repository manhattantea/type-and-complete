# python 340_dunder_repr_format_and_comparisons.py

from functools import total_ordering


def repr_str_and_custom_format() -> None:

    # Python connects core syntax—repr(), print(), f"{v:spec}", ==, and <—to
    # your custom classes through special double-underscore ("dunder") methods.
    # For speed and predictability, CPython looks these hooks up directly on
    # type(obj), not inside obj.__dict__.
    #
    # Three display dunders cover almost every formatting need:
    # - __repr__(self) -> str is the unambiguous developer representation,
    #   ideally valid Python like Version(1, 2, 0). Containers ALWAYS call
    #   __repr__: print([v]) prints v.__repr__() even if print(v) calls __str__!
    # - __str__(self) -> str is human-friendly output used by print(v) and
    #   f"{v}". If you omit __str__, Python falls back to __repr__. If you omit
    #   __repr__, you get an unhelpful <... object at 0x...>. Always write
    #   __repr__ first!
    # - __format__(self, format_spec: str) -> str runs for f"{obj:spec}" and
    #   format(obj, "spec"). When no :spec is given, format_spec is "", which
    #   conventionally returns str(self).
    #
    #     Suppose v = DisplayVersion(1, 2, 0):
    #         str(v)        -> "1.2.0"
    #         repr(v)       -> "DisplayVersion(1, 2, 0)"
    #         str([v])      -> "[DisplayVersion(1, 2, 0)]"
    #         f"{v:short}"  -> "1.2"

    sample = "hi"
    print("Built-in str vs repr:", str(sample), "|", repr(sample))

    # Define class DisplayVersion: with
    # def __init__(self, major: int, minor: int, patch: int = 0) -> None:
    # storing self.major, self.minor, self.patch, plus:
    # - def __repr__(self) -> str: returning
    #   f"DisplayVersion({self.major}, {self.minor}, {self.patch})"
    # - def __str__(self) -> str: returning
    #   f"{self.major}.{self.minor}.{self.patch}"
    # - def __format__(self, format_spec: str) -> str: supporting "short"
    #   (f"{self.major}.{self.minor}"), "v" (f"v{self.major}.{self.minor}.{self.patch}"),
    #   "" (str(self)), and raising ValueError(f"Unknown spec: {format_spec!r}")
    #   for any other spec.


    # Instantiate dv = DisplayVersion(1, 2, 0). Print str(dv), repr(dv),
    # [dv] (confirming lists use __repr__!), f"{dv:short}", and f"{dv:v}".
    # Then wrap format(dv, "unknown") in try/except ValueError to confirm invalid
    # format specs fail loudly.


def not_implemented_and_comparison_protocol() -> None:

    # One of Python's sharpest data-model rules is the difference between
    # NotImplemented and NotImplementedError:
    # - NotImplemented is a built-in singleton value you RETURN (never raise!)
    #   from __eq__, __lt__, or binary operators when 'other' has an unknown type.
    # - Returning NotImplemented from a == b tells Python: "I don't know how to
    #   compare against this type—try b.__eq__(a) instead." If both return
    #   NotImplemented, Python cleanly evaluates == to False (and != to True).
    # - Returning NotImplemented from a < b lets Python try b.__gt__(a) before
    #   raising a clean TypeError: '<' not supported between instances.
    # - NotImplementedError is an Exception class for unimplemented stubs. If
    #   you raise NotImplementedError inside __eq__, evaluating
    #   Version(1, 2, 0) == "1.2.0" crashes instead of returning False!
    #
    #     Suppose Version.__eq__ returns NotImplemented for non-Version values:
    #         Version(1, 2, 0) == "1.2.0"  -> tries str.__eq__ -> returns False!
    #         Version(1, 2, 0) < "2.0.0"   -> tries str.__gt__ -> raises TypeError!

    print(
        "NotImplemented type:",
        type(NotImplemented).__name__,
        "| is Exception:",
        isinstance(NotImplemented, BaseException),
    )

    # Define @total_ordering class Version: at module level (so sections 3 and 4
    # can sort and hash-test it) initialized with
    # def __init__(self, major: int, minor: int, patch: int = 0) -> None:
    # implementing:
    # - __repr__ -> f"Version({self.major}, {self.minor}, {self.patch})"
    # - __str__ -> f"{self.major}.{self.minor}.{self.patch}"
    # - __format__ supporting "short" and ""
    # - def __eq__(self, other: object) -> bool: returning NotImplemented if
    #   not isinstance(other, Version), else comparing
    #   (self.major, self.minor, self.patch) == (other.major, other.minor, other.patch)
    # - def __lt__(self, other: object) -> bool: returning NotImplemented if
    #   not isinstance(other, Version), else comparing the two 3-tuples.


    # Test equality and mismatched types on Version:
    # verify Version(1, 2, 0) == Version(1, 2, 0) is True,
    # Version(1, 2, 0) != Version(1, 3, 0) is True, and
    # Version(1, 2, 0) == "1.2.0" evaluates cleanly to False.
    # Next catch TypeError when evaluating Version(1, 2, 0) < "2.0.0" (or try
    # uncommenting the line below once Version exists):
    # print(Version(1, 2, 0) < "2.0.0")


def total_ordering_and_sorting() -> None:

    # Writing all six rich comparison methods (__eq__, __ne__, __lt__, __le__,
    # __gt__, __ge__) by hand is repetitive. Decorating a class with
    # @functools.total_ordering lets you define __eq__ plus ONE ordering method
    # (such as __lt__), and Python synthesizes __le__, __gt__, and __ge__ for
    # you at class-creation time. (Python derives __ne__ automatically from __eq__.)
    #
    #     Suppose versions = [Version(2, 0, 1), Version(1, 10, 0), Version(1, 2, 0)].
    #     Plain string sorting puts "1.10.0" before "1.2.0" (wrong!), whereas
    #     sorted(versions) compares integer tuples and produces
    #     [Version(1, 2, 0), Version(1, 10, 0), Version(2, 0, 1)].

    print("total_ordering decorator ready:", callable(total_ordering))

    # Build versions = [Version(2, 0, 1), Version(1, 10, 0), Version(1, 2, 0)]
    # and ordered = sorted(versions). Print ordered (confirming __repr__ inside
    # the list and numeric order 1.2.0 < 1.10.0 < 2.0.1) plus str(ordered[0]).


    # Test the synthesized operators from @total_ordering: print the results
    # of Version(1, 2, 0) <= Version(1, 2, 0), Version(1, 10, 0) > Version(1, 2, 0),
    # and Version(2, 0, 1) >= Version(1, 10, 0) (all True).


def eq_disables_hash_contract() -> None:

    # Every plain class inherits identity-based __eq__ and __hash__ from object.
    # The instant you define a custom __eq__ WITHOUT defining __hash__, Python
    # automatically sets YourClass.__hash__ = None!
    #
    # Why does Python disable hashing automatically? Hash tables (set and dict)
    # depend on one ironclad invariant: if a == b, then hash(a) MUST equal
    # hash(b). If Python kept object.__hash__ (derived from memory address),
    # two equal Version(1, 2, 0) objects at different addresses would hash to
    # different buckets and vanish inside sets and dicts!
    #
    #     Suppose Version defines __eq__ without __hash__:
    #         Version.__hash__ is None              # True!
    #         {Version(1, 2, 0)}                    # raises TypeError: unhashable type!
    #     Once you define __hash__ using the SAME immutable fields as __eq__:
    #         hash((self.major, self.minor, self.patch))
    #     equal instances produce identical hashes and work safely in sets/dicts.

    print(
        "object.__hash__ is set:",
        object.__hash__ is not None,
        "| list.__hash__ is None:",
        list.__hash__ is None,
    )

    # Prove that defining __eq__ disabled hashing on Version:
    # print Version.__hash__ (expect None), then wrap both
    # seen = {Version(1, 2, 0)} and lookup = {Version(1, 2, 0): "stable"} inside
    # try/except TypeError as exc: blocks and print each TypeError message!
    #
    # Try uncommenting below after defining Version to see the raw TypeError:
    # print({Version(1, 2, 0)})


    # Now define a hashable subclass class HashableVersion(Version): implementing
    # def __hash__(self) -> int: returning hash((self.major, self.minor, self.patch)).
    # (Remember: never mutate major/minor/patch after inserting into a set or dict!)
    # Create v_a = HashableVersion(1, 2, 0) and v_b = HashableVersion(1, 2, 0),
    # verify v_a == v_b and hash(v_a) == hash(v_b), place both into a set
    # (confirming len == 1), and look up release_notes[v_b] after inserting under v_a.


def main() -> None:

    print("=== 1. __repr__, __str__, and custom __format__ ===")
    repr_str_and_custom_format()

    print("\n=== 2. NotImplemented and the comparison protocol ===")
    not_implemented_and_comparison_protocol()

    print("\n=== 3. @total_ordering and sorting ===")
    total_ordering_and_sorting()

    print("\n=== 4. Defining __eq__ sets __hash__ = None ===")
    eq_disables_hash_contract()


if __name__ == "__main__":
    main()
