// Zero-allocation line and ASCII word tokenizer for 940_log_search_and_word_freq_lab

package main

import "core:fmt"
import "core:strings"

/*
File search and word-frequency indexing can easily churn the heap if you split
every line with 'strings.split' or allocate a fresh string for every word token
you inspect. Instead, this module treats each loaded file buffer as read-only
backing storage and walks slices directly inside it.

Notice the ownership split: 'Word_Stat' and 'Search_Result' are plain value
structs shared across all three files in 'package main'. While scanning a file,
each candidate word slice 'token := line[start:end]' points straight into the
existing file buffer with zero allocations. Only when a brand-new unique word
is inserted into 'freq_map' for the very first time do we clone the key with
'strings.clone(token)' so the map owns a stable key on the arena.
*/

Word_Stat :: struct {
	word:  string,
	count: int,
}

Search_Result :: struct {
	file:      string,
	line_num:  int,
	line_text: string,
}

preview_line_slicing :: proc(sample: string) {

	/*
	Calling 'strings.split_iterator(&rem, "\n")' advances 'rem' in place and
	returns a zero-allocation sub-slice for each line until the buffer is
	exhausted. Let us preview the first line of the sample corpus to verify the
	iterator contract before building the full tokenizer.
	*/

	rem := sample
	if first_line, ok := strings.split_iterator(&rem, "\n"); ok {
		fmt.printfln("Indexer preview line 1 (%d bytes): %q", len(first_line), first_line)
	}

	// Architectural Milestone 1 — Zero-allocation line iteration and search hits
	// Define scan_text_buffer at file scope with this exact signature:
	// scan_text_buffer :: proc(filename: string, content: string, query: string, freq_map: ^map[string]int, hits: ^[dynamic]Search_Result)
	// Walk content line by line with: for line in strings.split_iterator(&rem, "\n")
	// Increment line_num += 1 on each line. Whenever len(query) > 0 and
	// strings.contains(line, query) is true, append a Search_Result holding
	// file = filename, line_num = line_num, and line_text = strings.trim_space(line).

	// Architectural Milestone 2 — ASCII word boundary scan without temp allocations
	// Inside the line loop, scan byte index i over 0..<len(line) to locate
	// contiguous ASCII runs where b is 'a'..='z', 'A'..='Z', '0'..='9', or '_'.
	// Suppose a line reads "Odin arena, fast!": byte indices 0..<4 yield "Odin",
	// index 4 (' ') ends the token, and indices 5..<10 yield "arena". Skip
	// single-character tokens (end - start < 2) so punctuation noise is ignored.

	// Architectural Milestone 3 — Deduplicated map key cloning and lifetime safety
	// For each slice token := line[start:end], check whether token in freq_map^:
	// - When token in freq_map^ is true, increment freq_map^[token] += 1 directly
	//   without allocating anything!
	// - When token not_in freq_map^, insert freq_map^[strings.clone(token)] = 1 so
	//   every unique word key is cloned once onto context.allocator (your arena).
	// Notice also why Search_Result.line_text stays valid without cloning when
	// main keeps file buffers alive in the arena until reporting finishes: if
	// main instead freed each file's raw bytes immediately after scanning,
	// line_text would become a dangling slice unless cloned too!
}
