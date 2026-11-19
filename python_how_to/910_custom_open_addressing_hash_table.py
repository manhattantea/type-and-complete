# python 910_custom_open_addressing_hash_table.py

# Python's built-in dict is a highly tuned C implementation of open addressing.
# Building your own open-addressed linear-probing hash table in pure Python
# exposes the exact invariants hidden behind d[key] = val and del d[key]:
# power-of-2 bitmask indexing, tombstone deletion markers, load-factor resizing,
# and Python's collections.abc.MutableMapping mixin contract.
#
# IntEnum defines named integer constants that compare and hash like plain ints
# while printing readable names in debugging output. Decorating _Entry with
# @dataclass(slots=True) generates __init__ and __repr__ automatically while
# storing fields in fixed C-level slots instead of a per-object __dict__.
# The [K, V] syntax on _Entry[K, V] is PEP 695 generic type parameter syntax:
# K and V act as type placeholders filled in when you construct a table such as
# HashTable[str, int]().

from dataclasses import dataclass
from enum import IntEnum


class SlotState(IntEnum):
    EMPTY = 0
    OCCUPIED = 1
    TOMBSTONE = 2


@dataclass(slots=True)
class _Entry[K, V]:
    # We track an explicit SlotState enum instead of treating key is None as
    # empty because None itself is a valid, hashable dictionary key in Python.
    state: SlotState = SlotState.EMPTY
    key: K | None = None
    value: V | None = None


def power_of_two_masking_and_tombstones() -> None:

    # Keeping bucket capacity as a power of 2 (8, 16, 32, ...) lets us map any
    # Python hash integer to a starting bucket with one bitwise AND mask instead
    # of a modulo division:
    #
    #     idx = hash(key) & (capacity - 1)
    #
    # Python's hash(key) can return negative integers (signed ints!), yet in
    # two's-complement arithmetic, bitwise & with (capacity - 1) keeps only the
    # low bits and always yields a valid bucket index 0 <= idx < capacity.
    #
    # The Tombstone Trap in Linear Probing:
    #     Suppose capacity is 8 and both "alpha" and "beta" mask to bucket 3.
    #     Inserting "alpha" stores it in slot 3 (OCCUPIED).
    #     Inserting "beta" checks slot 3, sees it OCCUPIED, and probes forward
    #     to slot 4 (OCCUPIED).
    #     If deleting "alpha" reset slot 3 back to SlotState.EMPTY, then looking
    #     up "beta" would check slot 3, see EMPTY, conclude "beta" cannot exist
    #     further down the probe chain, and falsely raise KeyError!
    #
    # Marking deleted slot 3 as SlotState.TOMBSTONE solves this cleanly: lookups
    # keep probing past tombstones until they hit a true EMPTY slot or matching
    # key, while future insertions can recycle that tombstone slot.
    #
    # Why tombstones must also count toward resizing:
    # Even if live len(table) stays small, thousands of insert-then-delete cycles
    # can fill every bucket with TOMBSTONE slots, degrading O(1) lookups into
    # O(n) full-table scans. Checking (occupied + tombstones) * 10 >= capacity * 7
    # (a 70% threshold) and re-inserting ONLY OCCUPIED entries during _resize
    # sweeps every tombstone away and restores crisp O(1) probe chains.

    sample_slot: _Entry[str, int] = _Entry(state=SlotState.OCCUPIED, key="alpha", value=1)
    mask = 8 - 1
    print(f"Starter slot: {sample_slot}, bucket for 'alpha' in cap=8 -> {hash('alpha') & mask}")

    # Verify two foundational bucket invariants before building HashTable:
    # - Check negative hash masking: compute (-17) & (8 - 1) and assert the result
    #   is in range(8) (expected: 7).
    # - Avoid the bucket-aliasing bug: allocate fresh = [_Entry() for _ in range(4)]
    #   and assert fresh[0] is not fresh[1]. (Writing [_Entry()] * 4 would point
    #   every bucket at the exact same _Entry instance in memory!)


