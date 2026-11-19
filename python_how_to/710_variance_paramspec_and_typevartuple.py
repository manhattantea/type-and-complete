# python 710_variance_paramspec_and_typevartuple.py

from collections.abc import Callable, Mapping, Sequence
from functools import wraps
from typing import Concatenate


def invariance_covariance_and_contravariance() -> None:

    # One of the biggest shocks when turning on mypy or pyright is passing a
    # list[int] into a parameter typed list[int | float] (or passing list[Dog]
    # into list[Animal]) and watching the checker reject it.
    #
    # Why does that fail? Because list is MUTABLE, so it must be INVARIANT:
    #
    #     Suppose nums: list[int] = [1, 2, 3].
    #     If def add_float(xs: list[int | float]) -> None: accepted nums and
    #     ran xs.append(3.14), the caller's list[int] would silently contain a
    #     float! To keep mutable containers sound, list[A] is NOT a subtype of
    #     list[B] even when A is a subtype of B. The same rule holds for
    #     dict[K, V] and set[T].
    #
    # Read-only collection protocols fix this through COVARIANCE: Sequence[T],
    # Mapping[K, V], Iterable[T], and Iterator[T] expose no mutating .append()
    # or .add() methods, so Sequence[int] IS safely a subtype of
    # Sequence[int | float]. A golden rule for clean Python signatures: accept
    # read-only protocols in parameters, and return concrete types like list[T].
    #
    # Callables follow a dual rule: Callable[[Arg], Ret] is CONTRAVARIANT in
    # its argument types and COVARIANT in its return type. If a caller expects
    # Callable[[Dog], Animal], you can safely pass Callable[[Animal], Dog]:
    # the caller promises to supply a Dog (which a handler accepting any Animal
    # handles easily), and the handler returns a Dog (which satisfies anyone
    # expecting an Animal).

    readings: Sequence[int | float] = [1, 2, 3]
    print("Starter covariant Sequence[int | float]:", readings)

    # Write def sum_numbers(nums: Sequence[int | float]) -> float: that returns
    # float(sum(nums)).
    # Pass both int_list: list[int] = [1, 2, 3] and
    # float_tuple: tuple[float, ...] = (1.5, 2.5) into sum_numbers and print
    # both totals.


    # Practice read-only Mapping covariance:
    # write def average_score(scores: Mapping[str, int | float]) -> float:
    # returning 0.0 if scores is empty, else sum(scores.values()) / len(scores).
    # Pass raw_scores: dict[str, int] = {"alice": 10, "bob": 15} into
    # average_score and print the result.


    # Practice Callable contravariance and covariance together:
    # define class Animal: storing self.name = name and class Dog(Animal):
    # storing super().__init__(name) plus self.breed = breed.
    # Write def run_handler(dog: Dog, fn: Callable[[Dog], Animal]) -> str:
    # returning fn(dog).name.
    # Then write def rename_pet(pet: Animal) -> Dog: returning a fresh Dog with
    # name f"{pet.name}-adopted" and breed="mixed", pass rename_pet into
    # run_handler(Dog("Rex", "shepherd"), rename_pet), and print the result.


    # Observe mutable list invariance under a static type checker:
    # Try uncommenting below and passing int_list to _append_zero(int_list):
    # def _append_zero(nums: list[int | float]) -> None:
    #     nums.append(0.0)


