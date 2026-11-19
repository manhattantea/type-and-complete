# python 280_mutation_during_iteration_and_defensive_copies.py


def silent_list_skip_bug() -> None:

    # Modifying a container while looping over it does NOT behave the same way
    # across Python's built-in collections: dict and set fail loudly with
    # RuntimeError, whereas list fails SILENTLY and corrupts your result!
    #
    # Here is why a list iterator silently skips items: under the hood, a
    # list_iterator simply keeps a private integer index i = 0, 1, 2...
    #
    #     Suppose nums = [2, 4, 5, 6] and you run:
    #         for n in nums:
    #             if n % 2 == 0:
    #                 nums.remove(n)
    #     - Step i = 0: reads nums[0] (2), removes 2; trailing items slide left
    #       so nums is now [4, 5, 6].
    #     - Step i = 1: iterator increments i to 1, reading nums[1] (5) and
    #       COMPLETELY SKIPPING 4, which just slid into index 0!
    #     - Step i = 2: reads nums[2] (6), removes 6, leaving [4, 5].
    #     - Step i = 3: 3 >= len(nums), loop exits with even number 4 still in
    #       the list!

    starter_vals = [1, 2, 3, 4]
    print("Starter list ready:", starter_vals)

    # Reproduce the silent list-iterator skip bug directly:
    # create buggy_nums: list[int] = [2, 4, 5, 6], loop with
    # for n in buggy_nums: calling buggy_nums.remove(n) whenever n % 2 == 0,
    # and print buggy_nums afterward to see it silently leave [4, 5] instead of
    # [5].


    # Observe the flip side — appending to a list while iterating over it
    # chases a moving end boundary forever unless you iterate over a snapshot:
    # create growing: list[int] = [1, 2] and steps = 0. Loop for x in growing:
    # appending x * 10, incrementing steps += 1, and breaking when steps == 5
    # so the loop cannot run forever; print growing to see it grew mid-loop!


def safe_list_filtering_and_in_place_compaction() -> None:

    # Reach for one of three safe patterns whenever you need to filter or prune
    # a list:
    # - Comprehension filtering (fastest, O(N)): build a new list
    #   items = [x for x in items if keep(x)], OR assign to a whole-list slice
    #   items[:] = [x for x in items if keep(x)] when external aliases MUST see
    #   the in-place mutation without changing id(items)!
    # - Shallow defensive slice copy: for x in items[:]: iterates over a copied
    #   snapshot while mutating items. Clean for rare removals, though calling
    #   items.remove(x) repeatedly degrades to O(N^2) because every .remove()
    #   scans from index 0 and shifts trailing elements left.
    # - Reverse-index deletion: for i in range(len(items) - 1, -1, -1): deletes
    #   from the tail toward index 0 with del items[i], so shifting elements at
    #   indices > i never changes the indices you have yet to visit.
    #
    #     Suppose items = [2, 4, 5, 6] and alias = items.
    #     items[:] = [n for n in items if n % 2 != 0] leaves items == [5],
    #     alias == [5], and alias is items == True.

    starter_target = [10, 20, 30]
    starter_alias = starter_target
    starter_target[:] = [x for x in starter_target if x > 10]
    print("Starter in-place slice filter:", starter_alias, "same object?", starter_alias is starter_target)

    # Filter a list in place in O(N) while preserving object identity for
    # aliases:
    # create clean_nums: list[int] = [2, 4, 5, 6], bind alias = clean_nums, and
    # record before_id = id(clean_nums). Assign
    # clean_nums[:] = [n for n in clean_nums if n % 2 != 0], then print
    # clean_nums, alias, and id(clean_nums) == before_id (True).


    # Contrast slice assignment (items[:] = [...]) with plain rebinding
    # (items = [...]):
    # create rebound: list[int] = [2, 4, 5, 6] and stale_alias = rebound.
    # Rebind rebound = [n for n in rebound if n % 2 != 0] and print both
    # rebound ([5]) and stale_alias ([2, 4, 5, 6]) to prove plain rebinding
    # leaves external references pointing at the old unfiltered list!


    # Practice defensive shallow-copy iteration when imperative removal is
    # clearer:
    # create slice_nums: list[int] = [2, 4, 5, 6], loop for n in slice_nums[:]:
    # calling slice_nums.remove(n) when n % 2 == 0, and print slice_nums ([5]).


    # Practice reverse-index deletion from tail to head:
    # create rev_nums: list[int] = [2, 4, 5, 6], loop
    # for i in range(len(rev_nums) - 1, -1, -1): deleting with del rev_nums[i]
    # whenever rev_nums[i] % 2 == 0, and print rev_nums to verify [5].


def dict_and_set_runtimeerror_guards() -> None:

    # Unlike list, both dict and set iterators snapshot the container's size
    # (and table state) when iteration starts. Adding or deleting keys mid-loop
    # could trigger a hash-table resize or rehash, so CPython raises
    # RuntimeError immediately instead of silently skipping entries:
    #
    #     Suppose scores = {"alice": 10, "bob": 3}.
    #     Running del scores["bob"] directly inside for name in scores: raises
    #     RuntimeError: dictionary changed size during iteration.
    #     Iterating over a snapshot list instead — for name in list(scores): —
    #     walks a separate list of keys so deleting from scores is completely
    #     safe!
    #
    # One practical nuance: overwriting an EXISTING key's value (d[k] = new_val)
    # does NOT change the dictionary's size and is safe during iteration—only
    # inserting or removing keys triggers RuntimeError.

    starter_map = {"a": 1, "b": 2}
    for key in starter_map:
        starter_map[key] *= 10
    print("Starter safe value update:", starter_map)

    # Trigger RuntimeError on a dict, then fix it with a list(d) key snapshot:
    # create scores: dict[str, int] = {"alice": 10, "bob": 3, "cara": 12, "dan": 4}.
    # Wrap a direct deletion loop:
    # for name, pts in scores.items(): if pts < 5: del scores[name]
    # inside try / except RuntimeError as err: and print err.
    # Next reset scores = {"alice": 10, "bob": 3, "cara": 12, "dan": 4}, remove
    # every entry with score < 5 safely using for name in list(scores):, and
    # print scores (expected: {"alice": 10, "cara": 12}).


    # Trigger RuntimeError on a set, then fix it with a list(s) snapshot:
    # create active_ids: set[int] = {101, 102, 103, 104}.
    # Wrap a direct removal loop:
    # for item in active_ids: if item % 2 == 0: active_ids.remove(item)
    # inside try / except RuntimeError as err: and print err.
    # Next reset active_ids = {101, 102, 103, 104}, remove even IDs safely via
    # for item in list(active_ids):, and print active_ids (expected: {101, 103}).


    # Practice bulk in-place set pruning without allocating a snapshot loop:
    # create tags: set[str] = {"draft", "live", "stale", "archived"}, bind
    # tags_alias = tags, compute to_drop = {t for t in tags if t in {"draft", "stale"}},
    # call tags.difference_update(to_drop), and print tags alongside
    # tags_alias is tags (True — mutated safely in place!).


def main() -> None:

    print("=== 1. The silent list-iterator skip bug ===")
    silent_list_skip_bug()

    print("\n=== 2. Safe list filtering and in-place compaction ===")
    safe_list_filtering_and_in_place_compaction()

    print("\n=== 3. dict and set RuntimeError guards ===")
    dict_and_set_runtimeerror_guards()


if __name__ == "__main__":
    main()
