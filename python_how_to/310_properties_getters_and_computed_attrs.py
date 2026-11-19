# python 310_properties_getters_and_computed_attrs.py

from functools import cached_property


def validated_properties_and_recursion_trap() -> None:

    # In Java or C++, developers often wrap fields in get_balance() and
    # set_balance() methods up front because exposing a raw field locks callers
    # into direct memory access forever. Idiomatic Python skips that ceremony:
    # start with a plain public attribute like temp.kelvin, and if you later need
    # range checks, unit conversions, or logging, decorate it with @property so
    # every caller keeps writing temp.kelvin with zero breaking changes.
    #
    # Under the hood, @property creates a data descriptor (a class attribute
    # implementing __get__, __set__, and __delete__). Because data descriptors
    # outrank instance.__dict__, reads and writes on temp.kelvin always route
    # through your property methods instead of reading raw dict keys directly.
    #
    # Two rules prevent the most common @property bugs:
    # - Always store the raw backing value under a distinct private name such as
    #   self._kelvin. Writing self.kelvin = value inside the kelvin setter calls
    #   the setter recursively until Python crashes with RecursionError!
    # - Inside __init__, assign self.kelvin = kelvin (through the property, not
    #   self._kelvin) so initial construction runs your validation too.
    #
    #     Suppose Temperature validates value >= 0.0 inside @kelvin.setter:
    #         t = Temperature(300.0)   # calls setter -> stores self._kelvin = 300.0
    #         t.kelvin = 250.0         # calls setter -> updates self._kelvin = 250.0
    #         Temperature(-5.0)        # calls setter -> raises ValueError immediately!

    print(
        "property is a data descriptor:",
        hasattr(property, "__get__") and hasattr(property, "__set__"),
    )

    # Define class Temperature: whose def __init__(self, kelvin: float) -> None:
    # assigns self.kelvin = kelvin.
    # Add @property def kelvin(self) -> float: returning self._kelvin, and
    # @kelvin.setter def kelvin(self, value: float) -> None: raising ValueError
    # if value < 0.0, otherwise setting self._kelvin = float(value).


    # Instantiate temp = Temperature(300.0), update temp.kelvin = 273.15, and
    # print temp.kelvin and vars(temp) to confirm "_kelvin" (not "kelvin") is
    # stored in the instance dictionary. Then wrap Temperature(-10.0) in a
    # try/except ValueError block to verify construction-time validation works.


    # Observe the setter RecursionError trap safely: define a small class
    # BrokenGauge: with @property def level(self) -> int: returning self._level
    # and @level.setter def level(self, value: int) -> None: mistakenly writing
    # self.level = value. Catch RecursionError when setting BrokenGauge().level = 5
    # and print the exception type name.


def computed_views_and_read_only_properties() -> None:

    # Properties shine when one stored canonical field (self._kelvin) drives
    # multiple unit views without risking stale or out-of-sync fields.
    # - A read/write computed property like celsius defines both @property and
    #   @celsius.setter, delegating self.kelvin = value + 273.15 so range checks
    #   stay in one place.
    # - Omitting @attr.setter makes a property read-only: attempting
    #   temp.fahrenheit = 72.0 raises AttributeError because property still defines
    #   __set__ on the descriptor and rejects writes when fset is None.
    #
    #     Suppose sensor starts at 300.0 K:
    #         sensor.celsius = 100.0      # delegates to self.kelvin = 373.15
    #         sensor.kelvin               # 373.15
    #         round(sensor.fahrenheit, 2) # 212.0 (computed fresh, never stale)

    sample_c = 100.0
    print(f"Baseline unit check: {sample_c} C == {sample_c + 273.15} K")

    # Define class ThermalSensor: storing self.kelvin = kelvin in __init__ with
    # the validated kelvin getter and setter from above, plus:
    # - @property def celsius(self) -> float: returning self._kelvin - 273.15
    # - @celsius.setter def celsius(self, value: float) -> None: setting
    #   self.kelvin = value + 273.15
    # - Read-only @property def fahrenheit(self) -> float: returning
    #   self.celsius * 9.0 / 5.0 + 32.0 (with no setter).


    # Instantiate sensor = ThermalSensor(300.0), print sensor.kelvin,
    # round(sensor.celsius, 2), and round(sensor.fahrenheit, 2).
    # Assign sensor.celsius = 0.0 and verify sensor.kelvin == 273.15 and
    # round(sensor.fahrenheit, 2) == 32.0.
    # Also verify sensor.celsius = -300.0 raises ValueError via the kelvin setter.


    # Verify read-only enforcement by catching AttributeError when assigning
    # sensor.fahrenheit = 72.0 (or try uncommenting a direct write below once
    # ThermalSensor is defined):
    # sensor.fahrenheit = 72.0


