# python 385_descriptor_protocol_deep_dive.py

from typing import Any


def functions_as_descriptors_and_lookup_order() -> None:

    # Almost every seemingly magical OOP feature in Python—bound methods,
    # @property, @classmethod, @staticmethod, @cached_property, __slots__, and
    # ORM fields—is built on one compact engine: the Descriptor Protocol.
    #
    # A descriptor is any class defining __get__, __set__, or __delete__ AND
    # stored as a CLASS attribute. (Placing a descriptor inside instance.__dict__
    # does nothing special; Python invokes descriptors only from classes/MRO.)
    #
    # Python splits descriptors into two kinds that govern exact obj.attr lookup:
    # - Data Descriptors (define __set__ or __delete__, such as @property or
    #   BoundedFloat): checked FIRST—they OUTRANK instance.__dict__!
    # - Instance dictionary obj.__dict__["attr"]: checked SECOND.
    # - Non-Data Descriptors (define __get__ ONLY, such as plain Python
    #   functions/methods and @cached_property) and regular class attributes:
    #   checked THIRD.
    #
    #     Suppose Greeter defines def hello(self) -> str: return "from class".
    #     Because functions define __get__ (non-data), accessing g.hello calls
    #     Greeter.__dict__["hello"].__get__(g, Greeter), returning a bound method.
    #     Assigning g.hello = lambda: "from dict" writes into g.__dict__, which
    #     outranks the non-data function descriptor on future reads!

    print(
        "Plain function is a non-data descriptor (__get__ only):",
        hasattr(functions_as_descriptors_and_lookup_order, "__get__")
        and not hasattr(functions_as_descriptors_and_lookup_order, "__set__"),
    )

    # Define class Greeter: with def hello(self) -> str: returning "from class".
    # Instantiate g = Greeter(). Manually bind the function descriptor via
    # bound = Greeter.__dict__["hello"].__get__(g, Greeter) and print bound().
    # Next shadow it with g.hello = lambda: "from instance dict" and print
    # g.hello() vs Greeter().hello() to prove instance.__dict__ beats non-data
    # descriptors without modifying the class.


def reusable_data_descriptor_with_set_name() -> None:

    # When several attributes need identical validation (like voltage and
    # temperature bounds), writing separate @property getters and setters for
    # every field repeats boilerplate. A reusable data descriptor writes the
    # validation logic once and attaches cleanly to any class attribute:
    # - __set_name__(self, owner: type, name: str) -> None runs automatically at
    #   class-definition time so voltage = BoundedFloat(0.0, 5.0) discovers the
    #   name "voltage" without repeating the string twice!
    # - __get__(self, instance: Any, owner: type | None = None) -> Any receives
    #   instance=None on class access (SensorReading.voltage), so always return
    #   self when instance is None; otherwise fetch the value from instance.
    # - __set__(self, instance: Any, value: Any) -> None validates the incoming
    #   value and stores it on 'instance' via setattr(instance, self.private_name, num).
    #
    #     Suppose SensorReading sets voltage = BoundedFloat(0.0, 5.0):
    #         s1 = SensorReading(3.3, 22.5)  # writes s1._voltage = 3.3 via __set__
    #         SensorReading.voltage          # instance is None -> returns BoundedFloat
    #         s1.voltage = 9.0               # out of range -> raises ValueError!

    print("Descriptor hooks: __set_name__, __get__, __set__, __delete__")

    # Define class BoundedFloat: at module level (so section 4 can reuse
    # SensorReading too) with:
    # - def __init__(self, min_val: float, max_val: float) -> None: storing
    #   self.min_val = min_val, self.max_val = max_val, and self.private_name = "".
    # - def __set_name__(self, owner: type, name: str) -> None: setting
    #   self.private_name = f"_{name}".
    # - def __get__(self, instance: Any, owner: type | None = None) -> Any:
    #   returning self if instance is None, else getattr(instance, self.private_name).
    # - def __set__(self, instance: Any, value: Any) -> None: converting
    #   num = float(value), raising ValueError if not (self.min_val <= num <= self.max_val),
    #   and calling setattr(instance, self.private_name, num).


    # Define class SensorReading: at module level with two class-level descriptors:
    #     voltage = BoundedFloat(0.0, 5.0)
    #     temp_c = BoundedFloat(-40.0, 125.0)
    # and def __init__(self, voltage: float, temp_c: float) -> None: assigning
    # self.voltage = voltage and self.temp_c = temp_c.
    # Create s1 = SensorReading(3.3, 22.5) and s2 = SensorReading(4.8, 30.0).
    # Print s1.voltage, s2.voltage, vars(s1), and SensorReading.voltage, then
    # catch ValueError when attempting s1.voltage = 9.0.


