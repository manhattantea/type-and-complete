# python 220_dicts_insertion_order_and_views.py


def insertion_order_and_safe_lookups() -> None:

    # Since Python 3.7 (building on CPython 3.6's compact dict redesign), every
    # dict is guaranteed by the language specification to preserve insertion
    # order. Instead of one sparse table full of empty slots, CPython stores a
    # compact array of small integer indices pointing into a dense,
    # insertion-ordered array of (hash, key, value) entries—cutting memory use
    # by roughly 20-25% while keeping keys in insertion order automatically.
    #
    # Updating an existing key keeps its original position in the order.
    # Deleting a key and inserting it again places it at the very end.
    #
    # Everyday lookup and removal tools:
    # - d[key] raises KeyError when key is absent.
    # - d.get(key, default) returns default (None if omitted) without mutating d.
    # - d.pop(key, default) removes key and returns its value (or default if
    #   absent; omitting default raises KeyError on a missing key).
    # - d.popitem() removes and returns the LAST inserted (key, value) pair in
    #   LIFO order (raising KeyError if the dict is empty).
    #
    #     Suppose counts: dict[str, int] = {} and words = ["go", "py", "go"].
    #     Running counts[w] = counts.get(w, 0) + 1 in a loop starts each new
    #     word at 0 + 1 and increments seen words, yielding {"go": 2, "py": 1}.

    order_demo: dict[str, int] = {"first": 1, "second": 2, "third": 3}
    order_demo["first"] = 100
    print("Starter order preserved on update:", list(order_demo.keys()))

    # Practice safe lookup with .get() and frequency counting:
    # create scores: dict[str, int] = {"alice": 90, "bob": 75, "cara": 88}.
    # Look up "dan" safely with scores.get("dan", 0) and print the result.
    # Then count occurrences in words = ["red", "blue", "red", "green", "blue", "red"]
    # into counts: dict[str, int] = {} using counts[w] = counts.get(w, 0) + 1,
    # and print counts.


    # Practice .pop(key, default) and .popitem() LIFO removal:
    # remove "bob" from scores using removed = scores.pop("bob"), then try
    # missing = scores.pop("zed", -1) to see the fallback default avoid KeyError.
    # Finally call last_pair = scores.popitem() and print removed, missing,
    # last_pair, and the remaining scores dict.


def fromkeys_and_setdefault_traps() -> None:

    # Two convenient dict methods hide classic bugs if you forget how Python
    # evaluates arguments and stores object references:
    #
    # First, dict.fromkeys(keys, value) binds EVERY key to the exact same
    # value object. That is completely safe for immutable values like 0 or None,
    # but disastrous if you pass a mutable list like []:
    #
    #     Suppose bad = dict.fromkeys(["a", "b"], []).
    #     bad["a"] is bad["b"] is True! Calling bad["a"].append(1) turns bad
    #     into {"a": [1], "b": [1]}.
    #     Use a dict comprehension {k: [] for k in keys} so each key gets its
    #     own freshly allocated list.
    #
    # Second, d.setdefault(key, default) returns d[key] if key exists, or
    # inserts d[key] = default and returns it if missing. Remember that Python
    # ALWAYS evaluates function arguments BEFORE calling the method! So writing
    # cache.setdefault(k, make_expensive()) calls make_expensive() on EVERY
    # lookup even when k is already in cache (and d.setdefault(k, []) allocates
    # a throwaway empty list on every hit). For grouping or expensive defaults,
    # an explicit if k not in d: check (or collections.defaultdict) avoids the
    # wasted work.

    safe_zeros = dict.fromkeys(["x", "y", "z"], 0)
    print("Starter safe fromkeys with immutable 0:", safe_zeros)

    # Reproduce the dict.fromkeys(keys, []) shared-list bug and fix it:
    # create bad_groups: dict[str, list[str]] = dict.fromkeys(["eng", "ops"], []).
    # Append "ada" to bad_groups["eng"], then print bad_groups and
    # bad_groups["eng"] is bad_groups["ops"] (True!).
    # Next, build good_groups: dict[str, list[str]] = {k: [] for k in ["eng", "ops"]},
    # append "ada" to good_groups["eng"], and print good_groups to confirm
    # "ops" stays empty.


    # Group pairs using if key not in groups: vs. setdefault():
    # given pairs = [("fruit", "apple"), ("veg", "carrot"), ("fruit", "pear")],
    # build grouped: dict[str, list[str]] = {} by checking if cat not in grouped:
    # grouped[cat] = [] before calling grouped[cat].append(item). Print grouped.


    # Prove setdefault() evaluates its default argument EAGERLY on every call:
    # define a tiny helper def make_bucket() -> list[int]: right here that
    # prints "allocating new bucket" and returns [].
    # Create cache: dict[str, list[int]] = {"existing": [1]}.
    # Call cache.setdefault("existing", make_bucket()) twice and notice
    # "allocating new bucket" prints BOTH times even though "existing" is
    # already present! Contrast that with checking if "existing" not in cache:
    # before calling make_bucket().


