# python 610_io_streams_buffering_and_encodings.py

import io
from pathlib import Path
import tempfile


def three_layer_io_and_disk_files() -> None:

    # Whenever you call open() or Path.open(), Python assembles a stack of up to
    # three layered objects from the io module, each with one clear job:
    # - Raw binary layer (io.FileIO): talks directly to the OS file descriptor.
    #   Every .read() or .write() triggers a system call and handles raw bytes.
    # - Buffered binary layer (io.BufferedReader / io.BufferedWriter): wraps
    #   FileIO with an in-memory buffer so small reads and writes batch together
    #   in RAM instead of making a syscall on every byte. Modes "rb" and "wb"
    #   stop right here and yield bytes.
    # - Text layer (io.TextIOWrapper): wraps the buffered binary stream to decode
    #   bytes into Unicode str (or encode str into bytes) AND perform universal
    #   newline translation. Modes "r", "w", "a", and "x" give you this layer.
    #
    # File modes at a glance:
    # - "r" / "rb": read from start; raises FileNotFoundError if missing.
    # - "w" / "wb": create or truncate to zero bytes and write.
    # - "a" / "ab": append to the end without truncating existing data.
    # - "x" / "xb": exclusive creation; fails atomically with FileExistsError if
    #   the file already exists, preventing accidental overwrites.
    #
    # Two subtle Windows traps live inside TextIOWrapper:
    # - Omitting encoding="utf-8" falls back to the OS locale encoding (often
    #   cp1252 on Windows), which crashes on characters like "\u2713" or emoji.
    # - Default newline=None translates every "\n" you write into os.linesep
    #   ("\r\n" on Windows) and converts "\r\n" back to "\n" on read. Passing
    #   newline="" disables newline translation completely (mandatory for csv
    #   files and exact byte-for-byte line endings), while newline="\n" forces LF.
    #
    #     Suppose path = tmp / "log.txt".
    #     Opening with path.open("w", encoding="utf-8", newline="") as f:
    #     and calling f.write("a\nb\n") writes exact bytes b"a\nb\n" on every OS,
    #     even Windows, with zero hidden \r insertion.

    with tempfile.TemporaryDirectory() as probe_str:
        probe = Path(probe_str) / "layers.txt"
        with probe.open("w", encoding="utf-8", newline="") as fh:
            fh.write("layer check\n")
            print("Text wrapper type:", type(fh).__name__, "| inner buffer:", type(fh.buffer).__name__)

    # Open with tempfile.TemporaryDirectory() as tmp_str: and bind tmp = Path(tmp_str).
    # Create target = tmp / "notes.txt" and open it with
    # target.open("w", encoding="utf-8", newline="") as f:
    # Write "status: \u2713\nsecond line\n", close the with block, then verify
    # the exact bytes on disk via target.read_bytes() (confirm there is no b"\r\n"
    # even on Windows) and read it back with target.open("r", encoding="utf-8", newline="").


    # Inside that same TemporaryDirectory block, practice exclusive creation ("x")
    # and append ("a"):
    # - Create lock_file = tmp / "report.txt" using lock_file.open("x", encoding="utf-8").
    #   Write "first entry\n".
    # - Try opening lock_file with mode "x" a second time inside a
    #   try ... except FileExistsError as err: block and print the caught error.
    # - Open lock_file in "a" mode with encoding="utf-8", append "second entry\n",
    #   and print lock_file.read_text(encoding="utf-8").


    # Inspect the binary layer directly on disk: open lock_file with
    # lock_file.open("rb") as bin_fh:, print type(bin_fh).__name__ and
    # type(bin_fh.raw).__name__, then read the first 5 bytes with bin_fh.read(5)
    # and print bin_fh.tell() to see the cursor position.


