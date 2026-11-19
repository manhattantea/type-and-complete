# python 695_subprocess_and_os_processes.py

import os
from pathlib import Path
import subprocess
import sys
import tempfile


def safe_argv_lists_and_sys_executable() -> None:

    # Legacy os.system("...") and os.popen("...") invoke an OS shell (/bin/sh
    # or cmd.exe), opening command-injection vulnerabilities whenever any part
    # of the command comes from input. Modern Python uses
    # subprocess.run(args, ...) -> subprocess.CompletedProcess.
    #
    # Always pass a list of separate argument strings with shell=False (the
    # default). Python spawns the executable directly via OS process APIs so
    # spaces, quotes, ;, and | inside arguments are delivered verbatim as a
    # single argv entry instead of being interpreted by a shell.
    #
    #     Suppose you spawn Python itself as a child process:
    #     Always pass sys.executable instead of "python" or "python3" so the
    #     child runs inside the exact same virtual environment and version.
    #     Passing capture_output=True, text=True, encoding="utf-8" captures
    #     both .stdout and .stderr as UTF-8 strings (avoiding Windows cp1252).

    probe = subprocess.run(
        [sys.executable, "-c", "import sys; print(sys.version_info[:2])"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
        timeout=10,
    )
    print("Child Python version:", probe.stdout.strip(), f"(rc={probe.returncode})")

    # Run [sys.executable, "-c", "import sys; print(repr(sys.argv[1:]))", "hello; whoami", "a b"]
    # via subprocess.run(..., capture_output=True, text=True, encoding="utf-8", check=True, timeout=10)
    # and print result.stdout to confirm shell metacharacters stayed literal.


    # Run a child script that writes one line to sys.stdout and one line to
    # sys.stderr, and print both result.stdout.strip() and result.stderr.strip()
    # separately from the returned CompletedProcess.


def stdin_env_and_cwd_isolation() -> None:

    # subprocess.run lets you pass stdin data, custom environment variables, and
    # a child working directory without mutating the parent process:
    # - input="...": pipes text into the child's stdin and closes it cleanly.
    # - env={**os.environ, "APP_MODE": "test"}: passes an isolated environment
    #   dict to the child without modifying os.environ in the parent.
    # - cwd=some_dir: runs the child inside some_dir without calling os.chdir.

    echo = subprocess.run(
        [sys.executable, "-c", "import os; print(os.getenv('DEMO_FLAG', 'unset'))"],
        env={**os.environ, "DEMO_FLAG": "active"},
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
        timeout=10,
    )
    print("Starter child env DEMO_FLAG:", echo.stdout.strip())

    # Feed input="hello from parent\n" to
    # [sys.executable, "-c", "import sys; print(sys.stdin.read().upper().strip())"]
    # via subprocess.run(..., capture_output=True, text=True, encoding="utf-8", check=True, timeout=10)
    # and print result.stdout and result.returncode.


    # Open with tempfile.TemporaryDirectory() as tmp_str: and run
    # [sys.executable, "-c", "import os, pathlib; print(pathlib.Path.cwd(), os.getenv('MODE'))"]
    # with cwd=Path(tmp_str) and env={**os.environ, "MODE": "sandbox"}. Print
    # the child's stdout and also print Path.cwd() in the parent to verify the
    # parent's working directory never changed.


def check_true_stderr_and_timeouts() -> None:

    # Without check=True, subprocess.run silently returns a CompletedProcess
    # with returncode != 0. With check=True, any non-zero exit raises
    # subprocess.CalledProcessError, carrying .returncode, .cmd, .stdout, and
    # .stderr so you can log diagnostics cleanly. Passing timeout=seconds bounds
    # hung children and raises subprocess.TimeoutExpired.

    res = subprocess.run([sys.executable, "-c", "import sys; sys.exit(0)"], check=True, timeout=10)
    print("Starter check=True exit code:", res.returncode)

    # Run [sys.executable, "-c", "import sys; print('bad config', file=sys.stderr); sys.exit(3)"]
    # with capture_output=True, text=True, encoding="utf-8", and check=True inside
    # try ... except subprocess.CalledProcessError as err: and print
    # err.returncode, err.cmd, and err.stderr.strip().


    # Try uncommenting the snippet below to observe subprocess.TimeoutExpired:
    # try:
    #     subprocess.run([sys.executable, "-c", "import time; time.sleep(2)"], timeout=0.2)
    # except subprocess.TimeoutExpired as exc:
    #     print(f"Timed out after {exc.timeout}s")


def main() -> None:

    print("=== 1. Safe argv lists and sys.executable ===")
    safe_argv_lists_and_sys_executable()

    print("\n=== 2. stdin, env, and cwd isolation ===")
    stdin_env_and_cwd_isolation()

    print("\n=== 3. check=True, stderr inspection, and timeouts ===")
    check_true_stderr_and_timeouts()


if __name__ == "__main__":
    main()
