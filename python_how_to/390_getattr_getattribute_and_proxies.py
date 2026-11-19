# python 390_getattr_getattribute_and_proxies.py

from typing import Any


def fallback_getattr_and_attribute_error_contract() -> None:

    # Python gives you two hooks for dynamic attribute reads, and picking the
    # wrong one leads straight to RecursionError or broken hasattr() calls.
    #
    # Start with __getattr__(self, name: str) -> Any, the SAFE fallback hook:
    # - Python calls __getattr__ ONLY when normal lookup (data descriptors ->
    #   self.__dict__ -> class/MRO) fails with AttributeError. Normal attributes
    #   pay zero extra overhead!
    # - Crucial contract: if 'name' does not exist virtually either, __getattr__
    #   MUST raise AttributeError—NEVER let KeyError escape from an internal dict!
    #   Why? Built-ins like hasattr(obj, "missing") and getattr(obj, "missing", "fallback")
    #   ONLY catch AttributeError; a leaked KeyError crashes them!
    #
    #     Suppose cfg = LazyConfigProxy({"host": "localhost"}):
    #         cfg.host                       -> __getattr__("host") -> "localhost"
    #         getattr(cfg, "missing", "def") -> __getattr__ raises AttributeError -> "def"
    #         hasattr(cfg, "missing")        -> catches AttributeError -> False

    print("getattr fallback on object():", getattr(object(), "missing_key", "safe_default"))

    # Define class LazyConfigProxy: at module level (so section 3 can wrap it) with:
    # - def __init__(self, data: dict[str, Any]) -> None: storing a defensive
    #   copy via super().__setattr__("_data", dict(data)).
    # - def __getattr__(self, name: str) -> Any: checking if name in self._data
    #   and returning self._data[name], otherwise raising
    #   AttributeError(f"{type(self).__name__!r} has no attribute {name!r}").
    # - def __setattr__(self, name: str, value: Any) -> None: raising
    #   AttributeError("LazyConfigProxy is read-only").


    # Create cfg = LazyConfigProxy({"host": "localhost", "port": 8080}).
    # Print cfg.host, cfg.port, hasattr(cfg, "missing") (False), and
    # getattr(cfg, "missing", "fallback") ("fallback").
    # Catch AttributeError when attempting cfg.port = 9090 (or try uncommenting):
    # cfg.port = 9090


    # Prove why leaking KeyError breaks Python's built-ins: define a 4-line
    # class LeakyProxy: whose __getattr__ blindly returns self._data[name]
    # without converting KeyError to AttributeError. Wrap
    # hasattr(LeakyProxy({}), "missing") in try/except KeyError and print the
    # crashed exception!


def setattr_and_init_bootstrap_trap() -> None:

    # Unlike __getattr__, __setattr__(self, name: str, value: Any) -> None is
    # NOT a fallback—it intercepts EVERY attribute assignment on the instance,
    # including writes inside __init__ and writes inside __setattr__ itself!
    #
    #     Suppose __setattr__ tries to write self.host = value directly:
    #         self.host = value -> calls __setattr__("host", value) -> infinite loop!
    #     Always perform the real storage write through
    #     super().__setattr__(name, value) (or object.__setattr__(self, name, value)).

    print("Base write hook:", object.__setattr__.__name__)

    # Define class StrictRecord: that permits writing only an allowed set of
    # attribute names:
    # - def __init__(self, allowed: set[str]) -> None: saving the whitelist via
    #   super().__setattr__("_allowed", set(allowed)).
    # - def __setattr__(self, name: str, value: Any) -> None: raising
    #   AttributeError(f"Field {name!r} is not allowed") if name not in self._allowed,
    #   otherwise calling super().__setattr__(name, value).
    # Create rec = StrictRecord({"host", "port"}), set rec.host = "127.0.0.1"
    # and rec.port = 443, print vars(rec), and catch AttributeError on rec.typo = 1.


def universal_getattribute_and_recursion_trap() -> None:

    # __getattribute__(self, name: str) -> Any is the unconditional interceptor:
    # Python calls it on EVERY single obj.name access, even when 'name' already
    # lives in self.__dict__, and even when code inside __getattribute__ reads
    # self._target!
    #
    # Writing self._target inside __getattribute__ immediately invokes
    # __getattribute__("_target") recursively until RecursionError! To read
    # internal fields safely, ALWAYS delegate to super().__getattribute__(name)
    # (or object.__getattribute__(self, name)).
    #
    #     Suppose audited = AuditProxy(cfg):
    #         audited.host -> __getattribute__("host")
    #                      -> log = super().__getattribute__("access_log")
    #                      -> log.append("host")
    #                      -> target = super().__getattribute__("_target")
    #                      -> returns getattr(target, "host") ("localhost")

    print("Base read hook:", object.__getattribute__.__name__)

    # Define class AuditProxy: at module level (so section 4 can subclass it) with:
    # - def __init__(self, target: Any) -> None: calling
    #   super().__setattr__("_target", target) and
    #   super().__setattr__("access_log", []).
    # - def __getattribute__(self, name: str) -> Any: returning
    #   super().__getattribute__(name) directly when name in ("_target", "access_log");
    #   for any other name, fetching log = super().__getattribute__("access_log")
    #   and target = super().__getattribute__("_target"), appending name to log,
    #   and returning getattr(target, name).


    # Create cfg = LazyConfigProxy({"host": "localhost", "port": 8080}) and wrap
    # it in audited = AuditProxy(cfg). Read audited.host and audited.port, then
    # print audited.access_log (expect ['host', 'port']).


def implicit_dunder_lookup_bypasses_proxies() -> None:

    # Watch out for one famous proxy limitation: Python's built-in operator and
    # protocol syntax—len(proxy), str(proxy), iter(proxy), proxy[0]—looks up
    # dunder methods directly on type(proxy), completely bypassing instance
    # __getattribute__ and __getattr__!
    #
    #     Suppose wrapped = AuditProxy([10, 20, 30]):
    #         wrapped.count(20)  -> regular attribute access -> forwarded! (1)
    #         len(wrapped)       -> looks up AuditProxy.__len__ -> raises TypeError!
    #
    # Whenever a proxy must support built-in protocols like len() or iteration,
    # define explicit forwarding dunders (__len__, __iter__, __getitem__) on the
    # proxy class itself.

    print("Implicit dunder syntax looks on type(obj), bypassing __getattr__.")

    # Wrap items = [10, 20, 30] in wrapped = AuditProxy(items).
    # Print wrapped.count(20) (1—forwarded through __getattribute__) and
    # wrapped.access_log (['count']), then catch TypeError when calling
    # len(wrapped).


    # Define class SizedAuditProxy(AuditProxy): adding explicit forwarding
    # def __len__(self) -> int: returning len(super().__getattribute__("_target")).
    # Verify len(SizedAuditProxy([10, 20, 30])) returns 3 cleanly.


def main() -> None:

    print("=== 1. Fallback __getattr__ and the AttributeError contract ===")
    fallback_getattr_and_attribute_error_contract()

    print("\n=== 2. __setattr__ and the __init__ bootstrap trap ===")
    setattr_and_init_bootstrap_trap()

    print("\n=== 3. Universal __getattribute__ and the recursion trap ===")
    universal_getattribute_and_recursion_trap()

    print("\n=== 4. Implicit dunder lookups bypass proxies ===")
    implicit_dunder_lookup_bypasses_proxies()


if __name__ == "__main__":
    main()
