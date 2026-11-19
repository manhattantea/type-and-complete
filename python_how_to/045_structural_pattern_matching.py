# python 045_structural_pattern_matching.py

from dataclasses import dataclass
from enum import IntEnum


@dataclass
class Point:
    x: int
    y: int


class HttpStatus(IntEnum):
    OK = 200
    CREATED = 201
    BAD_REQUEST = 400
    NOT_FOUND = 404


def literals_or_patterns_and_capture_trap() -> None:

    # Structural pattern matching (match / case, PEP 634) is NOT a C switch
    # statement. A C switch checks integer equality and falls through to the
    # next label unless you write break. Python's match inspects an object's
    # structure (literals, sequence lengths, dict keys, class types) top to
    # bottom, binds sub-values into local names, and stops at the first match
    # with zero fallthrough.
    #
    # New pattern pieces to know right away:
    # - The pipe | means OR between patterns: case 200 | 201: matches either
    #   200 or 201.
    # - The keyword 'as' binds whatever a sub-pattern matched into a variable:
    #   case (400 | 404) as err_code: matches 400 or 404 and sets err_code.
    # - The underscore _ is the wildcard pattern: it matches anything without
    #   binding a variable, acting like a fallback branch.
    #
    # Watch out for the #1 pattern-matching trap: bare name capture vs. dotted
    # value patterns! Any bare identifier in a case pattern is a CAPTURE
    # variable that matches EVERY value and overwrites that local name:
    #
    #     Suppose OK = 200 and you write:
    #         match 404:
    #             case OK:
    #                 print(OK)   # prints 404! OK was rebound, NOT compared!
    #
    # To compare against a named constant instead of capturing, the name MUST
    # contain a dot (such as HttpStatus.OK). The dot tells Python to look up
    # the attribute value and check subject == HttpStatus.OK.

    starter_code = HttpStatus.OK
    match starter_code:
        case HttpStatus.OK:
            print("Starter status matched HttpStatus.OK (200)")
        case _:
            print("Other status")

    # Prove the bare-name capture trap directly:
    # Bind OK = 200, then run match 404: with case OK: printing f"Captured OK={OK}"
    # to watch 404 overwrite OK!
    # Next, run match 404: with case HttpStatus.OK: printing "matched 200" and
    # case _: printing "did not match HttpStatus.OK" so you see the dotted lookup
    # behave as a real value comparison.


    # Define def classify_status(code: int) -> str: inside this function using
    # match code: with these branches in order:
    # - case HttpStatus.OK | HttpStatus.CREATED: returning "success"
    # - case (HttpStatus.BAD_REQUEST | HttpStatus.NOT_FOUND) as err_code:
    #   returning f"client error {err_code}"
    # - case status if 500 <= status < 600: returning f"server error {status}"
    # - case _: returning f"other ({code})"
    # Call classify_status on 200, 201, 404, 503, and 418 and print each result.


    # Practice 'as' sub-pattern bindings inside a sequence:
    # Loop over commands = [("deploy", "fast"), ("deploy", "safe"), ("deploy", "turbo")].
    # Match each item with case ["deploy", ("fast" | "safe") as mode]: printing
    # f"Deploying in {mode} mode", and case _: printing f"Rejected: {item}".


