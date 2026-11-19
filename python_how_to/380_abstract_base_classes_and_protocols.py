# python 380_abstract_base_classes_and_protocols.py

from abc import ABC, abstractmethod
from typing import Protocol, runtime_checkable


def nominal_interfaces_with_abc() -> None:

    # Python offers two complementary ways to define interfaces: nominal
    # subtyping (abc.ABC) and structural subtyping (typing.Protocol). Choosing
    # the right one controls how tightly coupled your code stays.
    #
    # Nominal subtyping uses abc.ABC together with @abstractmethod:
    # - Implementing classes must explicitly inherit from the base class
    #   (class MemoryStorage(StorageBackend):).
    # - ABC uses ABCMeta as its metaclass, which collects every @abstractmethod
    #   into cls.__abstractmethods__. Attempting to instantiate a class whose
    #   __abstractmethods__ set is non-empty raises TypeError immediately at
    #   construction time—far safer than letting an incomplete class construct
    #   and crashing later with NotImplementedError on a rarely executed branch!
    # - ABCs shine when you own the hierarchy and want to share concrete
    #   template or helper methods (such as exists()) on the base class.
    #
    #     Suppose StorageBackend(ABC) marks load() and save() as abstract:
    #         StorageBackend()         -> TypeError right at instantiation!
    #         MemoryStorage()          -> succeeds once load() and save() exist!
    #         MemoryStorage().exists() -> reuses the concrete base helper!

    print("ABC metaclass:", type(ABC).__name__)

    # Define class StorageBackend(ABC): with:
    # - @abstractmethod def load(self, key: str) -> bytes | None: using ... (Ellipsis)
    # - @abstractmethod def save(self, key: str, data: bytes) -> None: using ...
    # - Concrete helper def exists(self, key: str) -> bool: returning
    #   self.load(key) is not None.
    # Then define class MemoryStorage(StorageBackend): backed by
    # self._store: dict[str, bytes] = {} implementing both load and save.


    # Instantiate storage = MemoryStorage(), call storage.save("greeting", b"hello"),
    # and print storage.exists("greeting") (True), storage.load("greeting"),
    # storage.load("missing") (None), StorageBackend.__abstractmethods__, and
    # MemoryStorage.__abstractmethods__ (empty frozenset).


    # Prove instantiation-time enforcement: define an incomplete subclass
    # class PartialStorage(StorageBackend): that implements only load() (omitting
    # save()), then catch TypeError when instantiating both StorageBackend() and
    # PartialStorage().
    #
    # Try uncommenting below after defining StorageBackend to see the raw error:
    # StorageBackend()


def stacking_abstractmethod_with_descriptors() -> None:

    # You can mark properties, classmethods, and staticmethods as abstract too,
    # as long as you keep the decorator stacking order right: ALWAYS put
    # @abstractmethod innermost (closest to 'def') so the outer @property or
    # @classmethod wraps the marked abstract function!
    #
    #     Suppose NamedPlugin requires a read-only plugin_name property:
    #         @property
    #         @abstractmethod
    #         def plugin_name(self) -> str: ...
    #     Putting @abstractmethod on top of @property raises or breaks binding
    #     expectations on older idioms; innermost is the documented standard.

    sample_marked = abstractmethod(lambda: None)
    print("abstractmethod sets __isabstractmethod__:", getattr(sample_marked, "__isabstractmethod__", False))

    # Define class NamedPlugin(ABC): with:
    # - @property stacked above @abstractmethod def plugin_name(self) -> str: ...
    # - @classmethod stacked above @abstractmethod def from_default(cls) -> "NamedPlugin": ...
    # Then define concrete class CachePlugin(NamedPlugin): returning "memory-cache"
    # from @property def plugin_name(self) -> str: and returning cls() from
    # @classmethod def from_default(cls) -> "CachePlugin":.
    # Instantiate plugin = CachePlugin.from_default() and print plugin.plugin_name.


def structural_subtyping_with_protocol() -> None:

    # Structural subtyping (static duck typing via typing.Protocol, PEP 544)
    # requires ZERO inheritance! Any class that supplies the matching method and
    # attribute signatures satisfies the Protocol automatically for static type
    # checkers (mypy, pyright)—even built-in or third-party classes whose source
    # code you cannot modify.
    #
    # Method bodies in a Protocol conventionally contain only ... (Ellipsis).
    # Adding @runtime_checkable enables isinstance(obj, MyProtocol) at runtime;
    # without @runtime_checkable, isinstance() against a Protocol raises TypeError.
    #
    #     Suppose Renderable(Protocol) declares def render(self) -> str: ...
    #     Banner does NOT inherit from Renderable, yet:
    #         draw_item(Banner("Hi"))           -> works cleanly!
    #         isinstance(Banner("Hi"), Renderable) -> True (with @runtime_checkable)
    #         Renderable in Banner.__mro__      -> False (zero inheritance coupling!)

    print("Protocol base ready:", Protocol.__name__)

    # Define @runtime_checkable class Renderable(Protocol): at module level (so
    # section 4 can reuse it) with def render(self) -> str: ... (Ellipsis body).
    # Define two completely unrelated classes (do NOT inherit from Renderable!):
    # - class Banner: storing self.title = title with def render(self) -> str:
    #   returning f"[ {self.title} ]"
    # - class Badge: storing self.label = label with def render(self) -> str:
    #   returning f"<{self.label}>".
    # Define def draw_item(item: Renderable) -> None: at module level printing item.render().


    # Instantiate banner = Banner("Python 3.12") and badge = Badge("stable").
    # Call draw_item(banner) and draw_item(badge), then print
    # isinstance(banner, Renderable) (True) alongside Renderable in Banner.__mro__
    # (False) to verify structural matching without inheritance.


def runtime_checkable_limits_and_choosing_contracts() -> None:

    # Keep one crucial limitation of @runtime_checkable in mind: at runtime,
    # isinstance(obj, Renderable) ONLY verifies that an attribute named "render"
    # exists on obj—it does NOT check parameter counts, parameter types, or
    # return types! Static type checkers verify full signatures; runtime checks
    # only verify attribute presence.
    #
    # Rule of thumb for choosing between them:
    # - Use abc.ABC when you control the implementations, want shared concrete
    #   template methods on the base class, or want instantiation-time checks.
    # - Use typing.Protocol when writing functions or libraries that accept any
    #   compatible object (duck typing) without forcing callers to subclass you.

    print("runtime_checkable decorator ready:", callable(runtime_checkable))

    # Prove the runtime limitation of @runtime_checkable: define
    # class BadRenderable: with def render(self, width: int) -> int: return width
    # (wrong parameters and wrong return type!).
    # Print isinstance(BadRenderable(), Renderable) (still True at runtime!),
    # then wrap draw_item(BadRenderable()) in try/except TypeError to watch the
    # mismatched signature fail when actually called.


    # Verify why @runtime_checkable is opt-in: define a plain Protocol without
    # the decorator (class PlainCloser(Protocol): with def close(self) -> None: ...)
    # and catch TypeError when calling isinstance(object(), PlainCloser).


def main() -> None:

    print("=== 1. Nominal interfaces with abc.ABC ===")
    nominal_interfaces_with_abc()

    print("\n=== 2. Stacking @abstractmethod with descriptors ===")
    stacking_abstractmethod_with_descriptors()

    print("\n=== 3. Structural subtyping with typing.Protocol ===")
    structural_subtyping_with_protocol()

    print("\n=== 4. @runtime_checkable limits and choosing contracts ===")
    runtime_checkable_limits_and_choosing_contracts()


if __name__ == "__main__":
    main()
