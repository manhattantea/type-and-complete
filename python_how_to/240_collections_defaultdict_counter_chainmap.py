# python 240_collections_defaultdict_counter_chainmap.py

from collections import ChainMap, Counter, defaultdict


def defaultdict_grouping_and_missing_trap() -> None:

    # Grouping items into buckets with a regular dict forces repetitive guard
    # code on every iteration: if dept not in by_dept: by_dept[dept] = [].
    # collections.defaultdict(default_factory) removes that boilerplate by
    # overriding __missing__(key). Whenever you access d[key] and key is
    # absent, defaultdict calls default_factory() with zero arguments (such as
    # list, int, or set), inserts the brand-new object under key, and returns
    # it:
    #
    #     Suppose buckets = defaultdict(list).
    #     Running buckets["math"].append("Ada") calls list() -> [], binds
    #     buckets["math"] = [], and appends "Ada", leaving {"math": ["Ada"]}.
    #
    # Watch out for one subtle mutation trap:
    # - d.get(key) does NOT call __missing__! It returns None (or your fallback)
    #   and leaves the dictionary untouched.
    # - Reading d[key] DOES call __missing__ and silently mutates the dict by
    #   inserting a fresh default entry even if you only meant to inspect it!

    starter_groups: defaultdict[str, list[int]] = defaultdict(list)
    starter_groups["even"].append(2)
    print("Starter defaultdict:", dict(starter_groups))

    # Group records without any manual membership checks:
    # given pairs: list[tuple[str, str]] = [("math", "Ada"), ("cs", "Alan"), ("math", "Grace"), ("cs", "Ada")],
    # build by_dept: defaultdict[str, list[str]] = defaultdict(list) and loop
    # with for dept, person in pairs: appending person into by_dept[dept].
    # Print dict(by_dept) afterward.


    # Verify the d.get() vs d[] __missing__ distinction on by_dept:
    # first print by_dept.get("physics") and "physics" in by_dept (False!).
    # Next read empty_list = by_dept["physics"] and print empty_list alongside
    # "physics" in by_dept (True — reading via [] inserted an empty list!).


    # Use defaultdict(set) to deduplicate tags per user in one pass:
    # given events = [("u1", "py"), ("u1", "py"), ("u1", "sql"), ("u2", "py")],
    # collect into tags_by_user: defaultdict[str, set[str]] = defaultdict(set)
    # with tags_by_user[user].add(tag) and print dict(tags_by_user).


def counter_frequencies_and_multiset_math() -> None:

    # collections.Counter is a dict subclass designed for counting hashable
    # items and doing multiset (bag) arithmetic. Unlike defaultdict(int),
    # reading a missing key counts["ghost"] returns 0 WITHOUT inserting "ghost"
    # into the dictionary!
    #
    # Everyday Counter helpers include:
    # - .most_common(n): returns the n highest-count (item, count) pairs.
    # - .total(): sums all counts across the Counter (Python 3.10+).
    # - .elements(): lazily yields each item repeated by its positive count.
    # - Operators c1 + c2, c1 - c2, c1 & c2 (min counts), c1 | c2 (max counts).
    #
    # Pay close attention to the difference between operators and in-place
    # methods .update() and .subtract():
    #
    #     Suppose req = Counter(bolt=4, nut=4) and inv = Counter(bolt=2, nut=5).
    #     - req - inv returns a new Counter({"bolt": 2}): nut is dropped
    #       automatically because 4 - 5 <= 0.
    #     - req.subtract(inv) mutates req in place and KEEPS zero and negative
    #       counts: Counter({"bolt": 2, "nut": -1}), useful for tracking deltas
    #       or inventory surpluses/deficits!
    #     - req.update({"bolt": 1}) ADDS counts in place (bolt becomes 3),
    #       unlike dict.update() which overwrites values!

    starter_bag = Counter("banana")
    print("Starter Counter top-2:", starter_bag.most_common(2))

    # Count words: list[str] = ["log", "warn", "log", "err", "log", "warn"]
    # with counts = Counter(words). Print counts.most_common(2), counts.total(),
    # counts["debug"], and "debug" in counts to verify missing lookups return 0
    # without inserting the key.


    # Contrast non-negative multiset subtraction (-) with in-place .subtract():
    # create required = Counter(bolt=4, nut=4, washer=2) and
    # inventory = Counter(bolt=2, nut=5).
    # Print required - inventory (nut drops out because 4 - 5 <= 0).
    # Next create balance = Counter(bolt=4, nut=4, washer=2), call
    # balance.subtract(inventory), and print balance to see nut: -1 preserved.


    # Practice Counter.update() adding counts from both a mapping and an
    # iterable, then compare intersection (&) vs union (|):
    # call balance.update({"nut": 3, "bolt": 1}) and
    # balance.update(["washer", "washer"]), then print balance and
    # list(balance.elements()). Finally print required & inventory (min counts)
    # and required | inventory (max counts).


