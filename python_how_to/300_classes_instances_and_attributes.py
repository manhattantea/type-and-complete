# python 300_classes_instances_and_attributes.py


def class_namespaces_and_attribute_lookup() -> None:

    # In Python, a 'class' statement does not merely declare a static
    # compile-time struct. At runtime, Python executes the class body top to
    # bottom like a tiny script and constructs a live 'type' object whose
    # namespace lives in Class.__dict__.
    #
    # Python wraps Class.__dict__ in a read-only view called a mappingproxy
    # (a read-only dictionary wrapper) so internal C caches stay consistent
    # unless you modify the class through attribute syntax or setattr().
    # Meanwhile, each normal instance carries its own mutable dictionary
    # stored in obj.__dict__, which the built-in vars(obj) returns directly.
    #
    # Reading vs. writing an attribute has a key asymmetry:
    # - Reading obj.attr checks obj.__dict__ first, and falls back to
    #   type(obj).__dict__ and base classes only if the key is missing.
    #   (Data descriptors on the class run even earlier; Primer 385 covers why.)
    # - Writing obj.attr = val ALWAYS writes into obj.__dict__["attr"] = val,
    #   shadowing any class attribute of the same name without touching the class.
    #
    #     Suppose class Box has color = "blue", and a = Box(), b = Box().
    #     Before writing: vars(a) is {} and a.color reads "blue" from Box.__dict__.
    #     After a.color = "red": vars(a) is {"color": "red"}, a.color is "red",
    #     while b.color and Box.color both remain "blue".
    #     After del a.color: vars(a) is {} again, so a.color falls back to "blue".

    plain = object()
    print("Plain object() has __dict__:", hasattr(plain, "__dict__"))
    print("int.__dict__ wrapper type:", type(int.__dict__).__name__)

    # Define class ServiceConfig: with two immutable class attributes:
    # env: str = "dev" and retries: int = 3.
    # Instantiate c1 = ServiceConfig() and c2 = ServiceConfig().
    # Print vars(c1) (expect {}), "env" in ServiceConfig.__dict__ (expect True),
    # and c1.env (expect "dev").


    # Shadow the class attribute on c1 only: assign c1.retries = 5.
    # Print c1.retries, c2.retries, ServiceConfig.retries, and vars(c1) to see
    # that only c1.__dict__ received the new key.


    # Remove the instance shadow with del c1.retries and print c1.retries and
    # vars(c1) again so you see lookup fall back to ServiceConfig.retries (3).


def mutable_class_attribute_trap() -> None:

    # The read/write asymmetry creates one of Python's most famous OOP bugs.
    # Calling obj.bag.append("gem") does NOT assign to obj.bag: it READS
    # obj.bag (finding the class-level list if the instance has none) and
    # mutates that single shared list in place!
    #
    #     Suppose BuggyPlayer defines bag: list[str] = [] directly in the class body:
    #         p1 = BuggyPlayer("Ada")
    #         p2 = BuggyPlayer("Linus")
    #         p1.bag.append("gem")
    #     Because neither instance has "bag" in vars(self), both p1.bag and
    #     p2.bag resolve to BuggyPlayer.__dict__["bag"], so p2.bag now holds ["gem"]!
    #
    # Put immutable shared defaults (like strings, ints, tuples) on the class body
    # if you want to share them, and ALWAYS create per-instance mutable containers
    # (list, dict, set) inside __init__ on self.

    shared_list: list[str] = []
    alias_a = shared_list
    alias_b = shared_list
    alias_a.append("gem")
    print("Shared reference mutation check:", alias_b, "| same object:", alias_a is alias_b)

    # Define class BuggyPlayer: with a mutable class attribute
    # bag: list[str] = [] directly inside the class body, and
    # def __init__(self, name: str) -> None: setting self.name = name.
    # Instantiate p1 = BuggyPlayer("Ada") and p2 = BuggyPlayer("Linus"), call
    # p1.bag.append("gem"), and print p1.bag, p2.bag, p1.bag is p2.bag (True),
    # and "bag" in vars(p1) (False).


    # Now rebind p1.bag = ["scroll"] on the same BuggyPlayer instances and print
    # p1.bag, p2.bag, and vars(p1). Notice that rebinding writes a brand-new list
    # into p1.__dict__ while BuggyPlayer.bag and p2.bag still share ["gem"].


    # Define a fixed class Player: with an immutable class attribute
    # role: str = "adventurer" and def __init__(self, name: str) -> None: that
    # sets self.name = name and self.bag: list[str] = [].
    # Instantiate fixed_p1 = Player("Ada") and fixed_p2 = Player("Linus"), append
    # "compass" to fixed_p1.bag, and verify fixed_p2.bag == [] and
    # fixed_p1.bag is not fixed_p2.bag. Print vars(fixed_p1), fixed_p1.role, and
    # list(Player.__dict__.keys()) to see where each name lives.


