# python 180_generators_and_yield.py

from collections.abc import Generator, Iterator
from itertools import islice
import sys
from typing import Any


def lazy_yield_streaming_pipeline_and_memory() -> None:

    # Any function containing yield anywhere in its body compiles differently
    # from an ordinary function—it becomes a generator factory. Calling
    # gen = chunked_range(0, 10, 2) does NOT run a single line of the body yet
    # (not even argument validation before the first yield!). Instead, Python
    # allocates a generator iterator with a heap-suspended stack frame
    # (gen.gi_frame) and instruction pointer (gen.gi_lasti).
    #
    # Calling next(gen) resumes that suspended frame until it hits yield expr,
    # freezes all local variables on the heap, and returns expr. Calling
    # next(gen, default) returns default instead of raising StopIteration once
    # the generator finishes.
    #
    # Because only ONE frame lives on the heap regardless of stream length,
    # generators let you chain lazy pipelines in O(1) memory. When you only want
    # the first N items from a huge or infinite generator, itertools.islice(it, n)
    # pulls at most n items and stops immediately without building a list:
    #
    #     Suppose raw_lines yields 1_000_000 log lines lazily.
    #     errors = (line for line in raw_lines if line.startswith("ERROR:"))
    #     first_three = list(islice(errors, 3))
    #     Python stops generating lines the instant the 3rd error arrives!

    starter_gen = (n * 10 for n in range(3))
    print(f"Starter next={next(starter_gen)}, rest={list(starter_gen)}")

    # Write a basic generator factory and observe lazy validation:
    # Define chunked_range(start: int, stop: int, step: int) -> Iterator[int]
    # raising ValueError("step must be positive") if step <= 0, then yielding
    # values from start up to (excluding) stop in increments of step.
    # Create gen = chunked_range(0, 15, 3), print next(gen) (0), next(gen) (3),
    # list(gen) ([6, 9, 12]), and next(gen, -1) (-1).
    # Also create bad = chunked_range(0, 10, 0) to observe no exception happens
    # until you call next(bad) inside try / except ValueError:.


    # Build an everyday streaming log-line pipeline with itertools.islice:
    # Define fake_log_lines(total: int) -> Iterator[str] yielding
    # f"ERROR: disk full #{i}" when i % 3 == 0 else f"INFO: ok #{i}" for i in
    # range(total).
    # Chain a lazy filter:
    # error_lines = (line for line in fake_log_lines(1_000_000) if line.startswith("ERROR:"))
    # Take only the first 3 matches with top_errors = list(islice(error_lines, 3))
    # and print top_errors (notice how instant it is despite 1_000_000 total!).


    # Contrast generator expression memory against a list comprehension:
    # Bind eager_list = [x * x for x in range(100_000)] and
    # lazy_gen = (x * x for x in range(100_000)).
    # Print sys.getsizeof(eager_list) right next to sys.getsizeof(lazy_gen) to
    # see ~800 KB versus ~200 bytes for the exact same sequence of squares.


def yield_from_and_stopiteration_return_value() -> None:

    # Writing yield from sub_iterable is stronger than for x in sub: yield x.
    # It connects the outer caller directly to the inner sub-generator,
    # forwarding .send(), .throw(), and .close() automatically—and evaluating to
    # the sub-generator's return value!
    #
    # Inside a generator, return summary does NOT yield summary—it ends the
    # generator by raising StopIteration(summary), storing summary on exc.value.
    # A normal for loop catches StopIteration and discards exc.value, so you
    # retrieve a generator's return value either manually via
    # except StopIteration as exc: exc.value OR cleanly via
    # result = yield from sub_gen():
    #
    #     Suppose def batch() -> Generator[str, None, int]:
    #         yield "a"
    #         yield "b"
    #         return 2
    #     Inside an outer generator, count = yield from batch() yields "a", "b"
    #     to the outer caller and binds count = 2 when batch() finishes.

    def chain_starter() -> Iterator[int]:

        yield from [1, 2]
        yield from [3, 4]

    print(f"Starter yield from: {list(chain_starter())}")

    # Write recursive delegation with yield from:
    # Define flatten_nested(items: list[Any]) -> Iterator[int] looping over item
    # in items: if isinstance(item, list), run yield from flatten_nested(item);
    # otherwise yield item.
    # Flatten [1, [2, [3, 4], 5], [], [[6]]] with list(flatten_nested(...)) and
    # assert it equals [1, 2, 3, 4, 5, 6].


    # Inspect a generator's return value on StopIteration.value directly:
    # Define read_batch() -> Generator[str, None, int] yielding "row-1",
    # "row-2", "row-3", and ending with return 3.
    # Drive batch = read_batch() in a while True: loop calling next(batch)
    # inside try / except StopIteration as exc:, printing each row and printing
    # exc.value (expected: 3) once StopIteration fires.


    # Capture read_batch()'s return value automatically using yield from:
    # Define outer_batch() -> Iterator[str] running count = yield from read_batch()
    # and printing f"Sub-generator returned count={count}". Drain it with
    # list(outer_batch()) and verify both the yielded rows and printed count.


