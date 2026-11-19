# python 360_dataclasses_slots_and_frozen.py

from dataclasses import FrozenInstanceError, InitVar, asdict, astuple, dataclass, field, replace


def frozen_slotted_and_ordered_dataclasses() -> None:

    # Writing __init__, __repr__, __eq__, __hash__, and ordering methods by hand
    # for every data-carrying class is repetitive and bug-prone. Decorating a
    # class with @dataclass reads its class-level type annotations at class
    # creation time and generates those methods cleanly for you. (Annotations
    # guide code generation and static type checkers—@dataclass does NOT enforce
    # runtime types automatically.)
    #
    # Four decorator flags shape modern Python 3.10+ value objects:
    # - slots=True replaces per-instance __dict__ with fixed slots, cutting
    #   memory overhead and catching attribute-name typos.
    # - frozen=True blocks attribute reassignment (raising FrozenInstanceError,
    #   a subclass of AttributeError) AND auto-generates __hash__ when eq=True so
    #   instances work inside sets and as dict keys.
    # - order=True generates __lt__, __le__, __gt__, and __ge__, comparing fields
    #   as a tuple in declaration order.
    # - field(compare=False) excludes non-identifying metadata (like a comment or
    #   timestamp) from __eq__, __hash__, and order=True comparisons!
    #
    #     Suppose ServerEndpoint has host, port, and note=field(default="", compare=False):
    #         a = ServerEndpoint("127.0.0.1", 8080, note="primary")
    #         b = ServerEndpoint("127.0.0.1", 8080, note="replica")
    #     a == b is True and hash(a) == hash(b) because 'note' is ignored in comparisons!

    print("dataclasses helpers ready:", callable(replace) and callable(asdict) and callable(astuple))

    # Define @dataclass(slots=True, frozen=True, order=True) class ServerEndpoint:
    # at module level (so section 3 can reuse it) with fields:
    # - host: str
    # - port: int = 8080
    # - tags: tuple[str, ...] = ()
    # - note: str = field(default="", compare=False)
    # - strip_host: InitVar[bool] = True
    # (InitVar[T] passes a parameter to __init__ and __post_init__ without
    # storing it as an attribute on self!)
    # Add def __post_init__(self, strip_host: bool) -> None: that strips
    # self.host via object.__setattr__(self, "host", self.host.strip()) when
    # strip_host is True, and raises ValueError if not (1 <= self.port <= 65535).


    # Instantiate ep_a = ServerEndpoint("  127.0.0.1  ", 8080, note="primary"),
    # ep_b = ServerEndpoint("127.0.0.1", 8080, note="replica"), and
    # ep_hi = replace(ep_a, port=9090, tags=("api", "tls")).
    # Print ep_a == ep_b (True via compare=False!), ep_a < ep_hi (True via
    # order=True!), len({ep_a, ep_b, ep_hi}) (2—proving hashability),
    # hasattr(ep_a, "strip_host") (False), asdict(ep_hi), and astuple(ep_hi).


def mutable_defaults_kw_only_and_repr_hiding() -> None:

    # @dataclass protects you from Primer 300's shared mutable class attribute
    # trap: writing jobs: list[str] = [] raises ValueError immediately when the
    # class is defined! Instead, pass a zero-arg factory function via
    # field(default_factory=list) so every instance gets a brand-new list.
    #
    # Two other field/decorator options save headaches in production code:
    # - field(repr=False) hides sensitive values (tokens, passwords) or massive
    #   buffers from repr() output and tracebacks while keeping normal attribute
    #   access intact.
    # - @dataclass(kw_only=True) (Python 3.10+) requires callers to pass fields
    #   by keyword name (RetryPolicy(max_attempts=5)), preventing positional
    #   argument swaps when a class has several booleans or numbers.
    #
    #     Suppose JobQueue defines secret_token: str = field(default="dev", repr=False):
    #         repr(JobQueue("main")) -> "JobQueue(name='main', jobs=[])"
    #         q.secret_token         -> "dev" (still readable, never leaked in logs!)

    print("FrozenInstanceError is an AttributeError:", issubclass(FrozenInstanceError, AttributeError))

    # Define mutable @dataclass(slots=True) class JobQueue: with fields:
    # - name: str
    # - jobs: list[str] = field(default_factory=list)
    # - secret_token: str = field(default="dev-secret", repr=False, compare=False)
    # Create q1 = JobQueue("default") and q2 = JobQueue("batch"). Append "build"
    # to q1.jobs, verify q2.jobs == [], and print repr(q1) alongside q1.secret_token.


    # Define @dataclass(slots=True, frozen=True, kw_only=True) class RetryPolicy:
    # with max_attempts: int = 3, base_delay_s: float = 0.5, and jitter: bool = True.
    # Create policy = RetryPolicy(max_attempts=5, jitter=False), print policy,
    # and catch TypeError when attempting positional construction RetryPolicy(5).


