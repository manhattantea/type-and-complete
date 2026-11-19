# python 025_operators_floor_div_and_walrus.py


def true_vs_floor_division_and_modulo() -> None:

    # Python separates division into two operators with completely different
    # contracts:
    # - '/' (true division) ALWAYS returns a float, even when the numbers divide
    #   evenly (8 / 2 evaluates to 4.0, not 4).
    # - '//' (floor division) rounds down toward NEGATIVE infinity, NOT toward
    #   zero! In C, Java, or Odin, -7 / 3 truncates toward zero (-2). In Python,
    #   -7 // 3 evaluates to -3 because floor(-2.333...) is -3.
    #
    # That choice makes Python's modulo operator '%' unusually clean. Python
    # guarantees the invariant (a // b) * b + (a % b) == a, which forces a % b
    # to carry the same sign as the divisor b:
    #
    #     Suppose you step backward in a circular ring buffer of capacity 8:
    #     From index 0, (0 - 1) % 8 evaluates straight to 7!
    #     Because -1 // 8 == -1 and -1 * 8 + 7 == -1, negative wraparound works
    #     automatically without extra if idx < 0: idx += capacity guards.
    #
    # Built-in divmod(a, b) computes both (a // b, a % b) in one step.

    print("8 / 2 =", 8 / 2, "| 8 // 2 =", 8 // 2, "| -7 // 3 =", -7 // 3, "| -7 % 3 =", -7 % 3)

    # Print divmod(-7, 3) and verify the invariant
    # (-7 // 3) * 3 + (-7 % 3) == -7.
    # Also test positive vs negative divisors: print 7 // -3 and 7 % -3.


    # Verify ring-buffer wraparound for capacity = 8:
    # print (0 - 1) % capacity (7), (0 - 9) % capacity (7), and
    # (7 + 1) % capacity (0).


def powers_and_bitwise_flags() -> None:

    # Exponentiation uses the power operator (2 ** 10 == 1024). When you need
    # modular exponentiation like (base ** exp) % mod (common in hashing and
    # cryptography), ALWAYS call 3-argument pow(base, exp, mod) instead of
    # building a gigantic intermediate integer first: pow() uses binary
    # exponentiation in O(log exp) time and tiny constant memory!
    #
    # Python supports standard bitwise operators on arbitrary-precision ints:
    # '&' (AND), '|' (OR), '^' (XOR toggle), '<<' (left shift), '>>' (right
    # shift), and '~x' (bitwise NOT). Because Python integers behave like
    # infinite two's-complement bit strings, ~x ALWAYS equals -(x + 1):
    #
    #     Suppose READ = 1 << 0 (1) and WRITE = 1 << 1 (2).
    #     perms = READ | WRITE sets both bits (3).
    #     perms & ~READ clears READ and leaves WRITE (2).

    print("2 ** 10 =", 2 ** 10, "| ~0 =", ~0, "| ~5 =", ~5)

    # Compute mod_result = pow(7, 10_000, 1_000_007) and print it (notice it
    # finishes instantaneously without allocating a massive power of 7).


    # Practice bit-flag operations:
    # define READ = 1 << 0, WRITE = 1 << 1, and EXEC = 1 << 2.
    # Combine perms = READ | WRITE, toggle WRITE off with perms ^= WRITE,
    # enable EXEC with perms |= EXEC, clear READ with perms &= ~READ, and print
    # bin(perms), bool(perms & EXEC), and bool(perms & WRITE).


def walrus_assignment_expressions() -> None:

    # The walrus operator (:=, PEP 572) assigns a value to a variable AND
    # returns that value inside a larger expression. It removes awkward
    # duplicate calls or extra setup lines right before an if or while check.
    #
    # Parentheses are required around (name := expr) inside comparisons because
    # ':=' has very low precedence:
    #
    #     Suppose payload = "abcdef":
    #         if (n := len(payload)) > 5:
    #             print(n)   # binds n = 6, then tests 6 > 5
    #     Without parentheses, n := len(payload) > 5 would bind n to True!

    sample = [10, 20, 30]
    if (size := len(sample)) > 2:
        print(f"Starter walrus check: sample has {size} items")

    # Bind payload = "session-token-123" and write
    # if (n := len(payload)) > 5: to print both payload and n without calling
    # len(payload) a second time.


    # Clean a list of lines using walrus filtering:
    # bind raw_lines = ["  ok  ", "   ", "  done  ", "\t"].
    # Loop over raw_lines, check if (clean := line.strip()):, append each
    # non-empty clean string into results: list[str] = [], and print results.


def main() -> None:

    print("=== 1. True vs floor division and modulo ===")
    true_vs_floor_division_and_modulo()

    print("\n=== 2. Powers and bitwise flags ===")
    powers_and_bitwise_flags()

    print("\n=== 3. Walrus assignment expressions ===")
    walrus_assignment_expressions()


if __name__ == "__main__":
    main()
