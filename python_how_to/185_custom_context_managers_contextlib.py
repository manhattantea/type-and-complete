# python 185_custom_context_managers_contextlib.py

from collections.abc import Iterator
from contextlib import ExitStack, contextmanager
import time
from types import TracebackType
from typing import Any


def class_protocol_enter_and_exit() -> None:

    # Python's with statement guarantees deterministic teardown the moment a
    # block exits—whether normally, via return, or via an exception—without
    # waiting for garbage collection. Any class becomes a context manager by
    # implementing two dunder methods:
    # - __enter__(self) -> T runs on entering with; its return value is bound
    #   to the "as target" variable (returning self is the standard idiom).
    # - __exit__(self, exc_type, exc_val, exc_tb) -> bool | None ALWAYS runs
    #   when leaving with. If no exception occurred, all three exception args
    #   are None. If an exception DID occur inside the block, returning True
    #   SUPPRESSES that exception; returning False or None lets it propagate
    #   normally (almost always what you want unless writing an explicit
    #   suppressor).
    #
    #     Suppose with StopwatchTimer("work") as timer: runs a slow loop.
    #     __enter__ records time.perf_counter_ns() (a monotonic nanosecond clock
    #     that never jumps backward) and returns self; __exit__ computes elapsed
    #     milliseconds and returns False so any error inside the block still
    #     surfaces.

    start_ns = time.perf_counter_ns()
    sample_total = sum(range(1_000))
    elapsed_ms = (time.perf_counter_ns() - start_ns) / 1_000_000
    print(f"Starter perf_counter_ns sample: total={sample_total}, {elapsed_ms:.4f} ms")

    # Implement a class-based context manager:
    # Define class StopwatchTimer: with:
    # - __init__(self, label: str = "task") -> None storing self.label = label,
    #   self.start_ns: int = 0, and self.elapsed_ms: float = 0.0.
    # - __enter__(self) -> "StopwatchTimer" setting
    #   self.start_ns = time.perf_counter_ns() and returning self.
    # - __exit__(self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: TracebackType | None) -> bool
    #   computing self.elapsed_ms = (time.perf_counter_ns() - self.start_ns) / 1_000_000,
    #   printing f"[{self.label}] elapsed: {self.elapsed_ms:.3f} ms", and
    #   returning False.
    # Wrap total = sum(range(100_000)) inside with StopwatchTimer("sum") as timer:
    # and print total and timer.elapsed_ms.


    # Verify __exit__ runs AND propagates exceptions when returning False:
    # Wrap with StopwatchTimer("failing"): raise RuntimeError("boom") inside
    # try / except RuntimeError as exc: and confirm both the elapsed timing
    # line AND "boom" appear.


    # Contrast with deliberate exception suppression (__exit__ returning True):
    # Define class SuppressKeyError: whose __enter__(self) -> None returns None
    # and whose __exit__(...) -> bool returns
    # exc_type is not None and issubclass(exc_type, KeyError).
    # Test reading {}["missing"] inside with SuppressKeyError(): (silently
    # suppressed!) vs raising ValueError("must propagate") inside
    # try / except ValueError: (still propagates because __exit__ returns False).


