# python 075_with_context_managers_basics.py

import io
import tempfile
from contextlib import nullcontext, redirect_stdout, suppress
from pathlib import Path


def with_protocol_and_redirect_stdout() -> None:

    # Relying on garbage collection (__del__) to close files, locks, or sockets
    # is a bug: reference cycles delay __del__ until cyclic GC runs, and
    # non-refcounted runtimes like PyPy do not fire __del__ immediately when a
    # variable leaves scope.
    #
    # Python's 'with' statement guarantees deterministic setup and teardown—the
    # same guarantee as try / finally, written cleanly in one header:
    # - First, Python evaluates the context expression to get manager mgr.
    # - Second, Python calls type(mgr).__enter__(mgr) and binds its return
    #   value to the optional 'as var' name.
    # - Third, Python guarantees type(mgr).__exit__(mgr, exc_type, exc_val, exc_tb)
    #   runs when the block exits—whether via normal end, return, break, or an
    #   exception!
    #
    # Two standard helpers make testing 'with' effortless without touching disk:
    # - io.StringIO() creates an in-memory text stream with .getvalue().
    # - redirect_stdout(stream) temporarily points sys.stdout (including print)
    #   at stream during the 'with' block and restores sys.stdout on exit:
    #
    #     Suppose buf = io.StringIO().
    #     Inside with redirect_stdout(buf): calling print("hi") writes into buf.
    #     After the block exits, buf.getvalue() == "hi\n" and print() is normal.

    starter_buf = io.StringIO()
    with redirect_stdout(starter_buf):
        print("starter captured line")
    print("Starter buffer contents:", repr(starter_buf.getvalue()))

    # Create buf = io.StringIO(), enter with redirect_stdout(buf): to call
    # print("captured output") and print("second line"), then outside the block
    # print repr(buf.getvalue()) to confirm normal stdout was restored.


    # Prove teardown still restores sys.stdout when an exception escapes:
    # Create err_buf = io.StringIO() and wrap a with redirect_stdout(err_buf):
    # block inside try / except RuntimeError as err:. Inside the 'with' block,
    # print("before crash") and raise RuntimeError("boom"). After catching err,
    # print("stdout restored:", repr(err_buf.getvalue())) to confirm normal
    # printing still works.


    # Prove teardown also runs on an early 'return':
    # Define def capture_greeting(name: str) -> str: that creates
    # out = io.StringIO(), enters with redirect_stdout(out):, calls
    # print(f"Hello, {name}"), and executes return out.getvalue().strip() from
    # INSIDE the 'with' block. Call capture_greeting("Odin") and print both the
    # returned string and a follow-up print("still on real stdout").


def multi_resource_parenthesized_with() -> None:

    # Modern Python (3.10+) supports parenthesized multi-resource 'with'
    # blocks so you can acquire several resources without nesting indentation:
    #
    #     with (
    #         src_path.open("r", encoding="utf-8") as src,
    #         dst_path.open("w", encoding="utf-8") as dst,
    #     ):
    #         dst.write(src.read().upper())
    #
    # Teardown always runs in LIFO order (Last In, First Out): src enters
    # first, dst enters second; on exit dst.__exit__ runs FIRST and
    # src.__exit__ runs SECOND. Even better, if dst.__enter__ raises an error
    # (for instance, bad path permissions), Python STILL runs src.__exit__ so
    # src never leaks!

    with tempfile.TemporaryDirectory() as starter_tmp:
        starter_file = Path(starter_tmp) / "hello.txt"
        starter_file.write_text("ready\n", encoding="utf-8")
        print("Starter temp file read:", repr(starter_file.read_text(encoding="utf-8")))

    # Combine two real file handles inside one parenthesized multi-resource with:
    # Inside with tempfile.TemporaryDirectory() as tmp:, write "alpha\nbeta\n"
    # to src_path = Path(tmp) / "input.txt" and set dst_path = Path(tmp) / "output.txt".
    # Open BOTH files using:
    # with (src_path.open("r", encoding="utf-8") as src, dst_path.open("w", encoding="utf-8") as dst):
    # Copy each line uppercased from src to dst. Outside the inner 'with' block,
    # print repr(dst_path.read_text(encoding="utf-8")), src.closed, and dst.closed.


    # Stack two redirect_stdout managers in one parenthesized 'with' block to
    # watch LIFO unwinding:
    # Create outer_buf = io.StringIO() and inner_buf = io.StringIO().
    # Enter with (redirect_stdout(outer_buf), redirect_stdout(inner_buf)): and
    # print("goes to inner"). Then verify outer_buf.getvalue() is "" while
    # inner_buf.getvalue() holds "goes to inner\n" because the second manager
    # took over stdout last and exited first.


    # Handle a dynamic number of resources with contextlib.ExitStack:
    # Import ExitStack inside this function (from contextlib import ExitStack).
    # Inside with tempfile.TemporaryDirectory() as tmp:, use
    # with ExitStack() as stack: to open three files ("a.txt", "b.txt", "c.txt")
    # in a loop via fh = stack.enter_context((Path(tmp) / name).open("w", encoding="utf-8")),
    # collect each handle in handles: list[io.TextIOBase] = [], write a line to
    # each, and after exiting the ExitStack confirm all(h.closed for h in handles).