def allocation_with_new_vs_init() -> None:

    # Calling Player("Ada") runs object creation in two distinct phases:
    # - __new__(cls, *args, **kwargs) is the allocator. Python calls it first
    #   with the class (cls) to allocate and return the fresh instance object.
    # - __init__(self, *args, **kwargs) is the initializer. Python calls it
    #   second on the already allocated self to populate attributes. Because
    #   self already exists, __init__ MUST return None (returning any other
    #   value raises TypeError).
    #
    # You rarely override __new__, except in two concrete cases:
    # - Subclassing immutable built-ins (str, int, tuple): once __new__ finishes
    #   allocating a str, its character buffer is frozen forever, so __init__ is
    #   too late to alter its text!
    # - Returning a cached or singleton instance instead of allocating a new one.
    #
    #     Suppose UpperStr subclasses str and overrides __new__(cls, text):
    #         return super().__new__(cls, text.upper())
    #     Calling UpperStr("python") allocates an immutable str holding "PYTHON"
    #     whose type is UpperStr before __init__ ever runs.

    raw = str.__new__(str, "allocated")
    print("Created directly via str.__new__:", repr(raw), "| type:", type(raw).__name__)

    # Define class UpperStr(str): overriding
    # def __new__(cls, text: str) -> "UpperStr": to return
    # super().__new__(cls, text.upper()).
    # Instantiate tag = UpperStr("python") and print tag, tag == "PYTHON",
    # isinstance(tag, str), and type(tag) is UpperStr.


    # Build an interning cache with __new__: define class Symbol: with a class
    # attribute _pool: dict[str, "Symbol"] = {}.
    # In def __new__(cls, name: str) -> "Symbol": check if name is already in
    # cls._pool and return the existing instance if found; otherwise allocate
    # obj = super().__new__(cls), set obj.name = name, save cls._pool[name] = obj,
    # and return obj. Verify Symbol("ready") is Symbol("ready") is True and
    # Symbol("ready") is not Symbol("idle").


    # Observe the __init__ return contract: try uncommenting below to confirm
    # Python rejects any non-None return value from __init__ with TypeError.
    # class BadInit:
    #     def __init__(self) -> int:
    #         return 42
    # BadInit()


def bound_methods_and_dynamic_attributes() -> None:

    # Functions defined inside a class body live once inside Class.__dict__, not
    # copied onto every instance. When you access instance.method, Python binds
    # instance as the first argument (self) and hands back a lightweight bound
    # method object whose .__self__ attribute points to the instance.
    #
    #     Suppose c = Counter(10) and Counter defines step(self, delta=1).
    #     Calling c.step(2) is identical to calling Counter.step(c, 2).
    #
    # Python also provides built-in helpers for dynamic attribute names:
    # getattr(obj, name, default), setattr(obj, name, value),
    # delattr(obj, name), and hasattr(obj, name).

    bound_upper = "odin".upper
    print("Bound method __self__:", repr(bound_upper.__self__), "| call:", bound_upper())

    # Define class Counter: with def __init__(self, start: int = 0) -> None:
    # setting self.value = start, and def step(self, delta: int = 1) -> int:
    # adding delta to self.value and returning self.value.
    # Create c = Counter(10), call both c.step(2) and Counter.step(c, 3), and
    # print c.value (expect 15) alongside c.step.__self__ is c (expect True).


    # Practice dynamic attribute helpers on c: attach a temporary tag using
    # setattr(c, "label", "requests"), print getattr(c, "label", "none"), remove
    # it with delattr(c, "label"), and confirm getattr(c, "label", "none") now
    # returns "none".


    # Confirm Class.__dict__ is a read-only mappingproxy: try uncommenting below
    # to trigger TypeError: 'mappingproxy' object does not support item assignment.
    # Counter.__dict__["injected"] = 1


def main() -> None:

    print("=== 1. Class namespaces and attribute lookup ===")
    class_namespaces_and_attribute_lookup()

    print("\n=== 2. Mutable class attribute trap ===")
    mutable_class_attribute_trap()

    print("\n=== 3. Allocation with __new__ vs. __init__ ===")
    allocation_with_new_vs_init()

    print("\n=== 4. Bound methods and dynamic attributes ===")
    bound_methods_and_dynamic_attributes()


if __name__ == "__main__":
    main()