def contextmanager_generator_and_finally_trap() -> None:

    # Writing a full class for a tiny setup/teardown pair can feel verbose.
    # @contextlib.contextmanager turns a single-yield generator function into a
    # context manager automatically:
    # - Everything BEFORE yield runs in __enter__.
    # - The yielded value is bound to "as target".
    # - Everything AFTER yield runs in __exit__.
    #
    # Critical @contextmanager trap: if an exception occurs inside the with
    # body, contextlib re-raises that exception directly AT THE yield LINE!
    #
    #     Broken (leaks state on error):
    #         cfg[key] = temp_val
    #         yield cfg
    #         cfg[key] = old_val    # SKIPPED if the with body raises!
    #
    #     Safe (always restores):
    #         cfg[key] = temp_val
    #         try:
    #             yield cfg
    #         finally:
    #             cfg[key] = old_val

    @contextmanager
    def starter_section(name: str) -> Iterator[str]:

        print(f"-> enter {name}")
        try:
            yield name
        finally:
            print(f"<- exit {name}")

    with starter_section("demo") as active_name:
        print(f"   running inside {active_name}")

    # Write a @contextmanager helper with mandatory try ... finally: cleanup:
    # Define @contextmanager def temp_config_override(cfg: dict[str, Any], key: str, temp_val: Any) -> Iterator[dict[str, Any]]:
    # Save had_key = key in cfg and old_val = cfg.get(key), set cfg[key] = temp_val,
    # and wrap yield cfg inside try: yield cfg finally: so finally restores
    # cfg[key] = old_val when had_key is True, or removes key with
    # cfg.pop(key, None) when had_key was False.


    # Test temp_config_override on BOTH normal exit AND exception exit:
    # Create cfg: dict[str, Any] = {"mode": "prod", "retries": 3}.
    # Enter with temp_config_override(cfg, "mode", "debug") as active: and
    # print active["mode"] ("debug"), then print cfg["mode"] after exit ("prod").
    # Next wrap with temp_config_override(cfg, "trace", True): raise RuntimeError("boom")
    # inside try / except RuntimeError: and assert "trace" not in cfg afterward!


    # Observe the single-yield contract of @contextmanager:
    # Define a tiny @contextmanager def bad_double_yield() -> Iterator[int]:
    # that yields 1 and then yields 2. Enter it inside try / except RuntimeError as exc:
    # and print exc to see contextlib reject multi-yield generators.


def dynamic_cleanup_with_exitstack() -> None:

    # Sometimes you do not know how many context managers you need until
    # runtime (opening N files in a loop, or registering cleanup callbacks
    # conditionally mid-function). contextlib.ExitStack acts like a dynamic
    # stack of with blocks—very similar to Odin's or Go's defer statement:
    # - stack.enter_context(cm) enters cm immediately and schedules cm.__exit__
    #   when the ExitStack leaves its with block.
    # - stack.callback(fn, *args, **kwargs) schedules any plain callable to run
    #   on exit.
    #
    # All registered context managers and callbacks unwind in strict LIFO
    # (last-in, first-out / reverse) order, even when an exception occurs!

    with ExitStack() as starter_stack:
        starter_stack.callback(print, "Starter ExitStack teardown callback fired")
        print("Starter ExitStack body running")

    # Verify strict LIFO defer-style callback ordering:
    # Open with ExitStack() as stack:, register three callbacks:
    # stack.callback(print, "cleanup #1")
    # stack.callback(print, "cleanup #2")
    # stack.callback(print, "cleanup #3")
    # Print "inside ExitStack body" and observe #3, #2, #1 running in reverse!


    # Enter a dynamic number of context managers in a loop:
    # Using a local temp_override (or temp_config_override), start with
    # cfg: dict[str, Any] = {"a": 1, "b": 2} and
    # overrides = [("a", 10), ("b", 20), ("c", 30)].
    # Inside with ExitStack() as stack:, loop over key, val in overrides and
    # call stack.enter_context(...) for each pair. Print cfg inside the block
    # ({"a": 10, "b": 20, "c": 30}) and after exit ({"a": 1, "b": 2}).


    # Prove ExitStack still unwinds registered callbacks when an exception fires:
    # Wrap a with ExitStack() as stack: block inside try / except RuntimeError:,
    # register two cleanup callbacks, raise RuntimeError("abort"), and verify
    # both callbacks still execute in reverse order before the error is caught.


def main() -> None:

    print("=== 1. Class protocol: __enter__ and __exit__ ===")
    class_protocol_enter_and_exit()

    print("\n=== 2. @contextlib.contextmanager and the finally trap ===")
    contextmanager_generator_and_finally_trap()

    print("\n=== 3. Dynamic LIFO cleanup with contextlib.ExitStack ===")
    dynamic_cleanup_with_exitstack()


if __name__ == "__main__":
    main()
