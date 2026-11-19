# python 260_itertools_combinatorics_and_streams.py

import itertools


def lazy_stream_combinators() -> None:

    # Building intermediate lists at every stage of a data pipeline allocates
    # extra memory and copies references over and over. Python's itertools
    # module provides C-implemented lazy combinators that pull one element at a
    # time in O(1) extra memory until you materialize the final result.
    #
    # Everyday stream combinators and what each one does:
    # - itertools.chain.from_iterable(chunks): flattens one nesting level
    #   lazily without unpacking every sub-iterable up front (preferred over
    #   chain(*chunks) when chunks itself is a generator).
    # - itertools.islice(it, start, stop, step): slices any iterator or
    #   infinite stream lazily (negative indices are disallowed because an
    #   arbitrary stream has no known length).
    # - itertools.batched(it, n) (Python 3.12+): groups any iterable into
    #   tuples of up to n items (the final tuple may be shorter).
    # - itertools.pairwise(it): yields overlapping (prev, curr) pairs:
    #       Suppose readings = [10, 25, 20].
    #       list(itertools.pairwise(readings)) yields [(10, 25), (25, 20)].
    # - itertools.accumulate(it, func=..., initial=...): yields running prefix
    #   reductions (running sums by default).
    # - itertools.zip_longest(*its, fillvalue=None): zips uneven iterables all
    #   the way to the longest input, padding shorter ones with fillvalue.
    # - itertools.takewhile(pred, it): yields items while pred(x) stays True,
    #   then stops PERMANENTLY at the first False item (unlike filter(), which
    #   keeps scanning later items!).

    print("Starter batched:", list(itertools.batched(range(7), 3)))
    print("Starter pairwise:", list(itertools.pairwise([10, 25, 20])))

    # Flatten nested chunks lazily and compose batched, pairwise, accumulate,
    # and islice:
    # given chunks = [[1, 2], [3, 4, 5], [6]], print
    # list(itertools.chain.from_iterable(chunks)).
    # Then print list(itertools.batched(range(10), 4)), consecutive deltas
    # [b - a for a, b in itertools.pairwise([10, 25, 20, 40])], running totals
    # list(itertools.accumulate([1, 2, 3, 4])), and the first 4 values of an
    # infinite counter via list(itertools.islice(itertools.count(100, 5), 4)).


    # Pair uneven iterables with zip_longest and contrast takewhile vs filter:
    # given names = ["Ada", "Alan", "Grace"] and scores = [98, 92], print
    # list(itertools.zip_longest(names, scores, fillvalue=0)).
    # Next scan readings = [12, 18, 25, 99, 14, 10] with
    # list(itertools.takewhile(lambda v: v < 50, readings)) and compare it to
    # list(filter(lambda v: v < 50, readings)) to confirm takewhile stops at 99
    # and never yields 14 or 10.


    # Practice custom reducers in accumulate and dropwhile on a header stream:
    # print list(itertools.accumulate([4, 2, 9, 3, 11], max)) for a running
    # maximum, then strip leading comment lines from
    # lines = ["# hdr1", "# hdr2", "row1", "# inline", "row2"] using
    # list(itertools.dropwhile(lambda line: line.startswith("#"), lines))
    # (notice "# inline" stays because dropwhile only skips the leading prefix!).


    # Chain a multi-stage zero-allocation pipeline without intermediate lists:
    # given batches = [[5, 10], [15, 20], [25, 30], [35, 40]], compose
    # flat = itertools.chain.from_iterable(batches),
    # capped = itertools.takewhile(lambda n: n <= 30, flat), and
    # print list(itertools.batched(capped, 2)).


def combinatorics_without_nested_loops() -> None:

    # Deeply nested for loops are noisy and hard to refactor when dimensions
    # change. itertools replaces them with three lazy combinatorial generators:
    # - itertools.product(*iterables, repeat=1): yields the Cartesian product
    #   (equivalent to nested for loops over each iterable).
    # - itertools.combinations(it, r): yields unordered r-length tuples with no
    #   repeated elements (so ("A", "B") appears, while ("B", "A") does not).
    # - itertools.permutations(it, r): yields all ordered r-length arrangements
    #   (both ("A", "B") and ("B", "A") appear).
    #
    #     Suppose items = ["A", "B", "C"].
    #     combinations(items, 2) yields 3 pairs: (A, B), (A, C), (B, C).
    #     permutations(items, 2) yields 6 ordered pairs including (B, A).

    print("Starter product:", list(itertools.product(["x", "y"], [1, 2])))

    # Print list(itertools.combinations(["A", "B", "C"], 2)),
    # list(itertools.permutations(["A", "B", "C"], 2)), and all 2-bit binary
    # pairs via list(itertools.product([0, 1], repeat=2)).


    # Replace a nested 2D grid loop with itertools.product:
    # loop using for row, col in itertools.product(range(3), range(3)): to
    # collect every off-diagonal coordinate (where row != col) into a list and
    # print the result.


def groupby_sorting_and_exhaustion_trap() -> None:

    # itertools.groupby(iterable, key=...) catches almost every Python learner
    # at least once because it does NOT behave like SQL GROUP BY!
    #
    # First trap — consecutive keys only:
    # itertools.groupby behaves like Unix uniq: it only merges adjacent items
    # that produce the same key. If matching keys are separated by another key,
    # groupby emits multiple fragmented runs:
    #
    #     Suppose data = [("a", 1), ("b", 2), ("a", 3)].
    #     groupby(data, key=lambda r: r[0]) yields THREE groups: "a", "b", "a"!
    #     Sorting first with sorted(data, key=lambda r: r[0]) puts all "a"
    #     rows together so groupby produces just TWO groups: "a" and "b".
    #
    # Second trap — shared inner iterator invalidation:
    # Each inner group iterator shares its cursor with the outer groupby
    # stream. The moment the outer loop advances to the next key, the previous
    # group iterator becomes empty! Always consume or convert it (such as
    # list(group)) immediately inside the loop body.

    starter_runs = [(k, list(g)) for k, g in itertools.groupby("AAABBA")]
    print("Starter consecutive runs:", starter_runs)

    # Reproduce the unsorted groupby fragmentation trap, then fix it:
    # given records: list[tuple[str, str]] = [("fruit", "apple"), ("veg", "carrot"), ("fruit", "banana"), ("veg", "pea")],
    # first print [(k, list(g)) for k, g in itertools.groupby(records, key=lambda r: r[0])]
    # to watch "fruit" and "veg" fragment into 4 separate runs.
    # Next sort sorted_records = sorted(records, key=lambda r: r[0]) and build
    # grouped: dict[str, list[str]] = {k: [item for _, item in grp] for k, grp in itertools.groupby(sorted_records, key=lambda r: r[0])},
    # then print grouped to verify just two clean groups.


    # Prove inner group iterator invalidation directly:
    # save raw iterators without materializing them inside the loop:
    # raw_groups = list(itertools.groupby("AAABBB"))
    # Then print [(k, list(g)) for k, g in raw_groups] and observe that the
    # first group "A" is now empty [] because advancing to "B" exhausted it!


def main() -> None:

    print("=== 1. Lazy stream combinators ===")
    lazy_stream_combinators()

    print("\n=== 2. Combinatorics without nested loops ===")
    combinatorics_without_nested_loops()

    print("\n=== 3. groupby pre-sorting and inner-iterator traps ===")
    groupby_sorting_and_exhaustion_trap()


if __name__ == "__main__":
    main()
