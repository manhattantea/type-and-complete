# python 580_buffer_protocol_and_mmap.py

import mmap
from pathlib import Path
import tempfile


def mmap_file_read_write_and_find() -> None:

    # Calling file.read() on a multi-gigabyte binary file copies the entire
    # file into Python heap memory at once. Memory-mapped I/O (mmap.mmap) asks
    # the OS kernel (CreateFileMapping on Windows, POSIX mmap on Linux/macOS)
    # to map the file's pages directly into your process's virtual address
    # space. The kernel demand-pages 4 KB chunks from disk only as you touch
    # offsets, so you can search and edit random offsets with constant RAM.
    #
    # Calling mmap.mmap(f.fileno(), 0) maps the whole file from byte 0. Notice
    # that mapping a 0-byte empty file with length=0 raises ValueError (Windows
    # forbids zero-length file mappings), and on Windows open handles lock files
    # against deletion, so always close mmap before closing the file! Nesting
    # 'with' blocks handles teardown in exact reverse order:
    #
    #     Suppose records.bin holds b"JOB=001;STAT=WAIT;JOB=002;STAT=WAIT".
    #     Opening with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_WRITE) as mm:
    #     lets mm.find(b"WAIT") return byte offset 13 without allocating a copy,
    #     and mm[13:17] = b"DONE" updates the mapped page in place on disk.

    print("OS virtual page size:", mmap.PAGESIZE, "bytes")

    # Create a deterministic temporary directory using with tempfile.TemporaryDirectory() as tmp_dir:
    # Build bin_path = Path(tmp_dir) / "records.bin" and write initial bytes
    # b"JOB=001;STAT=WAIT;JOB=002;STAT=WAIT" with bin_path.write_bytes(...).


    # Inside the temp-dir block, open with bin_path.open("r+b") as f: and
    # with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_WRITE) as mm:.
    # Locate the first b"WAIT" offset via offset = mm.find(b"WAIT"), overwrite
    # mm[offset : offset + 4] = b"DONE", call mm.flush(), and after exiting both
    # 'with' blocks print bin_path.read_bytes() to confirm disk updated.


def memoryview_zero_copy_and_copy_on_write() -> None:

    # Slicing regular bytes (data[100:200]) allocates and copies a brand-new
    # bytes object every time. Python's Buffer Protocol exposes raw backing
    # memory through memoryview(obj): slicing mv[100:200] creates a zero-copy
    # O(1) view pointing into the exact same OS pages!
    #
    # Pairing memoryview with mmap.ACCESS_COPY gives copy-on-write (COW)
    # semantics: writes modify private RAM pages for your process without ever
    # touching the file on disk (whereas mmap.ACCESS_READ raises TypeError on
    # any write). One strict Windows/CPython rule: you MUST release every
    # exported memoryview (using with memoryview(mm) as mv: or mv.release())
    # BEFORE closing mm, otherwise Python raises BufferError!
    #
    #     Suppose mm is mapped with access=mmap.ACCESS_COPY over b"JOB=001...".
    #     Inside with memoryview(mm) as mv:, header = mv[:7] reads b"JOB=001"
    #     with zero allocation, and writing mm[0:3] = b"MOD" leaves disk untouched.

    sample = bytearray(b"HEADER:PAYLOAD")
    with memoryview(sample) as view:
        print("Zero-copy slice bytes:", bytes(view[:6]))

    # Reopen bin_path from the first section (or a fresh temp file) with "rb"
    # and map it using access=mmap.ACCESS_COPY. Wrap with memoryview(mm) as mv:,
    # slice header = mv[:7], assert bytes(header) == b"JOB=001", write
    # mm[0:3] = b"MOD" in memory, and verify after closing that
    # bin_path.read_bytes() on disk still starts with b"JOB=001".


    # Try uncommenting a deliberate leak in a small test block: bind
    # leaked_mv = memoryview(mm) without a 'with' block or leaked_mv.release()
    # before exiting with mmap.mmap(...) as mm: to observe Python raise
    # BufferError: cannot close exported pointers exist.


def anonymous_arena_and_windows_gotchas() -> None:

    # Passing -1 as the file descriptor to mmap.mmap(-1, size) allocates an
    # anonymous virtual memory mapping backed by OS pages rather than a file
    # on disk. Think of it as reserving a raw scratch arena directly from the
    # virtual memory manager, zero-initialized by the OS on first touch.
    #
    #     Suppose with mmap.mmap(-1, 4096) as anon: reserves one 4 KB page.
    #     Writing anon[:5] = b"ARENA" stores bytes directly in that page, and
    #     closing anon returns the virtual pages to the OS immediately.

    with mmap.mmap(-1, 64) as scratch:
        scratch[:4] = b"INIT"
        print("Anonymous page prefix:", scratch[:4])

    # Open with mmap.mmap(-1, 4096) as anon:, write anon[:5] = b"ARENA", slice
    # anon[4090:4096] = b"TAIL!!", and assert both slices read back intact.


    # Verify the empty-file guard: create empty_path = Path(tmp_dir) / "empty.bin"
    # with empty_path.write_bytes(b""), open it in "rb" mode, and confirm
    # inside try / except ValueError: that mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
    # raises ValueError rather than silently mapping zero bytes.


def main() -> None:

    print("=== 1. mmap File Read/Write and Find ===")
    mmap_file_read_write_and_find()
    print("=== 2. memoryview Zero-Copy and Copy-on-Write ===")
    memoryview_zero_copy_and_copy_on_write()
    print("=== 3. Anonymous Arena and Windows Gotchas ===")
    anonymous_arena_and_windows_gotchas()


if __name__ == "__main__":
    main()
