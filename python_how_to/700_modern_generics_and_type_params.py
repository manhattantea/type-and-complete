# python 700_modern_generics_and_type_params.py

from collections.abc import Sequence
from typing import Protocol


def generic_functions_and_lazy_type_aliases() -> None:

    # Python 3.12 (PEP 695) overhauled generics with native type-parameter
    # syntax. Before 3.12, writing a single generic helper meant importing
    # TypeVar, declaring T = TypeVar("T") at module scope (polluting the module
    # namespace), inheriting from Generic[T] on classes, and dodging name
    # collisions between unrelated functions that both wanted the letter T.
    #
    # With PEP 695, type parameters live directly in square brackets on the
    # function, class, or type alias that uses them:
    #
    #     Suppose you write:
    #         type Pair[T] = tuple[T, T]
    #         def first_item[T](seq: Sequence[T]) -> T | None:
    #             return seq[0] if seq else None
    #     Calling first_item(["alpha", "beta"]) binds T to str for that call,
    #     so a static checker knows the returned value is str | None.
    #
    # Under the hood, CPython still creates typing.TypeVar objects at
    # definition time and stores them in a tuple on obj.__type_params__. What
    # changed is scoping and laziness:
    # - Lexical scoping: Each [T] belongs strictly to its function, class, or
    #   type statement. It does not exist outside that scope and cannot clash
    #   with another [T] elsewhere in the module.
    # - Lazy evaluation on type statements: Writing type Alias = ... compiles
    #   the right-hand side inside a hidden annotation function and wraps it in
    #   a typing.TypeAliasType whose .__value__ evaluates on demand. That means
    #   recursive aliases like Tree[T] work without string quotes or NameError
    #   at import time.

    type JsonScalar = str | int | float | bool | None
    print("JsonScalar.__value__ =", JsonScalar.__value__)

    # Define a recursive generic type alias using PEP 695 syntax:
    # type Tree[T] = T | list[Tree[T]]
    # Print Tree.__type_params__ and Tree.__value__, then bind an example value
    # sample_tree: Tree[int] = [1, [2, 3], 4] and print sample_tree.


    # Write a generic function def first_item[T](seq: Sequence[T]) -> T | None:
    # that returns seq[0] when seq is non-empty and None otherwise.
    # Test it on ["alpha", "beta"] and () and print both results alongside
    # first_item.__type_params__.


    # Write def first_or_default[T](items: Sequence[T], default: T) -> T:
    # returning items[0] when items is non-empty and default otherwise.
    # Call it on ([], "fallback") and ([10, 20], 0) and print both results.


    # Verify lexical scoping of PEP 695 type parameters: T only exists inside
    # the definition that declared [T], never in the surrounding function body.
    # Try uncommenting below to observe NameError at runtime:
    # print(T)


