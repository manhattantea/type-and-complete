# python 320_classmethods_staticmethods_and_constructors.py

from typing import Self


def alternative_constructors_with_classmethod() -> None:

    # Python gives every class a single __init__—there is no C++ or Java
    # constructor overloading by parameter type. Whenever a type can be built
    # from multiple input formats (milliseconds, ISO text, dicts, env vars),
    # idiomatic Python uses @classmethod alternative constructors.
    #
    # The three method kinds differ only in what descriptor binding injects as
    # the first argument when accessed on a class or instance:
    # - Regular method: receives self (the instance).
    # - @classmethod: receives cls (the class object it was accessed through).
    # - @staticmethod: receives neither self nor cls—just a plain function
    #   grouped inside the class namespace.
    #
    # typing.Self (added in Python 3.11) annotates a @classmethod as returning
    # an instance of whichever class or subclass cls happens to be at the call
    # site, rather than hardcoding the base class name.
    #
    #     Suppose Timestamp has @classmethod def from_milliseconds(cls, ms) -> Self:
    #         return cls(ms / 1000.0)
    #     Calling Timestamp.from_milliseconds(2500.0) binds cls = Timestamp and
    #     returns Timestamp(seconds=2.5).

    print("Built-in classmethod dict.fromkeys:", dict.fromkeys(["a", "b"], 0))

    # Define class Timestamp: at module level (so later sections can subclass it) with:
    # - def __init__(self, seconds: float) -> None: validating via
    #   self.is_valid_epoch(seconds) (raising ValueError if invalid) and storing
    #   self.seconds = float(seconds).
    # - def __repr__(self) -> str: returning f"{type(self).__name__}(seconds={self.seconds})".
    # - @classmethod def from_milliseconds(cls, ms: float) -> Self: returning
    #   cls(ms / 1000.0).
    # - @classmethod def from_minutes(cls, minutes: float) -> Self: returning
    #   cls(minutes * 60.0).
    # - @staticmethod def is_valid_epoch(sec: float) -> bool: returning sec >= 0.0.


    # Instantiate ts = Timestamp.from_milliseconds(2500.0) and
    # ts_min = Timestamp.from_minutes(1.5). Print both values, check
    # type(ts) is Timestamp, and test Timestamp.is_valid_epoch(-1.0) (False)
    # alongside Timestamp.is_valid_epoch(0.0) (True).


    # Verify validation runs inside alternative constructors too: catch ValueError
    # when calling Timestamp.from_milliseconds(-500.0) (or try uncommenting):
    # Timestamp(-5.0)


def subclass_safety_classmethod_vs_staticmethod() -> None:

    # Here is why @classmethod + return cls(...) beats a @staticmethod that
    # hardcodes return Timestamp(...). When HighResTimestamp inherits from
    # Timestamp:
    # - HighResTimestamp.from_milliseconds(1500.0) passes cls = HighResTimestamp,
    #   so return cls(1.5) constructs and returns a HighResTimestamp!
    # - A @staticmethod calling Timestamp(ms / 1000.0) ignores the subclass and
    #   silently returns a base Timestamp, stripping away subclass methods.
    #
    #     Suppose HighResTimestamp adds nanoseconds(self) -> int:
    #         hr = HighResTimestamp.from_milliseconds(1500.0)  # HighResTimestamp!
    #         bad = HighResTimestamp.bad_from_ms(1500.0)       # plain Timestamp!

    print("Built-in classmethod descriptor type:", type(dict.__dict__["fromkeys"]).__name__)

    # Add a contrasting broken constructor onto Timestamp (or a sibling class):
    # @staticmethod def bad_from_ms(ms: float) -> "Timestamp": returning
    # Timestamp(ms / 1000.0).
    # Then define class HighResTimestamp(Timestamp): at module level with
    # def nanoseconds(self) -> int: returning int(self.seconds * 1_000_000_000).


    # Call hr = HighResTimestamp.from_milliseconds(1500.0) and print hr,
    # type(hr) is HighResTimestamp (True), and hr.nanoseconds() (1500000000).
    # Next call broken = HighResTimestamp.bad_from_ms(1500.0) and print
    # type(broken).__name__ ("Timestamp") and isinstance(broken, HighResTimestamp)
    # (False) to prove why staticmethod factories break polymorphism.


def instance_calls_and_staticmethod_tradeoffs() -> None:

    # You can invoke a @classmethod on an existing instance (hr.from_minutes(2.0)):
    # Python extracts cls = type(hr), binds that class as cls, and builds a fresh
    # instance without mutating hr.
    #
    # Use @staticmethod sparingly—mainly for pure domain helpers tightly coupled
    # to the class (like Timestamp.is_valid_epoch) that subclasses might want to
    # override. If a helper does not belong to the class interface, a plain
    # module-level function is simpler and more idiomatic in Python.

    sample = {"a": 1}
    print("Calling classmethod on an instance:", sample.fromkeys(["x", "y"], 0))

    # Instantiate hr = HighResTimestamp.from_milliseconds(1500.0), call
    # hr2 = hr.from_minutes(2.0), and print hr2, type(hr2) is HighResTimestamp
    # (True), and hr2 is not hr (True) to confirm instance-level classmethod
    # calls still receive cls = HighResTimestamp.


    # Override @staticmethod def is_valid_epoch(sec: float) -> bool: on a new
    # subclass StrictTimestamp(Timestamp) so it requires sec > 0.0 (rejecting 0.0).
    # Verify Timestamp(0.0) succeeds while StrictTimestamp(0.0) raises ValueError,
    # proving self.is_valid_epoch(seconds) dispatches polymorphically!


def main() -> None:

    print("=== 1. Alternative constructors with @classmethod ===")
    alternative_constructors_with_classmethod()

    print("\n=== 2. Subclass safety: @classmethod vs. @staticmethod ===")
    subclass_safety_classmethod_vs_staticmethod()

    print("\n=== 3. Instance calls and @staticmethod trade-offs ===")
    instance_calls_and_staticmethod_tradeoffs()


if __name__ == "__main__":
    main()
