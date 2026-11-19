# python 255_enum_intenum_and_flag.py

from enum import Enum, Flag, IntEnum, IntFlag, StrEnum, auto, unique
import json


def pure_enum_identity_and_unique() -> None:

    # Hardcoding magic strings ("pending", "paid") or bare integer codes
    # (1, 2, 3) invites silent typos and accidental cross-domain comparisons.
    # Python's enum.Enum creates named singleton members carrying .name and
    # .value attributes.
    #
    # One crucial rule separates pure Enum from C/Odin integer enums: a pure
    # Enum member is NEVER equal to its underlying value!
    #
    #     Suppose class Color(Enum): RED = 1.
    #     - Color.RED == 1 evaluates to False (preventing Color.RED == Status.OK
    #       accidents!).
    #     - Because every Enum member is a singleton, compare members with
    #       identity: current is Color.RED.
    #     - Look up by value with call syntax Color(1) -> Color.RED, and by
    #       name with subscript syntax Color["RED"] -> Color.RED.
    #
    # By default, defining two member names with the same value creates a
    # silent alias (the second name points to the first member and is skipped
    # during iteration). Decorating the class with @unique makes Python raise
    # ValueError immediately at class definition time if any value repeats.

    class StarterMode(Enum):
        IDLE = auto()
        ACTIVE = auto()

    print(
        "Starter Enum:",
        StarterMode.IDLE.name,
        StarterMode.IDLE.value,
        "equals 1?",
        StarterMode.IDLE == 1,
    )

    # Define @unique class TrafficState(Enum): with RED = auto(),
    # YELLOW = auto(), and GREEN = auto() (auto() yields 1, 2, 3 on Enum).
    # Verify TrafficState.RED == 1 is False, TrafficState.RED is TrafficState(1)
    # is True, and print TrafficState["GREEN"] alongside [s.name for s in TrafficState].


    # Observe silent aliases vs @unique enforcement:
    # define class AliasDemo(Enum): FIRST = 1 and DUPLICATE = 1 (without
    # @unique), print AliasDemo.DUPLICATE is AliasDemo.FIRST (True!) and
    # list(AliasDemo) (only [AliasDemo.FIRST] appears).
    #
    # Try uncommenting below to trigger ValueError at class definition time:
    # @unique
    # class BadEnum(Enum):
    #     A = 1
    #     B = 1


def strenum_intenum_and_json_interop() -> None:

    # Pure Enum protects against accidental comparisons, but fails when you
    # pass a member directly to string APIs, integer comparisons, SQL drivers,
    # or json.dumps() (which raises TypeError on pure Enum!).
    #
    # Python solves this with two typed subclasses:
    # - StrEnum (Python 3.11+): subclasses both str and Enum, so members ARE
    #   real strings! Even better, auto() on a StrEnum sets each member's value
    #   to its LOWERCASE member name:
    #
    #       Suppose class OrderStatus(StrEnum): PAID = auto().
    #       OrderStatus.PAID.value is "paid", OrderStatus.PAID == "paid" is
    #       True, and json.dumps({"status": OrderStatus.PAID}) produces
    #       '{"status": "paid"}' with zero custom encoder!
    #
    # - IntEnum: subclasses both int and Enum, so HttpCode.OK == 200 is True,
    #   HttpCode.OK < 300 works directly, and json.dumps() serializes it as 200.

    class StarterHttp(IntEnum):
        OK = 200

    print("Starter IntEnum JSON:", json.dumps({"code": StarterHttp.OK}), StarterHttp.OK == 200)

    # Build a StrEnum and verify string equality, lookups, and JSON round-trip:
    # define @unique class OrderStatus(StrEnum): with PENDING = auto(),
    # PAID = auto(), and SHIPPED = auto().
    # Print OrderStatus.PAID.value, verify OrderStatus.PAID == "paid" is True,
    # test value lookup OrderStatus("shipped") and name lookup
    # OrderStatus["PENDING"].
    # Then serialize payload = json.dumps({"order_id": 42, "status": OrderStatus.PAID}),
    # parse it back with data = json.loads(payload), and reconstruct
    # restored = OrderStatus(data["status"]) verifying restored is OrderStatus.PAID.


    # Contrast IntEnum interop with pure Enum JSON failure:
    # define class HttpCode(IntEnum): with OK = 200, NOT_FOUND = 404, and
    # SERVER_ERROR = 500. Print HttpCode.OK == 200, 200 <= HttpCode.OK < 300,
    # and json.dumps({"status": HttpCode.NOT_FOUND}).
    # Next wrap json.dumps({"color": StarterColor.RED}) on a tiny pure Enum
    # class StarterColor(Enum): RED = 1 inside try / except TypeError as err:
    # and print err to confirm pure Enum refuses implicit JSON serialization.


