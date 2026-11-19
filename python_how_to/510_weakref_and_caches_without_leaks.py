# python 510_weakref_and_caches_without_leaks.py

import gc
import weakref


class Asset:

    def __init__(self, name: str) -> None:

        self.name = name


def weak_value_caches_without_leaks() -> None:

    # One of the easiest ways to leak memory in Python is a long-lived normal
    # dictionary cache (_CACHE[key] = obj). Every entry in a regular dict holds
    # a strong reference to both its key and its value. Even after every caller
    # drops its handle to a large texture or session object, the dict keeps
    # ob_refcnt >= 1 and pins that object in RAM until the process exits.
    #
    # weakref.WeakValueDictionary solves this by storing weak references to its
    # values. It never keeps a cached object alive on its own: the instant all
    # external strong references disappear, the entry vanishes from the cache
    # automatically.
    #
    #     Suppose cache = weakref.WeakValueDictionary() and sky = Asset("sky").
    #     Assign cache["sky"] = sky -> list(cache.keys()) is ["sky"].
    #     Run del sky -> ob_refcnt hits 0, Asset("sky") frees, and cache.get("sky")
    #     immediately returns None!

    cache: weakref.WeakValueDictionary[str, Asset] = weakref.WeakValueDictionary()
    probe = Asset("probe.png")
    cache["probe"] = probe
    print("Starter cache keys:", list(cache.keys()))

    # Create sky = Asset("sky.png") and brick = Asset("brick.png"), insert both
    # into cache under keys "sky" and "brick", and print list(cache.keys()).
    # Run del sky, then print list(cache.keys()) and cache.get("sky") to verify
    # "sky" disappeared automatically while "brick" stayed live.


    # Build a small helper
    # def load_asset(name: str, pool: weakref.WeakValueDictionary[str, Asset]) -> Asset:
    # that checks existing = pool.get(name); if existing is not None, return it,
    # otherwise create fresh = Asset(name), store pool[name] = fresh, and return
    # fresh. Call a1 = load_asset("rock.png", cache) and a2 = load_asset("rock.png", cache),
    # assert a1 is a2, then run del a1, a2 and assert "rock.png" not in cache.


def weak_key_metadata_and_slots_gotcha() -> None:

    # weakref.WeakKeyDictionary is the mirror image: it holds weak references to
    # its keys. That lets you attach per-instance sidecar metadata to objects
    # without modifying their class or keeping them alive after callers drop them.
    #
    # Watch out for one important memory-layout trap: classes that declare
    # __slots__ remove the per-instance __dict__ AND remove the hidden
    # __weakref__ slot by default to stay tiny. Calling weakref.ref(obj) on a
    # slotted instance raises TypeError unless you explicitly include
    # "__weakref__" inside __slots__.
    #
    #     Suppose class Tight has __slots__ = ("x",) and class Trackable has
    #     __slots__ = ("x", "__weakref__").
    #     weakref.ref(Trackable(5)) succeeds, whereas weakref.ref(Tight(5))
    #     raises TypeError immediately.

    meta: weakref.WeakKeyDictionary[Asset, str] = weakref.WeakKeyDictionary()
    hud = Asset("hud.png")
    meta[hud] = "layer=ui"
    print("Starter WeakKeyDictionary size:", len(meta))

    # Create banner = Asset("banner.png"), assign meta[banner] = "mipmaps=True",
    # verify meta[banner] == "mipmaps=True" and len(meta) == 2, then run
    # del banner and assert len(meta) == 1 because banner's entry pruned itself.


    # Test the __slots__ weakref rule directly: define two classes
    # CompactPoint (__slots__ = ("x", "y")) and WeakPoint
    # (__slots__ = ("x", "y", "__weakref__")), each setting self.x and self.y
    # in __init__. Verify weakref.ref(WeakPoint(1, 2)) returns the live point,
    # and wrap weakref.ref(CompactPoint(1, 2)) in try / except TypeError as err:
    # to print the exact failure reason.


