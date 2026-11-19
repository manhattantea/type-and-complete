# python -m doctest -v 470_doctest_and_executable_documentation.py

# Executable documentation with Python's standard-library doctest module.
#
# Code examples written in plain comments quietly go stale as signatures change.
# Python's built-in doctest inspects every docstring (__doc__) in a module,
# finds interactive REPL blocks starting with >>> , executes them, and compares
# stdout and tracebacks character-for-character against your documented output.
#
# Both python 470_doctest_and_executable_documentation.py and
# python -m doctest -v 470_doctest_and_executable_documentation.py pass right
# out of the box on the two starter target functions below.

import doctest


def slugify(title: str) -> str:
    """Return a lowercase hyphenated slug for a title.

    >>> slugify("Hello Python")
    'hello-python'
    """

    return title.strip().lower().replace(" ", "-")


def make_marker() -> object:
    """Create a fresh sentinel object whose memory address changes per run.

    >>> make_marker()  # doctest: +ELLIPSIS
    <object object at 0x...>
    """

    return object()


def doctest_syntax_and_target_drills() -> None:

    # Four rules cover almost every real-world doctest inside a triple-quoted
    # docstring (kept in # comments here so doctest does not try to run prose):
    #
    # - Lines starting with >>> run as Python statements, and multi-line blocks
    #   continue with ... on subsequent lines.
    # - Blank lines in expected stdout MUST be written literally as <BLANKLINE>
    #   because an actual empty line ends the doctest block!
    #
    #     Suppose a helper prints "line 1\n\nline 2".
    #     Its doctest expects:
    #         line 1
    #         <BLANKLINE>
    #         line 2
    #
    # - Unpredictable output such as object hex addresses (0x7f...) uses the
    #   directive # doctest: +ELLIPSIS so ... acts as a wildcard (shown on
    #   make_marker above).
    # - Exceptions are verified by writing Traceback (most recent call last):
    #   followed by ... and the final ExceptionType: message line.

    print("Starter targets ->", slugify("Hello Python"), type(make_marker()).__name__)

    # Upgrade slugify(title: str) -> str above so it collapses runs of
    # non-alphanumeric characters into single "-" hyphens, strips leading and
    # trailing "-", and raises ValueError("title must not be empty") if the
    # cleaned result is empty.
    # Extend slugify's triple-quoted docstring with three runnable >>> examples:
    # - slugify("Hello Python World") expecting 'hello-python-world'
    # - slugify("  Modules, Imports & More!  ") expecting 'modules-imports-more'
    # - slugify("   ") expecting Traceback (most recent call last): / ... /
    #   ValueError: title must not be empty


    # Practice <BLANKLINE> matching by writing a module-level function
    # def print_two_sections(top: str, bottom: str) -> None: that prints top,
    # an empty line, and bottom. Give it a triple-quoted docstring with a >>>
    # example using <BLANKLINE> between the two expected output lines.


    # Practice # doctest: +NORMALIZE_WHITESPACE by adding a helper
    # def describe_pairs(n: int) -> list[tuple[int, int]]: returning
    # [(i, i * i) for i in range(n)] and documenting its long output wrapped
    # neatly across two lines in its docstring.


def programmatic_doctest_runner() -> None:

    # You do not have to rely solely on the CLI flag -m doctest. Calling
    # doctest.testmod() from inside Python runs every docstring example in the
    # current module and returns a TestResults(failed=..., attempted=...) tuple
    # you can assert in test suites or CI checks.

    results = doctest.testmod()
    print(f"doctest.testmod() -> failed={results.failed}, attempted={results.attempted}")

    # Assert results.failed == 0 and results.attempted >= 2 right below so
    # running python 470_doctest_and_executable_documentation.py fails loudly
    # whenever a docstring drifts out of sync with the implementation.


    # Re-run doctest.testmod(verbose=True) (or run
    # python -m doctest -v 470_doctest_and_executable_documentation.py in your
    # terminal) to see every single >>> case checked line by line.


    # Failure-diff experiment: temporarily change 'hello-python' in slugify's
    # docstring to 'wrong-slug' and run the file to observe doctest's Expected
    # vs. Got diff output, then restore 'hello-python'.


def main() -> None:

    print("=== 1. Doctest syntax and target functions ===")
    doctest_syntax_and_target_drills()

    print("\n=== 2. Programmatic doctest.testmod() runner ===")
    programmatic_doctest_runner()


if __name__ == "__main__":
    main()
