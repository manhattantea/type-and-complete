# python 070_raising_chaining_and_exception_groups.py


class ConfigError(Exception):
    def __init__(self, message: str, key: str = "") -> None:

        super().__init__(message)
        self.key = key


def custom_exceptions_and_bare_reraise() -> None:

    # Raising a custom Exception subclass (such as ConfigError above) gives
    # callers a clean, domain-specific type to catch without accidentally
    # swallowing unrelated bugs that raise ValueError or KeyError. Inheriting
    # from Exception—never BaseException—keeps Ctrl+C and sys.exit() intact.
    #
    # When you catch an exception only to log or clean up before letting it
    # keep traveling upward, use a bare 'raise' with no argument:
    #
    #     Suppose parse_positive("-3") raises ValueError:
    #         except ValueError:
    #             print("Logged bad input")
    #             raise   # re-raises active exception with original traceback!
    #
    # Calling bare 'raise' preserves the exact original stack frame where the
    # failure started.

    try:
        raise ConfigError("missing required key", key="host")
    except ConfigError as err:
        print(f"Starter custom error: {err} (key={err.key!r})")

    # Define a custom exception class ValidationError(Exception): inside this
    # function with def __init__(self, field: str, reason: str) -> None: that
    # calls super().__init__(f"{field}: {reason}") and stores self.field and
    # self.reason. Raise ValidationError("port", "must be positive"), catch it,
    # and print err, err.field, and err.reason.


    # Practice bare 'raise' to log and re-raise untouched:
    # Define def parse_positive(raw: str) -> int: that converts n = int(raw),
    # raises ValueError("must be > 0") if n <= 0, and wraps the logic in
    # try / except ValueError: printing "logging parse failure" followed by
    # bare raise. Call parse_positive("-5") inside an outer
    # try / except ValueError as err: to verify the original error arrives intact.


def exception_chaining_from_err_and_from_none() -> None:

    # When your except: block translates a low-level failure (KeyError,
    # ValueError) into a higher-level domain error (ConfigError), Python gives
    # you three exact ways to control the causal chain attached to the object:
    # - Implicit chaining (raise ConfigError("...") with no 'from'): Python
    #   sets __context__ = err and prints "During handling of the above
    #   exception, another exception occurred", signaling an accidental crash.
    # - Explicit chaining (raise ConfigError("...") from err): Python sets
    #   __cause__ = err and prints "The above exception was the direct cause of
    #   the following exception", marking an intentional translation.
    # - Suppressed chaining (raise ConfigError("...") from None): Python sets
    #   __cause__ = None and __suppress_context__ = True, hiding internal
    #   traceback noise from public API callers (note __context__ still stays
    #   accessible on the object for debuggers!).
    #
    #     Suppose cfg = {"port": "abc"} and load_port raises ConfigError(...) from err.
    #     Callers catching ConfigError see err.__cause__ is the exact ValueError!

    try:
        try:
            int("bad")
        except ValueError:
            raise ConfigError("implicit chain starter", key="port")
    except ConfigError as err:
        print(
            "Starter implicit chain:",
            err.__cause__,
            repr(err.__context__),
            err.__suppress_context__,
        )

    # Define def load_port(cfg: dict[str, str]) -> int: wrapping
    # return int(cfg["port"]) in try:, catching except (KeyError, ValueError) as err:,
    # and raising ConfigError("Invalid port configuration", key="port") from err.
    # Call load_port({"port": "not-a-number"}) and load_port({}) inside
    # try / except ConfigError as err:, printing err, repr(err.__cause__), and
    # err.__suppress_context__.


    # Define def load_port_clean(cfg: dict[str, str]) -> int: using
    # raise ConfigError("Port must be a valid integer", key="port") from None.
    # Catch ConfigError as err on load_port_clean({"port": "oops"}) and print
    # err.__cause__ is None, err.__suppress_context__, and repr(err.__context__).


    # Compare explicit vs. implicit chaining directly:
    # Inside an except KeyError: block, raise ConfigError("missing key") with
    # NO 'from' clause, catch it, and verify err.__cause__ is None while
    # isinstance(err.__context__, KeyError) is True and err.__suppress_context__
    # is False.


