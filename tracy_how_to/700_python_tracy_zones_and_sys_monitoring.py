# python 700_python_tracy_zones_and_sys_monitoring.py

# Before Python 3.12, attaching a profiler hook with sys.setprofile or
# sys.settrace forced the interpreter to dispatch callbacks on EVERY function
# call across the entire program. Python 3.12's sys.monitoring (PEP 669) solves
# that with targeted event masks:
# - You claim one of 8 global tool slots with sys.monitoring.use_tool_id(id, name).
# - You attach callbacks (PY_START, PY_RETURN, PY_UNWIND) ONLY to the specific
#   code objects you want to trace via sys.monitoring.set_local_events(id, code, mask).
# - Unmonitored functions pay zero callback overhead!
#
# Even with PEP 669, calling a Python callback on PY_START and PY_RETURN still
# costs ~100-400 ns per call. Just like manual Tracy zones, attaching
# sys.monitoring to a 40 ns inner helper distorts your trace—while returning
# sys.monitoring.DISABLE disables future events at that site, and hooking
# PY_UNWIND keeps your zone stack balanced when an exception unwinds.
#
# For basic LINE tracing and traceback inspection, see
# ../python_how_to/760_sys_monitoring_and_trace_hooks.py.

from collections import defaultdict
from collections.abc import Callable
import sys
import time
import types


def format_code_label(code: types.CodeType) -> str:

    return code.co_qualname


def fast_transform(x: int) -> int:

    return (x * 3 + 1) & 0xFFFF


def risky_parse(raw: str) -> int:

    if not raw.isdigit():
        raise ValueError(f"Expected digits, got {raw!r}")
    return int(raw)


class SysMonitoringTracyBridge:

    def __init__(
        self,
        targets: list[Callable[..., object]],
        disable_after_first: bool = False,
    ) -> None:

        self._targets = targets
        self._disable_after_first = disable_after_first
        self._tool_id: int | None = None
        self._start_stacks: list[tuple[str, int]] = []
        self.totals_ns: dict[str, int] = defaultdict(int)
        self.call_counts: dict[str, int] = defaultdict(int)
        self.unwind_counts: dict[str, int] = defaultdict(int)

    # Define _on_start(self, code: types.CodeType, offset: int) -> object | None
    # Push (format_code_label(code), time.perf_counter_ns()) onto
    # self._start_stacks. When self._disable_after_first is True, increment a
    # counter or return sys.monitoring.DISABLE after recording the first entry
    # so CPython stops firing PY_START at that bytecode offset!


    # Define _on_return(self, code: types.CodeType, offset: int, retval: object) -> object | None
    # Pop (name, start_ns) from self._start_stacks (guarding empty stack),
    # add time.perf_counter_ns() - start_ns into self.totals_ns[name],
    # increment self.call_counts[name], and optionally return
    # sys.monitoring.DISABLE when self._disable_after_first is True.


    # Define _on_unwind(self, code: types.CodeType, offset: int, exc: BaseException) -> None
    # Pop (name, start_ns) from self._start_stacks (guarding empty stack),
    # add elapsed nanoseconds into self.totals_ns[name], increment
    # self.call_counts[name], and increment self.unwind_counts[name] so
    # exceptions never leave stale entries on self._start_stacks!


    # Define __enter__(self) -> "SysMonitoringTracyBridge"
    # Find a free tool_id in (sys.monitoring.PROFILER_ID, 3, 4) where
    # sys.monitoring.get_tool(tid) is None, claim it with
    # sys.monitoring.use_tool_id(tid, "tracy_bridge"), register _on_start for
    # E.PY_START, _on_return for E.PY_RETURN, and _on_unwind for E.PY_UNWIND,
    # then enable E.PY_START | E.PY_RETURN | E.PY_UNWIND on fn.__code__ for
    # every fn in self._targets via sys.monitoring.set_local_events. Return self.


    # Define __exit__(self, exc_type: object, exc: object, tb: object) -> None
    # Inside try ... finally, clear set_local_events(self._tool_id, fn.__code__, 0)
    # for every target, unregister all three callbacks with None, and call
    # sys.monitoring.free_tool_id(self._tool_id) whenever self._tool_id is not None.