def chainmap_layered_configs() -> None:

    # When configuration comes from layered sources (such as CLI flags
    # overriding environment variables, which override defaults), merging dicts
    # with defaults | env | cli copies every key into a new dictionary.
    # collections.ChainMap(*maps) instead holds references to the original
    # dicts and searches them left-to-right on every lookup with zero copying!
    #
    # Mutations follow one strict rule: writes (cm[k] = v) and deletions
    # (del cm[k]) ALWAYS target ONLY the first dictionary, cm.maps[0]. Lower
    # layers are never modified through the ChainMap:
    #
    #     Suppose base = {"host": "localhost", "port": 8080} and
    #     cm = ChainMap({"port": 9000}, base).
    #     Reading cm["host"] falls through to base and returns "localhost".
    #     Running cm["host"] = "0.0.0.0" writes into cm.maps[0], leaving
    #     cm.maps[0] == {"port": 9000, "host": "0.0.0.0"} while base stays
    #     {"host": "localhost", "port": 8080}.
    #
    # Calling cm.new_child(override_dict) returns a new ChainMap with
    # override_dict pushed in front, and cm.parents returns a ChainMap skipping
    # cm.maps[0].

    starter_cm = ChainMap({"mode": "fast"}, {"mode": "safe", "threads": 4})
    print("Starter ChainMap:", starter_cm["mode"], starter_cm["threads"])

    # Layer three config dictionaries without copying:
    # create cli_args = {"timeout": 5},
    # env_vars = {"timeout": 30, "retries": 3}, and
    # defaults = {"timeout": 60, "retries": 1, "host": "localhost"}.
    # Build config = ChainMap(cli_args, env_vars, defaults) and print
    # config["timeout"], config["retries"], config["host"], and dict(config).


    # Push a temporary nested scope using .new_child():
    # bind scoped = config.new_child({"host": "127.0.0.1"}), set
    # scoped["debug"] = True, and print scoped["host"], scoped.maps[0],
    # scoped.parents["host"], and defaults to confirm lower layers remained
    # completely untouched.


    # Verify that ChainMap deletions only remove keys present in maps[0]:
    # run del scoped["debug"] and print scoped.maps[0].
    # Then notice that "retries" in scoped is True, yet deleting it fails
    # because it lives in env_vars (maps[2]), not maps[0].
    #
    # Try uncommenting below to trigger KeyError on a lower-layer key:
    # del scoped["retries"]


def main() -> None:

    print("=== 1. defaultdict grouping and __missing__ trap ===")
    defaultdict_grouping_and_missing_trap()

    print("\n=== 2. Counter frequencies, update, subtract, and multiset math ===")
    counter_frequencies_and_multiset_math()

    print("\n=== 3. ChainMap layered views and write scoping ===")
    chainmap_layered_configs()


if __name__ == "__main__":
    main()
