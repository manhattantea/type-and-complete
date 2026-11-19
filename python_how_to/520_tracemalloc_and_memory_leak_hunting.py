# python 520_tracemalloc_and_memory_leak_hunting.py

from collections import deque
import tracemalloc


def traced_memory_and_peak_watermarks() -> None:

    # When a long-running Python service slowly climbs in RAM, guessing which
    # function is retaining objects wastes hours. The built-in tracemalloc
    # module hooks CPython's internal memory allocators (PyMem and PyObject) and
    # records the exact source file, line number, and optional call stack for
    # every live Python allocation—similar to Odin's mem.Tracking_Allocator.
    #
    # Core lifecycle:
    # - tracemalloc.start(nframe=1) starts recording allocations.
    # - tracemalloc.get_traced_memory() returns (current_bytes, peak_bytes).
    # - tracemalloc.reset_peak() resets peak_bytes down to current_bytes so you
    #   can measure a new phase without old spikes hiding it.
    # - tracemalloc.stop() turns off hooks and frees trace tables. Always place
    #   tracemalloc.stop() in a finally: block so overhead never leaks onward.
    #
    # Caveat: tracemalloc tracks memory routed through CPython's allocator APIs;
    # raw C malloc() calls inside native C extensions bypass it.
    #
    #     Suppose tracemalloc.start() is active and you allocate
    #     buf = bytearray(65_536).
    #     current_bytes jumps by ~65 KiB and peak_bytes hits ~65 KiB.
    #     After del buf, current_bytes drops back near 0 while peak_bytes stays
    #     at ~65 KiB until tracemalloc.reset_peak() clears the high-water mark.

    print("tracemalloc active initially:", tracemalloc.is_tracing())

    # Wrap a tracing run in try / finally: tracemalloc.stop(). Call
    # tracemalloc.start(), allocate scratch = [bytearray(256) for _ in range(2_000)],
    # and print current_bytes, peak_bytes = tracemalloc.get_traced_memory().
    # Then run del scratch, read get_traced_memory() a second time, and verify
    # current_bytes dropped sharply while peak_bytes remained at the spike.


    # Inside that same tracing block (after deleting scratch), call
    # tracemalloc.reset_peak(), allocate a tiny small = bytearray(1024), and
    # print get_traced_memory() to verify peak_bytes now matches the small spike.


def snapshot_diffs_and_culprit_lines() -> None:

    # Total bytes only tell you THAT memory grew; snapshots tell you WHERE.
    # Calling tracemalloc.take_snapshot() freezes a map of every live allocation.
    # Always capture snap_before AFTER one-time startup and warmup so module
    # import noise does not clutter your report.
    #
    # Calling snap_after.compare_to(snap_before, "lineno") returns a list of
    # StatisticDiff records sorted from largest byte growth downward. Each stat
    # exposes stat.size_diff (net bytes added), stat.count_diff (net live blocks
    # added), and stat.traceback (exact file and line number).
    #
    #     Suppose snap_before is taken before calling batch = allocate_batch(5_000)
    #     and snap_after is taken right after.
    #     snap_after.compare_to(snap_before, "lineno")[0] points straight to the
    #     list comprehension inside allocate_batch with ~700+ KiB of size_diff.

    print("Tracer internal bytes while stopped:", tracemalloc.get_tracemalloc_memory())

    # Define a helper def allocate_batch(count: int) -> list[bytearray]: that
    # returns [bytearray(128) for _ in range(count)] (distinct heap buffers so
    # CPython cannot reuse cached small ints or interned string literals).
    # Inside try / finally: tracemalloc.stop(), start tracing, capture
    # snap_before = tracemalloc.take_snapshot(), call
    # batch = allocate_batch(5_000), capture snap_after = tracemalloc.take_snapshot(),
    # and print the top 3 entries of snap_after.compare_to(snap_before, "lineno")
    # along with each stat.size_diff and stat.count_diff.


    # Narrow snapshot output to this file using
    # only_here = snap_after.filter_traces((tracemalloc.Filter(True, __file__),)).
    # Filter(True, pattern) keeps only allocations matching that filename.
    # Delete batch, capture snap_freed = tracemalloc.take_snapshot(), and diff
    # snap_freed against snap_before to confirm the culprit line's size_diff
    # dropped back near 0.


