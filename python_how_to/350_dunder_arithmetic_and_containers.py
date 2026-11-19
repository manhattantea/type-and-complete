# python 350_dunder_arithmetic_and_containers.py


def binary_reflected_and_unary_operators() -> None:

    # When Python evaluates 2.0 * v, it first asks the left operand by calling
    # (2.0).__mul__(v). Because float does not know how to multiply a custom Vec2,
    # float.__mul__ returns NotImplemented. Python then reverses the operands and
    # tries the reflected dunder v.__rmul__(2.0)!
    #
    # That two-step dispatch is why every binary operator (__add__, __sub__,
    # __mul__) must return a brand-new instance without mutating self AND return
    # NotImplemented (never raise TypeError!) for unknown operand types. Unary
    # negation (-v) dispatches to __neg__(self).
    #
    #     Suppose v = Vec2(1.0, 2.0):
    #         v * 3    -> calls v.__mul__(3)    -> Vec2(3.0, 6.0)
    #         2.0 * v  -> (2.0).__mul__(v) is NotImplemented -> calls v.__rmul__(2.0)
    #                  -> Vec2(2.0, 4.0)
    #         -v       -> calls v.__neg__()     -> Vec2(-1.0, -2.0)

    print("(3.0).__mul__('x') returns:", (3.0).__mul__("x"))

    # Define class Vec2: at module level (so section 2 can contrast it) with
    # def __init__(self, x: float, y: float) -> None:
    # storing self.x = float(x) and self.y = float(y), plus:
    # - def __repr__(self) -> str: -> f"Vec2({self.x}, {self.y})"
    # - def __eq__(self, other: object) -> bool: returning NotImplemented for non-Vec2
    # - def __neg__(self) -> "Vec2": returning Vec2(-self.x, -self.y)
    # - def __add__(self, other: object) -> "Vec2": adding Vec2 + Vec2 (else NotImplemented)
    # - def __sub__(self, other: object) -> "Vec2": subtracting Vec2 - Vec2 (else NotImplemented)
    # - def __mul__(self, scalar: object) -> "Vec2": scaling by int | float (else NotImplemented)
    # - def __rmul__(self, scalar: object) -> "Vec2": delegating to self.__mul__(scalar).


    # Create v1 = Vec2(1.0, 2.0) and v2 = Vec2(3.0, 4.0). Print v1 + v2, v2 - v1,
    # -v1, v1 * 3, and 2.0 * v1 (proving __rmul__ fires when float is on the left).
    # Then catch TypeError for "bad" * v1 to confirm clean failure when both sides
    # return NotImplemented.


def inplace_iadd_and_return_none_trap() -> None:

    # Augmented assignment (v1 += v2) has a subtle rule that catches almost every
    # Python developer at least once. Python executes:
    #     v1 = v1.__iadd__(v2)
    # If __iadd__ is NOT defined, Python automatically falls back to
    # v1 = v1.__add__(v2) (which allocates a new object and rebinds v1—perfect
    # for immutable value types like tuples or immutable Vec2).
    #
    # If you DO define __iadd__ for in-place mutation, you MUST return self!
    # Because Python assigns the return value back to v1, forgetting return self
    # (implicitly returning None) silently overwrites v1 with None!
    #
    #     Suppose BrokenVec2.__iadd__ updates self.x and self.y but returns None:
    #         b = BrokenVec2(1.0, 1.0)
    #         alias = b
    #         b += BrokenVec2(2.0, 3.0)
    #     Result: alias is mutated to (3.0, 4.0), while b has become None!

    nums = [1, 2]
    before_id = id(nums)
    nums += [3]
    print("list += mutates in place (same id):", id(nums) == before_id, "| nums:", nums)

    # Define class MutableVec2: with x: float, y: float, __repr__, and
    # def __iadd__(self, other: object) -> "MutableVec2": returning NotImplemented
    # if not isinstance(other, MutableVec2), otherwise adding other.x and other.y
    # into self.x and self.y and returning self.
    # Bind m = MutableVec2(1.0, 2.0), save orig_id = id(m), run
    # m += MutableVec2(3.0, 4.0), and print m alongside id(m) == orig_id (True).


    # Reproduce the __iadd__ return-None trap: define class BrokenVec2: whose
    # def __iadd__(self, other: "BrokenVec2") -> None: updates self.x and self.y
    # without returning self. Run b = BrokenVec2(1.0, 1.0); alias = b;
    # b += BrokenVec2(2.0, 3.0) and print b (None!) and alias (mutated!).


    # Contrast with immutable Vec2 (no __iadd__ defined): bind v = Vec2(1.0, 1.0),
    # save before = id(v), run v += Vec2(2.0, 3.0), and verify id(v) != before
    # because Python fell back to __add__ and rebound v to a new Vec2.


