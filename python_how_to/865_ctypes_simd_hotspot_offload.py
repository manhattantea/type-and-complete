# python 865_ctypes_simd_hotspot_offload.py

from array import array
import ctypes
import operator
from pathlib import Path
import sys


def zero_copy_from_buffer_abi() -> None:

    # You do not have to abandon Python to get bare-metal hardware speed on the
    # 1%-5% of your program that burns CPU cycles: keep orchestration in Python,
    # store hot numeric data in contiguous unboxed buffers (array("f") from
    # Primer 585), and pass raw buffer pointers zero-copy into a compiled C or
    # Odin shared library via ctypes. For end-to-end hybrid trace capture across
    # that Python -> native boundary, see tracy_how_to/800.
    #
    # Calling (ctypes.c_float * len(arr)).from_buffer(arr) builds a C array
    # view pointing directly at arr's existing RAM (arr.buffer_info()[0]) with
    # zero copying. Notice two safety rules:
    # - from_buffer() requires a writable buffer (array, bytearray, writable
    #   memoryview) and raises TypeError on immutable bytes.
    # - Keep the Python arr object alive for as long as the ctypes view or
    #   pointer is in use, because the view borrows arr's memory!
    #
    #     Suppose buf = array("f", [1.0, 2.0, 3.0]):
    #         view = (ctypes.c_float * len(buf)).from_buffer(buf)
    #         view[0] = 99.0   # writes straight into buf's RAM -> buf[0] == 99.0!

    probe = array("f", [1.0, 2.0, 3.0, 4.0])
    print(f"Starter float32 buffer bytes={len(probe) * probe.itemsize}, addr=0x{probe.buffer_info()[0]:x}")

    # Build two contiguous 32-bit float buffers (1_024 elements = 4 KB each):
    # a = array("f", [1.0, 2.0, 3.0, 4.0] * 256)
    # b = array("f", [0.5, 1.5, 2.5, 3.5] * 256)
    # Create zero-copy ctypes views over both buffers:
    # CFloatArray = ctypes.c_float * len(a)
    # c_a = CFloatArray.from_buffer(a)
    # c_b = CFloatArray.from_buffer(b)
    # Assert a.buffer_info()[0] == ctypes.addressof(c_a) (identical RAM pointer!).
    # Save orig = a[0], set c_a[0] = 99.0, assert a[0] == 99.0, then restore
    # c_a[0] = orig.


    # Verify from_buffer() blocks immutable bytes:
    # Call (ctypes.c_ubyte * 4).from_buffer(b"abcd") inside try ... except TypeError:
    # and print the error confirming immutable objects cannot be mutated by C.


def dot_product_native_or_fallback() -> None:

    # When loading an optional native SIMD kernel (such as an Odin DLL built
    # with odin build hotspot_kernel.odin -file -build-mode:dll -o:speed
    # exporting dot_product_simd :: proc "c" (a, b: [^]f32, count: c.size_t) -> f32),
    # always configure .argtypes and .restype immediately after loading the
    # symbol (Primer 860), and keep a pure-Python fallback using map(operator.mul, a, b)
    # so the module still runs cleanly when the compiled .dll/.so is absent.

    lib_name = (
        "hotspot_kernel.dll"
        if sys.platform == "win32"
        else ("libhotspot_kernel.dylib" if sys.platform == "darwin" else "libhotspot_kernel.so")
    )
    kernel_path = Path(__file__).with_name(lib_name)
    print(f"Optional native kernel: {kernel_path.name} (present={kernel_path.exists()})")

    # Define class DotProductKernel: inside or above this function:
    # - __init__(self, lib_path: Path | None = None) -> None: sets
    #   self._lib_path = lib_path and self._fn = None. If lib_path is not None
    #   and lib_path.exists(), loads self._lib = ctypes.CDLL(str(lib_path)),
    #   fetches fn = self._lib.dot_product_simd, configures
    #   fn.argtypes = [ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float), ctypes.c_size_t]
    #   and fn.restype = ctypes.c_float, and saves self._fn = fn.
    # - @property def is_native(self) -> bool: returns self._fn is not None.
    # - dot(self, a: array, b: array) -> float: asserts len(a) == len(b) and
    #   a.typecode == b.typecode == "f". When self.is_native, creates zero-copy
    #   c_a = (ctypes.c_float * len(a)).from_buffer(a) and
    #   c_b = (ctypes.c_float * len(b)).from_buffer(b) (keeping a, b, c_a, c_b
    #   alive across the call!) and returns float(self._fn(c_a, c_b, len(a))).
    #   Otherwise returns float(sum(map(operator.mul, a, b))).


    # Instantiate kernel = DotProductKernel(kernel_path) using the same 1_024
    # element buffers a and b above, compute result = kernel.dot(a, b), assert
    # abs(result - 6400.0) < 1e-3, and print whether execution used
    # "native SIMD" or "pure-Python fallback" along with result.


def main() -> None:

    print("=== 1. Zero-copy ctypes.from_buffer pointer aliasing ===")
    zero_copy_from_buffer_abi()

    print("\n=== 2. 1D dot-product native SIMD offload with fallback ===")
    dot_product_native_or_fallback()


if __name__ == "__main__":
    main()
