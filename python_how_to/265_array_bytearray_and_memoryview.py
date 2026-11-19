# python 265_array_bytearray_and_memoryview.py

import array
import sys


def compact_arrays_vs_boxed_lists() -> None:

    # A Python list[int] is wonderfully flexible, yet surprisingly heavy in
    # RAM: the list itself stores a contiguous array of 8-byte PyObject*
    # pointers, and every integer sits in its own boxed heap PyLongObject
    # (28+ bytes each on 64-bit CPython!). Holding 1,000 integers in a list
    # burns ~36+ KB across the container and its boxed items.
    #
    # array.array(typecode, initializer) eliminates per-element boxing by
    # packing raw C primitives back-to-back in one contiguous buffer:
    # - 'b' / 'B': 1-byte signed / unsigned char
    # - 'h' / 'H': 2-byte signed / unsigned short
    # - 'i' / 'I': 4-byte signed / unsigned int
    # - 'q' / 'Q': 8-byte signed / unsigned long long
    # - 'f' / 'd': 4-byte float / 8-byte double
    #
    #     Suppose nums = array.array("i", [10, 20, 30]).
    #     nums.itemsize is 4 bytes, so all 3 integers occupy just 12 contiguous
    #     payload bytes (plus one small array object header).
    #
    # Remember that sys.getsizeof(obj) only measures the top-level object
    # header and pointer buffer: for a list, you must add the size of every
    # element inside it to get its true memory footprint!

    starter_arr = array.array("i", [10, 20, 30])
    print(
        "Starter array:",
        starter_arr.itemsize,
        "bytes/item,",
        sys.getsizeof(starter_arr),
        "total bytes, hex:",
        starter_arr.tobytes().hex(),
    )

    # Compare the real memory footprint of boxed list[int] vs unboxed array:
    # create boxed_nums = list(range(1000)) and
    # compact_nums = array.array("i", range(1000)).
    # Compute boxed_bytes = sys.getsizeof(boxed_nums) + sum(sys.getsizeof(x) for x in boxed_nums)
    # and compact_bytes = sys.getsizeof(compact_nums), then print both byte
    # counts and the compression ratio boxed_bytes / compact_bytes.


    # Serialize and reload unboxed C values via .tobytes() and .frombytes():
    # convert raw_bytes = compact_nums[:4].tobytes(), create an empty
    # reloaded = array.array("i"), call reloaded.frombytes(raw_bytes), and
    # print len(raw_bytes) alongside list(reloaded).


def bytearray_and_zero_copy_memoryview() -> None:

    # Slicing a Python list or bytes object (chunk = data[4:8]) ALWAYS
    # allocates a brand-new copy in memory. When parsing binary packets or
    # processing large buffers, those copies add up fast.
    #
    # memoryview(obj) exposes CPython's buffer protocol directly: wrapping a
    # bytes, bytearray, array.array, or mmap object gives you an Odin/C-style
    # zero-copy view over the exact same backing bytes. Slicing sub = mv[4:8]
    # returns another memoryview pointing into the same buffer, and assigning
    # sub[:] = b"1234" mutates the underlying bytearray in place!
    #
    #     Suppose raw = bytearray(b"ABCDEFGH") and sub = memoryview(raw)[2:6].
    #     Running sub[:] = b"1234" updates raw directly to bytearray(b"AB1234GH")
    #     with zero intermediate byte allocations.
    #
    # Safety lock to know: while ANY memoryview is still alive on a mutable
    # bytearray or array.array, resizing that backing buffer (append/extend)
    # raises BufferError so CPython never reallocates memory out from under
    # active views. Call .release() (or use with memoryview(buf) as mv:) once
    # you finish with the view so resizing is allowed again.

    starter_buf = bytearray(b"hello world")
    with memoryview(starter_buf) as starter_mv:
        print("Starter zero-copy slice:", bytes(starter_mv[:5]))

    # Mutate a bytearray in place through a zero-copy memoryview slice:
    # create raw = bytearray(b"ABCDEFGHIJKLMNOP"), wrap it with
    # mv = memoryview(raw), slice sub = mv[4:8], assign sub[:] = b"1234", and
    # print raw to verify it became bytearray(b'ABCD1234IJKLMNOP') in place.


    # Observe the BufferError resize lock and release it cleanly:
    # while mv and sub are still active, try calling raw.append(33) inside
    # try / except BufferError as err: and print err.
    # Next call sub.release() and mv.release(), call raw.append(33) again
    # (33 is ASCII '!'), and print raw to confirm resizing succeeds afterward.


    # Inspect read-only vs writable memoryviews using .readonly and .toreadonly():
    # wrap an immutable literal with ro_mv = memoryview(b"HEADER") and verify
    # ro_mv.readonly is True. Then wrap a mutable packet = bytearray(b"HEADER")
    # in rw_mv = memoryview(packet), create a read-only view
    # safe_mv = rw_mv.toreadonly(), verify safe_mv.readonly is True, and wrap
    # safe_mv[0] = 88 in try / except TypeError as err: printing err before
    # releasing ro_mv, safe_mv, and rw_mv.


def memoryview_cast_and_typed_reinterpretation() -> None:

    # memoryview.cast(format, shape=...) reinterprets the exact same raw bytes
    # as native C primitives (or even a multi-dimensional grid!) with zero
    # copying or struct unpacking:
    #
    #     Suppose buf = bytearray(8) and u32s = memoryview(buf).cast("I").
    #     Setting u32s[0] = 1 writes the 4-byte unsigned integer directly into
    #     buf[0:4] in host byte order (01000000 on little-endian CPUs).
    #
    # Using a with block (with memoryview(buf).cast("I") as view:) guarantees
    # view.release() runs automatically when the block exits.

    starter_raw = bytearray(8)
    with memoryview(starter_raw).cast("I") as u32_pair:
        u32_pair[0] = 1
    print("Starter cast hex:", starter_raw.hex())

    # Reinterpret a 16-byte buffer as four mutable 32-bit unsigned integers:
    # allocate buf = bytearray(16) and open
    # with memoryview(buf).cast("I") as int_view:
    # Assign int_view[0] = 0x12345678, int_view[1] = 0xDEADBEEF,
    # int_view[2] = 1, and int_view[3] = 42, then print list(int_view) and
    # buf.hex() to inspect the native byte order laid down inside buf.


    # View a flat array.array("f") as a zero-copy 2x3 matrix with shape=(2, 3):
    # create floats = array.array("f", [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]) and open
    # with memoryview(floats).cast("f", shape=(2, 3)) as grid:
    # Print grid[0, 2] and grid[1, 0], update grid[1, 2] = 99.0, and afterward
    # print list(floats) to prove the original flat array changed in place.


    # Compare zero-copy slices directly without converting back to bytes:
    # given frame = bytearray(b"SYNC\x01\x02PAYLOAD"), open
    # with memoryview(frame) as view: and check view[:4] == b"SYNC" and
    # view[6:] == b"PAYLOAD" (both return True with zero slice copies!).


def main() -> None:

    print("=== 1. Compact array.array vs boxed list[int] ===")
    compact_arrays_vs_boxed_lists()

    print("\n=== 2. bytearray and zero-copy memoryview slices ===")
    bytearray_and_zero_copy_memoryview()

    print("\n=== 3. memoryview.cast() typed reinterpretation ===")
    memoryview_cast_and_typed_reinterpretation()


if __name__ == "__main__":
    main()
