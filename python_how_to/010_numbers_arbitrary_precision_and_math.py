# python 010_numbers_arbitrary_precision_and_math.py

import math
from decimal import Decimal
from fractions import Fraction


def arbitrary_precision_ints_and_bases() -> None:

    # Python has a single integer type (int) and it NEVER overflows like fixed
    # 32-bit or 64-bit integers in C or Odin. When an integer grows beyond a
    # machine word, CPython automatically allocates extra storage so arithmetic
    # remains exact up to available RAM.
    #
    # Integer literals support underscores as visual separators (1_000_000) and
    # base prefixes: 0x for hex (0xDEAD_BEEF), 0b for binary (0b1010_0101), and
    # 0o for octal (0o755). To parse text in another base, pass the base as the
    # second argument to int(text, base).
    #
    # Two handy bit-inspection methods live directly on int:
    # - .bit_length() returns the minimum number of bits needed to represent the
    #   integer's magnitude in binary (excluding sign and leading zeros).
    # - .bit_count() returns how many 1-bits appear in its binary form.
    #
    # Suppose n = 10 (binary 0b1010):
    #     n.bit_length() is 4 and n.bit_count() is 2.

    million = 1_000_000
    print(f"million={million:,}, bit_length={million.bit_length()}")

    # Compute huge_power = 2 ** 128, then print huge_power,
    # huge_power.bit_length() (129), and huge_power.bit_count() (1).
    # Also bind mask = huge_power - 1 and print mask.bit_length() (128) and
    # mask.bit_count() (128).


    # Parse integers from text in hex, binary, and octal:
    # call int("0xFF_00", 16) (65280), int("1010_0101", 2) (165), and
    # int("755", 8) (493), printing each decimal result.


    # Format 255 back into base strings using bin(255), oct(255), and hex(255)
    # and print all three.


def ieee754_floats_and_special_values() -> None:

    # Unlike arbitrary-precision int, Python's float is a C 64-bit IEEE-754
    # double: fast in CPU hardware, bounded around ~1.8e308, and stored as a
    # binary fraction. Just as 1/3 repeats endlessly in base 10 (0.333...), 1/10
    # (0.1) repeats endlessly in base 2, so 0.1 + 0.2 evaluates to
    # 0.30000000000000004 rather than exact 0.3.
    #
    # Use math.isclose(a, b, *, rel_tol=1e-09, abs_tol=0.0) to compare floats
    # with a tolerance. Watch out when comparing a small float against 0.0:
    # relative tolerance multiplies by zero, so you must supply abs_tol (for
    # example abs_tol=1e-9).
    #
    # IEEE-754 also defines three special float values: float("inf"),
    # float("-inf"), and float("nan") (Not a Number). By IEEE-754 rule, nan is
    # never equal to anything -- even itself (nan == nan is False, nan != nan is
    # True). Always test with math.isnan(x), math.isinf(x), and math.isfinite(x).
    #
    # Suppose delta = 1e-12:
    #     math.isclose(delta, 0.0) returns False (abs_tol defaults to 0.0),
    #     while math.isclose(delta, 0.0, abs_tol=1e-9) returns True.

    print("0.1 + 0.2 repr:", repr(0.1 + 0.2), "| isclose:", math.isclose(0.1 + 0.2, 0.3))

    # Print 0.1 + 0.2 == 0.3 (False) alongside math.isclose(0.1 + 0.2, 0.3)
    # (True). Then compare math.isclose(1e-12, 0.0) against
    # math.isclose(1e-12, 0.0, abs_tol=1e-9).


    # Create pos_inf = float("inf"), neg_inf = float("-inf"), and
    # nan = float("nan"). Print nan == nan, nan != nan, math.isnan(nan),
    # math.isinf(pos_inf), math.isfinite(neg_inf), and math.isfinite(3.14).


    # Try uncommenting below to observe OverflowError (int too large to convert
    # to a 64-bit IEEE-754 float):
    # huge_float = float(10 ** 400)


def exact_decimal_and_fraction() -> None:

    # When exact base-10 arithmetic matters (prices, invoices, tax rates), use
    # decimal.Decimal. Always construct Decimal from a string like Decimal("0.1"),
    # NEVER from a binary float like Decimal(0.1) -- passing a float embeds that
    # float's imprecise binary approximation straight into the Decimal!
    #
    # When exact rational arithmetic matters (ratios, music intervals, exact
    # probabilities), fractions.Fraction(num, den) stores a reduced numerator
    # and denominator pair automatically:
    #
    #     Suppose f = Fraction(2, 6).
    #     Python reduces it immediately to Fraction(1, 3), with f.numerator == 1
    #     and f.denominator == 3.

    print("Exact Decimal sum:", Decimal("0.1") + Decimal("0.2"), "| Reduced Fraction:", Fraction(2, 6))

    # Verify Decimal("0.1") + Decimal("0.2") == Decimal("0.3") (True).
    # Then print Decimal("0.1") next to Decimal(0.1) so you see the exact binary
    # rounding noise that leaks in when you pass a float literal to Decimal().


    # Compute total = Fraction(1, 3) + Fraction(1, 6), print total,
    # total.numerator, total.denominator, and float(total). Also parse
    # Fraction("0.25") and verify it equals Fraction(1, 4).


def rounding_and_complex_numbers() -> None:

    # Built-in round(val, ndigits) uses round-half-to-even (banker's rounding),
    # NOT round-half-up! When a value lands halfway between two integers (.5),
    # Python picks the nearest EVEN integer so summing thousands of rounded
    # figures does not systematically drift upward.
    #
    #     Suppose you call round(2.5) and round(3.5):
    #     round(2.5) returns 2 and round(3.5) returns 4 (both even!).
    #
    # Negative ndigits round to powers of 10 (round(1234, -2) -> 1200). When you
    # want explicit directional rounding, reach for math.floor(), math.ceil(),
    # or math.trunc().
    #
    # Python also includes native complex numbers using j for the imaginary unit
    # (for example z = 3 + 4j). Inspect z.real, z.imag, z.conjugate(), and
    # abs(z) (which computes magnitude math.hypot(z.real, z.imag)).

    print("Banker's rounding: round(2.5) =", round(2.5), "| round(3.5) =", round(3.5))

    # Print round(0.5), round(1.5), round(2.5), round(3.5), and round(1234, -2).
    # Then compare math.floor(-2.3), math.ceil(-2.3), and math.trunc(-2.3) to
    # see how each handles negative floats.


    # Bind z = 3 + 4j and print z.real, z.imag, z.conjugate(), and abs(z) (5.0).
    # Also compute (1 + 2j) * (1 - 2j) and print the result (5+0j).


def main() -> None:

    print("=== 1. Arbitrary-precision ints and bases ===")
    arbitrary_precision_ints_and_bases()

    print("\n=== 2. IEEE-754 floats and special values ===")
    ieee754_floats_and_special_values()

    print("\n=== 3. Exact Decimal and Fraction ===")
    exact_decimal_and_fraction()

    print("\n=== 4. Banker's rounding and complex numbers ===")
    rounding_and_complex_numbers()


if __name__ == "__main__":
    main()
