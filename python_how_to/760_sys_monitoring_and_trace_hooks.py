# python 760_sys_monitoring_and_trace_hooks.py

import sys
import traceback


def per_code_line_and_call_monitoring() -> None:

    # Before Python 3.12, hooking line-by-line execution meant calling
    # sys.settrace, which attached a global Python callback to every frame in
    # the process and often slowed programs down by 10x to 30x.
    #
    # Python 3.12 added sys.monitoring (PEP 669) inside the VM so debuggers and
    # coverage tools can instrument only the exact code objects they care about:
    # - Tool slots (0 to 5): claim a slot with
    #   sys.monitoring.use_tool_id(tool_id, "line_tracer") and always release
    #   it in a finally block using sys.monitoring.free_tool_id(tool_id).
    # - Per-code-object targeting: sys.monitoring.set_local_events(tool_id, fn.__code__, mask)
    #   instruments only fn.__code__, leaving the rest of the VM at full speed.
    #
    # Pay close attention to two API rules:
    # - set_local_events takes a bitwise-OR mask such as
    #   events.LINE | events.PY_START | events.PY_RETURN, whereas
    #   sys.monitoring.register_callback(tool_id, event, fn) accepts ONE event
    #   per call (passing a combined mask raises ValueError).
    # - Each event passes a specific callback shape:
    #   - LINE receives (code, line_number)
    #   - PY_START receives (code, instruction_offset)
    #   - PY_RETURN receives (code, instruction_offset, retval)
    #   Returning sys.monitoring.DISABLE from a callback turns off future
    #   triggers at that exact site; returning None keeps firing every time.
    #   (See tracy_how_to/700 for profiler-overhead forensics and callback distortion.)
    #
    #     Suppose compute_sum(2) runs a 2-iteration loop:
    #     - When on_line returns None, the loop body line fires twice and
    #       visited_lines records that line number twice.
    #     - When on_line returns sys.monitoring.DISABLE, the VM disables that
    #       line site after the first hit, so a second call to compute_sum(2)
    #       fires zero more times at that site!

    print("Starter sys.monitoring LINE mask =", sys.monitoring.events.LINE)

    # Write a small multi-line helper def compute_sum(limit: int) -> int:
    # that initializes total = 0, loops for i in range(limit): accumulating
    # total += i, and returns total.


    # Instrument ONLY compute_sum.__code__:
    # - Find a free tool_id in range(6) via sys.monitoring.use_tool_id(tool_id, "line_tracer")
    #   (catching ValueError if a slot is already in use).
    # - Create visited_lines: list[int] = [] and register callbacks for LINE,
    #   PY_START, and PY_RETURN.
    # - Inside try:, enable events.LINE | events.PY_START | events.PY_RETURN on
    #   compute_sum.__code__, call result = compute_sum(4), and print result
    #   plus visited_lines.
    # - Inside finally:, clear set_local_events(tool_id, compute_sum.__code__, 0),
    #   unregister callbacks by passing None, and call free_tool_id(tool_id).


    # Test sys.monitoring.DISABLE on a second run of compute_sum(4):
    # Return sys.monitoring.DISABLE from your LINE callback after recording each
    # line once, and print visited_lines across two consecutive calls to
    # compute_sum(4) to observe each line firing only on its first hit.


def structured_tracebacks_with_extract_tb() -> None:

    # Alongside live VM hooks, Python's traceback module lets you inspect a
    # caught exception's call stack as structured data instead of letting it
    # dump directly to sys.stderr.
    #
    # Calling traceback.extract_tb(err.__traceback__) returns a list of
    # FrameSummary objects, each carrying .filename, .lineno, .name, and .line.
    #
    #     Suppose outer_step() calls inner_step(), which raises ZeroDivisionError:
    #     extract_tb(err.__traceback__) yields one FrameSummary per frame in
    #     call order so you can log "[outer_step:12, inner_step:8]" cleanly.
    #
    # When you want the full human-readable text as a string, call
    # "".join(traceback.format_exception(err)).

    try:
        1 / 0
    except ZeroDivisionError as demo_err:
        print("Starter extract_tb frame count =", len(traceback.extract_tb(demo_err.__traceback__)))

    # Write two nested helpers def inner_step() -> float: (raising
    # ZeroDivisionError via return 1 / 0) and def outer_step() -> float:
    # (calling and returning inner_step()).


    # Inside try / except ZeroDivisionError as err:, call outer_step().
    # Build frames = [f"{f.name}:{f.lineno}" for f in traceback.extract_tb(err.__traceback__)]
    # and print frames. Also build formatted = "".join(traceback.format_exception(err))
    # and print its line count and last line.


    # Compare traceback.format_exc() inside an except block:
    # Catch ValueError("bad config") in a fresh try / except ValueError:, call
    # text = traceback.format_exc(), and print text.splitlines()[-1] to see how
    # format_exc() reads sys.exc_info() automatically without an err argument.


def main() -> None:

    print("=== 1. Per-code sys.monitoring LINE, PY_START, and PY_RETURN ===")
    per_code_line_and_call_monitoring()

    print("\n=== 2. Structured tracebacks with traceback.extract_tb ===")
    structured_tracebacks_with_extract_tb()


if __name__ == "__main__":
    main()
