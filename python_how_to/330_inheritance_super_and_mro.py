# python 330_inheritance_super_and_mro.py


def mro_and_c3_linearization() -> None:

    # The biggest mental shift in Python OOP is unlearning what super() means in
    # single-inheritance languages. In Python, super() does NOT mean "call my
    # static parent class." It means: "call the next class in the runtime
    # instance's Method Resolution Order (type(self).__mro__)."
    #
    # Python computes every class's __mro__ tuple at class-definition time using
    # an algorithm called C3 linearization, which enforces three guarantees:
    # - Every subclass appears before its base classes.
    # - Base classes stay in the left-to-right order written in class Sub(A, B):.
    # - Monotonicity holds across the whole graph: if an inheritance graph asks
    #   for contradictory ordering (such as A before B and B before A), Python
    #   refuses to create the class and raises TypeError immediately!
    #
    #     Suppose class B(A): exists, so B must come before A.
    #     Writing class BadC(A, B): asks for A before B at the same time.
    #     C3 linearization has no valid order, so Python raises TypeError right
    #     when the class statement executes.

    print("bool MRO:", [cls.__name__ for cls in bool.__mro__])
    print("isinstance(True, int):", isinstance(True, int), "| issubclass(bool, int):", issubclass(bool, int))

    # Build a 3-level single-inheritance chain:
    # - class Animal: with def speak(self) -> str: returning "..."
    # - class Mammal(Animal): with def speak(self) -> str: returning "mammal sound"
    # - class Dog(Mammal): with def speak(self) -> str: returning "woof"
    # Print [cls.__name__ for cls in Dog.__mro__], isinstance(Dog(), Animal),
    # issubclass(Dog, Mammal), and Dog().speak().


    # Observe C3 linearization rejecting an inconsistent inheritance graph at
    # class-definition time: try uncommenting the three classes below to trigger
    # TypeError: Cannot create a consistent method resolution order (MRO).
    # class A:
    #     tag = "A"
    # class B(A):
    #     tag = "B"
    # class BadC(A, B):
    #     tag = "BadC"


def cooperative_mixins_with_super() -> None:

    # Zero-argument super() inspects the enclosing class (__class__) and self,
    # locates __class__ inside type(self).__mro__, and delegates to the class
    # immediately after it. That single rule enables cooperative Mixins (small
    # focused classes that layer behavior without inheriting from each other).
    #
    #     Suppose CompressedJsonSerializer inherits from (CompressionMixin, JsonMixin, Serializer).
    #     Its MRO is:
    #         CompressedJsonSerializer -> CompressionMixin -> JsonMixin -> Serializer -> object
    #     Neither CompressionMixin nor JsonMixin inherits from Serializer, yet:
    #     - CompressionMixin.process calls super().process(data) -> jumps sideways to JsonMixin!
    #     - JsonMixin.process calls super().process(data) -> jumps to Serializer!
    #     - Serializer.process returns "raw:user=ada" -> JsonMixin wraps it ->
    #       CompressionMixin wraps that -> final result: 'zlib<{"payload": "raw:user=ada"}>'.

    print("super is a built-in proxy type:", super.__name__)

    # Build the 4-class cooperative pipeline:
    # - class Serializer: with def process(self, data: str) -> str: printing
    #   "  -> Serializer" and returning f"raw:{data}".
    # - class JsonMixin: with def process(self, data: str) -> str: printing
    #   "  -> JsonMixin", calling inner = super().process(data), and returning
    #   f'{{"payload": "{inner}"}}'.
    # - class CompressionMixin: with def process(self, data: str) -> str: printing
    #   "  -> CompressionMixin", calling inner = super().process(data), and returning
    #   f"zlib<{inner}>".
    # - class CompressedJsonSerializer(CompressionMixin, JsonMixin, Serializer):
    #   with class attribute mode = "compressed-json".


    # Print [cls.__name__ for cls in CompressedJsonSerializer.__mro__] and verify
    # the exact list:
    # ['CompressedJsonSerializer', 'CompressionMixin', 'JsonMixin', 'Serializer', 'object'].
    # Instantiate pipeline = CompressedJsonSerializer(), call
    # output = pipeline.process("user=ada"), and print output to see both the
    # top-down call trace and the bottom-up wrapped output.


    # Prove mixin order alone controls pipeline order: define
    # class JsonCompressedSerializer(JsonMixin, CompressionMixin, Serializer):
    # with mode = "json-compressed", run .process("user=ada"), and compare the
    # wrapped output against CompressedJsonSerializer!


