# python 055_iteration_helpers_enumerate_zip_reversed.py


def enumerate_and_strict_zip() -> None:

    # Writing for i in range(len(items)): val = items[i] is a classic Python
    # anti-pattern. It adds manual indexing noise, does extra lookup work, and
    # breaks completely on iterables that have no index (sets, generators, open
    # files). Python provides lazy built-in helpers that work on any iterable:
    #
    # - enumerate(iterable, start=0) wraps an iterable and yields (index, item)
    #   pairs lazily one at a time.
    # - zip(*iterables, strict=False) walks two or more iterables in lockstep
    #   and yields tuples of corresponding elements.
    #
    # Watch out for the silent-truncation trap in zip(): without strict=True,
    # zip() stops silently when the shortest input runs out, hiding mismatched
    # lengths in your data:
    #
    #     Suppose names = ["Alice", "Bob", "Cara"] and scores = [92, 85].
    #     list(zip(names, scores)) silently drops "Cara" and returns
    #     [("Alice", 92), ("Bob", 85)].
    #     Adding strict=True (Python 3.10+) raises ValueError the moment one
    #     iterable finishes before the others!

    for idx, label in enumerate(["alpha", "beta"], start=1):
        print(f"Starter item #{idx}: {label}")

    # Given names = ["Alice", "Bob", "Cara"] and scores = [92, 85, 98], iterate
    # in lockstep with:
    # for rank, (name, score) in enumerate(zip(names, scores, strict=True), start=1):
    # and print each ranked line (expected: 1: Alice = 92, etc.).


    # Practice multi-list zip across three parallel lists:
    # Bind items = ["pen", "book", "lamp"], prices = [1.5, 12.0, 25.0], and
    # qtys = [4, 2, 1]. Loop with for item, price, qty in zip(items, prices, qtys, strict=True):
    # to print each line total (price * qty) and accumulate a grand_total.


    # Observe silent truncation vs. strict=True:
    # First print list(zip([1, 2, 3], [10, 20])) to see 3 vanish silently.
    #
    # Try uncommenting below to trigger ValueError on mismatched lengths:
    # mismatched = list(zip([1, 2, 3], [10, 20], strict=True))


def unzipping_and_matrix_transposition() -> None:

    # The same zip() function also runs in reverse when paired with the call
    # unpacking operator (*). Putting * in front of a sequence inside a call
    # unpacks each element as a separate positional argument:
    #
    #     Suppose pairs = [("a", 1), ("b", 2)].
    #     Calling zip(*pairs) is identical to calling zip(("a", 1), ("b", 2)).
    #     Python pairs index 0s -> ("a", "b") and index 1s -> (1, 2), so
    #     letters, nums = zip(*pairs) unzips the pairs into two column tuples!
    #
    # That exact same trick transposes rows and columns of any rectangular
    # matrix. Keep one edge case in mind: if pairs is empty ([]), zip(*[])
    # yields zero tuples, so attempting a, b = zip(*[]) raises ValueError.

    sample_pairs = [("x", 1), ("y", 2)]
    xs, ys = zip(*sample_pairs, strict=True)
    print("Starter unzip:", xs, ys)

    # Unzip records = [("Alice", 92), ("Bob", 85), ("Cara", 98)] using
    # names_out, scores_out = zip(*records, strict=True)
    # Print names_out, scores_out, and type(names_out).__name__ (notice tuple!).


    # Transpose a 2x3 matrix into 3x2 columns and back again:
    # Bind rows = [(1, 2, 3), (4, 5, 6)] and compute
    # cols = list(zip(*rows, strict=True))
    # Print cols (expected: [(1, 4), (2, 5), (3, 6)]). Then transpose cols a
    # second time with list(zip(*cols, strict=True)) to confirm it matches rows.


    # Build a dictionary directly from parallel key and value sequences:
    # Bind keys = ["host", "port", "tls"] and vals = ["localhost", 8443, True],
    # create cfg = dict(zip(keys, vals, strict=True)), and print cfg.