def breaking_parent_child_cycles_with_weakref() -> None:

    # Trees, UI widgets, and scene graphs almost always want two-way links:
    # a parent owns a list of children, and each child wants to know its parent.
    # If both directions use strong references (parent.children.append(child)
    # AND child.parent = parent), every parent-child pair forms a reference
    # cycle! Deleting the root leaves the whole tree alive at ob_refcnt >= 1
    # until cyclic GC eventually runs.
    #
    # The idiomatic ownership rule is simple: hold strong references DOWN the
    # tree (parent -> children), and hold a weakref.ref UP the tree
    # (child -> parent). When the parent disappears, every child's refcount
    # drops cleanly to 0 right away with zero cyclic GC work.
    #
    #     Suppose root = TreeNode("root") and leaf = TreeNode("leaf", parent=root)
    #     where leaf stores self._parent_ref = weakref.ref(root) and root appends
    #     leaf to root.children.
    #     Even with gc.disable(), running del root, leaf frees BOTH nodes
    #     immediately because there is no strong cycle!

    print("GC active before cycle-breaking checks:", gc.isenabled())

    # First observe the strong-cycle leak: define class LeakyNode: with
    # def __init__(self, name: str, parent: "LeakyNode | None" = None) -> None:
    # setting self.name = name, self.parent = parent, and
    # self.children: list[LeakyNode] = []. Inside a try / finally: block that
    # calls gc.disable() on entry and gc.collect(); gc.enable() in finally:,
    # create p = LeakyNode("root") and c = LeakyNode("leaf", parent=p), append c
    # to p.children, take pr = weakref.ref(p) and cr = weakref.ref(c), run
    # del p, c, and verify pr() is not None and cr() is not None (cycle leaked!).


    # Now break the back-pointer with weakref.ref: define class TreeNode: whose
    # __init__(self, name: str, parent: "TreeNode | None" = None) -> None stores
    # self.name = name, self.children: list[TreeNode] = [], and
    # self._parent_ref: weakref.ref[TreeNode] | None = weakref.ref(parent) if parent is not None else None.
    # Add @property def parent(self) -> "TreeNode | None": returning
    # self._parent_ref() if self._parent_ref is not None else None.
    # Under gc.disable() (restored in finally:), build root = TreeNode("root")
    # with two child TreeNodes attached to root.children, take weakrefs to all
    # three, delete the local names, and assert every weakref is None
    # immediately without calling gc.collect()!


    # Verify dangling-parent safety: create temp_parent = TreeNode("temp") and
    # orphan = TreeNode("orphan", parent=temp_parent), verify
    # orphan.parent is temp_parent, run del temp_parent, and assert
    # orphan.parent is None without raising an error or keeping temp_parent alive.


def deterministic_cleanup_with_weakref_finalize() -> None:

    # weakref.finalize(obj, callback, arg1, arg2, ...) registers an external
    # cleanup hook that runs once when obj is collected (or at interpreter exit).
    # It is far safer than __del__:
    # - A finalizer is idempotent: calling fin() explicitly runs it early, and
    #   later collection does NOT run it a second time.
    # - It tracks fin.alive (True until run or detached) and supports fin.detach()
    #   to cancel cleanup altogether.
    # - It avoids __del__ interpreter-shutdown ordering bugs and resurrection.
    #
    # Critical trap: NEVER pass obj itself (or a bound method like obj.close) as
    # an argument to weakref.finalize(obj, func, ...). The finalizer holds its
    # callback arguments strongly, so passing obj makes obj keep itself alive
    # until the process exits! Pass lightweight IDs, strings, or descriptors.
    #
    #     Suppose conn = Asset("db_1") and
    #     fin = weakref.finalize(conn, print, "Closed db_1").
    #     fin.alive is True -> del conn prints "Closed db_1" and sets fin.alive
    #     to False immediately.

    demo = Asset("demo_handle")
    demo_fin = weakref.finalize(demo, lambda label: None, demo.name)
    print("Starter finalizer alive:", demo_fin.alive)

    # Create resource = Asset("db_conn_1") and attach
    # fin = weakref.finalize(resource, print, "Cleaned up db_conn_1").
    # Assert fin.alive is True, run del resource to watch the message print right
    # away, assert not fin.alive, and call fin() a second time to confirm it is
    # a safe no-op.


    # Practice explicit early execution and cancellation:
    # - Create early = Asset("sock_1") with fin_early = weakref.finalize(early, print, "Early close sock_1").
    #   Call fin_early() BEFORE del early and assert not fin_early.alive.
    # - Create skipped = Asset("sock_2") with fin_skip = weakref.finalize(skipped, print, "Should not print").
    #   Call fin_skip.detach(), assert not fin_skip.alive, then del skipped and
    #   confirm nothing prints.
    #
    # Try uncommenting this anti-pattern in a small test to see why passing the
    # target inside the callback args prevents cleanup on del:
    # leaky = Asset("pinned")
    # weakref.finalize(leaky, lambda obj: print("Leaked until exit:", obj.name), leaky)
    # del leaky


def main() -> None:

    print("=== 1. WeakValueDictionary caches without leaks ===")
    weak_value_caches_without_leaks()

    print("\n=== 2. WeakKeyDictionary metadata and __slots__ ===")
    weak_key_metadata_and_slots_gotcha()

    print("\n=== 3. Breaking parent-child cycles with weakref.ref ===")
    breaking_parent_child_cycles_with_weakref()

    print("\n=== 4. Deterministic cleanup with weakref.finalize ===")
    deterministic_cleanup_with_weakref_finalize()


if __name__ == "__main__":
    main()