def cooperative_init_with_kwargs_diamond() -> None:

    # Real diamond hierarchies get tricky when different mixins need different
    # __init__ parameters. If NetworkMixin needs host: str and AuthMixin needs
    # token: str, how do both receive their arguments cleanly when ManagedClient
    # inherits from both?
    #
    # The cooperative pattern uses keyword-only parameters plus **kwargs forwarding:
    # each mixin consumes its own keyword argument(s) and forwards all remaining
    # **kwargs to super().__init__(**kwargs)!
    #
    #     Suppose BaseDevice, NetworkMixin(BaseDevice), AuthMixin(BaseDevice),
    #     and ManagedClient(NetworkMixin, AuthMixin) form a diamond:
    #         ManagedClient -> NetworkMixin -> AuthMixin -> BaseDevice -> object
    #     Calling ManagedClient(device_id="srv-1", host="10.0.0.5", token="sec-42"):
    #     - NetworkMixin consumes host="10.0.0.5" and forwards device_id & token.
    #     - AuthMixin consumes token="sec-42" and forwards device_id.
    #     - BaseDevice consumes device_id="srv-1" and calls super().__init__()
    #       (which hits object.__init__ with empty kwargs!).
    #     Notice BaseDevice.__init__ runs ONCE—and if a caller misspells an
    #     argument like bogus=1, object.__init__ raises TypeError automatically!

    print("Terminal object.__init__ rejects leftover kwargs cleanly.")

    # Build the cooperative diamond hierarchy:
    # - class BaseDevice: with def __init__(self, *, device_id: str) -> None:
    #   that stores self.device_id = device_id, appends "BaseDevice" to
    #   self.init_order (creating self.init_order: list[str] = [] first if needed
    #   or setting self.init_order = ["BaseDevice"]), and calls super().__init__().
    # - class NetworkMixin(BaseDevice): with
    #   def __init__(self, *, host: str, **kwargs: object) -> None: storing
    #   self.host = host, calling super().__init__(**kwargs), and appending
    #   "NetworkMixin" to self.init_order.
    # - class AuthMixin(BaseDevice): with
    #   def __init__(self, *, token: str, **kwargs: object) -> None: storing
    #   self.token = token, calling super().__init__(**kwargs), and appending
    #   "AuthMixin" to self.init_order.
    # - class ManagedClient(NetworkMixin, AuthMixin): with
    #   def summary(self) -> str: returning f"{self.device_id}@{self.host} (auth={len(self.token)} chars)".


    # Instantiate client = ManagedClient(device_id="srv-1", host="10.0.0.5", token="sec-42").
    # Print [cls.__name__ for cls in ManagedClient.__mro__], client.summary(),
    # and client.init_order to verify every class initialized exactly once
    # (['BaseDevice', 'AuthMixin', 'NetworkMixin']).


    # Verify typo protection at the end of the chain: wrap
    # ManagedClient(device_id="srv-1", host="10.0.0.5", token="sec-42", bogus=1)
    # in try/except TypeError and print the error message from object.__init__.


def hardcoded_parent_double_init_trap() -> None:

    # Why should you avoid naming a parent directly (BaseDevice.__init__(self))
    # inside a multiple-inheritance hierarchy? Because hardcoding the parent
    # bypasses the MRO! In a diamond where both Left and Right call
    # Root.__init__(self), Root.__init__ runs TWICE—duplicating side effects,
    # resetting state, or opening resources twice.
    #
    #     Suppose Root increments self.root_runs += 1:
    #     - Direct calls Left -> Root and Right -> Root produce root_runs == 2!
    #     - Cooperative super().__init__() calls produce root_runs == 1!
    #
    # Practical design reminder: reach for composition (storing a helper object
    # like self.auth = Authenticator(token)) whenever you do not genuinely need
    # polymorphic inheritance or cooperative mixins.

    trace = ["Root"]
    print("Healthy diamond Root init count target:", len(trace))

    # Reproduce the hardcoded-parent diamond bug:
    # - class Root: with def __init__(self) -> None: setting
    #   self.root_runs = getattr(self, "root_runs", 0) + 1.
    # - class BadLeft(Root): calling Root.__init__(self).
    # - class BadRight(Root): calling Root.__init__(self).
    # - class BadDiamond(BadLeft, BadRight): calling BadLeft.__init__(self) and
    #   BadRight.__init__(self).
    # Instantiate BadDiamond() and print .root_runs (expect 2!).


    # Now build GoodLeft(Root), GoodRight(Root), and GoodDiamond(GoodLeft, GoodRight)
    # where every __init__ simply delegates via super().__init__(). Instantiate
    # GoodDiamond() and verify .root_runs == 1.


def main() -> None:

    print("=== 1. Method Resolution Order and C3 linearization ===")
    mro_and_c3_linearization()

    print("\n=== 2. Cooperative mixins with super() ===")
    cooperative_mixins_with_super()

    print("\n=== 3. Cooperative diamond __init__ with **kwargs ===")
    cooperative_init_with_kwargs_diamond()

    print("\n=== 4. Hardcoded-parent double-init trap ===")
    hardcoded_parent_double_init_trap()


if __name__ == "__main__":
    main()
