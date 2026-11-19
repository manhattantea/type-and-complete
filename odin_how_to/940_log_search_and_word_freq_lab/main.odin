// odin run 940_log_search_and_word_freq_lab

package main

import "core:fmt"
import "core:mem/virtual"
import "core:os"
import "core:path/filepath"
import "core:strings"

/*
Log Search and Word Frequency Indexer Lab (main entry point)

This multi-file Lab separates concerns cleanly across three files in one
package:
- 'main.odin' owns the 'virtual.Arena' lifetime, CLI argument resolution,
  directory traversal ('core:os' + 'core:path/filepath'), and final output.
- 'indexer.odin' owns the shared domain structs ('Word_Stat', 'Search_Result')
  and zero-allocation line/word scanning.
- 'report.odin' owns ranking and deterministic top-N report extraction.

Why a single 'virtual.Arena' in 'main'? Scanning dozens of Markdown files creates
thousands of unique map keys, search hits, and file buffers. Installing the
arena as 'context.allocator' lets every file keep clean, allocator-agnostic code
while 'defer virtual.arena_destroy(&arena)' releases everything in one shot.
*/

SAMPLE_CORPUS :: "Odin arena allocators keep memory simple and fast.\nOdin slices never own memory.\n"

main :: proc() {

	fmt.println("=== 940 Log Search & Word Frequency Lab ===")

	// Boilerplate setup: install a growing virtual.Arena as context.allocator
	// so every map entry, cloned word key, and loaded file buffer is freed in
	// O(1) when main exits.

	arena: virtual.Arena
	if err := virtual.arena_init_growing(&arena); err != .None {
		fmt.eprintfln("Failed to initialize virtual arena: %v", err)
		return
	}
	defer virtual.arena_destroy(&arena)
	context.allocator = virtual.arena_allocator(&arena)

	// Resolve target directory and search query from os.args with clean defaults:

	search_dir := len(os.args) > 1 ? os.args[1] : "../docs/odin"
	query := len(os.args) > 2 ? os.args[2] : "arena"
	probe_path, _ := filepath.join([]string{search_dir, "README.md"}, context.temp_allocator)
	fmt.printfln("Target dir=%q (exists=%v) | query=%q | sample probe=%q (.md=%v)", search_dir, os.exists(search_dir), query, probe_path, strings.has_suffix(probe_path, ".md"))

	// Cross-file starter previews exercising indexer.odin and report.odin:

	preview_line_slicing(SAMPLE_CORPUS)
	starter_stats := [2]Word_Stat{
		{word = "odin", count = 2},
		{word = "arena", count = 3},
	}
	preview_stat_sort(starter_stats[:])
	free_all(context.temp_allocator)

	// Architectural Milestone 1 — Directory traversal with core:os and filepath
	// Declare freq_map: map[string]int and all_hits: [dynamic]Search_Result.
	// Open search_dir via dir_fd, open_err := os.open(search_dir). When open_err
	// succeeds, schedule defer os.close(dir_fd) and read entries with:
	// entries, dir_err := os.read_dir(dir_fd, -1)
	// Iterate over entries: skip directories (!entry.is_dir) and keep only
	// files matching strings.has_suffix(entry.name, ".md"). Build each full path
	// via full_path := filepath.join([]string{search_dir, entry.name}) and read
	// its bytes with os.read_entire_file(full_path).

	// Architectural Milestone 2 — Corpus scanning with graceful sample fallback
	// Track scanned_files := 0. Pass each loaded file's string(data) straight
	// into scan_text_buffer(full_path, string(data), query, &freq_map, &all_hits)
	// and increment scanned_files += 1. If search_dir was missing or yielded
	// scanned_files == 0, fall back seamlessly by calling:
	// scan_text_buffer("sample.txt", SAMPLE_CORPUS, query, &freq_map, &all_hits)

	// Architectural Milestone 3 — Search hit display and top-10 frequency report
	// Loop over all_hits printing "%s:%d: %s" (file, line_num, line_text).
	// Call top := top_n_words(freq_map, 10) and print each rank, count, and word.
	// Call free_all(context.temp_allocator) afterward to discard scratch sorting
	// buffers while preserving arena-owned results for the duration of main.
}
