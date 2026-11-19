# python 395_init_subclass_and_metaclasses.py

from typing import Any


def classes_as_runtime_objects_and_3arg_type() -> None:

    # In Python, classes themselves are runtime objects—specifically, instances
    # of 'type' (and 'type' is even an instance of itself!).
    #
    # Calling type(obj) with one argument inspects an object's class; calling
    # type(name, bases, namespace_dict) with three arguments dynamically builds
    # a brand-new class object at runtime. In fact, every 'class Foo(Base):'
    # block you write simply executes its body into a dictionary and hands
    # (name, bases, namespace) to type(...) under the hood!
    #
    #     Suppose you call:
    #         DynamicBox = type("DynamicBox", (), {"kind": "box"})
    #     DynamicBox is a real class: DynamicBox.kind == "box",
    #     type(DynamicBox()) is DynamicBox, and type(DynamicBox) is type.

    print("type(int) is type:", type(int) is type, "| type(type) is type:", type(type) is type)

    # Build a class dynamically with 3-argument type():
    # DynamicBox = type("DynamicBox", (), {"kind": "box", "label": lambda self: f"item:{self.kind}"})
    # Instantiate box = DynamicBox() and print DynamicBox.kind, box.label(),
    # type(box) is DynamicBox, and type(DynamicBox) is type.


    # Create a dynamic subclass inheriting from DynamicBox:
    # LabeledBox = type("LabeledBox", (DynamicBox,), {"kind": "crate"})
    # Print [cls.__name__ for cls in LabeledBox.__mro__] and LabeledBox().label()
    # (expect "item:crate").


def plugin_registries_with_init_subclass() -> None:

    # Before Python 3.6, hooking into subclass creation (for plugin registries,
    # validating subclass invariants, or accepting extra class keyword arguments)
    # required writing a custom metaclass inheriting from type—which often caused
    # painful metaclass-conflict TypeErrors when mixing libraries.
    #
    # Modern Python solves ~95% of those tasks cleanly in ~5 lines via
    # __init_subclass__ (PEP 487):
    # - Define def __init_subclass__(cls, **kwargs: Any) -> None: on a base class.
    # - Whenever ANY subclass finishes being created, Python automatically calls
    #   Parent.__init_subclass__(SubClass, **kwargs) at CLASS-DEFINITION TIME
    #   (zero instances required!), forwarding any keyword arguments written in
    #   class PingPlugin(CommandPlugin, command_name="ping"):.
    # - Always call super().__init_subclass__(**kwargs) so cooperative
    #   multiple inheritance stays intact!
    #
    #     Suppose CommandPlugin tracks REGISTRY: dict[str, type["CommandPlugin"]] = {}:
    #         class PingPlugin(CommandPlugin, command_name="ping"): ...
    #     The moment that 'class' statement finishes executing,
    #     CommandPlugin.REGISTRY["ping"] is already PingPlugin!

    print("object provides default __init_subclass__:", hasattr(object, "__init_subclass__"))

    # Define class CommandPlugin: with a class-level registry
    # REGISTRY: dict[str, type["CommandPlugin"]] = {} (quoting "CommandPlugin"
    # because the name is not bound until the class body finishes).
    # Add def __init_subclass__(cls, *, command_name: str, **kwargs: Any) -> None:
    # that calls super().__init_subclass__(**kwargs), raises ValueError if
    # not command_name or command_name in cls.REGISTRY, stores
    # cls.REGISTRY[command_name] = cls, and sets cls.command_name = command_name.


    # Define two subclasses:
    # - class PingPlugin(CommandPlugin, command_name="ping"): with
    #   def run(self) -> str: return "pong"
    # - class StatusPlugin(CommandPlugin, command_name="status"): with
    #   def run(self) -> str: return "ok"
    # Print list(CommandPlugin.REGISTRY.keys()) BEFORE creating any instance,
    # then look up plugin_cls = CommandPlugin.REGISTRY["ping"] and print
    # plugin_cls().run() ("pong").


    # Verify duplicate command rejection: wrap defining a duplicate subclass
    # reusing command_name="ping" in try/except ValueError (or verify by
    # uncommenting) to confirm validation fires at class-definition time!


