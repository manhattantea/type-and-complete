# python 250_heapq_and_priority_queues.py

import heapq
from itertools import count


def min_heaps_and_stream_merges() -> None:

    # Python does not wrap priority queues in a separate Heap class; instead,
    # the heapq module operates directly in place on an ordinary Python list.
    # Every heapq function maintains the binary min-heap invariant:
    # heap[k] <= heap[2 * k + 1] and heap[k] <= heap[2 * k + 2] for every valid
    # index k. That guarantees heap[0] is ALWAYS the smallest element in O(1)
    # peek time, even though the rest of the list is only partially ordered:
    #
    #     Suppose nums = [9, 3, 5, 7].
    #     Running heapq.heapify(nums) rearranges nums in place in O(N) time so
    #     nums[0] == 3. Calling heapq.heappop(nums) removes and returns 3 in
    #     O(log N) time, promoting 5 to nums[0].
    #
    # Key operations to know:
    # - heapq.heapify(x): converts an unsorted list into a min-heap in O(N).
    # - heapq.heappush(h, item) / heapq.heappop(h): O(log N) insert / extract-min.
    # - heapq.heappushpop(h, item) (push then pop) and heapq.heapreplace(h, item)
    #   (pop then push): perform both steps in a single O(log N) sift.
    # - heapq.nlargest(n, it) / heapq.nsmallest(n, it): top-N selection without
    #   sorting the whole collection.
    # - heapq.merge(*sorted_iterables): lazily merges multiple already-sorted
    #   streams in O(1) memory per stream.
    # - Max-heap idiom: because heapq is strictly a min-heap, store negated
    #   numeric priorities (-priority) when you want largest values popped first.

    starter_heap = [9, 3, 5, 7]
    heapq.heapify(starter_heap)
    print("Starter min peek:", starter_heap[0], "raw heap:", starter_heap)

    # Heapify an unsorted list, push a new minimum, and extract the 3 smallest:
    # start with nums: list[int] = [25, 10, 40, 5, 30]. Call
    # heapq.heapify(nums), print nums[0], push 2 via heapq.heappush(nums, 2),
    # and pop 3 values with heapq.heappop(nums) printing each popped value.


    # Practice single-sift replacement, top-N selection, and lazy K-way merge:
    # call heapq.heappushpop(nums, 1) (returns 1 immediately because 1 < nums[0])
    # and heapq.heapreplace(nums, 50) (pops the current minimum first, then
    # inserts 50). Also print heapq.nlargest(2, [25, 10, 40, 5, 30]) and
    # list(heapq.merge([1, 4, 7], [2, 3, 8])).


    # Select top-N structured records using the key= parameter on nsmallest and
    # nlargest without sorting the entire list:
    # given tasks = [("parse", 45), ("render", 12), ("sync", 80), ("io", 5)],
    # print heapq.nsmallest(2, tasks, key=lambda row: row[1]) and
    # heapq.nlargest(2, tasks, key=lambda row: row[1]).


    # Simulate a max-heap by negating numbers:
    # build max_heap = [-n for n in [15, 40, 10, 30]], call
    # heapq.heapify(max_heap), and pop items printing -heapq.heappop(max_heap)
    # to verify descending order [40, 30, 15, 10].


    # Merge three pre-sorted timestamp streams lazily and take only the first
    # 5 combined events without sorting the full concatenation:
    # print list(heapq.merge([10, 50, 90], [20, 40, 80], [15, 35, 60]))[:5].


def priority_queues_and_tie_breakers() -> None:

    # Priority queues usually store (priority, payload) tuples so heapq orders
    # entries by priority first. That introduces a famous runtime crash: when
    # two entries have the SAME priority, Python breaks the tie by comparing
    # tuple slot [1]. If slot [1] is a dict (or any unorderable object), Python
    # immediately raises TypeError: '<' not supported between instances of
    # 'dict' and 'dict'!
    #
    # The standard fix uses itertools.count(), a lazy infinite counter yielding
    # 0, 1, 2, 3... on each next(tie_breaker) call. Storing 3-tuples
    # (priority, next(tie_breaker), task_dict) guarantees every tie resolves at
    # slot [1] in FIFO insertion order and NEVER compares task_dict:
    #
    #     Suppose job_a = (1, 0, {"job": "backup"}) and
    #     job_b = (1, 1, {"job": "alert"}).
    #     Comparing job_a < job_b checks 1 == 1, then 0 < 1 -> True, stopping
    #     before Python ever touches the dicts at slot [2]!

    starter_seq = count()
    print("Starter tie-breaker IDs:", next(starter_seq), next(starter_seq))

    # Build a crash-proof FIFO priority queue with itertools.count():
    # create pq: list[tuple[int, int, dict[str, str]]] = [] and
    # tie_breaker = count(). Push three jobs using heapq.heappush:
    # (2, next(tie_breaker), {"job": "email"}),
    # (1, next(tie_breaker), {"job": "backup"}), and
    # (1, next(tie_breaker), {"job": "alert"}).
    # Pop all three in a while pq: loop with heapq.heappop(pq) and print each
    # entry to verify "backup" runs before "alert" with zero TypeError.


    # Verify the equal-priority dict comparison crash directly:
    # Try uncommenting the two lines below to observe TypeError when two jobs
    # share priority 1 without a tie-breaker:
    # bad_pq: list[tuple[int, dict[str, str]]] = [(1, {"job": "backup"})]
    # heapq.heappush(bad_pq, (1, {"job": "alert"}))


def main() -> None:

    print("=== 1. Min-heaps, top-N, merges, and max-heap negation ===")
    min_heaps_and_stream_merges()

    print("\n=== 2. Priority queues and itertools.count tie-breakers ===")
    priority_queues_and_tie_breakers()


if __name__ == "__main__":
    main()
