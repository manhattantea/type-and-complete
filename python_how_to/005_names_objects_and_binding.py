# python 005_names_objects_and_binding.py

import sys


def labels_and_rebinding() -> None:

    # In C, C++, Go, or Odin, declaring int a = 10 reserves a typed memory box
    # and writes 10 into it; b = a copies those bits into a second box. Python
    # works very differently: variables have no type and are NOT memory boxes.
    # A Python variable is simply a name (label) inside a namespace dictionary
    # pointing to a heap-allocated PyObject (which carries a reference count,
    # a type pointer, and the object's payload).
    #
    # id(obj) returns an object's unique identity (its memory address in
    # CPython), and type(obj).__name__ gives the class name of the heap object
    # that the label currently points to.
    #
    # Watch what happens with an immutable object like int:
    #     Suppose a = 10 and b = a.
    #     Both labels point at the exact same 10 object on the heap.
    #     When you write a = 20, Python does NOT overwrite the memory holding 10.
    #     It moves label a to a different 20 object, leaving b pointing at 10.
    #
    # Now contrast that with a mutable object like list:
    #     Suppose first = [1, 2] and second = first.
    #     Calling first.append(3) mutates the shared heap list in place, so BOTH
    #     first and second now read [1, 2, 3]. Rebinding first = [9, 10] afterward
    #     creates a brand-new list and detaches first without touching second.

    x = 42
    print(f"x={x}, id={id(x):#x}, type={type(x).__name__}")

    # Test immutable rebinding with int and str:
    # bind a = 10 and b = a, print id(a) == id(b), then rebind a = 20 and print
    # a, b, and id(a) == id(b) (False).
    # Repeat with s1 = "odin", s2 = s1, and s1 = s1 + "!" to confirm s2 remains
    # "odin" because strings cannot be mutated in place.


    # Observe mutable aliasing through a shared list:
    # bind first_label = [1, 2, 3] and second_label = first_label.
    # Print id(first_label) == id(second_label) and first_label is second_label.
    # Call first_label.append(4) and print second_label (expected: [1, 2, 3, 4]).


    # Detach the alias by rebinding:
    # assign first_label = [99, 100] (a brand-new list object), then print
    # first_label, second_label, and first_label is second_label (False) to prove
    # rebinding one name never changes what another alias points to.


def identity_vs_equality_and_none() -> None:

    # Keep identity (is) and value equality (==) strictly separate:
    # - a is b checks id(a) == id(b) in O(1) pointer time (same heap object?).
    # - a == b calls a.__eq__(b) (do these two objects hold equal contents?).
    #
    # Never use 'is' to compare numbers or strings for equality! As an internal
    # optimization, CPython pre-allocates small integers from -5 through 256 as
    # shared singletons (and also folds identical compile-time constants inside
    # the same code block). That means int("200") is int("200") happens to be
    # True, whereas runtime-built int("5000") is int("5000") is False even though
    # both values equal 5000!
    #
    # By contrast, ALWAYS check None with 'x is None' or 'x is not None' -- never
    # 'x == None'. None is guaranteed to be a single global singleton, whereas a
    # custom class can override __eq__ to return True when compared against None:
    #
    #     Suppose class AlwaysEqual defines def __eq__(self, other: object) -> bool:
    #     returning True. Then AlwaysEqual() == None evaluates to True, while
    #     AlwaysEqual() is None reliably evaluates to False.

    left = [1, 2]
    right = [1, 2]
    print("Equal contents:", left == right, "| Same heap object:", left is right)

    # Observe CPython's -5..256 small-integer singleton cache:
    # bind small_a = int("200") and small_b = int("200"), then
    # big_a = int("5000") and big_b = int("5000") (using int(...) avoids
    # compile-time constant folding). Print both == and is for each pair, then
    # check the cache edges with int("-5") vs int("-6") and int("256") vs
    # int("257").


    # Bind result: int | None = None and print result is None and
    # result is not None.


    # Prove why == None is unsafe:
    # define class AlwaysEqual: inside this function with
    # def __eq__(self, other: object) -> bool: returning True.
    # Create weird = AlwaysEqual() and print weird == None (True!) alongside
    # weird is None (False!).