def paramspec_and_concatenate_decorators() -> None:

    # Before ParamSpec, writing a typed decorator forced a painful choice:
    # annotating the wrapper as Callable[..., Any] threw away all parameter
    # names, keyword checks, and default values at every call site.
    #
    # PEP 695 lets a decorator declare a parameter specification using the
    # double-star form [**P, R] directly in its brackets. Inside the signature,
    # write Callable[P, R] (notice NO inner brackets around P!) and forward the
    # captured arguments with *args: P.args and keyword arguments with
    # kwargs annotated as P.kwargs. Static checkers then keep the exact
    # signature of whatever function you decorate.
    #
    # When a decorator injects or peels off a leading argument, combine P with
    # typing.Concatenate[str, P]:
    #
    #     Suppose def format_entry(prefix: str, code: int, ok: bool) -> str:
    #     Wrapping it with inject_prefix("[SYS]", format_entry) removes the
    #     leading str from the public signature so callers pass (code, ok)
    #     with full type checking and autocomplete intact.

    def passthrough[**P, R](fn: Callable[P, R]) -> Callable[P, R]:

        @wraps(fn)
        def wrapped(*args: P.args, **kwargs: P.kwargs) -> R:

            return fn(*args, **kwargs)

        return wrapped

    print("Starter ParamSpec decorator:", passthrough.__name__, passthrough.__type_params__)

    # Write a generic audit decorator with PEP 695 ParamSpec:
    # def with_audit[**P, R](fn: Callable[P, R]) -> Callable[P, R]:
    # Inside it, decorate an inner wrapper using @wraps(fn), print
    # f"[audit] calling {fn.__name__}", compute result = fn(*args, **kwargs),
    # print f"[audit] finished {fn.__name__} -> {result!r}", and return result.


    # Decorate def scale_reading(value: float, factor: int = 2) -> float: with
    # @with_audit, returning value * factor.
    # Call both scale_reading(4.5) and scale_reading(4.5, factor=3) to confirm
    # default arguments and keyword arguments still work cleanly.


    # Write a leading-argument injector using Concatenate:
    # def inject_prefix[**P, R](prefix: str, fn: Callable[Concatenate[str, P], R]) -> Callable[P, R]:
    # Have it return a @wraps(fn) wrapper that forwards prefix ahead of the
    # captured args and kwargs into fn.
    # Define def format_entry(prefix: str, code: int, ok: bool) -> str:
    # returning f"{prefix} code={code} ok={ok}", bind
    # bound_fmt = inject_prefix("[SYS]", format_entry), and call both
    # bound_fmt(200, True) and bound_fmt(404, ok=False), printing each string.


def variadic_tuples_with_typevartuple() -> None:

    # Standard tuple[T, ...] handles variable-length tuples only when every
    # element shares the same type T. When you need to preserve distinct
    # per-position types across a variable-length tuple, PEP 695 provides
    # TypeVarTuple using [*Ts] (similar to variadic template packs in C++).
    #
    #     Suppose row: tuple[str, int, bool] = ("header", 42, True).
    #     Calling split_head(row) binds T to str and *Ts to (int, bool), so
    #     the static return type is precisely tuple[str, tuple[int, bool]]—not
    #     an erased tuple[object, tuple[object, ...]].

    sample_row: tuple[str, int, bool] = ("header", 42, True)
    print("Starter heterogeneous tuple:", sample_row)

    # Write def split_head[T, *Ts](items: tuple[T, *Ts]) -> tuple[T, tuple[*Ts]]:
    # returning (items[0], items[1:]).
    # Call split_head(("header", 42, True)) and split_head((99,)) and print
    # each (head, tail) pair.


    # Write def prepend_tag[T, *Ts](tag: T, rest: tuple[*Ts]) -> tuple[T, *Ts]:
    # returning (tag, *rest).
    # Prepend "v1" onto (200, True) and print the returned 3-tuple.


    # Write def split_tail[*Ts, T](items: tuple[*Ts, T]) -> tuple[tuple[*Ts], T]:
    # returning (items[:-1], items[-1]). Notice *Ts can appear before T as long
    # as there is at most one unpacked TypeVarTuple in the tuple annotation.
    # Call split_tail(("alpha", 1, 2.5)) and print (init_items, last_item).


def main() -> None:

    print("=== 1. Invariance, covariance, and contravariance ===")
    invariance_covariance_and_contravariance()

    print("\n=== 2. ParamSpec and Concatenate decorators ===")
    paramspec_and_concatenate_decorators()

    print("\n=== 3. Variadic tuples with TypeVarTuple ===")
    variadic_tuples_with_typevartuple()


if __name__ == "__main__":
    main()
