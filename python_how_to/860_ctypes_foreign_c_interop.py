# python 860_ctypes_foreign_c_interop.py

import ctypes
import sys


def _libc_name() -> str:

    if sys.platform == "win32":
        return "msvcrt"
    if sys.platform == "darwin":
        return "libc.dylib"
    return "libc.so.6"


def loading_libc_and_abi_types() -> None:

    # ctypes dynamically loads C ABI symbols from .dll, .so, or .dylib shared
    # libraries at runtime using libffi—without reading any C header files.
    # Because ctypes has no compile-time knowledge of a foreign function's
    # signature, it assumes by default that EVERY C function accepts arbitrary
    # c_int-like arguments and returns a 32-bit c_int!
    #
    # On 64-bit operating systems, calling a C function that actually returns a
    # 64-bit pointer (char *, void *) or a 64-bit double without setting
    # fn.argtypes and fn.restype silently truncates the upper 32 bits of the
    # return value—producing garbage numbers or an instant segmentation fault.
    #
    #     Suppose libc.strlen returns a 64-bit size_t:
    #         libc.strlen.argtypes = [ctypes.c_char_p]
    #         libc.strlen.restype = ctypes.c_size_t
    #     Now ctypes validates that inputs are bytes (catching accidental str
    #     arguments with ctypes.ArgumentError) and reads the full 64-bit result.
    #
    # Also remember that ctypes.c_char_p maps to NUL-terminated C strings
    # (bytes in Python, NOT str—encode Unicode text to UTF-8 bytes first).

    libc = ctypes.CDLL(_libc_name())
    libc.abs.argtypes = [ctypes.c_int]
    libc.abs.restype = ctypes.c_int
    print(f"Starter libc.abs(-7) = {libc.abs(-7)}")

    # Configure libc.strlen with argtypes = [ctypes.c_char_p] and
    # restype = ctypes.c_size_t, call libc.strlen(b"hello ctypes"), and assert
    # the returned length equals 12.


    # Verify argtypes type safety on C strings:
    # Wrap libc.strlen("not bytes") inside try ... except ctypes.ArgumentError:
    # (passing str instead of bytes) and print the caught error message so you
    # can see ctypes catching the mismatch before calling into C.


    # Load and configure a floating-point C function from libc:
    # Set libc.atof.argtypes = [ctypes.c_char_p] and
    # libc.atof.restype = ctypes.c_double, call libc.atof(b"3.125"), and assert
    # the result equals 3.125.


def c_structs_and_fixed_arrays() -> None:

    # To pass composite data to C, subclass ctypes.Structure and declare a
    # _fields_ list of (field_name, ctype) tuples matching the C struct layout
    # in order. ctypes computes alignment padding automatically to match the
    # platform C ABI.
    #
    # When a C function expects a pointer to a struct (&vec), pass
    # ctypes.byref(inst) instead of ctypes.pointer(inst): byref() builds a
    # lightweight temporary pointer for the call without allocating a full
    # Python pointer wrapper object.
    #
    # Fixed-size C arrays use type multiplication: (ctypes.c_int * 4)(1, 2, 3, 4)
    # allocates one contiguous 16-byte C buffer of four 32-bit integers.

    sample_arr = (ctypes.c_int * 3)(10, 20, 30)
    print(f"Starter C array bytes={ctypes.sizeof(sample_arr)}, items={list(sample_arr)}")

    # Define class CVec2(ctypes.Structure): with
    # _fields_ = [("x", ctypes.c_double), ("y", ctypes.c_double)].
    # Create vec = CVec2(3.0, 4.0), assert ctypes.sizeof(vec) == 16, print
    # vec.x, vec.y, and ctypes.byref(vec), and mutate vec.x = 9.0 in place.


    # Build a fixed-size C byte buffer with ctypes.create_string_buffer(b"odin", 16):
    # Print ctypes.sizeof(buf), buf.value (the NUL-terminated bytes b"odin"), and
    # buf.raw (all 16 bytes including trailing NUL padding).


    # Practice pointer aliasing with ctypes.cast and ctypes.POINTER:
    # Create pair = (ctypes.c_int * 2)(100, 200), obtain
    # ptr = ctypes.cast(pair, ctypes.POINTER(ctypes.c_int)), and verify that
    # ptr[0] == 100 and ptr[1] == 200 reflect live updates when pair[1] = 250.


def c_callbacks_with_cfunctype() -> None:

    # C libraries such as qsort() accept a function pointer callback. In ctypes,
    # ctypes.CFUNCTYPE(restype, *argtypes) generates an executable C trampoline
    # wrapping a Python function so C can call back into Python.
    #
    # Critical GC lifetime rule: you MUST keep a Python reference to the
    # CFUNCTYPE instance for as long as C might invoke it!
    #
    #     Suppose you pass CMP_FUNC(compare_ints) directly as an inline
    #     temporary argument to a C function that stores the callback:
    #         Python drops its last reference right after the call returns, the
    #         garbage collector frees the executable C trampoline, and the next
    #         C callback jumps to freed memory and segfaults!
    #
    # Always bind the trampoline to a variable (comparator = CMP_FUNC(fn)) that
    # stays alive across the entire lifetime of the C usage.

    libc = ctypes.CDLL(_libc_name())
    libc.qsort.restype = None
    print(f"Starter libc.qsort symbol loaded: {libc.qsort}")

    # Sort a 6-element C array in place using C's qsort and a CFUNCTYPE callback:
    # - Create c_arr = (ctypes.c_int * 6)(42, 7, 19, -3, 100, 12).
    # - Define CMP_FUNC = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)).
    # - Define def compare_ints(a, b) -> int: returning (a[0] > b[0]) - (a[0] < b[0])
    #   (using comparisons avoids signed integer overflow on extreme ints).
    # - Keep the trampoline alive in comparator = CMP_FUNC(compare_ints).
    # - Set libc.qsort.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.c_size_t, CMP_FUNC]
    #   and libc.qsort.restype = None.
    # - Call libc.qsort(c_arr, len(c_arr), ctypes.sizeof(ctypes.c_int), comparator)
    #   and assert list(c_arr) == [-3, 7, 12, 19, 42, 100].


    # Reverse the sort order using a second kept-alive trampoline:
    # Define def compare_desc(a, b) -> int: returning (b[0] > a[0]) - (b[0] < a[0]),
    # bind desc_cmp = CMP_FUNC(compare_desc), re-run libc.qsort on c_arr, and
    # assert list(c_arr) == [100, 42, 19, 12, 7, -3].


def main() -> None:

    print("=== 1. Loading libc and configuring argtypes / restype ===")
    loading_libc_and_abi_types()

    print("\n=== 2. C structs, fixed arrays, and byref ===")
    c_structs_and_fixed_arrays()

    print("\n=== 3. C callbacks with CFUNCTYPE and GC lifetime ===")
    c_callbacks_with_cfunctype()


if __name__ == "__main__":
    main()