def enriching_errors_with_add_note() -> None:

    # Starting in Python 3.11, every exception has an .add_note(text) method
    # that appends extra diagnostic strings into err.__notes__ without wrapping
    # or changing the exception's type! That solves a common headache: callers
    # who expect ValueError still catch ValueError, while engineers reading the
    # traceback see the exact record number, file, or job ID that failed:
    #
    #     Suppose parsing row #42 fails with ValueError("invalid literal..."):
    #         except ValueError as err:
    #             err.add_note("while processing record #42")
    #             raise
    #     Now err.__notes__ holds ["while processing record #42"].

    try:
        try:
            raise ValueError("starter bad field")
        except ValueError as err:
            err.add_note("starter context: field=age")
            raise
    except ValueError as caught:
        print("Starter notes:", caught.__notes__)

    # Loop over rows = ["10", "20", "bad", "40"] with
    # for row_num, text in enumerate(rows, start=1):
    # Wrap int(text) in try / except ValueError as err:, call
    # err.add_note(f"while processing record #{row_num} ({text!r})"), and re-raise
    # with bare raise. Catch ValueError outside the loop and print err and
    # err.__notes__.


    # Accumulate multiple notes across two nested try layers:
    # Have an inner try / except ValueError as err: attach
    # err.add_note("stage=parse_amount") and bare raise, then an outer
    # try / except ValueError as err: attach err.add_note("job_id=99") and print
    # err.__notes__ to confirm both notes stay preserved in order.


def exception_groups_and_except_star() -> None:

    # Sometimes a single operation produces multiple independent failures at
    # once—for example, batch validation or concurrent tasks inside
    # asyncio.TaskGroup. ExceptionGroup(message, [err1, err2, ...]) bundles
    # several exceptions together, and except* (PEP 654, Python 3.11+) handles
    # them selectively:
    # - Unlike regular except: (which runs at most ONE branch), multiple
    #   except* clauses on the same try: can ALL execute as each clause peels
    #   off its matching subset into a smaller ExceptionGroup.
    # - Any sub-exceptions not matched by any except* clause automatically keep
    #   propagating upward as a smaller ExceptionGroup!
    # - You cannot mix regular except: and except*: on the same try: block.
    #
    #     Suppose try: raises ExceptionGroup("batch", [ValueError("a"), TypeError("b")]).
    #     except* ValueError as vg: handles ValueError("a"), AND
    #     except* TypeError as tg: handles TypeError("b") in the same run!

    starter_eg = ExceptionGroup("starter batch", [ValueError("bad value")])
    print("Starter group:", starter_eg.message, starter_eg.exceptions)

    # Construct:
    # eg = ExceptionGroup("batch failed", [ValueError("bad int"), TypeError("bad type"), ValueError("negative")])
    # Raise eg inside try: and handle it with both:
    # except* ValueError as vg: printing "ValueErrors:", vg.exceptions
    # except* TypeError as tg: printing "TypeErrors:", tg.exceptions
    # Verify that BOTH except* blocks execute for the same raise!


    # Prove that unhandled sub-exceptions keep propagating automatically:
    # Wrap an inner try: raising
    # ExceptionGroup("mixed", [ValueError("v1"), KeyError("k1")])
    # with ONLY except* ValueError as vg: (printing vg.exceptions).
    # Catch the leftover KeyError in an outer except* KeyError as kg: and print
    # "Unhandled remainder caught:", kg.exceptions.


    # Inspect programmatic filtering with .split():
    # Create batch = ExceptionGroup("all", [ValueError("v1"), KeyError("k1"), ValueError("v2")]),
    # call matched, rest = batch.split(ValueError), and print matched.exceptions
    # and rest.exceptions.


def main() -> None:

    print("=== 1. Custom exceptions and bare re-raise ===")
    custom_exceptions_and_bare_reraise()

    print("\n=== 2. Exception chaining: from err vs. from None ===")
    exception_chaining_from_err_and_from_none()

    print("\n=== 3. Enriching errors with .add_note() ===")
    enriching_errors_with_add_note()

    print("\n=== 4. ExceptionGroup and except* ===")
    exception_groups_and_except_star()


if __name__ == "__main__":
    main()
