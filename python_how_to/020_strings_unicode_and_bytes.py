# python 020_strings_unicode_and_bytes.py

SAMPLE_NOTE = """name,score
ada,98
linus,95"""


def literals_escapes_and_raw_strings() -> None:

    # Single quotes ('...') and double quotes ("...") create identical str
    # objects in Python; choose the outer quote that avoids escaping the inner
    # quote. Triple quotes ("""...""") create a multi-line string value that
    # preserves embedded newlines (and any indentation spaces inside it).
    #
    # Inside normal string literals, a backslash starts an escape sequence:
    # - \n inserts a newline, \t inserts a tab, \\ inserts one literal backslash,
    #   and \" or \' inserts a quote without ending the string.
    #
    # Putting 'r' right before the opening quote creates a raw string literal
    # (r"...") that keeps backslashes literal instead of turning \n into a
    # newline. Raw strings are ideal for Windows paths and regular expressions.
    # One lexer quirk to remember: a raw literal cannot end with an odd number
    # of backslashes (r"C:\dir\" fails to parse; write r"C:\dir" + "\\" instead).
    #
    # Suppose you write a Windows path without 'r':
    #     "C:\new\test" quietly turns \n into a newline and \t into a tab!
    #     r"C:\new\test" preserves the exact 11 characters C:\new\test.

    print("Multi-line literal:\n" + SAMPLE_NOTE)

    # Create quote_double = "She said \"hi\"" and quote_single = 'She said "hi"',
    # confirm quote_double == quote_single, and print a tabbed 2-row string
    # "item\tqty\npen\t4" using both print(table) and print(repr(table)).


    # Assign a 3-line triple-quoted string value to query = """...""" inside
    # this function (remember triple quotes here are a real assigned string
    # value, not a comment), then print query and len(query.splitlines()).


    # Compare bad_path = "C:\new\test" against win_path = r"C:\new\test".
    # Print repr(bad_path), len(bad_path), repr(win_path), and len(win_path),
    # then append a trailing backslash cleanly with win_path + "\\".


def cleaning_and_splitting_pipelines() -> None:

    # Because str is immutable, every string method returns a brand-new string
    # (or list/tuple of strings) and leaves the original untouched. Knowing a
    # handful of everyday methods handles most log, CSV, and config parsing:
    # - .strip() trims leading/trailing whitespace (or given chars like "/").
    # - .splitlines() splits on \n, \r\n, or \r without leaving a trailing empty
    #   string when the input ends with a newline.
    # - .split() splits on whitespace runs; .split(sep, maxsplit=1) splits ONLY
    #   on the first separator -- critical when values also contain separators!
    # - sep.join(parts) joins an iterable of strings in one allocation (avoid
    #   building strings with += inside loops).
    # - .replace(old, new), .removeprefix(pre), .removesuffix(suf), and
    #   .partition(sep) (always returns a 3-tuple (before, sep, after) even if
    #   sep is missing).
    #
    # Suppose raw = "url:https://example.com:8080":
    #     raw.split(":") breaks the URL into 4 pieces,
    #     whereas raw.split(":", maxsplit=1) cleanly yields
    #     ["url", "https://example.com:8080"].

    raw_line = "  host:https://example.com:8080  \n"
    key, value = raw_line.strip().split(":", maxsplit=1)
    print("Starter split(maxsplit=1):", key, "->", value)

    # Parse a messy multi-line config block:
    # bind block = "  user = ada  \n  role = admin=lead \n  region = eu  \n".
    # Loop over block.splitlines(), trim each line with .strip(), split with
    # .split("=", maxsplit=1), collect cleaned keys into keys: list[str] = [],
    # print each cleaned key/value pair, and join all keys with ", ".join(keys).


    # Chain everyday URL cleanup methods:
    # bind url = "https://example.com:8080/api/".
    # Strip "https://" with .removeprefix("https://"), strip "/api/" with
    # .removesuffix("/api/"), swap "example.com" for "localhost" with
    # .replace("example.com", "localhost"), and split host and port using
    # .partition(":"), printing each step.


    # Test prefix/suffix matching with tuples:
    # bind files = ["main.py", "notes.txt", "vec.odin", "README.md"] and print
    # every filename where name.endswith((".py", ".odin")).