def flag_and_intflag_bitmasks() -> None:

    # When options combine as bitmasks (permissions, file modes, packet flags),
    # hand-writing 1 << 0, 1 << 1, 1 << 2 is error-prone and hard to debug.
    # Flag and IntFlag make auto() generate powers of two (1, 2, 4, 8...) and
    # support bitwise | (union), & (intersection), ^ (toggle), ~ (invert),
    # membership testing (Permission.READ in rw), and iterating for bit in rw:
    # to yield each individual set bit!
    #
    #     Suppose class Permission(Flag): READ = auto(); WRITE = auto().
    #     Building rw = Permission.READ | Permission.WRITE sets bits 1 | 2 = 3.
    #     Permission.READ in rw is True, and list(rw) yields
    #     [Permission.READ, Permission.WRITE].
    #
    # Choose Flag vs IntFlag intentionally:
    # - Flag is strictly typed: combining Permission.READ | 2 raises TypeError.
    # - IntFlag subclasses int, so it interoperates smoothly with raw integer
    #   bitmasks from C APIs, wire protocols, or JSON payloads while keeping
    #   readable flag names when printed.

    class StarterBits(IntFlag):
        ALPHA = auto()
        BETA = auto()

    print("Starter IntFlag:", StarterBits.ALPHA | StarterBits.BETA, "as int:", int(StarterBits.ALPHA | StarterBits.BETA))

    # Build a type-safe Flag bitmask and iterate its active bits:
    # define class Permission(Flag): with READ = auto(), WRITE = auto(),
    # EXECUTE = auto(), and ADMIN = READ | WRITE | EXECUTE.
    # Create rw = Permission.READ | Permission.WRITE, print
    # Permission.READ in rw (True), Permission.EXECUTE in rw (False),
    # rw & Permission.ADMIN, toggled = rw ^ Permission.WRITE, and
    # list(Permission.READ | Permission.EXECUTE).


    # Practice IntFlag integer and JSON interoperability:
    # define class WireFlag(IntFlag): with COMPRESSED = auto(),
    # ENCRYPTED = auto(), and CHECKSUM = auto().
    # Combine header_flags = WireFlag.COMPRESSED | WireFlag.CHECKSUM, verify
    # header_flags == 5, combine with raw int bit 2 using
    # upgraded = header_flags | 2, serialize json.dumps({"flags": upgraded}),
    # and reconstruct WireFlag(7) to inspect its active members via list(WireFlag(7)).
    #
    # Try uncommenting below to confirm pure Flag rejects raw integer masks:
    # bad_mask = Permission.READ | 2


    # Invert a Flag mask cleanly with ~ to subtract a single permission bit:
    # compute read_only = Permission.ADMIN & ~Permission.WRITE & ~Permission.EXECUTE
    # and print read_only alongside read_only is Permission.READ (True!).


def main() -> None:

    print("=== 1. Pure Enum identity, lookups, and @unique ===")
    pure_enum_identity_and_unique()

    print("\n=== 2. StrEnum, IntEnum, and JSON interoperability ===")
    strenum_intenum_and_json_interop()

    print("\n=== 3. Flag and IntFlag bitmasks ===")
    flag_and_intflag_bitmasks()


if __name__ == "__main__":
    main()