def parallel_swap_and_del_refcount() -> None:

    # Python supports parallel assignment such as width, height = height, width.
    # Python evaluates the entire right-hand side first into a temporary tuple
    # holding references to both objects, and only then binds the left-hand
    # names simultaneously -- no scratch temp variable needed.
    #
    # When you write del name, Python does NOT force-free memory like C's free().
    # del simply removes the label from the current namespace and decrements the
    # object's reference count by 1. If another alias still points to that
    # object, the object stays completely alive!
    #
    # sys.getrefcount(obj) lets you peek at CPython's reference count for any
    # object. Note that the count is always at least 1 higher than you expect
    # because passing obj into getrefcount() itself creates a temporary reference
    # during the call:
    #
    #     Suppose primary = [10, 20] and alias = primary.
    #     sys.getrefcount(primary) returns 3 (primary, alias, and the call arg).
    #     After del primary, reading primary raises NameError, while alias still
    #     holds [10, 20] with sys.getrefcount(alias) equal to 2.

    sentinel = object()
    print("Fresh object refcount (includes call arg):", sys.getrefcount(sentinel))

    # Bind width, height = 1920, 1080, swap them in one statement using
    # width, height = height, width, and print (width, height).


    # Track reference counts across aliasing and del:
    # create primary = [10, 20, 30] and print sys.getrefcount(primary).
    # Bind alias = primary and print sys.getrefcount(primary) again (rises by 1).
    # Run del primary, then print alias and sys.getrefcount(alias) to verify the
    # list stayed alive after unbinding primary.
    #
    # Try uncommenting below after del primary to observe NameError:
    # print(primary)


def plus_equals_rebinding_vs_mutation() -> None:

    # Augmented assignment (x += y) is NOT always shorthand for x = x + y!
    # Python first asks the object whether it supports in-place addition
    # (__iadd__). That creates a sharp split between immutable and mutable types:
    # - On immutable types (int, str, tuple), in-place mutation is impossible, so
    #   x += y builds a new object and rebinds x (leaving aliases unchanged).
    # - On mutable types like list, x += y mutates the existing list in place
    #   (just like list.extend), so EVERY alias sees the new elements! By
    #   contrast, x = x + y always builds a brand-new list and rebinds x.
    #
    #     Suppose nums = [1, 2] and alias = nums.
    #     Running nums += [3] keeps id(nums) unchanged and turns alias into
    #     [1, 2, 3]. Running nums = nums + [4] allocates a new list for nums
    #     ([1, 2, 3, 4]) and leaves alias at [1, 2, 3].

    tag = "py"
    before_id = id(tag)
    tag += "3"
    print("str += kept same id:", id(tag) == before_id, "| tag:", tag)

    # Test += on immutable tuple and int:
    # bind t1 = (1, 2) and t2 = t1, run t1 += (3,), and print t1, t2, and
    # t1 is t2 (False). Repeat with count = 1000, backup = count, count += 1.


    # Contrast += mutation vs + rebinding on a list:
    # bind items = [1, 2] and shared = items, record start_id = id(items), run
    # items += [3], and print items, shared, and id(items) == start_id (True).
    # Next run items = items + [4] and print items, shared, and
    # id(items) == start_id (False).


    # Combine immutability and aliasing in one puzzle:
    # bind box = ([1, 2], "fixed"), run box[0].append(3), and print box.
    # Notice why that succeeds: the tuple freezes which two object references sit
    # in slots 0 and 1, not the internal state of the mutable list in slot 0!


def main() -> None:

    print("=== 1. Labels and rebinding ===")
    labels_and_rebinding()

    print("\n=== 2. Identity vs equality and None ===")
    identity_vs_equality_and_none()

    print("\n=== 3. Parallel swap and del refcounts ===")
    parallel_swap_and_del_refcount()

    print("\n=== 4. += rebinding vs in-place mutation ===")
    plus_equals_rebinding_vs_mutation()


if __name__ == "__main__":
    main()