def single_pass_exhaustion_and_reusable_iterables() -> None:

    # Unlike a list (an iterable whose __iter__() creates a brand-new iterator
    # on every for loop), a generator IS its own iterator (iter(gen) is gen).
    # Once you consume a generator in one pass—such as total = sum(gen)—its
    # suspended frame is permanently closed (gen.gi_frame is None). A second
    # sum(gen) or for x in gen: does NOT raise an error; it silently yields zero
    # items!
    #
    # When callers need multiple lazy passes without materializing a list, wrap
    # the generator logic in a tiny class whose __iter__(self) method uses
    # yield. Every for loop or sum() call invokes __iter__() and gets a fresh
    # generator iterator.

    probe = (x for x in range(3))
    print(f"Starter generator is its own iterator? {iter(probe) is probe}")

    # Reproduce the single-pass exhaustion trap:
    # Create squares_gen = (x * x for x in range(5)).
    # Compute first_pass = sum(squares_gen) (30) and
    # second_pass = sum(squares_gen) (0—silently empty!). Print both alongside
    # squares_gen.gi_frame (None once exhausted).


    # Fix multi-pass laziness with a tiny re-iterable class:
    # Define class ReusableSquares: with __init__(self, count: int) -> None
    # storing self.count = count, and def __iter__(self) -> Iterator[int]:
    # yielding x * x for x in range(self.count).
    # Instantiate reusable = ReusableSquares(5) and verify sum(reusable) == 30
    # on BOTH the first and second passes.


def finally_cleanup_generator_exit_and_send() -> None:

    # What happens if a caller stops iterating a generator early with break,
    # calls gen.close(), or lets the generator be garbage collected? Python
    # injects a GeneratorExit exception right at the paused yield line!
    # Note that GeneratorExit inherits from BaseException (not Exception), so
    # an except Exception: handler cannot accidentally swallow teardown—and any
    # try ... finally: block wrapping your yield loop is guaranteed to run its
    # cleanup immediately on early break or .close().
    #
    # Generators also support bidirectional communication via gen.send(value):
    # - Prime a newly created generator once with next(gen) so it pauses at its
    #   first yield expression.
    # - Calling gen.send(val) resumes execution with val as the result of the
    #   suspended received = yield emitted expression.

    print(f"Starter check: issubclass(GeneratorExit, Exception) = {issubclass(GeneratorExit, Exception)}")

    # Prove try ... finally: cleanup runs on early break AND explicit .close():
    # Define managed_stream() -> Iterator[int] that prints "stream opened",
    # enters try: yielding 1, 2, 3, 4, 5, and prints "stream closed" inside
    # finally:.
    # First iterate with for item in managed_stream(): printing item and
    # breaking when item == 2—observe "stream closed" firing on early break!
    # Then bind s = managed_stream(), call print(next(s)), and call s.close()
    # to watch GeneratorExit trigger "stream closed" immediately.


    # Drive bidirectional .send() and .close() with finally: cleanup:
    # Define running_average() -> Generator[float | None, float | None, None]
    # holding total = 0.0 and count = 0 inside try: ... finally: print("average closed").
    # Loop while True:, emit avg = total / count if count else None via
    # value = yield avg, and when value is not None add value to total and
    # increment count.
    # Create avg_gen = running_average(), prime with print(next(avg_gen)) (None),
    # send 10.0 (10.0), 20.0 (15.0), and 30.0 (20.0), then call avg_gen.close().


def main() -> None:

    print("=== 1. Lazy yield, streaming pipelines, and memory ===")
    lazy_yield_streaming_pipeline_and_memory()

    print("\n=== 2. yield from and StopIteration.value ===")
    yield_from_and_stopiteration_return_value()

    print("\n=== 3. Single-pass exhaustion vs reusable iterables ===")
    single_pass_exhaustion_and_reusable_iterables()

    print("\n=== 4. finally cleanup, GeneratorExit, and .send() ===")
    finally_cleanup_generator_exit_and_send()


if __name__ == "__main__":
    main()
