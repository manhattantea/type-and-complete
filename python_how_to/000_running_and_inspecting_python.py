# python 000_running_and_inspecting_python.py

import py_compile
import sys


def bytecode_and_interpreter_info() -> None:

    # Unlike Ahead-of-Time (AOT) compiled languages such as C or Odin, CPython
    # compiles your .py source file into bytecode instructions (cached inside
    # __pycache__/*.pyc when a module is imported) and executes that bytecode on
    # the CPython virtual machine. Subsequent imports reuse the cached .pyc file
    # instead of re-parsing the source from scratch.
    #
    # The sys module exposes live facts about the running interpreter:
    # - sys.version_info is a named tuple (major, minor, micro, ...) so you can
    #   write clean version checks like sys.version_info >= (3, 12) instead of
    #   fragile string parsing.
    # - sys.platform reports the host OS ("win32", "linux", "darwin"), and
    #   sys.executable prints the exact path of the running python binary.
    # - __debug__ is a built-in boolean constant (True by default, False under
    #   python -O), while sys.flags.optimize reports the optimization level (0
    #   normally, 1 under -O).
    #
    # Suppose you launch a script normally:
    #     __debug__ is True and sys.flags.optimize is 0.
    # Launch the same script with python -O and __debug__ flips to False while
    # sys.flags.optimize becomes 1.

    print("Python runtime:", sys.version.split()[0])

    # Print __name__, sys.version_info[:3], sys.platform, sys.executable,
    # sys.flags.optimize, and __debug__ with clear labels.


    # Evaluate sys.version_info >= (3, 12) and print whether this interpreter
    # supports Python 3.12+ features (such as PEP 695 type aliases and PEP 701
    # f-string quote reuse).


def compiling_and_cli_flags() -> None:

    # Everyday CLI flags you will actually reach for at the terminal:
    # - python <file>.py               run a standalone script directly
    # - python -m <module>             run an importable library module as main
    # - python -c "print(1 + 2)"       execute a quick one-liner from the shell
    # - python -i <file>.py            run the script, then open an interactive REPL
    # - python -O <file>.py            optimized mode: sets __debug__ = False and
    #                                  strips assert statements completely
    # - python -B <file>.py            do not write __pycache__/*.pyc on import
    # - python -W error <file>.py      turn runtime warnings into exceptions
    #
    # Watch out for -O stripping assert statements: never put required input
    # validation or side effects inside assert, because running under -O removes
    # those lines completely!
    #
    # When you want to check syntax or generate a .pyc file without executing
    # top-level code, py_compile.compile(path, doraise=True) compiles a source
    # file and returns the exact path of the resulting .pyc cache file (raising
    # py_compile.PyCompileError if syntax is invalid).
    #
    # Suppose you run:
    #     python -B 000_running_and_inspecting_python.py
    # Python sets sys.dont_write_bytecode to True for the entire process so
    # importing helper modules leaves the directory free of __pycache__ folders.

    print("Current source file:", __file__)
    print("Bytecode writes disabled (-B):", sys.dont_write_bytecode)

    # Call compiled_path = py_compile.compile(__file__, doraise=True) and print
    # compiled_path to see the exact .pyc location inside __pycache__/.


    # Re-run this file from your terminal with two different flags and watch the
    # printed flags change:
    # - python -O 000_running_and_inspecting_python.py
    # - python -B 000_running_and_inspecting_python.py
    # Also try a quick shell one-liner and module compile check:
    # - python -c "import sys; print(sys.version_info[:3])"
    # - python -m py_compile 000_running_and_inspecting_python.py


def entry_point_and_import_guard() -> None:

    # When another Python file imports your .py module, Python executes EVERY
    # top-level statement in that file immediately from top to bottom. Placing
    # your runnable script logic inside def main() -> None: and calling it under
    # if __name__ == "__main__": guarantees that it runs ONLY when executed
    # directly as a script (__name__ == "__main__"), not when another file
    # imports your helper functions (where __name__ equals the module's name).
    #
    # Suppose math_tools.py defines def double(n: int) -> int: and puts a demo
    # print inside if __name__ == "__main__":. Running python math_tools.py runs
    # the demo, while import math_tools loads double() silently with no stray
    # console output.

    print("Module __name__ right now:", __name__)

    # Define a small helper def format_tag(label: str) -> str: inside this
    # function returning f"[{label.upper()}]", call it with "ready", and print
    # the returned string.


    # Verify how -W error escalates warnings into exceptions from your terminal:
    # run python -W error -c "import warnings; warnings.warn('old api')"
    # and compare that against running the same command without -W error.


def main() -> None:

    print("=== 1. Bytecode and interpreter info ===")
    bytecode_and_interpreter_info()

    print("\n=== 2. Compiling and CLI flags ===")
    compiling_and_cli_flags()

    print("\n=== 3. Entry point and import guard ===")
    entry_point_and_import_guard()


if __name__ == "__main__":
    main()
