# python 245_collections_deque_and_bisect.py

import bisect
from collections import deque


def deque_ends_and_rotation() -> None:

    # A Python list stores a single contiguous C array of PyObject* pointers.
    # Appending or popping at the right end is O(1) amortized, but inserting or
    # popping at index 0 (items.pop(0)) has to slide every remaining pointer
    # left by one slot in O(N) time.
    #
    # collections.deque ("double-ended queue") solves this by using a
    # doubly-linked list of fixed-size pointer blocks (64 pointers per block in
    # CPython). That layout delivers O(1) .append(), .appendleft(), .pop(),
    # .popleft(), and .rotate(k) at BOTH ends:
    #
    #     Suppose q = deque(["A", "B", "C", "D"]).
    #     Calling q.rotate(1) moves 1 item from the right end to the left end,
    #     producing deque(["D", "A", "B", "C"]).
    #     Calling q.rotate(-1) shifts 1 item from left to right, restoring
    #     deque(["A", "B", "C", "D"]).
    #
    # The trade-off for fast ends is middle access: indexing d[len(d) // 2]
    # walks linked blocks from the nearest end in O(N) time, and slice syntax
    # like d[1:3] is unsupported (raising TypeError).

    starter_q: deque[str] = deque(["a", "b"])
    starter_q.appendleft("start")
    print("Starter deque:", starter_q)

    # Practice O(1) FIFO queue operations and rotation:
    # create work_queue: deque[str] = deque(["job_1", "job_2"]), append
    # "job_3" on the right, pop from the left with work_queue.popleft(), rotate
    # right by 1 via work_queue.rotate(1), and print work_queue.


    # Use a deque as a clean breadth-first work queue:
    # start with pending: deque[str] = deque(["root"]) and an adjacency map
    # graph = {"root": ["left", "right"], "left": ["leaf_1"], "right": ["leaf_2"], "leaf_1": [], "leaf_2": []}.
    # Loop while pending:, pop node = pending.popleft(), append it to
    # visited: list[str] = [], and extend pending with graph[node]. Print
    # visited to verify breadth-first order.
    #
    # Try uncommenting below to confirm deque rejects slice syntax with TypeError:
    # bad_slice = work_queue[0:2]


def bounded_ring_buffers_with_maxlen() -> None:

    # Passing maxlen=N to deque(iterable, maxlen=N) turns it into a fixed-size
    # O(1) ring buffer. Once len(d) == maxlen, adding a new item on one end
    # automatically evicts the oldest item from the opposite end without
    # shifting memory:
    #
    #     Suppose ring = deque([10, 20], maxlen=2).
    #     Calling ring.append(30) drops 10 from the left -> deque([20, 30], maxlen=2).
    #     Calling ring.appendleft(5) drops 30 from the right -> deque([5, 20], maxlen=2).
    #
    # This makes deque(maxlen=N) ideal for "last N log lines", undo history,
    # and streaming sliding-window metrics.

    starter_ring: deque[int] = deque([10, 20], maxlen=2)
    starter_ring.append(30)
    print("Starter bounded deque:", list(starter_ring))

    # Observe automatic eviction on a bounded log buffer:
    # create recent_logs: deque[str] = deque(maxlen=3), loop over
    # ["e1", "e2", "e3", "e4", "e5"] appending each string, and print
    # list(recent_logs) (expected: ["e3", "e4", "e5"]).
    # Then call recent_logs.appendleft("urgent") and print list(recent_logs) to
    # confirm "e5" was evicted from the right end.


    # Compute a streaming 3-sample moving average using a bounded deque:
    # create window: deque[float] = deque(maxlen=3) and iterate over
    # readings = [10.0, 12.0, 14.0, 20.0, 22.0]. Append each value to window;
    # whenever len(window) == 3, compute sum(window) / 3 and collect it into
    # averages: list[float] = []. Print averages (expected: [12.0, 15.33..., 18.66...]).


def bisect_binary_search_and_insort() -> None:

    # When a list is ALREADY sorted, scanning it linearly takes O(N) time,
    # whereas the bisect module finds insertion points in O(log N) comparisons
    # via binary search.
    #
    # Understanding bisect_left vs bisect_right is the whole secret to bisect:
    #
    #     Suppose nums = [10, 20, 20, 30] and you search for x = 20.
    #     - bisect.bisect_left(nums, 20) returns 1 (the slot BEFORE existing 20s).
    #     - bisect.bisect_right(nums, 20) returns 3 (the slot AFTER existing 20s).
    #     Notice that bisect_right - bisect_left (3 - 1 = 2) equals the exact
    #     frequency of 20 in the sorted list!
    #
    # Because bisect_right advances past exact boundary matches, it maps
    # numeric intervals cleanly to buckets (a score of 60 lands after the 60
    # breakpoint, entering bucket "D").
    #
    # bisect.insort(a, x) locates the insertion point in O(log N) and then
    # inserts x into list a in O(N) time (still requiring a list shift). Both
    # bisect_* and insort accept an optional key=... function (Python 3.10+)
    # for searching sorted records by a field.

    starter_sorted = [10, 20, 20, 30]
    print(
        "Starter bisect bounds for 20:",
        bisect.bisect_left(starter_sorted, 20),
        bisect.bisect_right(starter_sorted, 20),
    )

    # Turn sorted numeric thresholds into an O(log N) grade lookup table:
    # given breakpoints = [60, 70, 80, 90] and
    # grades = ["F", "D", "C", "B", "A"], compute the grade for each score in
    # scores = [55, 60, 75, 89, 92] using
    # grades[bisect.bisect_right(breakpoints, score)] and print the
    # (score, grade) pairs (notice why 60 maps to "D" and 55 maps to "F"!).


    # Maintain a sorted leaderboard and inspect duplicate bounds:
    # start with leaderboard: list[int] = [100, 250, 400], insert 175 and 250
    # using bisect.insort(leaderboard, ...), and print leaderboard alongside
    # bisect.bisect_left(leaderboard, 250) and
    # bisect.bisect_right(leaderboard, 250).


    # Write a clean O(log N) exact-membership helper using bisect_left:
    # define def contains_sorted(items: list[int], target: int) -> bool:
    # compute idx = bisect.bisect_left(items, target) and return
    # idx < len(items) and items[idx] == target (checking idx < len(items)
    # first prevents IndexError when target is larger than every item!).
    # Test it on leaderboard with 250, 300, and 999.


    # Search a sorted list of records using the key= parameter:
    # given events = [("boot", 100), ("auth", 250), ("sync", 400), ("done", 650)],
    # find the first event at or after timestamp 300 using
    # idx = bisect.bisect_left(events, 300, key=lambda row: row[1]) and print
    # events[idx].


def main() -> None:

    print("=== 1. deque O(1) ends and rotation ===")
    deque_ends_and_rotation()

    print("\n=== 2. Bounded ring buffers with maxlen ===")
    bounded_ring_buffers_with_maxlen()

    print("\n=== 3. bisect binary search and insort ===")
    bisect_binary_search_and_insort()


if __name__ == "__main__":
    main()
