# python 200_lists_dynamic_arrays_and_aliasing.py

import sys


def dynamic_array_growth_and_size() -> None:

    # Coming from C, Odin, or Rust, it is easy to guess that a Python list
    # might be a linked list because it holds mixed types and grows freely.
    # Under the hood in CPython, a list is actually a contiguous, dynamically
    # resized C array of PyObject pointers (each slot is an 8-byte pointer on
    # 64-bit systems pointing out to a heap-allocated object).
    #
    # Because the slots sit side by side in memory:
    # - Indexing items[i] is O(1) pointer arithmetic.
    # - Calling .append(x) or .pop() at the back is O(1) amortized, because
    #   CPython over-allocates extra spare slots (~12.5% plus a small constant)
    #   whenever the backing pointer array runs out of room.
    # - Inserting or removing at index 0 with items.insert(0, x) or items.pop(0)
    #   is O(N), because every remaining pointer must be shifted right or left.
    #   Reach for collections.deque whenever you need a fast FIFO queue.
    #
    # sys.getsizeof(obj) returns the memory size of the list header and its
    # backing pointer array in bytes (excluding the heap objects pointed to).
    #
    #     Suppose buf = [] starts at 56 bytes on 64-bit CPython.
    #     When you append the first element, CPython jumps straight to 4 slots
    #     (88 bytes) so the next 3 appends need zero reallocation.

    starter: list[int] = []
    print("Empty list byte size:", sys.getsizeof(starter))

    # Measure CPython's over-allocation pattern yourself:
    # create growing: list[int] = [] and track prev_size = sys.getsizeof(growing).
    # Loop with for i in range(32): appending i via growing.append(i).
    # Whenever sys.getsizeof(growing) != prev_size, print len(growing) and the
    # new byte size, then update prev_size so you see the exact growth jumps.


    # Verify O(1) indexing and negative indexing on the populated list:
    # print growing[0], growing[-1], and len(growing).


def core_list_mutations_and_lookups() -> None:

    # Everyday list methods fall into two groups: methods that mutate the list
    # in place (and return None, except .pop()) and methods that inspect it.
    #
    # Watch the difference between .append(x) and .extend(iterable):
    # - items.append(x) adds x as one single slot, even if x is itself a list.
    # - items.extend(iterable) loops over iterable and appends each element.
    #
    #     Suppose nums = [1, 2].
    #     nums.append([3, 4]) turns nums into [1, 2, [3, 4]] (length 3).
    #     nums.extend([3, 4]) turns nums into [1, 2, 3, 4] (length 4).
    #
    # For removal and lookup:
    # - items.insert(index, x) shifts slots from index onward right by one.
    # - items.pop() removes and returns the last item; items.pop(i) removes
    #   and returns the item at index i (raising IndexError if out of range).
    # - items.remove(value) scans left-to-right and removes the FIRST matching
    #   value, raising ValueError if the value is not present.
    # - items.index(value) returns the index of the first matching value, and
    #   also raises ValueError when absent (unlike str.find which returns -1).
    # - items.clear() empties the list in place so any aliases see [].

    tasks: list[str] = ["build", "test"]
    tasks.append("ship")
    print("Starter tasks:", tasks)

    # Contrast .append() and .extend() on two separate lists:
    # create a: list[object] = [1, 2] and b: list[int] = [1, 2].
    # Call a.append([3, 4]) and b.extend([3, 4]), then print a, len(a), b,
    # and len(b) to observe the structural difference.


    # Practice .insert(), .pop(), .remove(), and .clear() in sequence:
    # start with queue: list[str] = ["b", "c", "b", "d"].
    # Insert "a" at index 0 with queue.insert(0, "a"), remove the first "b"
    # with queue.remove("b"), pop the last item into last = queue.pop(), and
    # print queue and last. Then keep an alias mirror = queue, call
    # queue.clear(), and print both queue and mirror to confirm in-place clearing.


    # Test .index() on both a present and missing value:
    # create tags: list[str] = ["fast", "safe", "tiny"].
    # Print tags.index("safe"). Next, wrap tags.index("missing") inside
    # try: / except ValueError as exc: and print the caught error so you see
    # why checking if "missing" in tags: (or catching ValueError) is required.