def custom_metaclasses_and_new_validation() -> None:

    # Reserve full custom metaclasses (class Meta(type):) for the rare cases
    # that __init_subclass__ cannot handle:
    # - Intercepting or transforming the namespace dict or constructed class
    #   object inside __new__(metacls, name, bases, namespace, **kwargs).
    # - Providing a custom namespace mapping BEFORE the class body executes via
    #   __prepare__(metacls, name, bases, **kwargs).
    # - Customizing how Cls(*args, **kwargs) constructs instances via Meta.__call__.
    #
    #     Suppose EnforceSnakeCaseMeta.__new__ scans namespace.items():
    #     - class CleanService(metaclass=EnforceSnakeCaseMeta): def fetch_data -> ok!
    #     - class BrokenService(metaclass=EnforceSnakeCaseMeta): def badMethod ->
    #       raises TypeError immediately at class definition time!

    print("Metaclasses subclass type:", issubclass(type, object))

    # Define class EnforceSnakeCaseMeta(type): overriding
    # def __new__(metacls, name: str, bases: tuple[type, ...], namespace: dict[str, Any], **kwargs: Any) -> type:
    # Iterate over attr_name, attr_val in namespace.items(): if callable(attr_val)
    # and not attr_name.startswith("_") and any(ch.isupper() for ch in attr_name),
    # raise TypeError(f"Public method {attr_name!r} on {name} must be snake_case").
    # Otherwise return super().__new__(metacls, name, bases, namespace, **kwargs).


    # Define compliant class CleanService(metaclass=EnforceSnakeCaseMeta): with
    # def fetch_data(self) -> str: return "ready", instantiate it, and print
    # CleanService().fetch_data().
    #
    # Try uncommenting below after defining EnforceSnakeCaseMeta to observe
    # class-definition-time rejection (notice no instance is ever created!):
    # class BrokenService(metaclass=EnforceSnakeCaseMeta):
    #     def badMethod(self) -> str:
    #         return "rejected"


def prepare_hook_and_metaclass_conflicts() -> None:

    # One capability belongs exclusively to metaclasses: __prepare__. Python
    # calls Meta.__prepare__(name, bases, **kwargs) BEFORE executing the class
    # body and uses the returned mapping to collect every assignment inside the
    # class! That lets you catch duplicate attribute or method definitions in
    # the same class body—something a plain dict silently overwrites before
    # __init_subclass__ or __new__ ever sees it!
    #
    # Keep metaclasses minimal because inheriting from two bases with unrelated
    # metaclasses raises TypeError: metaclass conflict, whereas __init_subclass__
    # composes cleanly through super().

    prepared = type.__prepare__("Demo", ())
    print("Default type.__prepare__ returns:", type(prepared).__name__)

    # Define class UniqueDict(dict): overriding
    # def __setitem__(self, key: str, value: Any) -> None: to raise
    # TypeError(f"Duplicate class attribute: {key!r}") if key in self and not key.startswith("__"),
    # else delegating to super().__setitem__(key, value).
    # Define class NoDuplicateAttrMeta(type): with
    # @classmethod def __prepare__(metacls, name: str, bases: tuple[type, ...], **kwargs: Any) -> UniqueDict:
    # returning UniqueDict().


    # Define class UniqueConfig(metaclass=NoDuplicateAttrMeta): with
    # host = "localhost" and port = 8080, and print UniqueConfig.host and
    # UniqueConfig.port.
    #
    # Try uncommenting a duplicate key class below to watch __prepare__ catch a
    # silent overwrite right as the class body executes:
    # class DuplicateConfig(metaclass=NoDuplicateAttrMeta):
    #     port = 8080
    #     port = 9090


def main() -> None:

    print("=== 1. Classes as runtime objects and 3-arg type() ===")
    classes_as_runtime_objects_and_3arg_type()

    print("\n=== 2. Plugin registries with __init_subclass__ ===")
    plugin_registries_with_init_subclass()

    print("\n=== 3. Custom metaclasses and __new__ validation ===")
    custom_metaclasses_and_new_validation()

    print("\n=== 4. __prepare__ hooks and metaclass conflicts ===")
    prepare_hook_and_metaclass_conflicts()


if __name__ == "__main__":
    main()