def open_addressing_hash_table_design() -> None:

    # Inheriting from collections.abc.MutableMapping[K, V] turns a 5-method class
    # into a full Python mapping: once you implement __getitem__, __setitem__,
    # __delitem__, __iter__, and __len__, Python automatically synthesizes
    # .get(), .pop(), .setdefault(), .update(), .keys(), .values(), .items(),
    # 'in' membership, and '==' equality against built-in dicts!
    #
    # Two subtle contract details to get right:
    # - MutableMapping.__contains__ and .get() rely on __getitem__ raising
    #   KeyError(key) when a key is absent.
    # - When __delitem__ marks a slot as TOMBSTONE, clearing slot.key = None and
    #   slot.value = None drops references immediately so CPython's refcounter
    #   reclaims deleted objects instead of leaking them inside dead slots.

    states = [state.name for state in SlotState]
    print("Starter slot states ready for HashTable:", states)

    # Import from collections.abc import Iterator, MutableMapping at the top of
    # the file (or above the class) and define:
    # class HashTable[K, V](MutableMapping[K, V]):
    #
    # Add __init__(self, initial_capacity: int = 8) -> None:
    # Round self._capacity: int up to the smallest power of 2 >= max(8, initial_capacity)
    # (for example: cap = 8; while cap < initial_capacity: cap *= 2).
    # Allocate self._buckets: list[_Entry[K, V]] = [_Entry() for _ in range(self._capacity)],
    # and set self._count: int = 0 and self._tombstones: int = 0.


    # Add _find_slot(self, key: K) -> tuple[int, bool]:
    # Compute mask = self._capacity - 1 and idx = hash(key) & mask, and track
    # first_tombstone: int | None = None across up to self._capacity probe steps:
    # - Read entry = self._buckets[idx].
    # - If entry.state == SlotState.EMPTY: return
    #   (first_tombstone if first_tombstone is not None else idx, False).
    #   (We stop only at EMPTY because key might still live past a tombstone!)
    # - If entry.state == SlotState.TOMBSTONE: record first_tombstone = idx when
    #   first_tombstone is None, then keep probing.
    # - If entry.state == SlotState.OCCUPIED and entry.key == key: return (idx, True).
    #   (Hash collisions are legal in Python—equality == confirms a true key match.)
    # - Advance idx = (idx + 1) & mask.
    # If the loop finishes without hitting EMPTY, return
    # (first_tombstone if first_tombstone is not None else 0, False).


    # Add _resize(self, new_capacity: int) -> None:
    # Save old_buckets = self._buckets, reset self._capacity = new_capacity,
    # self._buckets = [_Entry() for _ in range(new_capacity)], self._count = 0,
    # and self._tombstones = 0.
    # Loop over entry in old_buckets: for every slot with
    # entry.state == SlotState.OCCUPIED, locate its fresh slot via
    # idx, _ = self._find_slot(entry.key) (narrowing entry.key safely because
    # OCCUPIED slots always store a key), write OCCUPIED + key + value into
    # self._buckets[idx], and increment self._count += 1.


    # Implement the 5 MutableMapping dunder methods on HashTable:
    # - __getitem__(self, key: K) -> V:
    #   Call idx, found = self._find_slot(key). If not found, raise KeyError(key).
    #   Otherwise return self._buckets[idx].value.
    # - __setitem__(self, key: K, value: V) -> None:
    #   First check load factor including tombstones:
    #   if (self._count + self._tombstones) * 10 >= self._capacity * 7:
    #   choose next_cap = self._capacity * 2 if self._count * 2 >= self._capacity else self._capacity
    #   (doubling when live entries are dense, or rehashing in place to purge tombstones)
    #   and call self._resize(next_cap).
    #   Then call idx, found = self._find_slot(key): if found, overwrite
    #   self._buckets[idx].value = value; otherwise if
    #   self._buckets[idx].state == SlotState.TOMBSTONE, decrement self._tombstones -= 1,
    #   store SlotState.OCCUPIED, key, and value into self._buckets[idx], and
    #   increment self._count += 1.
    # - __delitem__(self, key: K) -> None:
    #   Call idx, found = self._find_slot(key). If not found, raise KeyError(key).
    #   Transition slot = self._buckets[idx] to SlotState.TOMBSTONE, set
    #   slot.key = None and slot.value = None, decrement self._count -= 1, and
    #   increment self._tombstones += 1.
    # - __iter__(self) -> Iterator[K]:
    #   Yield entry.key for every entry in self._buckets where
    #   entry.state == SlotState.OCCUPIED.
    # - __len__(self) -> int:
    #   Return self._count (live OCCUPIED entries only, never tombstones).


def verify_resizes_tombstones_and_mapping_contract() -> None:

    # The strongest way to verify a custom container is differential testing:
    # run the exact same sequence of inserts, overwrites, and deletes against
    # both HashTable and a built-in Python dict oracle, then assert they match.

    oracle: dict[str, int] = {"key_0": 0, "key_1": 10}
    print("Starter oracle dict ready for differential checks:", oracle)

    # Instantiate table = HashTable[str, int]() and expected: dict[str, int] = {}.
    # Insert 20 pairs (f"key_{i}" -> i * 10 for i in range(20)) into both table
    # and expected (triggering 70% load-factor resizes from 8 -> 16 -> 32).
    # Delete 5 even keys (for i in range(0, 10, 2): del table[f"key_{i}"] and
    # del expected[f"key_{i}"]) to create tombstones, then overwrite one surviving
    # key (table["key_3"] = 999 and expected["key_3"] = 999).


    # Verify probe-chain integrity and synthesized MutableMapping helpers:
    # - Assert "key_5" in table and "key_0" not in table.
    # - Assert table.get("missing", -1) == -1.
    # - Assert len(table) == len(expected) and dict(table) == expected.
    # - Print len(table), table._capacity, table._tombstones, and dict(table) == expected.


    # Verify two edge cases that break naive hash tables:
    # - None as a key: create nullable = HashTable[str | None, str](), store
    #   nullable[None] = "sentinel", and assert None in nullable and nullable[None] == "sentinel".
    # - Tombstone churn: in a fresh table, insert and immediately delete 40
    #   distinct temporary keys in a loop, then check that table._capacity stays
    #   small (in-place rehash purges tombstones instead of doubling forever).
    #
    # Try uncommenting after implementing HashTable to observe KeyError:
    # missing_value = table["definitely_missing"]


def main() -> None:

    print("=== 1. Power-of-2 masking and tombstones ===")
    power_of_two_masking_and_tombstones()

    print("\n=== 2. Open-addressing HashTable design ===")
    open_addressing_hash_table_design()

    print("\n=== 3. Differential verification and edge cases ===")
    verify_resizes_tombstones_and_mapping_contract()


if __name__ == "__main__":
    main()
