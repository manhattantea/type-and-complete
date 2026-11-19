# python 110_positional_keyword_and_default_args.py

MISSING = object()


def positional_keyword_and_default_storage() -> None:

    # Python lets callers pass arguments either positionally (matched by slot
    # index) or by keyword (matched by parameter name), as long as all
    # positional arguments come before any keyword arguments.
    #
    # The crucial runtime rule behind default arguments is WHEN Python evaluates
    # them: default expressions are evaluated ONCE when the def statement runs
    # (typically at module import time), NOT each time the function is called.
    # Python attaches those pre-evaluated objects directly onto the function
    # object in two attributes:
    # - fn.__defaults__: a tuple holding defaults for positional-or-keyword
    #   parameters (aligned to the rightmost parameters).
    # - fn.__kwdefaults__: a dict holding defaults for keyword-only parameters
    #   (or None if there are none).
    #
    #     Suppose def connect(host: str, port: int = 8080, *, tls: bool = False):
    #     connect.__defaults__ is (8080,) and connect.__kwdefaults__ is {'tls': False}.

    def format_host(host: str, port: int = 8080) -> str:

        return f"{host}:{port}"

    print(f"Starter: {format_host('127.0.0.1')} | __defaults__={format_host.__defaults__}")

    # Define connect(host: str, *, port: int = 8080, tls: bool = False) -> str
    # returning f"{host}:{port} (tls={tls})".
    # Call connect("127.0.0.1") and connect("127.0.0.1", port=9000, tls=True),
    # then print connect.__defaults__ (None) alongside connect.__kwdefaults__
    # ({'port': 8080, 'tls': False}).


    # Prove default expressions run ONCE at def time rather than per call:
    # Create eval_count = [0] and a helper def next_token() -> int: that
    # increments eval_count[0] by 1 and returns eval_count[0].
    # Define def make_ticket(user: str, token: int = next_token()) -> tuple[str, int]:
    # returning (user, token).
    # Call make_ticket("ada") and make_ticket("grace") and print both results
    # alongside eval_count[0]—both calls get token 1 because next_token() ran
    # only once when def executed!


    # Python enforces parameter ordering at compile time: every non-default
    # positional parameter must come before parameters with defaults.
    # Try uncommenting below to trigger SyntaxError:
    # def invalid_param_order(a: int = 1, b: int) -> int:
    #     return a + b


def mutable_default_list_and_dict_traps() -> None:

    # Because default values are evaluated once and stored inside fn.__defaults__,
    # using a mutable literal like [] or {} as a default value creates Python's
    # most infamous state-leak bug.
    #
    # Whenever a caller omits that argument, Python binds the parameter directly
    # to the single shared list or dict living inside fn.__defaults__. Mutating
    # that parameter inside the function permanently mutates the default for
    # every future call across the entire program!
    #
    #     Suppose def buggy_append(item: str, bucket: list[str] = []) -> list[str]:
    #         bucket.append(item)
    #         return bucket
    #     First call:  buggy_append("a") returns ["a"], __defaults__ is (["a"],).
    #     Second call: buggy_append("b") returns ["a", "b"], __defaults__ is (["a", "b"],)!
    #
    # The exact same trap hits dict defaults (cache: dict[str, int] = {}) and
    # set defaults (seen: set[str] = set()).

    fresh_a: list[str] = []
    fresh_b: list[str] = []
    print(f"Two separate [] literals share identity? {fresh_a is fresh_b}")

    # Reproduce the mutable [] default list trap and inspect __defaults__:
    # Define buggy_append(item: str, bucket: list[str] = []) -> list[str]
    # calling bucket.append(item) and returning bucket.
    # Call first = buggy_append("a") and print first plus buggy_append.__defaults__.
    # Call second = buggy_append("b") and print second, first is second (True!),
    # and buggy_append.__defaults__ (now (['a', 'b'],)).


    # Reproduce the mutable {} default dict trap alongside []:
    # Define buggy_cache(key: str, val: int, store: dict[str, int] = {}) -> dict[str, int]
    # that sets store[key] = val and returns store.
    # Call c1 = buggy_cache("hits", 1) and c2 = buggy_cache("misses", 2).
    # Print c1, c2, c1 is c2 (True—both variables point to the same dict!), and
    # buggy_cache.__defaults__ (now ({'hits': 1, 'misses': 2},)).


    # Observe what happens when one call passes an explicit dict and a later
    # call omits it again:
    # Call isolated = buggy_cache("local", 99, {}) and verify isolated is not c1.
    # Then call c3 = buggy_cache("timeouts", 3) with no third argument and print
    # c3 to confirm the polluted default dict inside __defaults__ is still alive.


def none_and_custom_object_sentinels() -> None:

    # To give each omitted call a fresh container, use the immutable singleton
    # None as the default and allocate inside the function body:
    #
    #     def safe_append(item: str, bucket: list[str] | None = None) -> list[str]:
    #         if bucket is None:
    #             bucket = []
    #         bucket.append(item)
    #         return bucket
    #
    # Always test with "is None" instead of "if not bucket:"! If a caller passes
    # an existing empty list caller_list = [] expecting safe_append to fill it,
    # "if not bucket:" treats [] as falsy, discards caller_list, and allocates a
    # brand-new list instead of mutating caller_list.
    #
    # What if None itself is a meaningful explicit value (for example, "clear
    # this config option to None" versus "the caller did not pass this option")?
    # Create a unique module-level sentinel object: MISSING = object(). Because
    # every object() instance has a distinct identity, checking val is MISSING
    # cleanly separates omitted arguments from explicit None, 0, "", or False.

    print(f"Module sentinel ready: MISSING is None -> {MISSING is None}")

    # Write safe_append(item: str, bucket: list[str] | None = None) -> list[str]
    # allocating bucket = [] when bucket is None, appending item, and returning
    # bucket.
    # Call a = safe_append("a") and b = safe_append("b"); verify a == ["a"],
    # b == ["b"], and a is not b.
    # Then prove why "is None" beats "if not bucket:": create
    # caller_list: list[str] = [], call safe_append("x", caller_list), and print
    # caller_list (must be ["x"], mutated in place!).


    # Write safe_cache(key: str, val: int, store: dict[str, int] | None = None) -> dict[str, int]
    # allocating store = {} when store is None, setting store[key] = val, and
    # returning store.
    # Verify two omitted calls return independent dicts (d1 is not d2), AND pass
    # an explicit empty caller_dict: dict[str, int] = {} to confirm it gets
    # populated in place.


    # Write update_setting(val: int | None | object = MISSING) -> str using
    # identity checks (is):
    # - val is MISSING -> return "omitted (keep existing setting)"
    # - val is None    -> return "cleared (explicit None)"
    # - anything else  -> return f"updated to {val!r}"
    # Call and print update_setting(), update_setting(None), update_setting(0),
    # and update_setting(42) to confirm 0 is not confused with None or MISSING.


def main() -> None:

    print("=== 1. Positional, keyword, and __defaults__ storage ===")
    positional_keyword_and_default_storage()

    print("\n=== 2. Mutable [] and {} default argument traps ===")
    mutable_default_list_and_dict_traps()

    print("\n=== 3. None and custom object() sentinels ===")
    none_and_custom_object_sentinels()


if __name__ == "__main__":
    main()
