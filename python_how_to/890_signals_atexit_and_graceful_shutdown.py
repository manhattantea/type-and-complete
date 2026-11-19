# python 890_signals_atexit_and_graceful_shutdown.py

import atexit
import signal
from types import FrameType


def atexit_lifo_cleanup() -> None:

    # atexit.register(fn, *args, **kwargs) registers cleanup callbacks that run
    # in Last-In, First-Out (LIFO) order when the Python interpreter exits
    # normally or via sys.exit() (such as flushing buffered logs or deleting
    # temp files). Why LIFO? Later resources often depend on earlier ones, so
    # tearing down in reverse setup order prevents use-after-close errors.
    #
    # If a registered callback turns out to be unnecessary later,
    # atexit.unregister(fn) removes it. Keep two hard limits in mind: atexit
    # hooks do NOT run if a process is killed abruptly with os._exit() or an
    # uncatchable SIGKILL.

    def starter_hook(tag: str) -> None:
        print(f"Starter atexit hook ran: {tag}")

    atexit.register(starter_hook, "baseline")

    # Define def cleanup_hook(label: str) -> None: printing
    # f"atexit cleanup: {label}". Register "first" and "second" via
    # atexit.register(cleanup_hook, ...), plus a temporary hook that you remove
    # immediately with atexit.unregister(...), so when main() exits you observe
    # "second" running BEFORE "first" and the unregistered hook staying silent.


def cooperative_signal_handler_and_restore() -> None:

    # Unlike C signal handlers that can fire on arbitrary OS stacks, CPython
    # catches OS signals at the C layer, sets a pending flag, and invokes your
    # Python signal.signal(sig, handler) callback on the main thread between
    # bytecode instructions.
    #
    # Even on the main thread, a signal can interrupt normal code AT ANY LINE—
    # including while the main thread is holding a threading.Lock or an internal
    # sys.stdout stream lock inside print()!
    #
    #     Suppose the main thread is inside print() holding stdout's lock:
    #         SIGINT arrives -> Python runs your signal handler immediately ->
    #         if your handler calls print() or lock.acquire(), it tries to
    #         acquire the lock already held by the paused main frame -> DEADLOCK!
    #
    # Therefore, NEVER acquire locks, perform blocking I/O, or run heavy cleanup
    # inside a signal handler. Instead, flip a lightweight boolean flag (such as
    # controller.stop_requested = True) so the main loop finishes its current
    # unit of work and tears down cleanly outside the handler. Always save
    # prev = signal.getsignal(sig) and restore it inside finally:.

    previous_sigint = signal.getsignal(signal.SIGINT)
    print(f"Starter saved SIGINT handler: {previous_sigint!r}")

    # Define class ShutdownController: with:
    # - __init__(self) -> None: sets self.stop_requested: bool = False and
    #   self.received_signals: list[int] = [].
    # - handle_signal(self, signum: int, _frame: FrameType | None) -> None:
    #   sets self.stop_requested = True and appends signum to
    #   self.received_signals (zero locks, zero print() calls inside!).


    # Instantiate controller = ShutdownController(), install
    # signal.signal(signal.SIGINT, controller.handle_signal), and wrap a
    # for step in range(5): loop inside try ... finally: signal.signal(signal.SIGINT, previous_sigint).
    # Check if controller.stop_requested: break at the top of each iteration,
    # simulate Ctrl+C safely in-process on step == 2 via
    # signal.raise_signal(signal.SIGINT), and assert
    # controller.received_signals == [signal.SIGINT] and step == 3 (or 2 if
    # checked after raising).


def main() -> None:

    print("=== 1. atexit LIFO cleanup and unregister ===")
    atexit_lifo_cleanup()

    print("\n=== 2. Cooperative signal handler and safe restore ===")
    cooperative_signal_handler_and_restore()


if __name__ == "__main__":
    main()
