# Module for 940_log_search_and_word_freq_lab (run via: python 940_log_search_and_word_freq_lab/main.py)

# Separating presentation (report.py) from file scanning (indexer.py) keeps
# ranking and formatting logic pure and easy to test with in-memory data.
#
# Notice a subtle ranking detail with collections.Counter.most_common(limit):
# Counter.most_common(n) uses heapq.nlargest under the hood when n is small,
# running in O(U log n) rather than sorting the entire vocabulary U, and ties
# preserve insertion order. Whenever you want deterministic alphabetical
# tie-breaking regardless of which file happened to be scanned first, sort
# word_counts.items() with key=lambda pair: (-pair[1], pair[0]):
#
#     Suppose word_counts = Counter({"zebra": 2, "alpha": 2, "beta": 5}).
#     Sorting with key=lambda pair: (-pair[1], pair[0]) yields
#     ("beta", 5), ("alpha", 2), ("zebra", 2) because -2 == -2 breaks ties
#     by "alpha" < "zebra".
#
# When building multi-line reports, append each line to lines: list[str] and
# join once at the end with "\n".join(lines). Because Python str objects are
# immutable, repeated out += line concatenation allocates a growing copy on
# every iteration, whereas "\n".join(lines) computes the final buffer size once.

DEFAULT_TOP_LIMIT: int = 10
MAX_DISPLAY_HITS: int = 20


# Implement deterministic word-frequency ranking. First add
# from collections import Counter and from indexer import WordStat at the top
# of this file, then define:
# def top_words(word_counts: Counter[str], limit: int = DEFAULT_TOP_LIMIT) -> list[WordStat]:
# Guard with if limit <= 0 or not word_counts: return [].
# Sort word_counts.items() using key=lambda pair: (-pair[1], pair[0]), slice
# [:limit], and return [WordStat(word=word, count=count) for word, count in ...].


# Implement the summary formatter. Add from collections.abc import Sequence and
# import SearchHit alongside WordStat from indexer, then define:
# def render_summary(stats: Sequence[WordStat], hits: Sequence[SearchHit]) -> str:
# Build lines: list[str] = [], append f"=== Search Hits ({len(hits)}) ===", and
# format up to MAX_DISPLAY_HITS entries as f"  {hit.filename}:{hit.line_num}: {hit.line_text}"
# (appending a note if additional hits were omitted). Then append a blank line,
# f"=== Top {len(stats)} Words ===", and for rank, stat in enumerate(stats, start=1):
# append f"  {rank:>2}. {stat.word:<18} {stat.count}". Return "\n".join(lines).
