# python 530_string_and_bytes_concatenation_perf.py

import io
import time
import tracemalloc


def linear_string_builders() -> None:

    # Both str and bytes are immutable in Python: once allocated, their buffer
    # cannot grow in place. Appending out += chunk inside a loop is conceptually
    # O(N^2) because each step allocates a new buffer of length
    # len(out) + len(chunk) and copies every previous byte across.
    #
    # CPython has a narrow shortcut for str += chunk when ob_refcnt == 1, but it
    # is fragile: keeping any alias (prev = out), storing out in a container,
    # or running on another Python implementation breaks the shortcut and falls
    # back to O(N^2) copying silently.
    #
    # Prefer Python's guaranteed O(N) text builders:
    # - sep.join(parts) does two fast C passes: pass 1 sums exact total length
    #   and Unicode width, pass 2 allocates one buffer and copies every part.
    # - io.StringIO acts as a growable in-memory text stream (like Odin's
    #   strings.Builder), ideal when helpers stream via write() or print(file=buf).
    #
    #     Suppose parts = ["a", "b", "c"].
    #     ",".join(parts) allocates one 5-character string "a,b,c" in O(N).

    rows = [f"user_{i},{i * 10}" for i in range(5)]
    print("Starter row:", rows[0])

    # Collect fragments in parts: list[str] = ["id,score"], call
    # parts.extend(rows), build csv_joined = "\n".join(parts), and print it.


    # Assemble the same text with io.StringIO: open with io.StringIO() as buf:,
    # write "id,score\n", loop over rows calling print(row, file=buf), read
    # csv_stream = buf.getvalue(), and assert csv_stream.rstrip("\n") == csv_joined.


def mutable_binary_builders() -> None:

    # Binary frames face the exact same immutability cost on bytes. Two stdlib
    # tools give guaranteed amortized O(N) binary assembly:
    # - bytearray is genuinely mutable and over-allocates geometrically so
    #   packet.extend(chunk) runs in amortized O(1); freeze with bytes(packet).
    # - io.BytesIO behaves like an in-memory binary file supporting bio.write()
    #   and bio.getvalue() across helper functions.
    # - b"".join(chunks) allocates one exact immutable bytes buffer when all
    #   chunks are already collected.

    header = bytearray(b"HDR:")
    print("Starter binary header:", bytes(header))

    # Given chunks = [b"A1", b"B2", b"C3"], build packet = bytearray(b"HDR:")
    # calling packet.extend(chunk) for each chunk, then freeze to bytes(packet).


    # Build the same packet with b"".join([b"HDR:", *chunks]) and with
    # with io.BytesIO() as bio: writing b"HDR:" and each chunk; assert all three
    # outputs equal b"HDR:A1B2C3".


def bytes_concat_vs_bytearray_allocation_contrast() -> None:

    # Repeated bytes += chunk (especially when another reference exists, or
    # across thousands of chunks) triggers repeated reallocations and full-prefix
    # copies. Appending 2,000 chunks of 64 bytes produces a 128 KiB result, yet
    # quadratic copying moves over 128 MiB of intermediate bytes! By contrast,
    # bytearray.extend() and io.BytesIO.write() copy each byte only a tiny
    # constant number of times.
    #
    #     Suppose chunks = [b"X" * 64 for _ in range(2_000)].
    #     In a naive loop with prev = out; out += chunk, every pass allocates a
    #     bigger bytes object and copies all prior data.
    #     With buf = bytearray(); buf.extend(chunk), growth happens in a handful
    #     of geometric resizes, keeping both time and peak allocation low.

    chunks = [b"X" * 64 for _ in range(2_000)]
    print("Benchmark payload:", len(chunks), "chunks =", len(chunks) * 64, "bytes")

    # Define three builders over chunks:
    # - def build_bytes_slow(items: list[bytes]) -> bytes: looping out = b""
    #   with prev = out; out += item (the alias prevents any in-place shortcut).
    # - def build_bytearray(items: list[bytes]) -> bytes: extending a bytearray
    #   and returning bytes(buf).
    # - def build_bytesio(items: list[bytes]) -> bytes: writing into io.BytesIO
    #   and returning bio.getvalue().
    # Time each one with time.perf_counter_ns(), print elapsed milliseconds, and
    # assert all three return equal 128_000-byte payloads.


    # Now contrast memory allocation peaks with tracemalloc: inside a
    # try / finally: tracemalloc.stop() block, call tracemalloc.start(). Before
    # each of build_bytes_slow, build_bytearray, and build_bytesio, call
    # tracemalloc.reset_peak(), run the builder, read
    # current_bytes, peak_bytes = tracemalloc.get_traced_memory(), and print
    # peak_bytes for each approach to observe how much less churn bytearray and
    # BytesIO produce compared to repeated bytes concatenation.


def main() -> None:

    print("=== 1. Linear string builders: join and StringIO ===")
    linear_string_builders()

    print("\n=== 2. Mutable binary builders: bytearray and BytesIO ===")
    mutable_binary_builders()

    print("\n=== 3. bytes += vs bytearray / BytesIO allocation contrast ===")
    bytes_concat_vs_bytearray_allocation_contrast()


if __name__ == "__main__":
    main()