def shared_descriptor_state_trap() -> None:

    # The #1 bug when writing a custom descriptor is storing the value on 'self'
    # (self.value = value) inside __set__ instead of on 'instance'! Remember:
    # the descriptor object 'self' lives once on the CLASS and is shared by
    # EVERY instance of that class. Storing on self makes every instance
    # overwrite every other instance's data!
    #
    #     Suppose LeakyDescriptor writes self._val = value in __set__:
    #         b1 = LeakyBox(10)   # sets descriptor._val = 10
    #         b2 = LeakyBox(99)   # overwrites the SAME descriptor._val = 99!
    #         b1.item             # prints 99 instead of 10!

    print("One class-level descriptor serves every instance of the owning class.")

    # Reproduce the cross-instance leak bug:
    # - Define class LeakyDescriptor: with def __set__(self, instance: Any, value: Any) -> None:
    #   storing self._shared = value, and def __get__(self, instance: Any, owner: type | None = None) -> Any:
    #   returning self if instance is None else self._shared.
    # - Define class LeakyBox: with item = LeakyDescriptor() and
    #   def __init__(self, item: int) -> None: setting self.item = item.
    # Instantiate b1 = LeakyBox(10) and b2 = LeakyBox(99), then print b1.item
    # and b2.item (both 99!) to see why storage must live on 'instance'.


def data_vs_nondata_precedence_proof() -> None:

    # Putting the 3-step precedence rule to the test explains both @property
    # and @cached_property in one stroke:
    # - Data descriptor (BoundedFloat): even if someone pokes directly into
    #   s1.__dict__["voltage"] = 999.0, reading s1.voltage STILL calls
    #   BoundedFloat.__get__ and returns 3.3—instance.__dict__ cannot shadow it!
    # - Non-data descriptor (defining __get__ only): writing the computed result
    #   into instance.__dict__[self.name] shadows the descriptor on all future
    #   reads—that is literally the entire trick behind @functools.cached_property!

    print("Precedence: Data Descriptor > instance.__dict__ > Non-Data Descriptor")

    # Prove Data Descriptor precedence on s1 = SensorReading(3.3, 22.5):
    # forcibly inject s1.__dict__["voltage"] = 999.0, then print
    # s1.__dict__["voltage"] (999.0) vs s1.voltage (still 3.3!).


    # Build a miniature non-data caching descriptor class SimpleCached: with
    # def __init__(self, fn: Any) -> None:,
    # def __set_name__(self, owner: type, name: str) -> None: saving self.name = name,
    # and def __get__(self, instance: Any, owner: type | None = None) -> Any:
    # (NO __set__!) that returns self when instance is None, else computes
    # val = self.fn(instance), stores instance.__dict__[self.name] = val, and
    # returns val. Attach @SimpleCached def total(self) -> int: to a small
    # class Report: printing "computing..." once, read report.total twice, and
    # confirm "computing..." prints only once!


def main() -> None:

    print("=== 1. Functions as descriptors and lookup order ===")
    functions_as_descriptors_and_lookup_order()

    print("\n=== 2. Reusable data descriptor with __set_name__ ===")
    reusable_data_descriptor_with_set_name()

    print("\n=== 3. The shared descriptor state trap ===")
    shared_descriptor_state_trap()

    print("\n=== 4. Data vs. non-data precedence proof ===")
    data_vs_nondata_precedence_proof()


if __name__ == "__main__":
    main()