def containers_setitem_and_truthiness() -> None:

    # Custom containers plug into Python's built-in syntax via five core dunders:
    # - __len__(self) -> int powers len(c).
    # - __getitem__(self, index: int | slice) powers c[i] and slicing c[0:2].
    # - __setitem__(self, index: int, value: int) -> None powers indexed writes
    #   like c[i] = val.
    # - __contains__(self, item: object) -> bool powers x in c.
    # - __iter__(self) returns an iterator for 'for x in c:' and list(c).
    #
    # Truthiness (bool(obj) and 'if obj:') follows a two-step lookup:
    # - Python checks __bool__(self) -> bool FIRST.
    # - If __bool__ is absent, Python falls back to __len__(self) != 0!
    # - If neither __bool__ nor __len__ exists, every instance is truthy (True).
    #
    #     Suppose ring = RingSlice([10, 20, 30]):
    #         ring[3]          -> index 3 % 3 == 0 -> 10
    #         ring[4] = 99     -> index 4 % 3 == 1 -> internal list becomes [10, 99, 30]
    #         bool(ring)       -> len(ring) == 3 != 0 -> True
    #         bool(RingSlice([])) -> len == 0 -> False!

    print("Truthiness fallback: bool([]) =", bool([]), "| bool(object()) =", bool(object()))

    # Define class RingSlice: wrapping self._data = list(items) in
    # def __init__(self, items: list[int]) -> None: and implementing:
    # - def __len__(self) -> int: returning len(self._data)
    # - def __getitem__(self, index: int | slice) -> int | list[int]: returning
    #   self._data[index] for a slice, raising IndexError if empty, else returning
    #   self._data[index % len(self._data)]
    # - def __setitem__(self, index: int, value: int) -> None: raising IndexError
    #   if empty, else setting self._data[index % len(self._data)] = value
    # - def __contains__(self, item: object) -> bool: returning item in self._data
    # - def __iter__(self): returning iter(self._data).


    # Create ring = RingSlice([10, 20, 30]). Print len(ring), ring[3] (10),
    # ring[-1] (30), and ring[0:2] ([10, 20]). Mutate ring[4] = 99 via __setitem__,
    # then print list(ring) ([10, 99, 30]), 99 in ring (True), bool(ring) (True),
    # and bool(RingSlice([])) (False—powered by __len__!).


    # Practice explicit __bool__ overriding default truthiness: define
    # class TruthyVec2: storing x: float and y: float with
    # def __bool__(self) -> bool: returning self.x != 0.0 or self.y != 0.0.
    # Verify bool(TruthyVec2(0.0, 0.0)) is False and bool(TruthyVec2(0.0, 2.0)) is True.


def callable_objects_with_call() -> None:

    # Implementing def __call__(self, *args, **kwargs) lets an instance be called
    # like a function (obj(x)), and causes callable(obj) to return True. Unlike a
    # closure, a callable class gives callers clean, inspectable state attributes
    # (such as .factor or .calls) alongside function-call syntax.
    #
    #     Suppose times_ten = Multiplier(10.0):
    #         callable(times_ten) -> True
    #         times_ten(4.5)      -> 45.0 (and increments times_ten.calls to 1)

    print("callable(len):", callable(len), "| callable(42):", callable(42))

    # Define class Multiplier: with def __init__(self, factor: float) -> None:
    # storing self.factor = factor and self.calls = 0, and
    # def __call__(self, value: float) -> float: incrementing self.calls += 1
    # and returning value * self.factor.
    # Create times_ten = Multiplier(10.0), print callable(times_ten) (True),
    # call times_ten(4.5) and times_ten(2.0), and print times_ten.calls (2).


def main() -> None:

    print("=== 1. Binary, reflected, and unary operators ===")
    binary_reflected_and_unary_operators()

    print("\n=== 2. In-place __iadd__ and the return-None trap ===")
    inplace_iadd_and_return_none_trap()

    print("\n=== 3. Container protocol, __setitem__, and truthiness ===")
    containers_setitem_and_truthiness()

    print("\n=== 4. Callable objects with __call__ ===")
    callable_objects_with_call()


if __name__ == "__main__":
    main()
