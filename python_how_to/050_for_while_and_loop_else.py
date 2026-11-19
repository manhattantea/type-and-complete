# python 050_for_while_and_loop_else.py


def for_loops_and_lazy_ranges() -> None:

    # Python has no C-style for (i = 0; i < n; i += 1) loop. Every Python 'for'
    # loop walks an iterable using the iterator protocol: Python calls
    # it = iter(items) once when the loop starts, then calls next(it) on each
    # pass until StopIteration ends the loop.
    #
    # When you need a sequence of integers, range(stop) or
    # range(start, stop, step) generates numbers lazily on demand. Notice 'stop'
    # is always excluded, and range() does NOT build a giant list in memory:
    #
    #     Suppose r = range(2, 8, 2).
    #     It holds only start=2, stop=8, step=2 in memory, yields 2, 4, 6 when
    #     looped over, and answers 6 in r using instant math rather than
    #     scanning element by element.

    for step in range(3):
        print(step, end=" ")
    print()

    # Walk backward with range(10, 0, -2) (notice 0 is excluded!), collect each
    # yielded value into countdown: list[int] = [], and print countdown
    # (expected: [10, 8, 6, 4, 2]).


    # Prove range() stays tiny in memory: import sys inside this function
    # (import sys), create big = range(0, 10_000_000, 5), and print len(big),
    # big[-1], 5_000_000 in big, and sys.getsizeof(big).


    # Practice iterating collections directly without range(len(...)):
    # - Loop over every character in word = "Odin" and print each character.
    # - Loop over scores = {"alice": 10, "bob": 20} using for name, pts in scores.items():
    #   and print each pair.
    # - Loop over tags = {"fast", "safe"} and note why set order is arbitrary.


def while_sentinels_and_continue_traps() -> None:

    # A 'while cond:' loop repeats as long as cond evaluates to true. Python has
    # no do-while keyword; instead, writing 'while True:' with an explicit
    # 'break' check inside is Python's standard way to guarantee the body runs
    # at least once before stopping.
    #
    # Inside any loop, 'break' exits the loop immediately, while 'continue' skips
    # the rest of the current pass and jumps back to the loop header. Watch out
    # for a classic infinite-loop trap when combining 'while' and 'continue':
    #
    #     Suppose you write:
    #         n = 0
    #         while n < 4:
    #             if n == 2:
    #                 continue   # BUG: jumps past n += 1, so n stays 2 forever!
    #             n += 1
    #
    # Because 'while' has no automatic step clause, skipping past n += 1 hangs
    # forever unless you increment before 'continue' (or use a 'for' loop).
    #
    # For reading until a sentinel value (such as "QUIT"), Python has two clean
    # patterns:
    # - The walrus operator (:=): writing while (cmd := read_cmd()) != "QUIT":
    #   assigns the returned value to cmd AND compares it in one expression so
    #   you do not repeat read_cmd() before the loop and at the bottom.
    # - Two-argument iter(callable, sentinel): calling iter(read_cmd, "QUIT")
    #   wraps a zero-argument callable into an iterator that calls read_cmd()
    #   each pass and stops automatically the moment it returns "QUIT".

    fuel = 2
    while fuel > 0:
        print("Burn fuel:", fuel)
        fuel -= 1

    # Drain queue = ["job-1", "job-2", "job-3"] using a while True: loop.
    # Check if not queue: break at the top, remove from the front with
    # queue.pop(0), and print each processed job.


    # Practice the safe while + continue pattern: set idx = 0 and loop while
    # idx < 6. Increment idx += 1 BEFORE checking whether the current value is 3
    # so continue skips printing 3 without causing an infinite loop (expected
    # output: 0, 1, 2, 4, 5).


    # Practice both sentinel patterns cleanly:
    # Declare stream = iter(["PING", "STATUS", "QUIT", "IGNORED"]) and define
    # a tiny helper def next_cmd() -> str: return next(stream)
    # Use a walrus loop: while (cmd := next_cmd()) != "QUIT": to print each
    # active command.
    # Then create fresh_stream = iter(["LOAD", "RUN", "QUIT", "EXTRA"]), define
    # def read_next() -> str: return next(fresh_stream), and drain it using
    # for cmd in iter(read_next, "QUIT"): to print each command.


