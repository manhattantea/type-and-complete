# python 370_slots_and_object_memory_layout.py

import sys
import weakref


def dict_vs_slots_memory_layout() -> None:

    # Every normal Python instance carries a PyObject header (reference count +
    # type pointer) plus a pointer to a dynamic self.__dict__ hash table so you
    # can attach new attributes at any time. That flexibility costs roughly
    # 64 to 104+ extra bytes per instance AND silently accepts typos (writing
    # p.x_pos = 1.0 instead of p.xpos = 1.0 creates a brand-new key!).
    #
    # Declaring __slots__ = ("x", "y", "vx", "vy") changes the C struct layout:
    # - Python omits the per-instance __dict__ and __weakref__ pointers.
    # - Instead, each instance embeds a fixed array of PyObject* slots right in
    #   its struct, and Python places C member_descriptor objects on the class
    #   (SlottedParticle.x) that read/write fixed byte offsets directly!
    # - Assigning any undeclared attribute (sp.mass = 1.0) raises AttributeError.
    #
    # Note on measurement: sys.getsizeof(obj) is shallow—for a normal instance
    # it excludes the separate dictionary object, so compare
    # sys.getsizeof(dp) + sys.getsizeof(dp.__dict__) against sys.getsizeof(sp).
    #
    #     Suppose dp = DictParticle(1, 2, 0.5, -0.5) and sp = SlottedParticle(1, 2, 0.5, -0.5):
    #         dp stores 4 floats in a separate hash table (~150+ bytes total).
    #         sp stores 4 pointers inline in its C struct (~64 bytes total, no __dict__).

    print("Shallow size of plain object():", sys.getsizeof(object()), "bytes")

    # Define two classes at module level (so later sections can subclass them)
    # with identical __init__(self, x: float, y: float, vx: float, vy: float) -> None:
    # - class DictParticle: assigning self.x, self.y, self.vx, self.vy (no __slots__).
    # - class SlottedParticle: declaring __slots__ = ("x", "y", "vx", "vy") and
    #   assigning self.x, self.y, self.vx, self.vy.


    # Instantiate dp = DictParticle(1.0, 2.0, 0.5, -0.5) and
    # sp = SlottedParticle(1.0, 2.0, 0.5, -0.5). Print
    # dp_bytes = sys.getsizeof(dp) + sys.getsizeof(dp.__dict__),
    # sp_bytes = sys.getsizeof(sp), hasattr(dp, "__dict__") (True),
    # hasattr(sp, "__dict__") (False), and type(SlottedParticle.x).__name__
    # (expect "member_descriptor").


    # Prove typo protection: assign dp.x_pos = 9.0 (silently creates a typo key!),
    # then catch AttributeError when attempting sp.mass = 1.0 (or try uncommenting):
    # sp.mass = 1.0


def slot_inheritance_leaky_child_gotcha() -> None:

    # The #1 __slots__ bug happens in subclasses: if class LeakyChild(SlottedParticle):
    # omits __slots__ = () (empty tuple when adding no new fields, or a tuple of
    # new slot names), Python silently gives every LeakyChild instance a brand-new
    # __dict__, erasing both your memory savings and your typo protection!
    #
    #     Suppose SlottedChild declares __slots__ = ("label",) while LeakyChild
    #     declares no __slots__:
    #         hasattr(SlottedChild(...), "__dict__") -> False (still compact!)
    #         hasattr(LeakyChild(...), "__dict__")   -> True  (__dict__ is back!)

    print("Slotted subclasses must declare __slots__ to stay dict-free.")

    # Define two subclasses of SlottedParticle:
    # - class SlottedChild(SlottedParticle): declaring __slots__ = ("label",) and
    #   def __init__(self, x: float, y: float, vx: float, vy: float, label: str) -> None:
    #   calling super().__init__(x, y, vx, vy) and setting self.label = label.
    # - class LeakyChild(SlottedParticle): with def kind(self) -> str: return "leaky"
    #   (intentionally omitting __slots__).


    # Instantiate sc = SlottedChild(1.0, 2.0, 0.0, 0.0, "hero") and
    # lc = LeakyChild(1.0, 2.0, 0.0, 0.0). Print hasattr(sc, "__dict__") (False)
    # vs hasattr(lc, "__dict__") (True), and verify lc.extra = 42 works silently
    # while sc.extra = 42 raises AttributeError.


def weakref_and_multiple_inheritance_limits() -> None:

    # Because __slots__ drops the hidden __weakref__ slot too, calling
    # weakref.ref(sp) (a non-owning reference that lets caches avoid leaking
    # objects) raises TypeError unless you explicitly include "__weakref__" in
    # __slots__. Also, inheriting from two classes that both define non-empty
    # __slots__ raises TypeError: multiple bases have instance lay-out conflict.

    print("weakref.ref helper ready:", callable(weakref.ref))

    # Create sp = SlottedParticle(1.0, 2.0, 0.0, 0.0) and wrap weakref.ref(sp)
    # in try/except TypeError to observe the missing weakref slot error. Then
    # define class WeakSlotted: with __slots__ = ("name", "__weakref__") and
    # def __init__(self, name: str) -> None: setting self.name = name, create
    # w = WeakSlotted("node"), build ref = weakref.ref(w), and print ref() is w (True).


    # Observe the multiple-inheritance C struct layout conflict by uncommenting:
    # class LeftSlot:
    #     __slots__ = ("a",)
    # class RightSlot:
    #     __slots__ = ("b",)
    # class BadMix(LeftSlot, RightSlot):
    #     __slots__ = ()


def main() -> None:

    print("=== 1. __dict__ vs. __slots__ memory layout ===")
    dict_vs_slots_memory_layout()

    print("\n=== 2. Subclass __slots__ leaky-child gotcha ===")
    slot_inheritance_leaky_child_gotcha()

    print("\n=== 3. __weakref__ and multiple-inheritance limits ===")
    weakref_and_multiple_inheritance_limits()


if __name__ == "__main__":
    main()
