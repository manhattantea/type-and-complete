# python 270_sorting_timsort_and_stability.py


def in_place_sort_vs_sorted_and_none_trap() -> None:

    # Python's list.sort(*, key=None, reverse=False) and built-in
    # sorted(iterable, *, key=None, reverse=False) share the same C sorting
    # engine (Timsort / powersort), which exploits already-sorted runs in
    # real-world data in O(N log N) worst-case and O(N) best-case time.
    #
    # Two classic pitfalls trip up almost everyone at first:
    # - Why list.sort() returns None: items.sort() mutates the list in place
    #   and deliberately returns None (just like .append() and .reverse()) so
    #   you never write result = items.sort() thinking you built a separate
    #   sorted copy. Call sorted(iterable) whenever you want a brand-new list
    #   (it also accepts any iterable, such as a tuple, set, or string).
    # - The Python 3 None comparison trap: comparing None < 10 OR even
    #   None < None raises TypeError! That means a naive key function like
    #   key=lambda x: (x is None, x) STILL crashes whenever TWO None values
    #   appear in the same list:
    #
    #       Suppose vals = [42, None, 7, None].
    #       Both Nones map to (True, None). When Timsort compares them, slot 0
    #       ties (True == True), so it compares slot 1: None < None -> TypeError!
    #       Replacing slot 1 with a safe fallback:
    #       key=lambda x: (x is None, 0 if x is None else x)
    #       maps None to (True, 0), so False < True puts all real numbers first
    #       and ties compare 0 < 0 safely without ever comparing None.

    starter_nums = [3, 1, 2]
    print("Starter sorted():", sorted(starter_nums), "original:", starter_nums)

    # Confirm list.sort() mutates in place and returns None, while sorted()
    # works on any iterable:
    # bind copy_a = [30, 10, 20], run ret = copy_a.sort(), and print ret (None)
    # alongside copy_a ([10, 20, 30]). Also print sorted("python") to verify
    # sorted() returns a new list of characters from a string.


    # Sort a list containing multiple None values safely, and witness the naive
    # key crash:
    # given values_with_nones: list[int | None] = [42, None, 7, None, 19, 0],
    # print sorted(values_with_nones, key=lambda x: (x is None, 0 if x is None else x))
    # to confirm all integers come first and both Nones land at the end.
    # Then wrap sorted(values_with_nones, key=lambda x: (x is None, x)) inside
    # try / except TypeError as err: and print err to verify why two Nones
    # break the naive tuple key.


    # Apply the same None-safe pattern to records with an optional due day and
    # practice case-insensitive text sorting with key=str.casefold:
    # given tasks = [("docs", None), ("build", 2), ("lint", None), ("test", 1)],
    # sort tasks by due day ascending with Nones last using
    # key=lambda row: (row[1] is None, 0 if row[1] is None else row[1]), and
    # sort names = ["bob", "Alice", "cara", "ALICE"] with key=str.casefold to
    # see "Alice" stay ahead of "ALICE" thanks to Timsort stability!


def timsort_stability_and_multi_key_sorts() -> None:

    # Timsort is strictly STABLE: whenever two items produce equal sort keys,
    # their original relative order is preserved.
    #
    # Stability gives you a clean way to build complex multi-column sorts with
    # mixed ascending and descending directions—even for strings or dates where
    # numeric negation (-x) is impossible! Just run multiple passes from LEAST
    # significant key to MOST significant key:
    #
    #     Suppose rows = [("bob", 90), ("alice", 90), ("cara", 95)].
    #     Pass 1 (secondary key — name ascending):
    #         rows.sort(key=lambda r: r[0]) -> [("alice", 90), ("bob", 90), ("cara", 95)]
    #     Pass 2 (primary key — score descending):
    #         rows.sort(key=lambda r: r[1], reverse=True)
    #         -> [("cara", 95), ("alice", 90), ("bob", 90)]
    #     Because Timsort is stable, ("alice", 90) stays ahead of ("bob", 90)
    #     when their primary score keys tie!

    starter_pairs = [("b", 1), ("a", 1), ("c", 0)]
    print("Starter stable sort:", sorted(starter_pairs, key=lambda r: r[1]))

    # Compare a single tuple key against two stable passes on mixed directions:
    # given scores: list[tuple[str, int]] = [("cara", 90), ("alice", 95), ("bob", 90), ("alice", 80)],
    # sort by score descending and player name ascending in two ways:
    # first compute by_tuple = sorted(scores, key=lambda row: (-row[1], row[0])).
    # Next copy by_stability = scores.copy(), run
    # by_stability.sort(key=lambda row: row[0]) (secondary ascending), then run
    # by_stability.sort(key=lambda row: row[1], reverse=True) (primary
    # descending). Print both lists and verify by_tuple == by_stability.


    # Use two-pass stability where unary minus is impossible (sorting strings
    # in opposite directions):
    # given tickets = [("infra", "low"), ("api", "high"), ("api", "low"), ("infra", "high")],
    # copy into ordered = tickets.copy(), sort first by priority ascending
    # (key=lambda t: t[1]), then by team descending
    # (key=lambda t: t[0], reverse=True), and print ordered.


    # Verify stability on string lengths without needing a tuple key:
    # given words = ["pear", "fig", "plum", "kiwi", "apple"], sort with
    # sorted(words, key=len) and confirm equal-length words ("pear", "plum",
    # "kiwi") remain in their exact original relative order.


def main() -> None:

    print("=== 1. list.sort() vs sorted() and the None comparison trap ===")
    in_place_sort_vs_sorted_and_none_trap()

    print("\n=== 2. Timsort stability and multi-pass sorting ===")
    timsort_stability_and_multi_key_sorts()


if __name__ == "__main__":
    main()