def frozen_post_init_and_replace_validation() -> None:

    # On a frozen=True dataclass, writing self.host = self.host.strip() inside
    # __post_init__ raises FrozenInstanceError because __setattr__ is already
    # locked! That is why normalization inside __post_init__ must call
    # object.__setattr__(self, "host", ...), matching what the generated __init__
    # itself uses under the hood.
    #
    # To "modify" a frozen dataclass, call dataclasses.replace(obj, **changes).
    # replace() builds a brand-new instance and re-runs __post_init__, so every
    # invariant stays enforced on derived copies too!

    print("InitVar helper type:", InitVar.__name__)

    # Verify frozen immutability and replace() validation on ServerEndpoint:
    # create ep = ServerEndpoint("127.0.0.1", 8080), catch FrozenInstanceError
    # when attempting ep.port = 80, and catch ValueError when calling
    # replace(ep, port=99999).
    #
    # Try uncommenting the class below to observe @dataclass rejecting mutable
    # defaults at class-definition time with ValueError:
    # @dataclass
    # class BadQueue:
    #     items: list[str] = []


def dataclass_inheritance_caveats() -> None:

    # Dataclass inheritance works smoothly once you know three sharp rules that
    # Python enforces at decoration time:
    # - Field ordering trap: because generated __init__ concatenates base fields
    #   followed by subclass fields, if a base dataclass has a field WITH a
    #   default (retries: int = 3), a subclass CANNOT add a positional field
    #   WITHOUT a default (url: str)—Python raises TypeError! Putting kw_only=True
    #   on the subclass (or base) fixes this cleanly in Python 3.10+.
    # - Frozen mismatch trap: a frozen=False dataclass cannot inherit from a
    #   frozen=True dataclass (and vice versa); both must agree on frozen.
    # - slots=True inheritance rule: each subclass should also specify
    #   @dataclass(slots=True) so Python does not silently re-introduce __dict__
    #   on subclass instances, and avoid inheriting from two slotted dataclasses
    #   that both declare fields (C layout conflict).
    #
    #     Suppose BaseTask has name: str and retries: int = 3:
    #         @dataclass(slots=True, kw_only=True)
    #         class HttpTask(BaseTask):
    #             url: str
    #     HttpTask(name="health", url="https://example.com") works cleanly,
    #     keeps slots (no __dict__), and avoids the positional default-order error!

    print("Dataclass inheritance checks run at class decoration time.")

    # Define @dataclass(slots=True) class BaseTask: with name: str and
    # retries: int = 3.
    # Then define @dataclass(slots=True, kw_only=True) class HttpTask(BaseTask):
    # adding a required field url: str (no default value!).
    # Instantiate task = HttpTask(name="health", url="https://example.com"),
    # print task, and verify hasattr(task, "__dict__") is False.


    # Observe the non-default-after-default TypeError trap: try uncommenting the
    # subclass below (missing kw_only=True) after defining BaseTask.
    # @dataclass
    # class BrokenHttpTask(BaseTask):
    #     url: str


    # Observe the frozen mismatch TypeError trap: try uncommenting below to see
    # Python reject a mutable subclass of a frozen base dataclass.
    # @dataclass(frozen=True)
    # class FrozenBase:
    #     code: int
    # @dataclass(frozen=False)
    # class MutableChild(FrozenBase):
    #     detail: str


def main() -> None:

    print("=== 1. Frozen, slotted, ordered dataclasses and compare=False ===")
    frozen_slotted_and_ordered_dataclasses()

    print("\n=== 2. Mutable defaults, kw_only=True, and repr hiding ===")
    mutable_defaults_kw_only_and_repr_hiding()

    print("\n=== 3. Frozen __post_init__ and replace() validation ===")
    frozen_post_init_and_replace_validation()

    print("\n=== 4. Dataclass inheritance caveats ===")
    dataclass_inheritance_caveats()


if __name__ == "__main__":
    main()
