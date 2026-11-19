# python 170_operator_module_and_key_functions.py

from dataclasses import dataclass
from functools import cmp_to_key, reduce
from operator import add, attrgetter, itemgetter, methodcaller, mul


def itemgetter_attrgetter_and_methodcaller() -> None:

    # Whenever you sort or map records with key=lambda r: r["score"], Python
    # creates a new Python stack frame and runs bytecode for every element.
    # The operator module replaces those trivial lambdas with C-level callable
    # factories that avoid frame overhead and read clearly:
    # - itemgetter(*keys) returns a callable running obj[k], or returning a
    #   tuple of values for multi-column sorting (itemgetter("dept", "level")).
    # - attrgetter(*attrs) reads obj.attr and follows dotted attribute paths
    #   like attrgetter("profile.team", "profile.seniority").
    # - methodcaller(name, *args, **kwargs) invokes obj.name(*args, **kwargs).
    # - Named operator functions like operator.add and operator.mul replace
    #   lambda a, b: a + b when passing math operations to map() or reduce().
    #
    #     Suppose rows = [{"k": 2}, {"k": 1}].
    #     sorted(rows, key=itemgetter("k")) returns [{"k": 1}, {"k": 2}]
    #     without allocating a Python lambda call per row.
    #
    #     Suppose member has member.profile.team == "core" and seniority == 4.
    #     attrgetter("profile.team", "profile.seniority")(member) returns
    #     ("core", 4) in one fast C call.
    #
    #     Suppose lines = ["alice,eng", "bob,ops"].
    #     list(map(methodcaller("split", ","), lines)) calls s.split(",") on
    #     each string and returns [["alice", "eng"], ["bob", "ops"]].
    #
    # Remember: list.sort(key=...) mutates in place and returns None, whereas
    # sorted(iterable, key=...) accepts any iterable and allocates a new list.

    pairs = [("b", 2), ("a", 3), ("c", 1)]
    print(f"Starter sorted by itemgetter(1): {sorted(pairs, key=itemgetter(1))}")

    # Create employees: list[dict[str, str | int]] with 4 dicts containing
    # "name", "department", and "level" (put two people in the same department
    # with different levels so tie-breaking is visible).
    # Sort into a new list with:
    # by_dept_level = sorted(employees, key=itemgetter("department", "level"))
    # Print by_dept_level, then project (name, level) tuples via:
    # summaries = list(map(itemgetter("name", "level"), by_dept_level))


    # Use methodcaller("split", ",") with map() over ["alice,eng", "bob,ops"]
    # and print the resulting list of split lists.


    # Replace arithmetic lambdas with operator.add and operator.mul:
    # - Compute element-wise sums of [1, 2, 3] and [10, 20, 30] using
    #   list(map(add, [1, 2, 3], [10, 20, 30])) (expected: [11, 22, 33]).
    # - Compute the product of [2, 3, 4, 5] using reduce(mul, [2, 3, 4, 5], 1)
    #   (expected: 120).


    # Define two @dataclass(frozen=True) classes:
    # - Profile with fields team: str and seniority: int
    # - Member with fields name: str and profile: Profile
    # Build members: list[Member] across different teams and seniorities, then
    # sort with sorted(members, key=attrgetter("profile.team", "profile.seniority"))
    # and print list(map(attrgetter("name"), sorted_members)).


    # Contrast in-place list.sort() against sorted():
    # Call ret = members.sort(key=attrgetter("profile.seniority")) and verify
    # ret is None while members itself is now reordered in place.


def pairwise_ordering_with_cmp_to_key() -> None:

    # Python 3 removed the old cmp= parameter from sorted() because calling a
    # key(x) projection once per item (O(N)) is far faster than calling a
    # pairwise comparator O(N log N) times.
    #
    # Occasionally an ordering rule genuinely depends on comparing two items
    # together with no scalar projection—for example, ordering numeric strings
    # so their concatenation makes the largest possible integer:
    #
    #     Suppose a = "9" and b = "34".
    #     "9" + "34" is "934", while "34" + "9" is "349".
    #     Because "934" > "349", "9" must sort BEFORE "34".
    #
    # functools.cmp_to_key(cmp_fn) bridges a comparator returning -1 (a before
    # b), 0 (equal), or 1 (a after b) into a standard key= wrapper object.

    print(f"Starter concat check: '9'+'34'={'9'+'34'!r} vs '34'+'9'={'34'+'9'!r}")

    # Define compare_concat(a: str, b: str) -> int comparing a + b against b + a:
    # - Return -1 when a + b > b + a (a comes before b)
    # - Return 1 when a + b < b + a (a comes after b)
    # - Return 0 when a + b == b + a


    # Bind tokens = ["3", "30", "34", "5", "9"], sort them with
    # ranked = sorted(tokens, key=cmp_to_key(compare_concat)), join them into
    # largest = "".join(ranked), print largest, and assert largest == "9534330".


def main() -> None:

    print("=== 1. itemgetter, attrgetter, and methodcaller ===")
    itemgetter_attrgetter_and_methodcaller()

    print("\n=== 2. Pairwise comparators with functools.cmp_to_key ===")
    pairwise_ordering_with_cmp_to_key()


if __name__ == "__main__":
    main()
