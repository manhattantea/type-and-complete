# python 225_sets_and_frozensets.py


def empty_set_trap_and_mutations() -> None:

    # Checking x in my_list scans element by element in O(N) time. Checking
    # x in my_set hashes x and probes a hash table bucket in O(1) average time.
    # Whenever you need fast membership tests, deduplication, or relational
    # checks (subsets, intersections, differences), set and frozenset are the
    # right tools.
    #
    # Watch out for the empty-literal trap: {} creates an empty DICT, never an
    # empty set! Always call set() when you want an empty set.
    #
    # Everyday mutating methods on set:
    # - s.add(x) inserts one hashable element.
    # - s.update(iterable) inserts every element from iterable.
    # - s.discard(x) removes x if present and silently does nothing if absent.
    # - s.remove(x) removes x if present, or raises KeyError if absent.
    # - s.pop() removes and returns an arbitrary element (KeyError if empty).
    # - s.clear() empties the set in place.
    #
    #     Suppose seen = {"a", "b"}.
    #     seen.discard("z") leaves seen as {"a", "b"} with no error.
    #     seen.remove("z") raises KeyError: 'z'.

    empty_dict = {}
    empty_set: set[str] = set()
    print("Starter {} vs set():", type(empty_dict), type(empty_set))

    # Practice .add(), .update(), .discard(), and .remove():
    # create active_tags: set[str] = {"python", "odin"}.
    # Add "systems" with active_tags.add("systems") and add ["cli", "python"]
    # with active_tags.update(["cli", "python"]) (notice duplicate "python" is
    # ignored). Call active_tags.discard("missing") safely, then print
    # active_tags and len(active_tags).


    # Contrast .discard() with .remove() on a missing member:
    # wrap active_tags.remove("missing") inside try: / except KeyError as exc:
    # and print exc so you see when to choose .discard() vs. .remove().


def set_algebra_operators_vs_methods() -> None:

    # Python sets support mathematical set algebra in two forms:
    # - Binary operators: | (union), & (intersection), - (difference),
    #   ^ (symmetric difference: items in exactly one set), <= (subset),
    #   < (proper subset), >= (superset), > (proper superset).
    #   Operators require BOTH operands to be sets or frozensets.
    # - Named methods: .union(it), .intersection(it), .difference(it),
    #   .symmetric_difference(it), .issubset(it), .issuperset(it), and
    #   .isdisjoint(it) (True when two collections share zero elements).
    #   Methods accept ANY iterable on the right-hand side (lists, tuples,
    #   generators), saving you from allocating a temporary set first!
    # - In-place operators |=, &=, -=, ^= mutate the left-hand set directly.
    #
    #     Suppose a = {1, 2} and b = {2, 3}.
    #     a | b is {1, 2, 3}, a & b is {2}, a - b is {1}, and a ^ b is {1, 3}.

    base_flags: set[str] = {"read", "write"}
    print("Starter union with a list via .union():", base_flags.union(["exec"]))

    # Express permission checks cleanly with set operators:
    # create required_perms: set[str] = {"read", "write"} and
    # user_perms: set[str] = {"read", "write", "execute"}.
    # Print required_perms <= user_perms (subset check),
    # required_perms < user_perms (proper subset), required_perms - user_perms
    # (missing permissions), and required_perms ^ user_perms (symmetric diff).


    # Contrast set methods accepting arbitrary iterables with binary operators:
    # print user_perms.isdisjoint(["admin", "root"]) (True) and
    # user_perms.intersection(["execute", "admin"]) ({"execute"}).
    # Next, update user_perms in place via user_perms |= {"audit"} and
    # user_perms -= {"execute"}, then print user_perms.
    #
    # Try uncommenting below to observe TypeError when passing a list to |:
    # bad = user_perms | ["admin"]


def order_preserving_deduplication() -> None:

    # Unlike dict, Python's set does NOT preserve insertion order: its elements
    # live in hash-probe bucket order, which depends on each object's hash and
    # the randomized per-process hash seed (PYTHONHASHSEED) for strings!
    #
    # Calling list(set(items)) removes duplicates quickly, but scrambles order.
    # Because dict preserves insertion order since Python 3.7 and keeps the
    # first-seen position of duplicate keys, the canonical Python idiom for
    # order-preserving deduplication is list(dict.fromkeys(items)).
    #
    #     Suppose events = ["a", "b", "a", "c"].
    #     dict.fromkeys(events) inserts "a", then "b", ignores duplicate "a",
    #     then inserts "c", so list(dict.fromkeys(events)) is ["a", "b", "c"].

    sample: list[str] = ["x", "y", "x"]
    print("Starter order-preserving dedup:", list(dict.fromkeys(sample)))

    # Deduplicate an event log while preserving first-seen order:
    # given raw_events: list[str] = ["login", "click", "login", "scroll", "click", "logout"],
    # compute ordered_unique = list(dict.fromkeys(raw_events)) and print it
    # alongside list(set(raw_events)) to contrast order preservation.


    # Verify fast O(1) membership lookup on the unique set:
    # bind seen_events: set[str] = set(raw_events) and print
    # "scroll" in seen_events and "delete" in seen_events.


def frozenset_as_hashable_keys() -> None:

    # Because a regular set can be mutated after creation (.add / .remove),
    # Python refuses to hash it—mutating a key inside a dict or outer set would
    # corrupt the hash table!
    #
    # frozenset is the immutable twin of set: once created, no elements can be
    # added or removed, so frozenset IS hashable. That lets you use unordered
    # tag combinations as dict keys or store sets inside another set.
    #
    #     Suppose a = frozenset({"api", "v2"}) and b = frozenset(["v2", "api"]).
    #     Because sets ignore element order, a == b is True and
    #     hash(a) == hash(b) is True, so looking up route_table[b] finds a!

    tag_key = frozenset({"core", "net"})
    print("Starter hashable frozenset:", tag_key, "hash:", hash(tag_key))

    # Use frozenset[str] as order-independent dictionary keys:
    # create route_table: dict[frozenset[str], str] mapping
    # frozenset({"api", "v2"}) to "v2_router" and
    # frozenset({"admin", "audit"}) to "audit_router".
    # Look up route_table[frozenset(["v2", "api"])] (reversed order!) and print
    # the matched router name.


    # Store frozensets inside an outer set (impossible with mutable sets):
    # create role_groups: set[frozenset[str]] = {frozenset({"read"}), frozenset({"read", "write"})}
    # and print role_groups and frozenset({"write", "read"}) in role_groups.
    #
    # Try uncommenting the line below to observe TypeError: unhashable type: 'set':
    # bad_table = {{"api", "v2"}: "v2_router"}


def main() -> None:

    print("=== 1. Empty set trap and mutations ===")
    empty_set_trap_and_mutations()

    print("\n=== 2. Set algebra: operators vs. methods ===")
    set_algebra_operators_vs_methods()

    print("\n=== 3. Order-preserving deduplication ===")
    order_preserving_deduplication()

    print("\n=== 4. Hashable frozenset keys ===")
    frozenset_as_hashable_keys()


if __name__ == "__main__":
    main()
