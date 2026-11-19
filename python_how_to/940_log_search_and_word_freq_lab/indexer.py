# Module for 940_log_search_and_word_freq_lab (run via: python 940_log_search_and_word_freq_lab/main.py)

# Why stream log files line-by-line instead of calling Path.read_text()?
# Reading a 500 MB log file with Path.read_text() allocates the entire file
# as a single Python str (up to 4 bytes per code point in UCS-4) before
# splitting it into another list of lines. By contrast, iterating directly over
# an open file object (for line_num, raw_line in enumerate(file_obj, start=1):)
# yields one buffered line at a time as a lazy iterator, keeping peak memory
# proportional to a single line rather than the whole corpus.
#
# Two stdlib performance and safety details matter here:
# - Pre-compiling WORD_RE = re.compile(r"[A-Za-z0-9_']+") at module import time
#   builds the regex state machine once instead of looking up the pattern string
#   in re's 512-entry global cache on every line of a million-line log.
# - Calling WORD_RE.finditer(raw_line) returns a lazy iterator of re.Match
#   objects instead of allocating a temporary list[str] on every line like
#   findall() does:
#
#     Suppose raw_line = "2026-11-14 WARN slow query\n".
#     WORD_RE.finditer(raw_line) yields matches whose .group(0) values are
#     "2026", "11", "14", "WARN", "slow", and "query" one by one with zero
#     intermediate list allocation.
#
# - Opening arbitrary logs with encoding="utf-8", errors="replace" substitutes
#   U+FFFD for stray non-UTF-8 bytes instead of crashing an entire directory
#   scan with UnicodeDecodeError.
# - Normalizing the search string with query.casefold() once before the loop
#   handles Unicode case folding (such as "ß" -> "ss") more consistently than
#   .lower().
#
# SearchHit and WordStat below use @dataclass(slots=True, frozen=True) so
# instances store fields in fixed C-level slots without a per-object __dict__
# and remain immutable across module boundaries.

from dataclasses import dataclass
import re

WORD_RE: re.Pattern[str] = re.compile(r"[A-Za-z0-9_']+")


@dataclass(slots=True, frozen=True)
class SearchHit:
    filename: str
    line_num: int
    line_text: str


@dataclass(slots=True, frozen=True)
class WordStat:
    word: str
    count: int


# Build the shared streaming line scanner so both in-memory text and open files
# share one tokenization and matching loop. First add from collections import Counter
# and from collections.abc import Iterable at the top of this file, then define:
# def _scan_lines(filename: str, lines: Iterable[str], query: str, word_counts: Counter[str]) -> list[SearchHit]:
# Normalize needle = query.casefold() once before the loop if query is non-empty,
# initialize hits: list[SearchHit] = [], and iterate
# for line_num, raw_line in enumerate(lines, start=1):.
# Strip trailing whitespace with clean_line = raw_line.strip(). When needle is
# non-empty and needle in clean_line.casefold(), append
# SearchHit(filename=filename, line_num=line_num, line_text=clean_line) to hits.
# Tokenize each line lazily with for match in WORD_RE.finditer(raw_line):,
# lowercase token = match.group(0).lower(), increment word_counts[token] += 1
# (optionally filtering if len(token) >= 2:), and return hits.


# Add the in-memory text wrapper used by SAMPLE_CORPUS and unit checks:
# def scan_text(filename: str, text: str, query: str, word_counts: Counter[str]) -> list[SearchHit]:
# Delegate directly to _scan_lines(filename, text.splitlines(), query, word_counts)
# so in-memory strings follow the exact same counting and hit-matching rules.


# Add recursive directory streaming. First import Path from pathlib at the top,
# then define:
# def index_directory(root: Path, pattern: str, query: str) -> tuple[Counter[str], list[SearchHit]]:
# Initialize word_counts: Counter[str] = Counter() and all_hits: list[SearchHit] = [].
# Guard with if not root.is_dir(): return (word_counts, all_hits).
# Walk files deterministically via for path in sorted(root.rglob(pattern)):,
# skipping non-files (if not path.is_file(): continue). Open each file with
# with path.open("r", encoding="utf-8", errors="replace") as f:
# and extend all_hits with _scan_lines(str(path), f, query, word_counts) so
# the open file object streams line-by-line, then return (word_counts, all_hits).
