# python 940_log_search_and_word_freq_lab/main.py

# This Lab combines three focused modules into a small analytics pipeline:
# - Streaming directory traversal (pathlib.Path.rglob + line-by-line file
#   iteration) and pre-compiled regex tokenization (WORD_RE.finditer) in indexer.py.
# - Deterministic frequency ranking and formatted summary output in report.py.
# - CLI argument handling and SAMPLE_CORPUS fallback orchestration here in main.py.
#
# Notice how running python 940_log_search_and_word_freq_lab/main.py places
# 940_log_search_and_word_freq_lab/ on sys.path[0] automatically, so sibling
# imports like from indexer import ... and from report import ... resolve
# regardless of which working directory you invoke Python from.

from pathlib import Path
import sys

from indexer import SearchHit, WORD_RE
from report import DEFAULT_TOP_LIMIT

SAMPLE_CORPUS: dict[str, str] = {
    "sample_app.log": (
        "2026-11-14 INFO python worker booted in streaming mode\n"
        "2026-11-14 WARN slow query on python index cache\n"
        "2026-11-14 INFO python worker finished batch\n"
    ),
    "sample_notes.md": (
        "# Streaming Indexer Notes\n"
        "Generators keep memory constant while scanning python logs.\n"
        "Pre-compiled regex patterns avoid repeated cache lookups.\n"
    ),
}


def main() -> None:

    target_dir: Path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("docs")
    query: str = sys.argv[2] if len(sys.argv) > 2 else "python"

    # Starter baseline proving cross-module imports and regex tokenization work:
    first_file = next(iter(SAMPLE_CORPUS))
    first_line = SAMPLE_CORPUS[first_file].splitlines()[0]
    preview_tokens = [m.group(0).lower() for m in WORD_RE.finditer(first_line)]
    preview_hit = SearchHit(filename=first_file, line_num=1, line_text=first_line)

    print("=== 940 Log Search & Word Frequency Lab ===")
    print(f"Target dir: {target_dir} | Query: {query!r} | Top limit: {DEFAULT_TOP_LIMIT}")
    print("Starter preview hit:", preview_hit)
    print("Starter preview tokens:", preview_tokens)

    # Wire the directory scan and SAMPLE_CORPUS fallback once indexer.py is ready:
    # import Counter from collections and index_directory, scan_text from indexer,
    # then call word_counts, hits = index_directory(target_dir, "*.md", query).
    # If not word_counts (meaning target_dir does not exist or yielded 0 files),
    # fall back cleanly to SAMPLE_CORPUS by creating word_counts = Counter() and
    # hits: list[SearchHit] = [], then looping for filename, content in SAMPLE_CORPUS.items():
    # and calling hits.extend(scan_text(filename, content, query, word_counts)).

    # Wire ranking, summary output, and invariant checks once report.py is ready:
    # import render_summary and top_words from report, compute
    # stats = top_words(word_counts, limit=DEFAULT_TOP_LIMIT), and format
    # summary = render_summary(stats, hits). Print summary and verify that when
    # running on SAMPLE_CORPUS with query "python", assert word_counts["python"] == 4
    # and assert len(hits) == 4 hold, and print total unique words len(word_counts).


if __name__ == "__main__":
    main()
