# python 500_refcounting_and_garbage_collection.py

import gc
import sys
import weakref


class Box:

    def __init__(self, label: str) -> None:

        self.label = label


def deterministic_refcounting_and_getrefcount() -> None:

    # CPython manages memory with two mechanisms running side by side. The first
    # is reference counting: every Python object lives on the heap inside a C
    # struct (PyObject) that stores an integer counter called ob_refcnt. Binding
    # a name (a = obj), putting obj into a list, or attaching it as an attribute
    # bumps ob_refcnt by 1. Rebinding the name, removing the list slot, or
    # leaving a function scope decrements ob_refcnt by 1.
    #
    # The exact instant ob_refcnt reaches 0, CPython frees that object right
    # away without waiting for any background collector sweep.
    #
    # Two standard-library tools let us watch this happen live:
    # - sys.getrefcount(obj) returns the current reference count of obj, PLUS 1
    #   extra temporary reference created just to pass obj as the argument into
    #   getrefcount itself. So a brand-new local variable reports 2, not 1.
    # - weakref.ref(obj) creates a non-owning observer that does NOT increment
    #   ob_refcnt. Calling the weakref like ref() returns the live object while
    #   it exists, and returns None the exact moment ob_refcnt hits 0.
    #
    #     Suppose a = Box("alpha") and obs = weakref.ref(a).
    #     sys.getrefcount(a) reports 2 (name 'a' plus the call argument).
    #     Bind b = a -> sys.getrefcount(a) becomes 3.
    #     Run del a, b -> ob_refcnt drops to 0 immediately and obs() is None!

    starter = Box("starter")
    print("Starter refcount:", sys.getrefcount(starter), "alive:", weakref.ref(starter)() is starter)

    # Create item = Box("packet") and a non-owning observer item_ref = weakref.ref(item).
    # Print sys.getrefcount(item) (expect 2), append item into
    # holders: list[Box] = [] and print sys.getrefcount(item) again (expect 3).
    # Call holders.clear() to see the count drop back to 2, then run del item
    # and assert item_ref() is None without ever calling gc.collect().


    # Verify deterministic scope-exit cleanup: define a tiny helper
    # def make_ephemeral() -> weakref.ref[Box]: that creates local_box = Box("tmp")
    # and returns weakref.ref(local_box). Call obs = make_ephemeral() and verify
    # obs() is None right away because local_box lost its only reference on return.


    # Contrast aliasing against rebinding: bind first = Box("shared") and
    # second = first, plus shared_ref = weakref.ref(first). Verify
    # sys.getrefcount(first) is 3, then rebind first = Box("fresh") and check
    # that shared_ref() is still alive with sys.getrefcount(second) == 2 until
    # you run del second.


def immortal_objects_and_weakref_limits() -> None:

    # Starting in Python 3.12 (PEP 683), singletons and small built-in constants
    # such as None, True, False, small integers like 42, and built-in types are
    # immortal objects. Their ob_refcnt is pinned to a huge sentinel number
    # (over a billion) that CPython never increments or decrements, avoiding
    # cache-line writes across threads and subinterpreters. Always run refcount
    # experiments on fresh user-defined objects rather than literals.
    #
    # Also note a memory-compactness rule: built-in list, dict, int, and str
    # objects omit a __weakref__ pointer slot to stay small in RAM, so calling
    # weakref.ref([1, 2]) raises TypeError. Plain user-defined classes include
    # weakref support automatically.

    print("Immortal refcounts -> None:", sys.getrefcount(None), "42:", sys.getrefcount(42))

    # Compare an immortal small integer against a freshly parsed large integer:
    # bind small_num = 42 and big_num = int("9876543210123456789"). Print
    # sys.getrefcount(small_num) and sys.getrefcount(big_num) before and after
    # placing both inside pair = (small_num, big_num) to see big_num change by 1
    # while small_num stays pinned.


    # Verify built-in weakref rejection cleanly: wrap weakref.ref([1, 2, 3]) in
    # a try / except TypeError as err: block and print the error message.
    #
    # Try uncommenting below to trigger TypeError on a built-in dict too:
    # bad_dict_ref = weakref.ref({"k": 1})


