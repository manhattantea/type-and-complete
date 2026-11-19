// Frequency ranking and report builder for 940_log_search_and_word_freq_lab

package main

import "core:fmt"
import "core:mem"
import "core:slice"

/*
Once 'indexer.odin' populates 'map[string]int', the map entries sit in hash
order rather than frequency order. Turning that unsorted histogram into a
top-N leaderboard has three clean stages: collect entries into a temporary
slice, sort with a deterministic comparator, and clone only the top N items
into the caller's allocator so temporary sorting buffers do not pollute the
persistent heap or arena.
*/

compare_word_stats :: proc(a, b: Word_Stat) -> bool {

	if a.count != b.count do return a.count > b.count
	return a.word < b.word
}

preview_stat_sort :: proc(samples: []Word_Stat, allocator: mem.Allocator = context.allocator) {

	/*
	Notice why tie-breaking matters in 'compare_word_stats': suppose "arena" and
	"odin" both appear 3 times. Without checking 'a.word < b.word' when counts
	match, hash iteration order varies across runs and makes test output flaky.
	Cloning into a short-lived slice before calling 'slice.sort_by' keeps the
	caller's input slice unmodified.
	*/

	if len(samples) == 0 do return
	copied := slice.clone(samples, allocator)
	defer delete(copied, allocator)

	slice.sort_by(copied, compare_word_stats)
	fmt.printfln("Report preview top entry: %q (%d)", copied[0].word, copied[0].count)

	// Architectural Milestone 1 — Guard empty inputs and stage into temp memory
	// Define top_n_words at file scope with this exact signature:
	// top_n_words :: proc(freq_map: map[string]int, n: int, allocator: mem.Allocator = context.allocator) -> []Word_Stat
	// Guard len(freq_map) == 0 || n <= 0 cleanly, then collect every (word, count)
	// pair from freq_map into a scratch dynamic array backed by temp memory:
	// items := make([dynamic]Word_Stat, 0, len(freq_map), context.temp_allocator)
	// Appending into context.temp_allocator ensures sorting memory for 10,000
	// unique words vanishes on the next free_all(context.temp_allocator).

	// Architectural Milestone 2 — Deterministic descending sort via slice.sort_by
	// Call slice.sort_by(items[:], compare_word_stats) (or pass an inline
	// comparator proc(a, b: Word_Stat) -> bool) so higher counts come first and
	// equal counts sort alphabetically by a.word < b.word.

	// Architectural Milestone 3 — Slice and clone only the requested top N results
	// Clamp limit := min(n, len(items)) so asking for top 10 on a 3-word corpus
	// never slices out of bounds, then return slice.clone(items[:limit], allocator)
	// so the returned []Word_Stat lives on the caller's chosen allocator.
}