def loop_else_and_nested_early_returns() -> None:

    # One of Python's most misunderstood features is 'for ... else:' and
    # 'while ... else:'. Read 'else:' on a loop as 'nobreak:': Python runs the
    # else block ONLY if the loop finished normally without ever hitting 'break'
    # (including when the iterable was empty from the start!).
    #
    #     Suppose nums = [3, 5, 7] and you search for an even number:
    #         for n in nums:
    #             if n % 2 == 0:
    #                 print("Found even:", n)
    #                 break
    #         else:
    #             print("No even numbers")   # runs because break never fired!
    #
    # That removes clunky found = False flag variables in search loops.
    #
    # Unlike Odin or Go, Python has NO labeled 'break outer' syntax to exit two
    # nested loops at once. Instead, extract the nested search into a helper
    # function and use 'return' the moment you find your match. Notice
    # enumerate(m) below yields (index, element) pairs so y receives 0, 1, ...
    # and row receives each inner list:
    #
    #     Suppose grid = [[1, 2], [3, -1]]:
    #         def find_negative(m: list[list[int]]) -> tuple[int, int] | None:
    #             for y, row in enumerate(m):
    #                 for x, val in enumerate(row):
    #                     if val < 0:
    #                         return (y, x)   # exits both loops and helper at once!
    #             return None

    for n in [3, 5, 7]:
        if n % 2 == 0:
            break
    else:
        print("Starter scan: no even numbers in [3, 5, 7]")

    # Test loop-else on prime checking without any boolean flag variable.
    # Bind candidate = 29 and write: for factor in range(2, candidate):
    # If candidate % factor == 0, print the divisor and break; attach an else:
    # clause on the for loop that prints f"{candidate} is prime".
    # Repeat with candidate = 28 to verify else: is skipped when break fires.


    # Verify the empty-iterable rule for loop-else:
    # declare pending_tasks: list[str] = []
    # Loop with for task in pending_tasks: checking if task == "URGENT": break,
    # and attach an else: branch printing "No urgent tasks found" to see else:
    # still run when pending_tasks is empty.


    # Declare grid = [[1, 4, 7], [2, -5, 8], [3, 6, 9]].
    # First print every (y, x, val) cell using nested loops:
    # for y, row in enumerate(grid): and for x, val in enumerate(row):
    # Then define def find_target(matrix: list[list[int]], target: int) -> tuple[int, int] | None:
    # inside this function that exits both nested loops immediately with
    # return (y, x) when val == target, returning None if missing. Test it on
    # target = -5 and target = 99.


def iteration_mutation_trap_preview() -> None:

    # Modifying a container while looping over it behaves very differently
    # depending on the container type:
    # - dict and set track size changes and immediately raise RuntimeError if
    #   you insert or remove keys mid-loop.
    # - list does NOT raise an error—it silently skips elements! A list iterator
    #   simply tracks an index i = 0, 1, 2... under the hood:
    #
    #     Suppose buggy = [2, 4, 5, 6] and you remove evens during iteration:
    #         for n in buggy:
    #             if n % 2 == 0:
    #                 buggy.remove(n)
    #     At i=0, Python reads 2 and removes it, shifting buggy to [4, 5, 6].
    #     At i=1, the iterator moves to index 1 (value 5) and completely skips 4,
    #     leaving [4, 5] at the end! (Primer 280 covers defensive fixes deeply.)

    sample = [1, 2, 3]
    print("Starter sample ready for safe filtering drills:", sample)

    # Reproduce the silent list-skip bug and fix it cleanly:
    # bind buggy = [2, 4, 5, 6], run for n in buggy: removing even numbers with
    # buggy.remove(n), and print buggy to observe [4, 5].
    # Then create fixed = [2, 4, 5, 6] and filter out evens safely using either
    # a shallow copy loop (for n in fixed[:]:) or a comprehension
    # ([n for n in fixed if n % 2 != 0]), printing fixed to confirm [5].


    # Show how dict prevents mid-loop resizing:
    # create counts = {"a": 1, "b": 2, "c": 3}. Remove every odd-valued key
    # safely by looping over a snapshot of keys: for key in list(counts):
    # Print counts afterward (expected: {"b": 2}).
    #
    # Try uncommenting below to trigger RuntimeError:
    # for key in counts:
    #     del counts[key]


def main() -> None:

    print("=== 1. For loops and lazy ranges ===")
    for_loops_and_lazy_ranges()

    print("\n=== 2. While, sentinels, and continue traps ===")
    while_sentinels_and_continue_traps()

    print("\n=== 3. Loop-else and nested early returns ===")
    loop_else_and_nested_early_returns()

    print("\n=== 4. Mutation-during-iteration trap preview ===")
    iteration_mutation_trap_preview()


if __name__ == "__main__":
    main()