def deleters_and_lazy_invalidation() -> None:

    # Alongside getter and setter, @attr.deleter hooks into the 'del obj.attr'
    # statement. Deleters are handy for clearing cached payloads, releasing
    # temporary buffers, or resetting an optional backing field cleanly without
    # letting callers poke private _underscore names directly.
    #
    #     Suppose buf = ScratchBuffer("draft"):
    #         del buf.text   # runs @text.deleter -> sets self._text = None
    #         buf.text       # raises AttributeError("buffer cleared")

    print("property also implements __delete__:", hasattr(property, "__delete__"))

    # Define class ScratchBuffer: with def __init__(self, text: str) -> None:
    # setting self._text: str | None = text.
    # Add @property def text(self) -> str: raising AttributeError("buffer cleared")
    # if self._text is None else returning self._text, @text.setter storing
    # self._text = value, and @text.deleter setting self._text = None.


    # Create buf = ScratchBuffer("hello"), print buf.text, run del buf.text,
    # catch AttributeError when reading buf.text, then assign buf.text = "reset"
    # and print buf.text to prove the property works cleanly again.


def cached_property_and_invalidation() -> None:

    # @functools.cached_property solves a different problem: expensive one-time
    # computation. Unlike @property, cached_property is a NON-data descriptor
    # (it defines __get__ only, with no __set__).
    #
    # On the first read of obj.calibration_table, cached_property runs your
    # method and writes the result directly into obj.__dict__["calibration_table"].
    # Because instance.__dict__ outranks non-data descriptors, every subsequent
    # read hits obj.__dict__ at raw dictionary-lookup speed with zero method call!
    #
    # Watch out for two practical trade-offs:
    # - Stale cache: mutating underlying fields does NOT recompute the cached
    #   value until you explicitly invalidate it with del obj.calibration_table.
    # - Requires __dict__: cached_property cannot cache onto a __slots__ class
    #   that omits "__dict__".
    #
    #     Suppose probe = CalibratedProbe(20.0):
    #         First read:  "calibration_table" not in vars(probe) -> runs method & caches.
    #         Second read: "calibration_table" in vars(probe) -> returns cached list directly.
    #         del probe.calibration_table -> removes dict entry so next read recomputes.

    print(
        "cached_property is non-data (__get__ only):",
        hasattr(cached_property, "__get__") and not hasattr(cached_property, "__set__"),
    )

    # Define class CalibratedProbe: with def __init__(self, base_celsius: float) -> None:
    # setting self.base_celsius = base_celsius, and
    # @cached_property def calibration_table(self) -> list[float]: that prints
    # "Computing table..." and returns
    # [round(self.base_celsius + offset, 2) for offset in (-5.0, 0.0, 5.0)].


    # Instantiate probe = CalibratedProbe(20.0). Print "calibration_table" in vars(probe)
    # before the first read (False), read probe.calibration_table twice in a row,
    # and verify "Computing table..." prints only ONCE while
    # "calibration_table" in vars(probe) becomes True.


    # Prove cache staleness and manual invalidation: set probe.base_celsius = 50.0,
    # print probe.calibration_table (still shows the old 20.0 offsets!), then run
    # del probe.calibration_table and read probe.calibration_table again to see
    # "Computing table..." fire once more and return [45.0, 50.0, 55.0].


def main() -> None:

    print("=== 1. Validated properties and the recursion trap ===")
    validated_properties_and_recursion_trap()

    print("\n=== 2. Computed views and read-only properties ===")
    computed_views_and_read_only_properties()

    print("\n=== 3. Deleters and controlled resets ===")
    deleters_and_lazy_invalidation()

    print("\n=== 4. cached_property and cache invalidation ===")
    cached_property_and_invalidation()


if __name__ == "__main__":
    main()
