# python 060_unpacking_and_starred_expressions.py


def exact_unpacking_and_swaps() -> None:

    # Python's unpacking syntax works on ANY iterable—tuples, lists, strings,
    # bytes, sets, dict views, and generators—not just tuples. When you write
    # a, b, c = iterable, Python pulls items from iter(iterable) one by one and
    # binds them left to right. If the iterable has fewer or more items than
    # targets, Python raises ValueError immediately rather than silently
    # padding with None or dropping extras.
    #
    # That exact rule also powers idiomatic variable swaps:
    #
    #     Suppose left = 10 and right = 20.
    #     Executing left, right = right, left builds the right-hand tuple
    #     (20, 10) completely BEFORE rebinding left = 20 and right = 10, so no
    #     temporary variable is ever needed.

    left, right = 10, 20
    left, right = right, left
    print(f"Starter swap: left={left}, right={right}")

    # Unpack three different iterable types into a, b, c and print each triple:
    # a tuple (1, 2, 3), a string "XYZ", and a generator (n * 10 for n in range(1, 4)).


    # Rotate three variables p, q, r = 1, 2, 3 in one line with p, q, r = q, r, p
    # and print them. Then practice single-item unpacking with [only] = [42]
    # (notice the brackets assert that the list has length 1—it would raise
    # ValueError if the list held 0 or 2 elements!).
    p, q, r = 1, 2, 3
    

    # Try uncommenting either line below to see ValueError on length mismatch:
    # x, y = [1, 2, 3]
    # x, y, z = [1, 2]


def starred_targets_and_throwaways() -> None:

    # When you care about the start or end of a sequence of unknown length,
    # place a single starred target (*rest) on the left-hand side of =. Python
    # binds the fixed targets first and gathers every leftover item into the
    # starred target.
    #
    # Two rules to remember:
    # - At most ONE starred target is allowed per unpacking level.
    # - A starred target ALWAYS produces a Python list—even if the input was a
    #   tuple, bytes, string, or generator, and even if zero items remain ([]):
    #
    #     Suppose pair = (10, 20) and you write first, *mid, last = pair.
    #     Python sets first = 10, mid = [], and last = 20.
    #
    # By convention, use _ to throw away a single unwanted value and *_ to
    # discard zero or more unwanted values.

    head, *tail = (1, 2, 3)
    print(f"Starter star unpack: head={head}, tail={tail} ({type(tail).__name__})")

    # Unpack raw binary packet = b"\xAA\x10\x20\x30\xFF" using
    # header, *payload, checksum = packet
    # Print header, payload, type(payload).__name__ (notice list of ints!),
    # and checksum.


    # Test the empty-middle edge case on two_bytes = b"\xAA\xFF":
    # unpack hdr, *empty_payload, chk = two_bytes and print all three variables
    # to confirm empty_payload is [].


    # Use throwaway targets to grab only the edges:
    # - Unpack first, *_, last = range(10) and print first and last.
    # - Given log_fields = ["2026-01-01", "INFO", "auth", "user=42", "ok"],
    #   unpack *_, user_field, status = log_fields and print user_field, status.


def nested_unpacking_in_assignments_and_loops() -> None:

    # Unpacking targets can mirror nested structure directly by wrapping inner
    # groups in parentheses or square brackets. This works identically in plain
    # assignments and in 'for' loop headers, replacing brittle chained indexing
    # like record[1][0] with self-documenting names:
    #
    #     Suppose record = ("NYC", (40.71, -74.00)).
    #     Writing city, (lat, lon) = record unpacks the outer 2-tuple and the
    #     inner 2-tuple in one step: city="NYC", lat=40.71, lon=-74.00.

    who, (x_pos, y_pos) = ("Alice", (10, 20))
    print(f"Starter nested unpack: {who} at ({x_pos}, {y_pos})")

    # Given records = [("NYC", (40.71, -74.00)), ("LON", (51.50, -0.12)), ("TYO", (35.68, 139.69))],
    # loop using nested unpacking directly in the header:
    # for city, (lat, lon) in records:
    # and print each city with its latitude and longitude.


    # Combine nested unpacking with a starred target inside a loop:
    # Bind rows = [("web", [200, 200, 500]), ("db", [200, 200])].
    # Loop with for service, [first_code, *other_codes] in rows: and print
    # service, first_code, and other_codes.


    # Nest enumerate() with tuple unpacking and a throwaway:
    # Loop over records using for idx, (city, (lat, _)) in enumerate(records, start=1):
    # printing only idx, city, and lat while ignoring longitude.


def literal_splatting_and_call_unpacking() -> None:

    # Putting * inside a list, tuple, or set literal splats (expands) an
    # iterable's items inline into the new collection. Putting ** inside a dict
    # literal splats a mapping's key-value pairs into the new dict, with later
    # keys overwriting earlier keys:
    #
    #     Suppose base = {"a": 1, "b": 2} and over = {"b": 9, "c": 3}.
    #     {**base, **over} allocates a new dict {"a": 1, "b": 9, "c": 3} and
    #     leaves both base and over untouched (equivalent to base | over).
    #
    # Inside function calls, *seq unpacks positional arguments and **mapping
    # unpacks keyword arguments into the callee's parameters.

    starter_merged = [*[1, 2], 0, *[3, 4]]
    print("Starter list splat:", starter_merged)

    # Given part_a = [1, 2] and part_b = [3, 4], build
    # combined = [*part_a, 0, *part_b]
    # and a tuple as_tuple = (*part_a, *part_b). Print both and verify part_a
    # is still [1, 2].


    # Merge base_cfg = {"host": "localhost", "port": 8080} and
    # env_cfg = {"port": 9000, "debug": True} using merged = {**base_cfg, **env_cfg}.
    # Print merged, verify merged == (base_cfg | env_cfg), and confirm
    # base_cfg["port"] is still 8080.


    # Practice call unpacking with * and **:
    # Define def format_endpoint(host: str, port: int, tls: bool = False) -> str:
    # returning f"{'https' if tls else 'http'}://{host}:{port}".
    # Call it once with positional splatting format_endpoint(*["db.local", 5432])
    # and once with keyword splatting
    # format_endpoint(**{"host": "api.local", "port": 443, "tls": True}),
    # printing both URLs.


def main() -> None:

    print("=== 1. Exact unpacking and swaps ===")
    exact_unpacking_and_swaps()

    print("\n=== 2. Starred targets and throwaways ===")
    starred_targets_and_throwaways()

    print("\n=== 3. Nested unpacking in assignments and loops ===")
    nested_unpacking_in_assignments_and_loops()

    print("\n=== 4. Literal splatting and call unpacking ===")
    literal_splatting_and_call_unpacking()


if __name__ == "__main__":
    main()