def reversed_and_sorted_non_mutating() -> None:

    # Two everyday built-ins keep your original collections intact:
    # - reversed(seq) returns a lazy reverse iterator in O(1) memory without
    #   copying the whole sequence the way seq[::-1] does. It works on lists,
    #   tuples, strings, ranges, and insertion-ordered dicts (anything defining
    #   __reversed__ or supporting len + integer indexing).
    # - sorted(iterable, key=..., reverse=False) works on ANY iterable and
    #   returns a brand-new sorted list. Contrast that with items.sort() and
    #   items.reverse(), which mutate items in place and return None!
    #
    #     Suppose nums = [3, 1, 2].
    #     out = sorted(nums) gives out == [1, 2, 3] while nums stays [3, 1, 2].
    #     res = nums.sort() mutates nums to [1, 2, 3] and binds res = None!

    print("Starter reversed string:", "".join(reversed("Odin")))

    # Reverse names = ["Alice", "Bob", "Cara"] lazily with list(reversed(names))
    # and also check list(reversed(range(1, 5))).
    # Then sort scores = [92, 85, 98] descending with sorted(scores, reverse=True)
    # and print both the sorted copy and the untouched original scores list.


    # Sort words = ["fig", "apple", "pear", "banana"] by length first and
    # alphabetically on ties using sorted(words, key=lambda w: (len(w), w))
    # Print both the sorted result and words to confirm words was not modified.


    # Walk a dictionary backward in reverse insertion order:
    # Bind steps = {"init": 1, "parse": 2, "emit": 3} and iterate with
    # for name, step_no in reversed(steps.items()): printing each pair.


def any_and_all_short_circuit_reductions() -> None:

    # any(iterable) answers "is at least one element truthy?" and all(iterable)
    # answers "are every single one of these elements truthy?". Both helpers
    # short-circuit immediately:
    # - any() stops consuming the iterable at the very first truthy element.
    # - all() stops consuming the iterable at the very first falsy element.
    #
    # Always feed any() and all() a generator expression like (x > 0 for x in data)
    # rather than a list comprehension [x > 0 for x in data]: a list computes
    # every item up front, throwing away the speed win of short-circuiting!
    #
    # Watch the vacuous-truth edge case on empty iterables:
    # - all([]) is True (because there is zero counterexample in an empty list!).
    # - any([]) is False (because there is zero truthy witness in an empty list!).
    #
    #     Suppose batch = [] and you check if all(x > 0 for x in batch):
    #     Python evaluates True! Guard with bool(batch) and all(...) if an empty
    #     batch must count as False.

    print("Starter checks:", any([0, "", 5]), all([1, 2, 3]))

    # Given scores = [92, 85, 98], evaluate
    # all_passed = all(s >= 80 for s in scores)
    # has_top_score = any(s > 95 for s in scores)
    # and print both results.


    # Prove short-circuiting with a visible side-effect trace:
    # Create visited: list[int] = [] and define a helper:
    # def check_even(n: int) -> bool:
    # that appends n to visited and returns n % 2 == 0.
    # Call all(check_even(x) for x in [2, 4, 5, 6, 8]) and print the boolean
    # result plus visited (expected: [2, 4, 5], proving 6 and 8 were skipped!).
    # Clear visited with visited.clear(), then call
    # any(check_even(x) for x in [1, 3, 4, 7]) and print the result and visited
    # (expected: [1, 3, 4], stopping as soon as 4 returned True!).


    # Verify vacuous truth and write an emptiness guard:
    # Print all([]) and any([]) to confirm True and False.
    # Then test is_nonempty_positive = bool(batch) and all(x > 0 for x in batch)
    # for both batch = [] and batch = [3, 7] and print each result.


def main() -> None:

    print("=== 1. Enumerate and strict zip ===")
    enumerate_and_strict_zip()

    print("\n=== 2. Unzipping and matrix transposition ===")
    unzipping_and_matrix_transposition()

    print("\n=== 3. Non-mutating reversed and sorted ===")
    reversed_and_sorted_non_mutating()

    print("\n=== 4. Short-circuit any and all ===")
    any_and_all_short_circuit_reductions()


if __name__ == "__main__":
    main()
