# python 540_object_interning_and_flyweight_pools.py

import sys
import weakref


def compile_time_vs_runtime_interning() -> None:

    # Parsers, JSON decoders, and log pipelines often see the same strings
    # ("status", "USD", "INFO") millions of times. Keeping millions of duplicate
    # str objects wastes RAM and forces character-by-character comparisons.
    #
    # CPython automatically interns identifier-like string literals at compile
    # time, which is why "hello" is "hello" often turns out True. Strings built
    # dynamically at runtime (from files, sockets, JSON, or "".join) bypass that
    # table and allocate fresh PyObjects every time.
    #
    # sys.intern(s) looks up or inserts s into CPython's canonical intern table
    # and returns the single shared str instance. Because str.__eq__ checks
    # pointer identity (a is b) first, comparing two interned strings matches in
    # O(1) without scanning characters. In modern Python, interned strings are
    # mortal: they leave the table automatically once no references remain.
    #
    #     Suppose s1 = "".join(["status", "_", "ok"]) and
    #     s2 = "".join(["status", "_", "ok"]).
    #     Initially s1 == s2 is True while s1 is s2 is False.
    #     After s1 = sys.intern(s1) and s2 = sys.intern(s2), s1 is s2 becomes
    #     True and id(s1) == id(s2).

    sample = "".join(["status", "_", "ok"])
    print("Starter dynamic string:", sample, "equals interned:", sys.intern(sample) == sample)

    # Construct s1 = "".join(["status", "_", "ok"]) and
    # s2 = "".join(["status", "_", "ok"]). Print s1 == s2 (True) and s1 is s2
    # (False). Next rebind s1 = sys.intern(s1) and s2 = sys.intern(s2), print
    # s1 is s2 (True), and assert id(s1) == id(s2).


    # Measure deduplication across a batch: build
    # raw = ["".join(["US", "D"]) for _ in range(1_000)] and print
    # len({id(x) for x in raw}) (expect 1000 distinct heap strings). Then build
    # canon = [sys.intern(x) for x in raw] and print len({id(x) for x in canon})
    # (expect 1). Keep using == for general value equality—interning speeds up
    # equality and dict lookups without making is a substitute for ==.


def flyweight_pool_with_new_and_weakref() -> None:

    # The Flyweight pattern extends interning to your own domain objects. In
    # Python, __new__(cls, ...) runs BEFORE __init__ and is responsible for
    # allocating and returning the object. If __new__ checks a class-level
    # weakref.WeakValueDictionary and returns an existing instance on a hit,
    # repeated calls share one object while unused instances still get collected.
    #
    # Watch out for a classic Python gotcha: whenever __new__ returns an
    # instance of cls, Python STILL invokes __init__ afterward! If you put
    # initialization in __init__, every cache hit re-runs __init__ and can
    # overwrite state. Instead, omit __init__ and assign attributes inside
    # __new__ only when creating a fresh instance.
    #
    #     Suppose InternedSymbol("USD") allocates once and stores itself in
    #     InternedSymbol._pool["USD"].
    #     A second call InternedSymbol("USD") returns that same object, and
    #     del on both local variables shrinks _pool back to 0 automatically.

    preview_pool: weakref.WeakValueDictionary[str, object] = weakref.WeakValueDictionary()
    print("Starter weak pool initial size:", len(preview_pool))

    # Define class InternedSymbol: with __slots__ = ("name", "__weakref__") and
    # _pool: weakref.WeakValueDictionary[str, "InternedSymbol"] = weakref.WeakValueDictionary().
    # Implement def __new__(cls, name: str) -> "InternedSymbol": checking
    # existing = cls._pool.get(name); if existing is not None, return existing.
    # Otherwise allocate instance = super().__new__(cls), set
    # instance.name = name, store cls._pool[name] = instance, and return
    # instance. Add __repr__(self) -> str returning f"InternedSymbol({self.name!r})".


    # Test pooling and eviction: bind usd_1 = InternedSymbol("USD") and
    # usd_2 = InternedSymbol("USD"), assert usd_1 is usd_2 and
    # len(InternedSymbol._pool) == 1, then run del usd_1, usd_2 and assert
    # len(InternedSymbol._pool) == 0 to prove zero leaks.


def verifying_single_allocation_in_flyweights() -> None:

    # Flyweights shine when the shared object is immutable and constructed from
    # a small vocabulary (currency codes, AST token kinds, font descriptors)
    # repeated across thousands of records. Tracking actual allocations proves
    # repeated lookups reuse existing objects instead of churning the heap.

    vocab = ("USD", "EUR", "JPY")
    print("Starter symbol vocabulary size:", len(vocab))

    # Add a class counter allocations: int = 0 on InternedSymbol (or a tiny
    # CachedCode subclass/class) incremented ONLY inside __new__ on a cache miss.
    # Hold anchor = InternedSymbol("EUR"), call InternedSymbol("EUR") four more
    # times, and assert allocations increased by only 1.


    # Build a 600-item list [InternedSymbol(vocab[i % 3]) for i in range(600)]
    # and assert both len(InternedSymbol._pool) == 3 and
    # len({id(sym) for sym in symbols}) == 3.


def main() -> None:

    print("=== 1. Compile-time vs runtime string interning ===")
    compile_time_vs_runtime_interning()

    print("\n=== 2. Flyweight pools via __new__ and WeakValueDictionary ===")
    flyweight_pool_with_new_and_weakref()

    print("\n=== 3. Verifying single allocation in flyweights ===")
    verifying_single_allocation_in_flyweights()


if __name__ == "__main__":
    main()