def reference_cycles_and_generational_gc() -> None:

    # Reference counting has one structural blind spot: reference cycles. If
    # two objects point to each other (n1.peer = n2 and n2.peer = n1), deleting
    # both local names leaves each object with ob_refcnt == 1. Neither counter
    # ever reaches 0, so the pair floats as an unreachable island in RAM.
    #
    # That is why CPython runs a second mechanism: the generational cyclic
    # garbage collector (the gc module). It tracks container objects (instances,
    # lists, dicts, closures) across three generations:
    # - gen 0: freshly allocated containers (swept most frequently)
    # - gen 1: containers that survived a gen 0 sweep
    # - gen 2: long-lived containers (swept least often)
    #
    # gc.get_threshold() shows the allocation thresholds that trigger automatic
    # sweeps, gc.get_count() shows current per-generation allocation counts, and
    # gc.collect() forces a full generation-2 sweep returning how many
    # unreachable cyclic objects were reclaimed.
    #
    #     Suppose n1 = CycleNode("A") and n2 = CycleNode("B") link to each other
    #     with n1.peer = n2 and n2.peer = n1.
    #     After gc.disable() and del n1, del n2, both weakrefs stay non-None.
    #     Calling gc.collect() detects the isolated island and frees both nodes!

    print("GC enabled:", gc.isenabled(), "thresholds:", gc.get_threshold(), "counts:", gc.get_count())

    # Define class CycleNode: inside this section with
    # def __init__(self, name: str) -> None: storing self.name = name and
    # self.peer: CycleNode | None = None.
    # Call gc.disable() inside a try / finally: block that always calls
    # gc.enable() at the end. Create n1 = CycleNode("A") and n2 = CycleNode("B"),
    # link n1.peer = n2 and n2.peer = n1, take r1 = weakref.ref(n1) and
    # r2 = weakref.ref(n2), then run del n1, n2 and assert both
    # r1() is not None and r2() is not None.


    # Inside that same try block, force a full sweep with collected = gc.collect(),
    # print collected (expect at least 2), and assert r1() is None and r2() is None
    # to confirm cyclic GC reclaimed the unreachable island.


    # Test a single-container self-cycle: create ring: list[object] = [] and
    # call ring.append(ring). Print gc.is_tracked(ring) (True, because lists can
    # hold cycles) vs gc.is_tracked(42) (False, because ints cannot point to
    # anything), then delete ring and run gc.collect().


def gc_control_and_referent_inspection() -> None:

    # Latency-sensitive programs (frame ticks, games, audio engines) sometimes
    # pause automatic cyclic sweeps with gc.disable() during a critical burst
    # and call gc.collect() explicitly at a safe pause point so a surprise gen-2
    # sweep never stalls a frame. Always pair gc.disable() with gc.enable() in a
    # finally: clause so an early exception never leaves GC turned off.
    #
    # When debugging why an object refuses to die, gc.get_referents(obj) lists
    # everything obj directly points to, while gc.get_referrers(obj) lists the
    # containers currently holding a strong reference to obj.

    probe = Box("probe")
    print("Tracked container:", gc.is_tracked(probe), "tracked str:", gc.is_tracked("plain"))

    # Practice a safe frame-budget pause: wrap a burst in try / finally: where
    # gc.disable() runs at entry and gc.enable() runs in finally:. Inside the
    # burst, build 20 short-lived cyclic list pairs (a = []; b = [a]; a.append(b))
    # without keeping them, print gc.get_count(), then run collected = gc.collect()
    # at the end of the burst and print how many objects were freed.


    # Inspect live ownership edges: create owner = Box("root") and
    # child = Box("leaf"), attach owner.child = child, and print
    # gc.get_referents(owner) to see the instance __dict__ holding child.
    # Print len(gc.get_referrers(child)) before and after setting
    # owner.child = None to confirm the reference link disappeared.


def main() -> None:

    print("=== 1. Deterministic refcounting and sys.getrefcount ===")
    deterministic_refcounting_and_getrefcount()

    print("\n=== 2. Immortal objects and weakref limits ===")
    immortal_objects_and_weakref_limits()

    print("\n=== 3. Reference cycles and generational GC ===")
    reference_cycles_and_generational_gc()

    print("\n=== 4. GC pause hygiene and referent inspection ===")
    gc_control_and_referent_inspection()


if __name__ == "__main__":
    main()