def upper_bounds_and_value_constraints() -> None:

    # Square-bracket type parameters support two distinct restriction forms,
    # and mixing them up leads to subtle static typing surprises:
    #
    # - Upper bound ([T: Bound]): T may be Bound itself or ANY subclass or
    #   Protocol implementation of Bound. Why use [T: Animal] instead of simply
    #   writing parameter type Animal -> Animal?
    #
    #       Suppose class Animal has subclass Dog with method bark(), and
    #       def keep_first[T: Animal](items: Sequence[T]) -> T: returns items[0].
    #       When you pass a list[Dog], T binds to Dog, so the static return
    #       type stays Dog and keep_first(dogs).bark() type-checks cleanly.
    #       Typing it as Sequence[Animal] -> Animal would widen the return to
    #       Animal and throw away the Dog subtype!
    #
    # - Value constraint ([T: (int, float)]): T must resolve to EITHER int OR
    #   float consistently across the entire call.
    #
    #       Suppose def clamp[T: (int, float)](val: T, lo: T, hi: T) -> T:
    #       Calling clamp(15, 0, 10) binds T to int and returns int, while
    #       clamp(2.5, 0.0, 5.0) binds T to float and returns float. Unlike a
    #       union int | float, constraints stop callers from mixing types and
    #       keep the return type narrow instead of int | float.

    class SupportsLabel(Protocol):
        label: str

    print("Starter protocol ready for upper-bound drills:", SupportsLabel.__name__)

    # Define a structural protocol class HasArea(Protocol): declaring method
    # def area(self) -> float: with an ellipsis body.
    # Then define two simple concrete classes Rect (taking width and height)
    # and Circle (taking radius) that each implement area(self) -> float
    # without inheriting from HasArea.


    # Write two upper-bounded generic helpers over HasArea:
    # - def total_area[T: HasArea](shapes: Sequence[T]) -> float:
    #   returning sum(shape.area() for shape in shapes).
    # - def largest_shape[T: HasArea](shapes: Sequence[T]) -> T:
    #   raising ValueError if shapes is empty, otherwise returning the shape
    #   with the maximum area via max(shapes, key=lambda s: s.area()).
    # Pass rects = [Rect(2.0, 3.0), Rect(4.0, 5.0)] into both helpers, print
    # total_area(rects), and access biggest.width on biggest = largest_shape(rects)
    # to confirm the concrete Rect type survived the generic call.


    # Write a value-constrained helper:
    # def clamp[T: (int, float)](val: T, lo: T, hi: T) -> T:
    # returning lo if val < lo, hi if val > hi, and val otherwise.
    # Test clamp(15, 0, 10) and clamp(2.5, 0.0, 5.0) and print both results.
    # Try checking clamp.__type_params__[0].__constraints__ to inspect the
    # runtime constraint tuple (int, float).


def generic_classes_and_runtime_erasure() -> None:

    # On generic classes, [T] sits right after the class name—no Generic[T]
    # base class is required. Just like generic functions, CPython stores the
    # created TypeVar objects in ClassName.__type_params__.
    #
    # Keep runtime erasure firmly in mind: Python's generics are a static
    # analysis tool, NOT a runtime type wall.
    #
    #     Suppose box = Box[int](10).
    #     Box[int] creates a lightweight generic alias wrapper whose call
    #     instantiates a plain Box object. At runtime, type(box) is simply Box,
    #     and box.value = "oops" executes without raising TypeError unless a
    #     static type checker (mypy or pyright) audits the file.

    class Box[T]:

        def __init__(self, value: T) -> None:

            self.value = value

    sample_box = Box[int](10)
    print("Box.__type_params__ =", Box.__type_params__, "value =", sample_box.value)

    # Implement class BoundedStack[T]: with four methods:
    # - __init__(self, capacity: int) -> None: raises ValueError when
    #   capacity <= 0, stores self._capacity = capacity, and creates
    #   self._items: list[T] = [].
    # - push(self, item: T) -> None: raises OverflowError when
    #   len(self._items) >= self._capacity, otherwise appends item.
    # - pop(self) -> T: raises IndexError when empty, otherwise pops and
    #   returns the top item.
    # - peek(self) -> T | None: returns self._items[-1] if non-empty, else None.


    # Instantiate stack = BoundedStack[int](capacity=2), inspect
    # BoundedStack.__type_params__, push 10 and 20, and print stack.peek().
    # Try pushing 30 inside a try / except OverflowError as err: block to
    # confirm the capacity guard fires, then pop both items and verify that a
    # third pop raises IndexError.


    # Observe runtime erasure directly: create a fresh BoundedStack[int](2)
    # and check type(stack) is BoundedStack.
    # Try uncommenting below under a static type checker vs. plain python:
    # stack.push("not-an-int")
    # Static tools flag the str/int mismatch, while CPython happily stores it.


def main() -> None:

    print("=== 1. Generic functions and lazy type aliases ===")
    generic_functions_and_lazy_type_aliases()

    print("\n=== 2. Upper bounds and value constraints ===")
    upper_bounds_and_value_constraints()

    print("\n=== 3. Generic classes and runtime erasure ===")
    generic_classes_and_runtime_erasure()


if __name__ == "__main__":
    main()
