# python 001_first.py

"""First Python script demonstrating print(), f-strings, and __doc__."""


def console_printing() -> None:

    # In Python, print(*objects, sep=" ", end="\n", file=sys.stdout, flush=False)
    # is your everyday output function. You can pass as many values as you want
    # of any type (strings, ints, floats, booleans, None, lists, dicts): print
    # calls str() on each argument, joins them using sep (a space by default),
    # and appends end (a newline by default).
    #
    # Two keyword flags matter in real scripts:
    # - file=sys.stderr sends warnings or errors to standard error instead of
    #   standard output, so redirecting program output to a file will not hide
    #   error messages.
    # - flush=True forces buffered characters onto the screen immediately, which
    #   keeps live progress dots or streaming logs from sitting in a buffer.
    #
    # Suppose you run:
    #     print("HP", 100, True, sep=":", end="!")
    # Python prints "HP:100:True!" with no trailing newline after the '!'.

    print("Hello, Python!")

    # Pass mixed types ("Player", 1, 3.5, True, None, and [10, 20]) to one
    # print() call using sep=" | " and end="!\n".


    # Print an inline loading indicator: loop 3 times calling:
    # print(".", end="", flush=True)
    # Then call print(" done!") afterward so it finishes cleanly on that line.


    # Import sys inside this function (import sys) and send an error message
    # "Warning: low battery" to standard error using file=sys.stderr, then print
    # a normal "Status: OK" line to standard output.


def fstrings_and_hex_formatting() -> None:

    # Putting an 'f' right before a string literal creates an f-string. When we
    # put an f in front of quotes, it means Python evaluates every expression
    # inside curly braces {...} at runtime and drops the result straight into
    # the string. Since Python 3.12 (PEP 701), expressions inside {...} can even
    # reuse the same quote style as the outer f-string, like f"HP: {stats['hp']}"
    # or f"HP: {stats["hp"]}".
    #
    # Suppose name = "Ada" and points = 42. Evaluating:
    #     f"{name} scored {points * 2}"
    # produces the string "Ada scored 84".
    #
    # Adding a colon inside the braces introduces a format spec ({value:spec}):
    # - :,     inserts thousands commas (1234567 -> "1,234,567")
    # - :.2f   fixed decimals (3.14159 -> "3.14")
    # - :.1%   multiplies by 100 and adds % (0.9375 -> "93.8%")
    # - :<12   left-aligns inside 12 spaces; :>8 right-aligns; :^10 centers
    #
    # Hex formatting reference:
    # 0x1234 is an integer literal (== 4660): the 0x prefix plus digits 0-9 and
    # a-f / A-F (case-insensitive). It is only a number; the format spec decides
    # how it is printed. The spec lives after the colon inside the braces:
    #
    #   f"{value:[fill][align][sign][#][0][width][grouping][type]}"
    #
    # Type + flags:
    #   x    lowercase hex            f"{0x1234:x}"        -> "1234"
    #   X    uppercase hex            f"{0xABCD:X}"        -> "ABCD"
    #   #    keep the 0x prefix       f"{0x1234:#x}"       -> "0x1234"
    #   08   zero-pad to width 8      f"{0x1234:08x}"      -> "00001234"
    #   _    group every 4 digits     f"{0x12345678:_x}"   -> "1234_5678"
    #
    # Alignment (needs an explicit width; default for numbers is right):
    #   >    right                    f"{0x1234:>10x}"     -> "      1234"
    #   <    left                     f"{0x1234:<10x}"     -> "1234      "
    #   ^    centre                   f"{0x1234:^10x}"     -> "   1234   "
    #   =    pad after any prefix     f"{0x1234:=#10x}"    -> "0x    1234"
    #   *>   custom fill character    f"{0x1234:*>10x}"    -> "******1234"
    #
    # Watch out: 0 is the fill character, so it combines with the alignment flag
    # rather than replacing it -- the padding just becomes zeros:
    #   f"{0x1234:>08x}"     -> "00001234"   (right, zero-filled)
    #   f"{0x1234:<08x}"     -> "12340000"   (left, zero-filled)
    #   f"{0x1234:^08x}"     -> "00123400"   (centre, zero-filled)

    sample_hex = 0x1234
    print(f"Sample value {sample_hex} in zero-padded hex: {sample_hex:08x}")

    # Bind player_name = "Ada", score = 1234567, and accuracy = 0.9375.
    # Print one summary line using f-string specifiers :, on score and :.1% on
    # accuracy.


    # Print a tiny two-row price table using :<12 for the item name and :>8.2f
    # for the price on ("Widget", 19.5) and ("Cable", 4.25).
    # Then declare stats = {"hp": 95} and print f"HP: {stats["hp"]}" using
    # Python 3.12+ nested double quotes inside a double-quoted f-string.


    # Format address = 0xBEEF and word = 0x12345678 using the hex reference
    # above: print address with :#X, address with :08x, word with :_x, and
    # address centered in 10 characters with :^10x.


def debug_fstrings_and_docstrings() -> None:

    # Inside an f-string, !s calls str() (friendly text for users) while !r
    # calls repr() (exact programmer representation with quotes and escapes).
    # Adding '=' at the end of the expression (f"{expr=}") prints the literal
    # expression text followed by '=' and its repr().
    #
    # Suppose tag = "42" and count = 42. Plain f"{tag}" and f"{count}" both print
    # 42, hiding which one is text! Writing f"{tag!r}" prints '42', while
    # f"{count!r}" prints 42, and f"{count * 2=}" prints count * 2=84.
    #
    # Also keep straight the two comment-like syntaxes in Python:
    # - '#' is a real comment: Python throws it away completely when reading the
    #   file. (Python has no /* ... */ block comment syntax.)
    # - """...""" is a real string literal, NOT a comment! When placed as the very
    #   first statement inside a module, class, or function, Python stores that
    #   string in the object's runtime __doc__ attribute (a docstring). Anywhere
    #   else inside code, a bare """...""" simply creates a string constant and
    #   discards it. Use '#' for explanations and notes.

    sample = "hello\nworld"
    print(f"str={sample} | repr={sample!r}")

    # Declare tag = "42" and count = 42.
    # Print f"{tag!s}", f"{tag!r}", f"{count!r}", f"{tag=}", and f"{count * 2=}".
    print(f"{tag!s}"")

    # Print both module __doc__ and main.__doc__ using debug f-strings:
    # print(f"{__doc__=}") and print(f"{main.__doc__=}")
    # Notice those top-level docstrings stayed alive in memory at runtime!


    # Define a small local function def greet(who: str) -> str: whose first
    # statement is a one-line docstring """Return a short greeting.""" followed
    # by return f"Hi, {who}!" and a '#' comment inside its body. Print
    # greet("Odin") and greet.__doc__ to verify '#' comments never enter __doc__.


def main() -> None:
    """Demonstrate print(), f-strings, and runtime __doc__ attributes."""

    print("=== 1. Console printing ===")
    console_printing()

    print("\n=== 2. F-strings and hex formatting ===")
    fstrings_and_hex_formatting()

    print("\n=== 3. Debug f-strings and __doc__ ===")
    debug_fstrings_and_docstrings()


if __name__ == "__main__":
    main()