def in_memory_streams_and_zero_copy_readinto() -> None:

    # io.StringIO and io.BytesIO implement the exact same file-like methods
    # (.read, .write, .seek, .tell, .getvalue) entirely in RAM, letting you test
    # parsers and writers without touching the disk. Remember that writing leaves
    # the stream cursor at the end, so call stream.seek(0) before reading back.
    #
    # For high-throughput binary streaming, calling stream.read(4096) allocates
    # a brand-new immutable bytes object on the heap for every chunk. Calling
    # stream.readinto(buf) instead copies bytes directly into one pre-allocated
    # mutable bytearray and returns the integer count n of bytes read (0 at EOF).
    #
    # Watch one important detail on the final short chunk:
    #
    #     Suppose bio = io.BytesIO(b"ABCDEF") and scratch = bytearray(4).
    #     Pass 1: n = bio.readinto(scratch) -> n is 4, scratch is bytearray(b"ABCD").
    #     Pass 2: n = bio.readinto(scratch) -> n is 2, scratch is bytearray(b"EFCD")!
    #     Notice bytes 2..3 still hold stale "CD" from Pass 1!
    #
    # Wrapping scratch with memoryview(scratch)[:n] creates a zero-copy window
    # exposing only the n freshly read bytes (b"EF"), never the stale tail.

    text_buf = io.StringIO("alpha\nbeta\n")
    print("Starter StringIO lines:", text_buf.read().splitlines())

    # Create bio = io.BytesIO(b"0123456789ABCDEF") and scratch = bytearray(4).
    # Stream bio using while (n := bio.readinto(scratch)) > 0:
    # Slice view = memoryview(scratch)[:n] on each pass and print bytes(view)
    # (expected four chunks: b"0123", b"4567", b"89AB", b"CDEF").


    # Prove the stale-tail hazard on an uneven stream length:
    # create short_bio = io.BytesIO(b"ABCDEF") and reuse a fresh buf = bytearray(4).
    # Loop with while (n := short_bio.readinto(buf)) > 0: and print both
    # bytes(buf) (full buffer showing stale bytes on pass 2) and
    # bytes(memoryview(buf)[:n]) (the exact valid slice).


    # Practice io.StringIO write-then-rewind: create out = io.StringIO(), write
    # three lines with out.write(...), print out.tell(), attempt out.read()
    # before seeking (observe empty string ""), then call out.seek(0) and print
    # out.readlines().


def decoding_errors_and_resilience() -> None:

    # When decoding bytes from untrusted files, sockets, or legacy logs, stray
    # invalid UTF-8 byte sequences (such as 0xFF) will eventually show up.
    # Both bytes.decode(encoding, errors=...) and open(..., errors=...) accept
    # an error handler strategy:
    # - "strict" (default): raises UnicodeDecodeError immediately. Use this for
    #   structured protocols where silent corruption is unacceptable.
    # - "replace": substitutes each invalid byte with the visible Unicode
    #   replacement glyph U+FFFD ("\ufffd"), keeping logs readable while clearly
    #   marking corruption.
    # - "ignore": silently drops invalid bytes (risky because data disappears
    #   with zero trace).
    # - "surrogateescape": maps invalid bytes 0x80..0xFF into lone surrogate
    #   code points U+DC80..U+DCFF so arbitrary OS filenames or byte blobs can
    #   round-trip back to the exact original bytes when re-encoded with
    #   errors="surrogateescape".
    #
    #     Suppose raw = b"ok-\xff-end".
    #     raw.decode("utf-8", errors="replace") produces "ok-\ufffd-end",
    #     whereas raw.decode("utf-8", errors="surrogateescape").encode("utf-8", errors="surrogateescape")
    #     recovers the exact original b"ok-\xff-end".

    valid_bytes = "caf\u00e9".encode("utf-8")
    print("Valid UTF-8 bytes:", valid_bytes, "->", valid_bytes.decode("utf-8"))

    # Decode corrupted = b"Hello \xff World" into decoded_replace using
    # errors="replace" and into decoded_ignore using errors="ignore", then print
    # repr(decoded_replace) and repr(decoded_ignore) side by side.


    # Catch UnicodeDecodeError explicitly on corrupted = b"Hello \xff World"
    # under default errors="strict", printing err.start, err.end, and err.reason.


    # Verify lossless round-tripping with "surrogateescape":
    # decode raw_name = b"report_\x80\xff.bin" with
    # escaped = raw_name.decode("utf-8", errors="surrogateescape"), re-encode
    # recovered = escaped.encode("utf-8", errors="surrogateescape"), and print
    # recovered == raw_name (expected: True).


    # Try uncommenting the line below to trigger an uncaught UnicodeDecodeError:
    # _boom = b"Hello \xff World".decode("utf-8", errors="strict")


def main() -> None:

    print("=== 1. Three-layer I/O stack and disk files ===")
    three_layer_io_and_disk_files()

    print("\n=== 2. In-memory streams and zero-copy readinto ===")
    in_memory_streams_and_zero_copy_readinto()

    print("\n=== 3. Encoding error policies and surrogateescape ===")
    decoding_errors_and_resilience()


if __name__ == "__main__":
    main()
