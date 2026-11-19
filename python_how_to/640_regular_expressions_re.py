# python 640_regular_expressions_re.py

import re


def raw_strings_and_matching_modes() -> None:

    # Every regex in Python should start with a raw string literal r"...". Without
    # the r prefix, Python's own string parser interprets backslashes before the
    # regex engine ever sees them: "\b" becomes an ASCII backspace byte (0x08)
    # instead of a word boundary, and unrecognized escapes like "\d" trigger a
    # SyntaxWarning in modern Python.
    #
    # Python's re module offers three distinct matching entry points, and mixing
    # them up causes silent validation bugs:
    # - re.search(pat, s) scans anywhere in s and returns the first Match or None.
    # - re.match(pat, s) anchors ONLY at index 0—NOT at the end of the string!
    # - re.fullmatch(pat, s) requires the entire string from start to end to match.
    #
    #     Suppose you validate user input "123abc" with pattern r"\d+":
    #     re.match(r"\d+", "123abc") returns a Match for "123" and silently
    #     ignores "abc", whereas re.fullmatch(r"\d+", "123abc") returns None.

    print("match('123abc'):", bool(re.match(r"\d+", "123abc")), "| fullmatch('123abc'):", bool(re.fullmatch(r"\d+", "123abc")))

    # Validate candidate_ids = ["1042", "1042abc", "ID-1042"] against r"\d+"
    # using both re.match and re.fullmatch, printing each candidate alongside
    # both boolean results to see why fullmatch is mandatory for input checks.


    # Search inside log_line = "err=404 path=/items/99" using re.search(r"\d+", log_line).
    # If the match object m is not None, print m.group(0) and m.span() to see the
    # first number found anywhere in the string.


    # Compare a normal string "\\d+" with a raw string r"\d+" by printing both
    # strings and checking len(r"\b") == 2 vs len("\b") == 1.


def greedy_vs_lazy_and_finditer_spans() -> None:

    # Quantifiers * (zero or more) and + (one or more) are greedy by default:
    # they swallow as many characters as possible while still letting the rest
    # of the pattern succeed. Appending ? (*? or +?) makes a quantifier lazy so
    # it stops at the earliest possible boundary:
    #
    #     Suppose html = "<b>hi</b>" and you search for tags:
    #     re.findall(r"<.*>", html) matches the whole string ["<b>hi</b>"] from
    #     the first < to the final >.
    #     re.findall(r"<.*?>", html) stops at each > and returns ["<b>", "</b>"].
    #
    # When you need match positions as well as text, re.finditer(pat, s) lazily
    # yields Match objects one by one instead of allocating a full list of
    # strings. Each Match exposes .group(0), .start(), .end(), and .span().

    sample_tags = "<b>hi</b>"
    print("Starter greedy vs lazy:", re.findall(r"<.*>", sample_tags), "vs", re.findall(r"<.*?>", sample_tags))

    # Extract every tag from snippet = "<em>warn</em>: <code>E42</code>" using
    # re.finditer(r"<.*?>", snippet). Loop over the yielded Match objects and
    # print m.group(0), m.span(), and snippet[m.start():m.end()] for each hit.


    # Contrast greedy r'".*"' vs lazy r'".*?"' on line = 'a="one" b="two"'
    # with re.findall, printing both results to verify greedy swallows from the
    # first quote all the way to the fourth quote.


    # Try uncommenting the line below to see what happens when a pattern has no
    # matches with re.search vs re.finditer:
    # print("No match:", re.search(r"\d+", "abc"), list(re.finditer(r"\d+", "abc")))


def verbose_patterns_named_groups_and_sub() -> None:

    # Dense one-line regexes quickly turn into unreadable noise. Compiling a
    # pattern with re.compile(..., re.VERBOSE) tells the regex engine to ignore
    # unescaped whitespace and # comments inside a multi-line raw string. If
    # you actually need to match a literal space or # under re.VERBOSE, escape
    # it as \  or \# or put it inside a character class like [ ].
    #
    # Pairing re.VERBOSE with named capture groups (?P<name>...) lets you read
    # extracted fields via m.group("name") or m.groupdict() instead of fragile
    # positional numbers:
    #
    #     Suppose pat = re.compile(r"(?P<user>\w+)@(?P<host>\w+)", re.VERBOSE).
    #     Matching "ada@core" gives m.groupdict() == {"user": "ada", "host": "core"}.
    #
    # Beyond matching, re.sub(pat, repl, s) can accept a callback function
    # def repl(m: re.Match[str]) -> str: that computes each replacement string
    # dynamically from the matched text.

    email_re = re.compile(r"(?P<user>\w+)@(?P<host>\w+)")
    starter_hit = email_re.fullmatch("ada@core")
    print("Starter named groups:", starter_hit.groupdict() if starter_hit else None)

    # Compile LOG_RE = re.compile(..., re.VERBOSE) using a raw string joined across
    # lines or concatenated literals (without triple quotes) to match lines like
    # "[ERROR] code=503 Connection timed out" with named groups:
    # (?P<level>INFO|WARN|ERROR), (?P<code_id>\d+), and (?P<msg>.*). Remember to
    # match the literal space after ] with \s+ or [ ] because re.VERBOSE ignores
    # unescaped spaces. Run m = LOG_RE.fullmatch(sample_line) and print m.groupdict().


    # Define def double_int(m: re.Match[str]) -> str: returning str(int(m.group(0)) * 2),
    # then call re.sub(r"\d+", double_int, "Order 12 has 3 items costing 15 dollars")
    # and print the transformed string.


    # Combine re.finditer with named groups on text = "port=8080 host=127.0.0.1"
    # using r"(?P<key>[a-z]+)=(?P<val>\S+)" and print each match's .group("key"),
    # .group("val"), and .span().


def main() -> None:

    print("=== 1. Raw strings and match vs fullmatch ===")
    raw_strings_and_matching_modes()

    print("\n=== 2. Greedy vs lazy quantifiers and finditer spans ===")
    greedy_vs_lazy_and_finditer_spans()

    print("\n=== 3. re.VERBOSE, named groups, and re.sub callbacks ===")
    verbose_patterns_named_groups_and_sub()


if __name__ == "__main__":
    main()
