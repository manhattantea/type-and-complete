# python 800_threads_gil_and_synchronization.py

import sys
import threading
import time


def threads_gil_and_race_conditions() -> None:

    # When you create a threading.Thread, Python asks the operating system for a
    # real kernel thread scheduled preemptively by the OS. Under standard
    # CPython, all threads inside one process share one heap and one Global
    # Interpreter Lock (GIL), which is a single process-wide mutex guarding
    # CPython's object allocator and reference counts (Py_INCREF / Py_DECREF).
    #
    # That single lock splits threaded programs into two opposite behaviors:
    # - Pure-Python CPU loops: only one thread can hold the GIL and run Python
    #   bytecode at a time, so CPU-heavy Python loops serialize across threads
    #   and do not speed up across cores (use ProcessPoolExecutor in Primer 820,
    #   or a free-threaded Python 3.13+ build where sys._is_gil_enabled() is
    #   False).
    # - Blocking I/O and cooperative C extensions: calls like time.sleep(),
    #   sockets, disk reads, sqlite3, hashlib, and zlib release the GIL before
    #   waiting and re-acquire it afterward, so waiting threads truly overlap!
    #
    # A very common trap is assuming the GIL makes shared Python state
    # thread-safe. It does not! The GIL only switches between bytecode
    # instructions (roughly every sys.getswitchinterval(), default 5 ms), not
    # around whole Python statements. Look at what self._value += 1 compiles to:
    #
    #     LOAD_ATTR   _value
    #     LOAD_CONST  1
    #     BINARY_OP   +=
    #     STORE_ATTR  _value
    #
    #     Suppose self._value starts at 10 and two threads both run += 1:
    #         Thread A executes LOAD_ATTR and reads 10, then the OS switches.
    #         Thread B reads 10, computes 11, and stores 11.
    #         Thread A resumes with its stale 10, computes 11, and stores 11.
    #     Both increments ran, yet self._value ended at 11 instead of 12!
    #
    # Wrapping every read-modify-write inside with self._lock: forces only one
    # thread into that critical section at a time, and __exit__ always releases
    # the lock even if an exception fires inside the block.

    gil_enabled: bool = getattr(sys, "_is_gil_enabled", lambda: True)()
    print(f"GIL enabled: {gil_enabled} (switch interval: {sys.getswitchinterval():.4f}s)")

    # Prove blocking I/O overlaps across threads even with the GIL enabled:
    # Measure 4 sequential time.sleep(0.04) calls with time.perf_counter(), then
    # spawn 4 threading.Thread(target=time.sleep, args=(0.04,)) threads, call
    # .start() on all 4 before calling .join() on all 4, and print both
    # durations (expected: ~0.16s sequential vs ~0.04s threaded).


    # Observe a real unprotected race condition before fixing it:
    # Create shared = [0] and a helper def bump_unsafe() -> None: that loops
    # 5_000 times reading current = shared[0], calling time.sleep(0) to yield
    # execution to another thread right between load and store, and writing
    # shared[0] = current + 1.
    # Run 4 threads on bump_unsafe, .start() all and .join() all, and print
    # shared[0] vs expected 20_000 to watch lost updates happen live!


    # Now build a thread-safe class SharedCounter: inside this function (or at
    # module scope):
    # - In __init__(self) -> None:, set self._value: int = 0 and
    #   self._lock = threading.Lock().
    # - Add def increment(self) -> None: that updates self._value += 1 inside
    #   with self._lock:.
    # - Add @property def value(self) -> int: that returns self._value inside
    #   with self._lock:.
    # Instantiate counter = SharedCounter(), run 4 threads each calling
    # counter.increment() 5_000 times (even with time.sleep(0) inside the loop),
    # assert counter.value == 20_000, and print the verified total.


