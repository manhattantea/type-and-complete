# python 820_multiprocessing_and_shared_memory.py

from concurrent.futures import ProcessPoolExecutor
from multiprocessing.shared_memory import SharedMemory
import os


def square_value(n: int) -> int:

    # Top-level worker helper: module-level functions can be serialized by
    # pickle as (module_name, qualname) so spawned child processes can import
    # and call them cleanly.
    return n * n


def process_pools_spawn_and_pickling() -> None:

    # Unlike threading, concurrent.futures.ProcessPoolExecutor launches separate
    # OS Python processes. Each child process gets its own virtual address
    # space, its own heap, and its own independent GIL, allowing pure-Python CPU
    # loops to scale across multiple physical CPU cores.
    #
    # Multiprocessing introduces two rules you must respect every time:
    # - Mandatory if __name__ == "__main__": guard: on Windows and macOS, Python
    #   starts worker processes using the "spawn" start method. Every child
    #   starts a fresh interpreter and re-imports your script from top to bottom
    #   to find the target function! Calling ProcessPoolExecutor at module top
    #   level without that guard triggers an infinite recursive spawn storm
    #   until Python aborts with RuntimeError.
    # - pickle serialization rules and cost: every argument and return value
    #   crossing processes is serialized with pickle over OS pipes. Anonymous
    #   lambdas, nested closures, and open sockets cannot be pickled
    #   (PicklingError), so worker functions MUST live at module top level. And
    #   if each item takes only microseconds, pickling one item at a time costs
    #   more than the math—batch work using pool.map(fn, items, chunksize=...).
    #
    #     Suppose workloads = [100_000, 200_000, 300_000, 400_000]:
    #         Parent process (PID 4100) pickles each integer to 2 child workers
    #         (e.g. PID 4108 and PID 4112). Each child runs sum_of_squares on
    #         its own CPU core and pickles back only the resulting integer!

    print(
        f"Parent PID={os.getpid()}, executor={ProcessPoolExecutor.__name__}, "
        f"starter square_value(7)={square_value(7)}"
    )

    # Define a top-level CPU worker def sum_of_squares(n: int) -> int: near
    # square_value above returning sum(i * i for i in range(n)).
    # Then here, bind workloads = [100_000, 200_000, 300_000, 400_000], open
    # with ProcessPoolExecutor(max_workers=2) as pool:, compute
    # results = list(pool.map(sum_of_squares, workloads)), and print results.


    # Prove child tasks genuinely run in separate OS processes:
    # Add a top-level def tag_with_pid(item: int) -> tuple[int, int]: returning
    # (os.getpid(), item * item). Run list(pool.map(tag_with_pid, range(6)))
    # inside ProcessPoolExecutor(max_workers=2), collect the unique worker PIDs,
    # and assert os.getpid() not in worker_pids.


    # Compare chunksize=1 vs chunksize=500 for many tiny tasks:
    # Import time inside this function, then inside one
    # with ProcessPoolExecutor(max_workers=2) as pool: time
    # list(pool.map(square_value, range(4_000), chunksize=1)) against
    # list(pool.map(square_value, range(4_000), chunksize=500)) using
    # time.perf_counter(), and print both durations to see IPC batching win.


    # Observe why lambdas and nested closures fail across process boundaries:
    # Inside with ProcessPoolExecutor(max_workers=1) as pool:, wrap
    # pool.submit(lambda k: k * k, 5).result() in try ... except Exception as err:
    # and print type(err).__name__ and err to confirm why workers must be
    # top-level named functions.


def shared_memory_zero_copy_ipc() -> None:

    # When child processes share large numeric buffers or images, sending
    # megabytes through pickle copies every byte multiple times.
    # SharedMemory(create=True, size=N) allocates an OS-named shared memory
    # segment exposed as shm.buf (a raw memoryview over N bytes). Another handle
    # or child process attaches to the exact same physical pages via
    # SharedMemory(name=shm.name) with zero copying!
    #
    # Two strict resource-lifetime rules prevent crashes and leaked OS memory:
    # - Release every cast or sliced memoryview BEFORE calling shm.close()!
    #   If you create view = shm.buf.cast("i") and call shm.close() while view
    #   is still alive, CPython raises BufferError: cannot close exported
    #   pointers exist. Always call view.release() (or del view) first.
    # - Always call .close() on EVERY handle and .unlink() ONCE on the creator
    #   handle inside finally:. On POSIX, .unlink() deletes the /dev/shm file
    #   entry; on Windows, the kernel frees the mapping once all handles close
    #   and .unlink() is a safe no-op.
    #
    #     Suppose handle A creates 32 bytes (8 C ints) and casts ints = shm.buf.cast("i"),
    #     and handle B opens SharedMemory(name=shm.name) and writes b_ints[0] = 999:
    #         ints[0] immediately reads 999 with zero pickle calls and zero copies!

    starter_shm = SharedMemory(create=True, size=8)
    try:
        starter_shm.buf[0] = 42
        print(f"Starter SharedMemory {starter_shm.name!r}: byte 0 = {starter_shm.buf[0]}")
    finally:
        starter_shm.close()
        starter_shm.unlink()

    # Demonstrate zero-copy mutation between two handles in one process:
    # Allocate shm = SharedMemory(create=True, size=32) (8 C ints at 4 bytes
    # each) wrapped in try ... finally:.
    # Inside try:, cast ints = shm.buf.cast("i"), populate
    # for i in range(8): ints[i] = (i + 1) * 10, attach a second handle
    # attached = SharedMemory(name=shm.name), cast attached_ints = attached.buf.cast("i"),
    # write attached_ints[0] = 999, assert ints[0] == 999, and print list(ints).
    # Inside finally:, release attached_ints and ints BEFORE calling
    # attached.close(), shm.close(), and shm.unlink().


    # Mutate SharedMemory from a separate worker process:
    # Define a top-level function def double_shared_ints(shm_name: str, count: int) -> int:
    # that attaches SharedMemory(name=shm_name), casts view = worker_shm.buf.cast("i"),
    # doubles view[i] *= 2 for i in range(count), computes total = sum(view[:count]),
    # releases view, calls worker_shm.close() (never .unlink() in a worker!),
    # and returns total.
    # Allocate a creator SharedMemory(create=True, size=32), fill [1..8], pass
    # (shm.name, 8) to ProcessPoolExecutor(max_workers=1), and assert the parent
    # sees [2, 4, 6, 8, 10, 12, 14, 16] zero-copy before closing and unlinking!


    # Trigger the exported-buffer lifetime error on purpose to recognize it:
    # Create a tiny SharedMemory(create=True, size=16), keep view = tmp.buf.cast("i")
    # alive, call tmp.close() inside try ... except BufferError as err: to print
    # the exact error message, then release view and close + unlink in finally:.


def main() -> None:

    print("=== 1. ProcessPoolExecutor, spawn guard, and pickling ===")
    process_pools_spawn_and_pickling()

    print("\n=== 2. Zero-copy IPC with SharedMemory ===")
    shared_memory_zero_copy_ipc()


if __name__ == "__main__":
    main()