def searching_casefolding_and_immutability() -> None:

    # Two methods search for a substring and return its starting index:
    # - .find(sub) returns -1 if sub is not found (no exception).
    # - .index(sub) raises ValueError if sub is not found.
    # If you only need a yes/no check, write sub in text instead of comparing
    # .find(sub) != -1.
    #
    # For case-insensitive comparison across international text, prefer
    # .casefold() over .lower(). Casefolding applies full Unicode rules:
    #
    #     Suppose word = "Straße" (German street).
    #     "Straße".lower() stays "straße" (does NOT equal "strasse"),
    #     whereas "Straße".casefold() becomes "strasse" and matches!
    #
    # Finally, str objects are strictly immutable: once created on the heap,
    # individual characters cannot be overwritten via text[0] = "B". To change
    # text, construct a new string via slicing or "".join(...).

    word = "Straße"
    print("lower:", word.lower(), "| casefold:", word.casefold())

    # Compare .find() vs .index() on fruit = "banana":
    # print fruit.find("na"), fruit.find("zz") (-1), fruit.index("na"), and
    # "nan" in fruit.
    #
    # Try uncommenting below to observe ValueError from .index():
    # fruit.index("zz")


    # Verify Unicode case-insensitive matching:
    # print "Straße".lower() == "strasse".lower() (False) alongside
    # "Straße".casefold() == "strasse".casefold() (True).


    # Build an updated copy of greeting = "hello" using "H" + greeting[1:] and
    # print both greeting and the new string to confirm greeting stayed "hello".
    #
    # Try uncommenting below to observe TypeError ('str' object does not support
    # item assignment):
    # greeting[0] = "H"


def unicode_bytes_and_bytearray() -> None:

    # Python 3 enforces a hard boundary between human text (str: immutable
    # sequence of Unicode code points) and raw binary data (bytes / bytearray:
    # sequence of 0..255 byte values). Attempting "hello" + b"world" raises
    # TypeError immediately instead of guessing an encoding.
    #
    # Notice two critical differences across that boundary:
    # - Length: len("Aα🚀") is 3 Unicode code points, whereas
    #   len("Aα🚀".encode("utf-8")) is 7 UTF-8 bytes (1 + 2 + 4 bytes).
    # - Indexing: "Aα🚀"[0] returns a 1-character str ("A"), whereas
    #   b"A"[0] returns an int in 0..255 (65)!
    #
    # Always cross text <-> binary explicitly with .encode("utf-8") and
    # .decode("utf-8"). When decoding untrusted or corrupted binary data, strict
    # .decode("utf-8") raises UnicodeDecodeError; passing errors="replace"
    # swaps invalid byte sequences with the Unicode replacement character U+FFFD
    # instead of crashing.
    #
    # Use ord(ch) / chr(code) to convert between a single character and its
    # integer code point, .hex() / bytes.fromhex(...) for hex wire dumps, and
    # bytearray when you need a mutable byte buffer.

    text = "Aα🚀"
    raw_utf8 = text.encode("utf-8")
    print(f"code points={len(text)}, utf8 bytes={len(raw_utf8)}, hex={raw_utf8.hex()}")

    # Decode raw_utf8 back to text with decoded = raw_utf8.decode("utf-8") and
    # verify decoded == text.
    # Contrast indexing types by printing (text[0], type(text[0]).__name__) next
    # to (raw_utf8[0], type(raw_utf8[0]).__name__).
    # Also print ord("Ω") (937), chr(937) ("Ω"), and bytes.fromhex("dead beef").


    # Handle invalid UTF-8 bytes safely:
    # bind corrupt = b"ok-\xff-end".
    # Print corrupt.decode("utf-8", errors="replace") and
    # corrupt.decode("utf-8", errors="ignore").
    #
    # Try uncommenting below to observe UnicodeDecodeError:
    # corrupt.decode("utf-8")


    # Mutate a binary buffer in place with bytearray:
    # create buf = bytearray(b"hello"), set buf[0] = ord("H"), call
    # buf.append(ord("!")), and print buf alongside bytes(buf).


def main() -> None:

    print("=== 1. Literals, escapes, and raw strings ===")
    literals_escapes_and_raw_strings()

    print("\n=== 2. Cleaning and splitting pipelines ===")
    cleaning_and_splitting_pipelines()

    print("\n=== 3. Searching, casefolding, and immutability ===")
    searching_casefolding_and_immutability()

    print("\n=== 4. Unicode, bytes, and bytearray ===")
    unicode_bytes_and_bytearray()


if __name__ == "__main__":
    main()