def merge_operators_and_live_views() -> None:

    # Python 3.9+ added PEP 584 dictionary merge operators:
    # - d1 | d2 allocates a brand-new merged dict leaving d1 and d2 untouched;
    #   when both dicts share a key, the right-hand dict (d2) wins.
    # - d1 |= d2 updates d1 IN PLACE (similar to d1.update(d2)).
    #
    # Calling d.keys(), d.values(), or d.items() does NOT copy keys or values
    # into a list. Instead, each returns a lightweight LIVE VIEW object backed
    # directly by the dict:
    # - Subsequent mutations to d show up in the view immediately.
    # - Both .keys() and .items() (when values are hashable) support set
    #   algebra directly: & (intersection), | (union), - (difference), and
    #   ^ (symmetric difference).
    #
    #     Suppose d = {"a": 1} and view = d.keys().
    #     After d["b"] = 2, list(view) is ["a", "b"] without recreating view.

    defaults: dict[str, int] = {"timeout": 30, "retries": 3}
    overrides: dict[str, int] = {"retries": 5}
    print("Starter merged config:", defaults | overrides)

    # Practice non-mutating | and in-place |= merges:
    # create scores: dict[str, int] = {"alice": 90, "bob": 75, "cara": 88} and
    # bonus: dict[str, int] = {"bob": 82, "dan": 95}.
    # Compute merged = scores | bonus and print merged and scores to verify
    # "bob" became 82 in merged while scores stayed unchanged.
    # Then update a copy patched = scores.copy() in place via patched |= bonus
    # and print patched.


    # Observe live view synchronization and set algebra on .keys() / .items():
    # capture live_keys = scores.keys().
    # Print the shared keys scores.keys() & bonus.keys() and bonus-only keys
    # bonus.keys() - scores.keys().
    # Then insert scores["frank"] = 70 and print live_keys to verify the new
    # key appears automatically in the existing view.


def safe_iteration_and_deletion() -> None:

    # CPython dicts track an internal version/size counter during iteration.
    # Adding or deleting keys while looping directly over a dict (or over its
    # live .keys() / .items() views) immediately raises RuntimeError so the
    # hash table cannot silently skip or revisit keys mid-resize.
    #
    # To delete keys safely during a loop, iterate over a snapshot copy such as
    # for name in list(d): or build a filtered dict with a comprehension.
    #
    #     Suppose table = {"a": 1, "b": 2}.
    #     for k in list(table): snapshots ["a", "b"] first, so del table[k]
    #     mutates table safely without disturbing the loop iterator.

    sample: dict[str, int] = {"keep": 10, "drop": 2}
    print("Starter dict before filtering:", sample)

    # Filter entries in place safely using a key snapshot:
    # create roster: dict[str, int] = {"alice": 90, "bob": 82, "cara": 88, "dan": 70}.
    # Delete every entry whose score is < 85 by looping with
    # for name in list(roster.keys()): and executing del roster[name].
    # Print roster afterward (expected: {"alice": 90, "cara": 88}).
    #
    # Try uncommenting the loop below to observe RuntimeError:
    # for name in roster:
    #     if roster[name] < 90:
    #         del roster[name]


def main() -> None:

    print("=== 1. Insertion order and safe lookups ===")
    insertion_order_and_safe_lookups()

    print("\n=== 2. fromkeys and setdefault traps ===")
    fromkeys_and_setdefault_traps()

    print("\n=== 3. Merge operators and live views ===")
    merge_operators_and_live_views()

    print("\n=== 4. Safe iteration and deletion ===")
    safe_iteration_and_deletion()


if __name__ == "__main__":
    main()