def sys_monitoring_auto_zones() -> None:

    # Why attach sys.monitoring to coarse pipeline functions instead of editing
    # every function with manual with-blocks? Because your domain functions stay
    # 100% unmodified! When you exit the bridge's with-block, __exit__ resets
    # local events to 0 and frees the tool slot so the rest of the process pays
    # zero monitoring cost again.

    if hasattr(sys, "monitoring"):
        e = sys.monitoring.events
        event_mask = e.PY_START | e.PY_RETURN | e.PY_UNWIND
        tool_state = sys.monitoring.get_tool(sys.monitoring.PROFILER_ID)
        print(
            f"sys.monitoring ready | PROFILER_ID={tool_state!r} | "
            f"event_mask={event_mask} | sample_code={format_code_label(fast_transform.__code__)}"
        )
    else:
        print("sys.monitoring requires Python 3.12+")

    # Define two clean, uninstrumented pipeline functions:
    # - stage_parse(raw: list[str]) -> list[int] converting each numeric string to int
    # - stage_compute(values: list[int]) -> int summing v * v over values
    # Build sample_raw = [str(i) for i in range(2_000)].
    # Enter with SysMonitoringTracyBridge([stage_parse, stage_compute]) as bridge:,
    # run stage_compute(stage_parse(sample_raw)) 5 times, and print
    # bridge.call_counts and bridge.totals_ns. Assert
    # sys.monitoring.get_tool(sys.monitoring.PROFILER_ID) is None after exiting!


def callback_distortion_and_disable() -> None:

    # Suppose fast_transform(x) executes ~40-80 ns of integer arithmetic per call
    # inside a 10,000-element loop (~0.6 ms total). Attaching PY_START and
    # PY_RETURN directly to fast_transform.__code__ fires TWO Python callbacks on
    # every element—20,000 Python frame entries for 10,000 tiny calls—inflating
    # total time by 5x to 20x!
    #
    # When we return sys.monitoring.DISABLE from a callback, CPython marks that
    # exact bytecode site as disabled for your tool_id so future iterations skip
    # the callback entirely and return to baseline speed.

    t0 = time.perf_counter_ns()
    acc = 0
    for i in range(1_000):
        acc += fast_transform(i)
    base_ns = max(1, time.perf_counter_ns() - t0)
    print(
        f"Unmonitored fast_transform preview (1,000 calls): "
        f"{base_ns / 1000:.1f} ns/call | sink={acc}"
    )

    # Measure direct sys.monitoring distortion on n = 10_000 calls:
    # First measure unmonitored loop timing calling fast_transform(i) directly
    # (base_ns). Next wrap the loop inside a coarse function run_batch(n: int) -> int
    # and monitor ONLY [run_batch] with SysMonitoringTracyBridge (coarse_ns).
    # Then monitor [fast_transform] directly across the 10,000-iteration loop
    # (inner_ns) so PY_START + PY_RETURN fire 10,000 times!
    # Print base_ns, coarse_ns, inner_ns, and distortion = inner_ns / max(1, base_ns).


    # Test sys.monitoring.DISABLE overhead elimination:
    # Run the same 10,000-call loop inside
    # with SysMonitoringTracyBridge([fast_transform], disable_after_first=True) as bridge:
    # (note: if _on_start disables PY_START after first entry while _on_return
    # also returns sys.monitoring.DISABLE, both sites turn off after 1 hit!).
    # Verify bridge.call_counts[format_code_label(fast_transform.__code__)] == 1
    # and observe total loop runtime return near base_ns!


def py_unwind_exception_safety() -> None:

    # What happens if you hook PY_START and PY_RETURN, skip PY_UNWIND, and a
    # monitored function raises ValueError? Normal RETURN_VALUE never runs!
    # CPython jumps straight into stack unwinding and fires PY_UNWIND instead.
    #
    # Suppose outer_job() calls risky_parse("bad").
    # - Without PY_UNWIND: _start_stacks pushes outer_job, pushes risky_parse,
    #   and NEVER pops risky_parse when ValueError escapes—corrupting every
    #   later zone's Self Time and leaving _start_stacks non-empty!
    # - With PY_UNWIND: _on_unwind pops risky_parse cleanly as the exception
    #   leaves the frame, then pops outer_job if outer_job also unwinds (or
    #   lets outer_job finish via PY_RETURN if outer_job catches ValueError!).

    parsed_ok = risky_parse("42")
    print(f"Starter risky_parse('42') -> {parsed_ok}")

    # Prove PY_UNWIND cleans up the active zone stack on exceptions:
    # Define outer_job(items: list[str]) -> int that loops over items calling
    # risky_parse(item) inside try: ... except ValueError: ... (or lets one
    # ValueError escape to a try/except around the call).
    # Monitor [outer_job, risky_parse] with SysMonitoringTracyBridge, pass
    # ["10", "bad", "30"], assert bridge.unwind_counts[format_code_label(risky_parse.__code__)] == 1,
    # assert len(bridge._start_stacks) == 0, and confirm the tool slot is freed
    # cleanly on exit!


def main() -> None:

    print("=== 1. Targeted sys.monitoring auto-zones (zero function edits) ===")
    sys_monitoring_auto_zones()

    print("\n=== 2. Callback distortion and sys.monitoring.DISABLE ===")
    callback_distortion_and_disable()

    print("\n=== 3. PY_UNWIND exception safety ===")
    py_unwind_exception_safety()


if __name__ == "__main__":
    main()