def multiplication_aliasing_traps() -> None:

    # Multiplying a list with seq * n repeats the object references stored in
    # seq n times—it never deep-copies the elements.
    #
    # Writing [0] * 3 is completely safe because 0 is an immutable int: sharing
    # 3 pointers to 0 cannot cause spooky action at a distance, because
    # assigning row[0] = 99 simply replaces slot 0's pointer with a pointer to
    # 99 without modifying the integer 0.
    #
    # Writing [[0] * 3] * 3 or [{}] * 3 is a classic bug: Python evaluates the
    # inner [0] * 3 or {} ONCE, then copies that single pointer into all 3
    # outer slots!
    #
    #     Suppose bad_buckets = [{}] * 3.
    #     All 3 slots point to the exact same dict object in memory.
    #     Running bad_buckets[0]["hits"] = 1 turns bad_buckets into
    #     [{"hits": 1}, {"hits": 1}, {"hits": 1}]!
    #
    # A list comprehension like [[0] * 3 for _ in range(3)] or
    # [{} for _ in range(3)] re-evaluates the inner expression on every pass,
    # allocating a fresh mutable container for each slot.

    safe_zeros: list[int] = [0] * 3
    safe_zeros[0] = 7
    print("Safe immutable repetition:", safe_zeros)

    # Reproduce the 2D list multiplication trap using id() to inspect each row:
    # create bad_grid: list[list[int]] = [[0] * 3] * 3, assign
    # bad_grid[0][0] = 99, and print bad_grid alongside
    # [id(row) for row in bad_grid] to see every row change together.


    # Fix the 2D grid with a comprehension:
    # create good_grid: list[list[int]] = [[0] * 3 for _ in range(3)], assign
    # good_grid[0][0] = 99, and print good_grid alongside
    # [id(row) for row in good_grid] to confirm distinct ids and isolated row 0.


    # Reproduce and fix the [{}] * 3 shared-dict trap:
    # create bad_buckets: list[dict[str, int]] = [{}] * 3, set
    # bad_buckets[0]["count"] = 5, and print bad_buckets and
    # bad_buckets[0] is bad_buckets[1].
    # Then build good_buckets: list[dict[str, int]] = [{} for _ in range(3)],
    # set good_buckets[0]["count"] = 5, and print good_buckets to verify
    # buckets 1 and 2 remain empty.


def in_place_iadd_vs_rebind_concat() -> None:

    # Unlike immutable ints (where x += 1 always rebinds x to a new int object),
    # a list implements __iadd__ so a += b mutates the existing list IN PLACE
    # (behaving just like a.extend(b)), whereas a = a + b allocates a brand-new
    # list and rebinds only the name a.
    #
    #     Suppose a = [1, 2] and b = a (both names point to the same list).
    #     Running a += [3] mutates that shared list to [1, 2, 3], so b becomes
    #     [1, 2, 3] too and a is b stays True.
    #     Running a = a + [4] builds a new [1, 2, 3, 4] and rebinds a, leaving
    #     b as [1, 2, 3] so a is b becomes False.
    #
    # Notice one extra detail: a += (5, 6) accepts any iterable (just like
    # .extend()), whereas a + (5, 6) raises TypeError because list + tuple is
    # forbidden.

    left: list[int] = [10, 20]
    combined = left + [30]
    print("New list via +:", combined, "left untouched:", left)

    # Contrast += and + with an active alias:
    # create a: list[int] = [1, 2] and bind b = a.
    # Execute a += [3] and print a, b, and a is b (expected: True).
    # Next, execute a = a + [4] and print a, b, and a is b (expected: False).


    # Verify that += accepts non-list iterables while + rejects them:
    # execute a += (5, 6) and print a.
    #
    # Try uncommenting the line below to observe TypeError:
    # bad = a + (7, 8)


def main() -> None:

    print("=== 1. Dynamic array growth and byte size ===")
    dynamic_array_growth_and_size()

    print("\n=== 2. Core list mutations and lookups ===")
    core_list_mutations_and_lookups()

    print("\n=== 3. Multiplication aliasing traps ===")
    multiplication_aliasing_traps()

    print("\n=== 4. In-place += vs. rebinding + ===")
    in_place_iadd_vs_rebind_concat()


if __name__ == "__main__":
    main()
