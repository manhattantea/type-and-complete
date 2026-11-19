# python 900_binary_hex_dumper.py

from pathlib import Path
import sys


def memoryview_and_byte_indexing() -> None:

    # Building a hex-and-ASCII file inspector brings together pathlib.Path,
    # zero-copy buffer slicing with memoryview, 16-byte stride iteration,
    # fixed-width hexadecimal formatting, and printable ASCII filtering.
    #
    # A classic hex dump aligns every 16-byte row like this:
    #   00000000  23 20 70 79 74 68 6f 6e  20 39 30 30 5f 62 69 6e  |# python 900_bin|
    #
    # Why wrap raw bytes in memoryview(data) instead of slicing bytes directly?
    # In Python, bytes objects are immutable, so slicing data[offset : offset + 16]
    # allocates and copies a brand-new bytes object on every single row. When we
    # create mv = memoryview(data), Python constructs a lightweight view object
    # pointing into the exact same underlying C buffer via the buffer protocol.
    # Slicing mv[offset : offset + 16] allocates zero payload copies—only a tiny
    # view header referencing the existing memory!
    #
    # Watch out for a classic Python byte-indexing distinction:
    # Indexing a single element out of bytes or memoryview (like row[0]) returns
    # a plain int in 0..255, NOT a 1-byte bytes object (whereas slicing row[0:1]
    # returns a 1-byte view). Because row[col] is already an integer, range checks
    # such as 0x20 <= b <= 0x7E work directly without calling ord(b):
    #
    #     Suppose sample = b"AB\x00~" and mv = memoryview(sample).
    #     mv[0] evaluates to 65 (0x41), mv[2] evaluates to 0, and
    #     0x20 <= mv[3] <= 0x7E is True for '~' (0x7E) and False for '\x00'.
    #
    # Notice also why hex dumpers check 0x20 <= b <= 0x7E instead of calling
    # chr(b).isprintable(): str.isprintable() returns True for multi-column or
    # non-ASCII Unicode code points above 0x7E, whereas a hex dump gutter stays
    # strictly single-column ASCII (' ' through '~') and replaces everything else
    # with '.' so terminal columns never drift.

    probe = memoryview(b"# python")
    print(f"Starter probe: len={len(probe)}, first byte=0x{probe[0]:02x} ({chr(probe[0])})")

    # Inspect byte indexing versus 1-byte slicing on a tiny binary header:
    # bind header = b"\x7fELF\x02\x01\x01\x00Hi!" and mv = memoryview(header).
    # Print mv[0] as both decimal and hex (f"0x{mv[0]:02x}"), and compare it to
    # mv[0:1].tobytes() to observe the int versus bytes difference.
    # Then build ascii_preview = "".join(chr(b) if 0x20 <= b <= 0x7E else "." for b in mv)
    # and print ascii_preview (expected: ".ELF....Hi!").


    # Practice fixed-width padding on a short trailing row before building the
    # full dumper. If the last row of a file has only 5 bytes and you print only
    # 5 hex pairs, the right-hand |...| ASCII gutter shifts leftward out of column.
    # Bind short_row = memoryview(b"Hi!\x00\n") and build a 16-entry list:
    # hex_cols = [f"{short_row[col]:02x}" if col < len(short_row) else "  " for col in range(16)]
    # Split it into two 8-byte halves separated by a visual gap:
    # left_hex = " ".join(hex_cols[:8])
    # right_hex = " ".join(hex_cols[8:])
    # Build gutter = "".join(chr(b) if 0x20 <= b <= 0x7E else "." for b in short_row)
    # and print f"00000000  {left_hex}  {right_hex}  |{gutter}|".


def hex_dump_formatter_and_file_cli() -> None:

    # To dump an entire buffer in 16-byte rows, walk offsets with a step of 16:
    # range(0, len(mv), 16) produces 0, 16, 32, ... lazily without copying data.
    # Slicing past len(mv) clamps automatically in Python, so short final rows
    # never raise IndexError:
    #
    #     Suppose mv has 21 bytes.
    #     Row 0 (offset 0) slices mv[0:16] -> 16 bytes.
    #     Row 1 (offset 16) slices mv[16:32] -> clamped cleanly to the final 5 bytes.
    #     Formatting offset as f"{offset:08x}" pads the address to 8 lowercase hex
    #     digits (00000000, 00000010, ...) matching classic xxd / hexdump output.
    #
    # When reading a file path from sys.argv, pathlib.Path.is_file() checks that
    # the path exists and points to a regular file (not a directory) before calling
    # target.read_bytes(). Writing failure diagnostics to sys.stderr via
    # print(..., file=sys.stderr) keeps error text separate from stdout hex lines.

    target: Path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__)
    preview = target.read_bytes()[:16] if target.is_file() else b""
    print(f"Starter target: {target.name} (previewing first {len(preview)} bytes)")

    # Define def dump_bytes(data: bytes | memoryview, max_rows: int = 16) -> list[str]:
    # inside this function (or at module scope) to format up to max_rows 16-byte rows:
    # - Wrap mv = memoryview(data) and return [] immediately if len(mv) == 0 or max_rows <= 0.
    # - Initialize lines: list[str] = [] and loop with
    #   for row_idx, offset in enumerate(range(0, len(mv), 16)):
    # - Break as soon as row_idx >= max_rows and slice row = mv[offset : offset + 16].
    # - Format offset_str = f"{offset:08x}" and build the 16-column hex_cols list
    #   using f"{row[col]:02x}" when col < len(row) else "  " (two spaces).
    # - Join left_hex = " ".join(hex_cols[:8]) and right_hex = " ".join(hex_cols[8:]).
    # - Build ascii_gutter = "".join(chr(b) if 0x20 <= b <= 0x7E else "." for b in row).
    # - Append f"{offset_str}  {left_hex}  {right_hex}  |{ascii_gutter}|" to lines
    #   and return lines at the end.


    # Guard missing or non-file targets and dump the chosen file:
    # Check if not target.is_file(): and print f"File not found: {target}" to
    # file=sys.stderr, then return early.
    # Otherwise read raw_bytes: bytes = target.read_bytes(), print target.name and
    # len(raw_bytes), call lines = dump_bytes(raw_bytes, max_rows=12), and print
    # each formatted line. (For multi-gigabyte binaries, you could slice or read
    # only the first 4096 bytes instead of loading the entire file at once.)


    # Verify edge cases and zero-copy interior slicing against dump_bytes:
    # - Assert dump_bytes(b"") == [] and dump_bytes(b"ABC", max_rows=0) == [].
    # - Compare the '|' gutter column index of dump_bytes(b"hello")[0].index("|")
    #   against dump_bytes(b"0123456789abcdef")[0].index("|") to prove short trailing
    #   rows keep exact alignment.
    # - Pass memoryview(raw_bytes)[4:68] directly into dump_bytes and print its rows
    #   to inspect an interior byte window without copying a single payload byte.


def main() -> None:

    print("=== 1. Memoryview slicing and byte indexing ===")
    memoryview_and_byte_indexing()

    print("\n=== 2. Hex dump formatter and file CLI ===")
    hex_dump_formatter_and_file_cli()


if __name__ == "__main__":
    main()