def suppress_and_nullcontext() -> None:

    # Two tiny contextlib tools eliminate noisy boilerplate:
    # - suppress(*exceptions) swallows ONLY the listed exception types inside
    #   its block. Watch out for one subtle rule: the moment a suppressed
    #   exception is raised, execution jumps IMMEDIATELY out of the 'with'
    #   block—any remaining statements inside that same block are skipped!
    # - nullcontext(enter_result=None) is a zero-overhead no-op manager whose
    #   __enter__ returns enter_result and whose __exit__ does nothing. It lets
    #   you write conditional resource blocks without duplicating the body:
    #
    #     Suppose stream is either an io.StringIO or None:
    #         cm = redirect_stdout(stream) if stream is not None else nullcontext()
    #         with cm:
    #             print("report ready")

    starter_cfg = {"mode": "fast"}
    with suppress(KeyError):
        del starter_cfg["missing"]
    with nullcontext("default-label") as starter_label:
        print("Starter suppress + nullcontext:", starter_cfg, starter_label)

    # Create settings = {"theme": "dark"}. Use with suppress(KeyError): to run
    # del settings["missing_key"] followed by print("this line is skipped!").
    # Print settings afterward to confirm no crash occurred AND observe that
    # the second line inside the 'with' block did NOT execute!


    # Verify suppress() is narrow and does NOT hide unrelated bugs:
    # Wrap with suppress(KeyError): int("not-an-int") inside
    # try / except ValueError as err: and print "ValueError still escaped:", err.


    # Practice nullcontext with an optional stream redirect:
    # Define def emit_report(stream: io.StringIO | None) -> None: using
    # cm = redirect_stdout(stream) if stream is not None else nullcontext()
    # and with cm: print("visible report line").
    # Call emit_report(None) (prints directly to stdout), then call
    # emit_report(capture) with capture = io.StringIO() and print
    # repr(capture.getvalue()).


def custom_enter_exit_protocol_preview() -> None:

    # Any class becomes a context manager simply by defining __enter__ and
    # __exit__. Look closely at what __exit__(self, exc_type, exc_val, exc_tb)
    # returns:
    # - Returning False (or None) lets any exception keep propagating normally.
    # - Returning True suppresses the exception completely (that is literally
    #   how contextlib.suppress works under the hood!).
    #
    #     Suppose TraceScope("outer") and TraceScope("inner") are entered in one
    #     parenthesized with block:
    #     Output order is: enter outer -> enter inner -> exit inner -> exit outer.

    with nullcontext("protocol-ready") as tag:
        print("Starter protocol check:", tag)

    # Define class TraceScope: inside this function with:
    # - def __init__(self, name: str) -> None: storing self.name = name
    # - def __enter__(self) -> str: printing f"enter {self.name}" and returning self.name
    # - def __exit__(self, exc_type: object, exc_val: object, exc_tb: object) -> bool:
    #   printing f"exit {self.name}: exc={exc_type}" and returning False
    # Enter two scopes together using:
    # with (TraceScope("outer") as a, TraceScope("inner") as b):
    # printing f"inside {a}/{b}" to watch exact LIFO teardown order.


    # Verify what TraceScope.__exit__ receives when an error occurs:
    # Wrap with TraceScope("failing"): raise ValueError("bad input") inside
    # try / except ValueError as err: and observe exc_type print
    # <class 'ValueError'> while the exception still propagates because
    # __exit__ returned False.


def main() -> None:

    print("=== 1. The with protocol and redirect_stdout ===")
    with_protocol_and_redirect_stdout()

    print("\n=== 2. Multi-resource parenthesized with ===")
    multi_resource_parenthesized_with()

    print("\n=== 3. contextlib.suppress and nullcontext ===")
    suppress_and_nullcontext()

    print("\n=== 4. Custom __enter__ / __exit__ protocol preview ===")
    custom_enter_exit_protocol_preview()


if __name__ == "__main__":
    main()
