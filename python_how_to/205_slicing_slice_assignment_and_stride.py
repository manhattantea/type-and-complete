# python 205_slicing_slice_assignment_and_stride.py


def shallow_slice_copies_and_clamping() -> None:

    # In systems languages like Odin, Go, or Rust, slicing an array creates a
    # zero-copy view pointing directly into the backing memory. In Python,
    # slicing a list with sub = items[1:4] works differently: it allocates a
    # brand-new list object and copies the selected element pointers into it.
    # (When you genuinely want a zero-copy view in Python, reach for memoryview
    # over a bytes-like buffer object.)
    #
    # Two practical consequences follow immediately:
    # - Graceful clamping: seq[start:stop:step] clamps out-of-bounds endpoints
    #   silently instead of raising IndexError (unlike single-item seq[i]).
    # - Shallow copy aliasing: copying only the top-level pointers isolates
    #   immutable elements like ints, but if the list contains nested mutable
    #   lists or dicts, both the original and the slice still point to the
    #   EXACT same inner objects!
    #
    #     Suppose matrix = [[1, 2], [3, 4]] and sub = matrix[:].
    #     sub is not matrix is True (two outer lists), yet sub[0] is matrix[0]
    #     is True! Running sub[0].append(99) changes matrix to
    #     [[1, 2, 99], [3, 4]].

    nums: list[int] = [10, 20, 30, 40, 50]
    print("Starter slice nums[1:4]:", nums[1:4])

    # Prove flat list slicing copies references into a new outer list and
    # clamps out-of-bounds endpoints safely:
    # bind middle = nums[1:4], assign middle[0] = 999, and print middle, nums,
    # and nums[3:999] (plus nums[50:100] to observe an empty list without error).


    # Prove that slicing a nested list is only a SHALLOW copy:
    # create matrix: list[list[int]] = [[1, 2], [3, 4]] and slice
    # sub = matrix[:]. Append 99 to sub[0] via sub[0].append(99), then print
    # matrix, sub, sub is matrix (False), and sub[0] is matrix[0] (True).


def negative_steps_and_bounds() -> None:

    # The third parameter in seq[start:stop:step] is the stride (step). When
    # step is positive (default 1), Python walks forward from start up to (but
    # excluding) stop. When step is negative, Python walks BACKWARD, so start
    # must sit to the RIGHT of stop, and omitted endpoints flip automatically:
    # - Omitting start with a negative step starts at the last element (-1).
    # - Omitting stop with a negative step runs all the way past index 0.
    #
    #     Suppose a = [10, 20, 30, 40, 50].
    #     a[3:1:-1] starts at index 3 (value 40), steps backward by -1, and
    #     stops BEFORE index 1 (value 20), returning [40, 30].
    #     Writing a[1:3:-1] returns [] because walking backward from index 1
    #     can never reach index 3!
    #     Writing a[::-1] flips both defaults and returns a reversed shallow
    #     copy [50, 40, 30, 20, 10].

    letters: list[str] = ["a", "b", "c", "d", "e"]
    print("Every second element letters[::2]:", letters[::2])

    # Practice negative-step bounds on a = [10, 20, 30, 40, 50]:
    # print a[::-1] (full reverse), a[3:1:-1] (expected: [40, 30]),
    # a[3::-1] (expected: [40, 30, 20, 10]), and a[1:3:-1] (expected: []).


    # Contrast including index 0 cleanly when stepping backward:
    # notice a[3:0:-1] stops BEFORE index 0 (giving [40, 30, 20]), while
    # a[3:None:-1] (or a[3::-1]) includes index 0. Print both to verify.


def named_slice_objects() -> None:

    # The colon notation seq[0:4:2] is syntactic sugar that Python compiles
    # into seq[slice(0, 4, 2)]. Because slice(start, stop, step) is a normal
    # first-class object, you can bind fixed field offsets to readable module
    # or function constants instead of repeating magic numbers like [2:].
    #
    #     Suppose MAGIC = slice(0, 2) and PAYLOAD = slice(2, None).
    #     Passing None for stop means "run to the end", identical to [2:].
    #     Calling packet[MAGIC] reads indices 0 and 1 cleanly across any packet.

    HEADER = slice(0, 2)
    sample_frame: list[int] = [0x01, 0x02, 100, 200]
    print("Starter header slice:", sample_frame[HEADER])

    # Define named slices MAGIC = slice(0, 2), PAYLOAD = slice(2, None), and
    # EVEN_PAYLOAD = slice(2, None, 2).
    # Create packet: list[int] = [0xCA, 0xFE, 10, 20, 30, 40], then print
    # packet[MAGIC], packet[PAYLOAD], and packet[EVEN_PAYLOAD].


    # Inspect how Python resolves a slice against a concrete sequence length:
    # call PAYLOAD.indices(len(packet)) (which returns a clamped
    # (start, stop, step) tuple) and print the result.


def in_place_slice_assignment_and_deletion() -> None:

    # Putting a slice on the LEFT-HAND SIDE of = does not allocate a new list;
    # it mutates the existing list object IN PLACE so every alias keeps the
    # same id() and sees the change immediately.
    #
    # Rules for slice mutation:
    # - Contiguous slice assignment (step == 1) accepts an iterable of ANY
    #   length, so you can shrink, grow, or even insert without deleting by
    #   assigning to an empty slice like items[1:1] = [99].
    # - Deleting a contiguous range works via del a[1:3] or a[1:3] = [].
    # - Whole-slice replacement a[:] = new_values clears and refills the
    #   existing list object in place (preserving id(a)), whereas a = new_values
    #   merely rebinds the local name a.
    # - Extended stride slice assignment (step != 1, such as a[::2] = [100, 300])
    #   replaces exact slots one-for-one, so the right-hand iterable MUST have
    #   the exact same length or Python raises ValueError.
    #
    #     Suppose a = [10, 20, 30, 40] and alias = a.
    #     del a[1:3] shrinks the shared list in place to [10, 40], so alias
    #     is also [10, 40] and alias is a remains True.

    buf: list[int] = [1, 2, 3, 4]
    buf[1:3] = [20]
    print("Starter in-place shrink:", buf)

    # Mutate a list in place while tracking an alias and its original id():
    # create nums: list[int] = [10, 20, 30, 40, 50], bind alias = nums, and
    # capture original_id = id(nums).
    # Replace the 3-element middle with 2 elements via nums[1:4] = [200, 300],
    # insert 150 at index 1 without deleting via nums[1:1] = [150], and print
    # nums after each step.


    # Practice del on a slice and whole-slice replacement:
    # delete indices 1 and 2 in place with del nums[1:3] and print nums.
    # Next, replace the entire contents in place via nums[:] = [1, 2, 3, 4],
    # then print nums, alias, and id(nums) == original_id (expected: True).


    # Practice extended stride assignment (step != 1):
    # replace every second slot in nums (which currently has 4 items, so
    # nums[::2] has length 2) via nums[::2] = [100, 300], and print nums.
    #
    # Try uncommenting the line below to observe ValueError from a length
    # mismatch on an extended stride slice:
    # nums[::2] = [99]


def main() -> None:

    print("=== 1. Shallow slice copies and clamping ===")
    shallow_slice_copies_and_clamping()

    print("\n=== 2. Negative steps and bounds ===")
    negative_steps_and_bounds()

    print("\n=== 3. Named slice objects ===")
    named_slice_objects()

    print("\n=== 4. In-place slice assignment and deletion ===")
    in_place_slice_assignment_and_deletion()


if __name__ == "__main__":
    main()