def sequences_and_partial_mappings() -> None:

    # Sequence patterns like case [cmd, *args]: match lists AND tuples
    # interchangeably (square brackets and parentheses mean the same sequence
    # pattern in match). Python deliberately excludes str, bytes, and bytearray
    # from sequence patterns so matching "quit" against case [first, *rest]:
    # does NOT accidentally split a string into single letters!
    #
    # Mapping patterns like case {"type": "cmd", "args": [first, *rest]}: do
    # PARTIAL matching on dicts: as long as the listed keys exist and their
    # values match, any extra keys in the dict are silently ignored. Adding
    # **extra captures any remaining unmatched keys into a new dict:
    #
    #     Suppose payload = {"type": "ping", "id": 7, "ts": 1234}.
    #     Matching case {"type": "ping", "id": req_id, **extra}: binds
    #     req_id = 7 and extra = {"ts": 1234} cleanly.

    starter_cmd = ["ping", "host-a"]
    match starter_cmd:
        case [action, target]:
            print(f"Starter command: action={action}, target={target}")
        case _:
            print("Unrecognized command")

    # Define def describe_route(parts: object) -> str: using match parts:
    # - case []: returning "root"
    # - case ["health"]: returning "healthcheck"
    # - case ["users", user_id]: returning f"user={user_id}"
    # - case ["files", *segments]: returning f"path={'/'.join(segments)}"
    # - case _: returning "not a route"
    # Test it on [], ("health",), ["users", 42], ["files", "docs", "spec.md"],
    # and the plain string "health" (confirming str does NOT match a sequence!).


    # Practice partial dict matching and **extra:
    # Bind msg = {"type": "cmd", "args": ["build", "--release"], "user": "ada", "retries": 2}.
    # Match msg against case {"type": "cmd", "args": [first, *rest], **extra}:
    # and print first, rest, and extra.


    # Combine mapping and sequence shapes across a batch of dicts:
    # Loop over packets = [{"kind": "batch", "items": [10, 20]}, {"kind": "batch", "items": []}, {"kind": "ping", "ms": 4}].
    # Match non-empty batches with case {"kind": "batch", "items": [head, *tail]}:,
    # empty batches with case {"kind": "batch", "items": []}:, and everything else
    # with case {"kind": kind}:, printing a short summary for each packet.


def class_patterns_types_and_guards() -> None:

    # Class patterns inspect an object's type and attributes at the same time.
    # Because Point is a @dataclass, Python automatically creates a
    # __match_args__ = ("x", "y") tuple on Point, letting you match either by
    # keyword (case Point(x=0, y=y):) or positionally (case Point(0, y):).
    #
    # Built-in type patterns like case ("move", int(dx), int(dy)): check
    # isinstance(val, int) and bind dx and dy—they do NOT call int("4") to
    # convert strings into integers!
    #
    # An 'if' guard attaches an extra boolean condition after a pattern:
    #
    #     Suppose p = Point(3, 3) and you match:
    #         case Point(x=x, y=y) if x == y:
    #             return f"diagonal({x})"
    #     Python first checks isinstance(p, Point) and binds x=3, y=3, then
    #     evaluates x == y. If the guard were False (e.g. Point(3, 5)),
    #     Python would skip this branch and keep testing lower cases.

    starter_pt = Point(0, 5)
    match starter_pt:
        case Point(x=0, y=y):
            print(f"Starter point lies on the y-axis at y={y}")
        case _:
            print("Starter point is off the y-axis")

    # Define def handle_event(event: object) -> str: using match event: with
    # these five cases in order:
    # - case Point(x=0, y=0): returning "origin"
    # - case Point(x=x, y=y) if x == y: returning f"diagonal({x})"
    # - case {"type": "cmd", "args": [first, *rest]}: returning f"cmd={first}, rest={rest}"
    # - case ("move", int(dx), int(dy)): returning f"delta=({dx}, {dy})"
    # - case _: returning "unknown"


    # Call handle_event(...) on all seven inputs below and print every result:
    # Point(0, 0), Point(3, 3), Point(3, 4),
    # {"type": "cmd", "args": ["build", "--release"], "source": "cli"},
    # ("move", 12, -5), ("move", "12", -5), and "unexpected".
    # Notice two key proofs: the extra "source" key in the dict is ignored, and
    # ("move", "12", -5) falls through to "unknown" because int(dx) checks
    # isinstance without converting strings!


    # Practice positional class matching with guards and OR patterns:
    # Loop over points = [Point(2, 4), Point(0, 9), Point(-3, 0), Point(-1, -2)].
    # Match each point with:
    # - case Point(x, y) if x > 0 and y > 0: printing "quadrant 1"
    # - case Point(0, _) | Point(_, 0): printing "on axis"
    # - case _: printing "other quadrant"
    #
    # Try uncommenting below to see SyntaxError (name capture makes later cases unreachable):
    # match 10:
    #     case x:
    #         print(x)
    #     case 10:
    #         print("never reached")


def main() -> None:

    print("=== 1. Literals, OR patterns, and the capture trap ===")
    literals_or_patterns_and_capture_trap()

    print("\n=== 2. Sequences and partial mappings ===")
    sequences_and_partial_mappings()

    print("\n=== 3. Class patterns, type checks, and guards ===")
    class_patterns_types_and_guards()


if __name__ == "__main__":
    main()