def before_and_after_leak_fix_snapshot_diff() -> None:

    # Real memory-leak hunting follows a tight before-and-after proof loop:
    # First, reproduce the suspect workload across repeated iterations and diff
    # snapshots to catch positive retained byte growth. Second, replace the
    # unbounded retention (such as an ever-growing audit list or cache) with a
    # bounded structure such as deque(maxlen=64) or a weakref cache. Third, run
    # the exact same workload again and diff snapshots to prove net retained
    # bytes stay flat near 0.
    #
    # Notice why warmup matters before snap_before on the fixed version: a
    # bounded deque(maxlen=64) legitimately grows during its first 64 inserts
    # while filling up, then flattens to 0 net growth for the next million calls!
    #
    #     Suppose leaky_log appends bytearray(512) on every request: after 2,000
    #     requests, compare_to shows ~1 MiB retained.
    #     Replacing leaky_log with deque(maxlen=64) and warming up 100 requests
    #     makes the next 2,000 requests show ~0 bytes net growth!

    sample_ring: deque[int] = deque(maxlen=3)
    sample_ring.extend([1, 2, 3, 4])
    print("Starter bounded deque after 4 pushes (maxlen=3):", list(sample_ring))

    # Reproduce the BEFORE-fix leak: inside try / finally: tracemalloc.stop(),
    # call tracemalloc.start() and create leaky_history: list[bytearray] = [].
    # Define def record_leaky() -> None: appending bytearray(512) to
    # leaky_history. Run 100 warmup calls, capture
    # snap_leak_before = tracemalloc.take_snapshot(), run 2_000 more calls, and
    # capture snap_leak_after = tracemalloc.take_snapshot().
    # Compute leak_stats = snap_leak_after.compare_to(snap_leak_before, "lineno"),
    # sum leak_growth = sum(stat.size_diff for stat in leak_stats), and print
    # leak_growth along with leak_stats[0] (expect ~1 MB retained!).


    # Now verify the AFTER-fix diff: create
    # bounded_history: deque[bytearray] = deque(maxlen=64) and
    # def record_fixed() -> None: appending bytearray(512) to bounded_history.
    # Run 100 warmup calls so the ring reaches full capacity, capture
    # snap_fix_before = tracemalloc.take_snapshot(), run 2_000 more calls, and
    # capture snap_fix_after = tracemalloc.take_snapshot().
    # Compute fixed_stats = snap_fix_after.compare_to(snap_fix_before, "lineno")
    # and fixed_growth = sum(stat.size_diff for stat in fixed_stats). Print
    # leak_growth vs fixed_growth side by side to prove the leak is gone!


    # Turn that diff into a leak-regression guard: assert leak_growth > 500_000
    # and assert abs(fixed_growth) < 16_384, then call leaky_history.clear() so
    # the earlier leaked buffers are released cleanly.


def multi_frame_tracebacks_for_shared_helpers() -> None:

    # Default tracemalloc.start(1) records only 1 stack frame—the exact leaf
    # line that allocated memory. When ten callers all invoke one shared utility
    # function like make_buffer(size), lineno grouping points only at
    # make_buffer and hides which caller leaked the returned buffers!
    #
    # Passing a deeper limit such as tracemalloc.start(5) and grouping with
    # snap_after.compare_to(snap_before, "traceback") captures up to 5 frames of
    # call stack per allocation. Calling stat.traceback.format() prints the full
    # caller chain straight to the culprit.

    print("Default traceback limit when stopped:", tracemalloc.get_traceback_limit())

    # Define a shared helper def make_payload(size: int) -> bytearray: returning
    # bytearray(size), plus two callers: def fleeting_caller() -> int: (allocates
    # make_payload(256) and returns its length without retaining it) and
    # def retaining_caller(sink: list[bytearray]) -> None: (appends
    # make_payload(256) into sink).
    # Inside try / finally: tracemalloc.stop(), start with tracemalloc.start(5),
    # capture snap_before, run both callers 500 times against sink: list[bytearray] = [],
    # capture snap_after, diff with compare_to(snap_before, "traceback"), and
    # print "\n".join(top_stat.traceback.format()) to watch retaining_caller
    # appear above make_payload!


def main() -> None:

    print("=== 1. Traced memory and peak high-water marks ===")
    traced_memory_and_peak_watermarks()

    print("\n=== 2. Snapshot diffs and pinpointing culprit lines ===")
    snapshot_diffs_and_culprit_lines()

    print("\n=== 3. Before-and-after leak-fix snapshot diff ===")
    before_and_after_leak_fix_snapshot_diff()

    print("\n=== 4. Multi-frame tracebacks for shared helpers ===")
    multi_frame_tracebacks_for_shared_helpers()


if __name__ == "__main__":
    main()