def reentrant_locks_and_deadlock_avoidance() -> None:

    # A plain threading.Lock() does NOT remember which thread acquired it. If
    # the SAME thread tries to acquire a plain Lock a second time before
    # releasing it, that thread blocks waiting for itself forever—an instant
    # self-deadlock!
    #
    # When one locked method needs to call another locked method on the same
    # object, use threading.RLock() (re-entrant lock). An RLock records the
    # owning thread ID plus an integer recursion depth counter:
    #
    #     Suppose BankAccount holds self._lock = threading.RLock():
    #         apply_bonus_and_fee() enters with self._lock:   # depth 0 -> 1
    #             calls self.deposit(50) -> with self._lock:  # depth 1 -> 2
    #             leaves deposit()                            # depth 2 -> 1
    #             calls self.withdraw(10) -> with self._lock: # depth 1 -> 2
    #             leaves withdraw()                           # depth 2 -> 1
    #         leaves apply_bonus_and_fee()                    # depth 1 -> 0
    #
    # Other threads stay locked out until depth returns all the way to 0, while
    # the owning thread never deadlocks on nested calls. Notice lock.acquire(blocking=False)
    # asks the lock for immediate entry and returns False instead of waiting if
    # the lock is already held—a safe way to probe lock state without hanging.

    probe_rlock = threading.RLock()
    with probe_rlock:
        with probe_rlock:
            print("Starter RLock re-entry succeeded on the same thread")

    # Contrast non-reentrant Lock behavior safely without hanging this script:
    # Create plain_lock = threading.Lock(), enter with plain_lock:, and call
    # acquired_again = plain_lock.acquire(blocking=False).
    # Print acquired_again (expected: False) and assert not acquired_again.
    #
    # Try uncommenting below to observe a real self-deadlock (press Ctrl+C):
    # with plain_lock:
    #     plain_lock.acquire()


    # Build a re-entrant class BankAccount: protected by self._lock = threading.RLock():
    # - Store self.balance: int = initial_balance in __init__(self, initial_balance: int) -> None:.
    # - Implement def deposit(self, amount: int) -> None: and
    #   def withdraw(self, amount: int) -> None: each guarded by with self._lock:.
    # - Implement def apply_bonus_and_fee(self, bonus: int, fee: int) -> None:
    #   that holds with self._lock: for the whole compound step while calling
    #   self.deposit(bonus) and self.withdraw(fee) inside it.
    # Spawn 4 threads each calling account.apply_bonus_and_fee(15, 5) 500 times
    # on BankAccount(1_000), join all 4, and assert account.balance == 21_000.


def events_barriers_and_thread_local() -> None:

    # Beyond mutual exclusion, threading gives you three lightweight tools for
    # coordinating thread timing and isolating per-thread scratch space:
    # - threading.Event(): a thread-safe boolean latch starting unset (False).
    #   Worker threads sleep cleanly in event.wait(timeout=...) until another
    #   thread calls event.set(), waking every waiter at once. Calling
    #   event.clear() resets the latch back to False.
    # - threading.Barrier(parties): a rendezvous gate where N threads block in
    #   barrier.wait() until all N arrive, then all release together. Notice
    #   barrier.wait() returns a unique integer 0 .. parties - 1 to each thread,
    #   which makes electing one leader thread for a phase summary effortless.
    # - threading.local(): an object whose attributes live in separate per-thread
    #   dictionaries. Two threads writing scratch.tag = "w0" and scratch.tag = "w1"
    #   never overwrite each other and need zero locking.
    #
    #     Suppose 3 threads share start_gate = threading.Event() and
    #     barrier = threading.Barrier(3):
    #         All 3 threads block at start_gate.wait() until main calls start_gate.set().
    #         Each thread runs Phase 1 work, then pauses at slot = barrier.wait().
    #         Nobody enters Phase 2 until all 3 have finished Phase 1!

    ready = threading.Event()
    ready.set()
    print(f"Starter Event is_set={ready.is_set()}, elapsed anchor={time.monotonic():.2f}")

    # Coordinate a 2-phase run across 3 threads with Event, Barrier, and local:
    # Create start_gate = threading.Event(), barrier = threading.Barrier(3),
    # scratch = threading.local(), and phase_log: list[str] = [] guarded by a
    # log_lock = threading.Lock().
    # Define def phased_worker(worker_id: int) -> None: that:
    # - blocks on start_gate.wait()
    # - sets scratch.tag = f"w{worker_id}" and records f"{scratch.tag}:phase1"
    # - calls slot = barrier.wait() so all 3 finish Phase 1 before Phase 2
    # - lets only slot == 0 append "leader:phase2-start", then appends
    #   f"{scratch.tag}:phase2" and prints a completion line.
    # Start all 3 threads, call start_gate.set(), join all 3, and verify every
    # ":phase1" entry appears in phase_log before "leader:phase2-start".


    # Test Event.wait(timeout=...) on an unset latch:
    # Create cancel_flag = threading.Event(), measure elapsed time around
    # woken = cancel_flag.wait(timeout=0.02), assert not woken, and print the
    # timeout result so you confirm wait() returns False cleanly instead of hanging.


def main() -> None:

    print("=== 1. OS threads, GIL, and race conditions ===")
    threads_gil_and_race_conditions()

    print("\n=== 2. Re-entrant locks (RLock) and deadlock avoidance ===")
    reentrant_locks_and_deadlock_avoidance()

    print("\n=== 3. Events, barriers, and thread-local storage ===")
    events_barriers_and_thread_local()


if __name__ == "__main__":
    main()
