// odin run 510_strings_and_strconv.odin -file

package main

import "core:fmt"
import "core:strconv"
import "core:strings"

/*
An Odin 'string' is an immutable 16-byte header holding a data pointer and a
byte length. Because slicing a string only builds a new 16-byte header pointing
into existing bytes, 'core:strings' and 'core:strconv' can split, trim, search,
and parse text with zero heap allocations.

This Primer splits string handling into three sections called from main at the
bottom: zero-allocation iterators versus heap splitting, substring predicates
and slicing, and numeric/hex conversions with 'core:strconv'.
*/

zero_alloc_slicing_and_iterators :: proc() {

	/*
	When we pass '&rem' to 'strings.split_iterator(&rem, ",")', it means
	"scan 'rem' for the next comma, slice out the token before it, and advance
	'rem' past the comma in place". No array is allocated on the heap!

	    Suppose row := "10,20":
	        Pass 1: token = "10", rem becomes "20", ok = true
	        Pass 2: token = "20", rem becomes "",   ok = true
	        Pass 3: token = "",   rem stays "",     ok = false (loop ends)

	For multi-line text, 'strings.split_lines_iterator(&rem)' works the same
	way while automatically stripping both Unix '\n' and Windows '\r\n' endings.
	By contrast, 'strings.split(s, sep)' allocates a '[]string' slice on
	'context.allocator' that you must free with 'defer delete(parts)'.
	*/

	raw_port := "  8080\n"
	port, port_ok := strconv.parse_int(strings.trim_space(raw_port))
	fmt.printfln("Starter trimmed port: %d (ok=%v)", port, port_ok)

	// Tokenize a CSV row without allocating:
	// declare csv_row := " 10, 25, -4, 100 " and total := 0
	// Loop using: for token in strings.split_iterator(&csv_row, ",")
	// Trim each token with strings.trim_space(token), parse via strconv.parse_int,
	// add valid numbers to total, and print total after the loop (expected: 131).


	// Stream lines from mixed LF/CRLF text using strings.split_lines_iterator:
	// declare log_text := "INFO: boot\r\nWARN: slow disk\nERROR: timeout"
	// Loop using: for line in strings.split_lines_iterator(&log_text)
	// Track a line_num counter starting at 1 and print each line with %q to verify
	// that '\r' and '\n' were both stripped cleanly.


	// Compare with heap-allocated splitting:
	// split "red,green,blue" on "," using: parts := strings.split("red,green,blue", ",")
	// Register defer delete(parts) immediately so the allocated []string is freed,
	// then print len(parts) and parts.
}

predicates_and_substring_search :: proc() {

	/*
	Predicates like 'strings.has_prefix', 'strings.has_suffix', and
	'strings.contains' scan bytes in place and return a 'bool'. When you need
	the byte offset of a delimiter so you can slice around it, 'strings.index'
	returns the starting byte index or '-1' if the substring is missing.

	Always guard 'idx >= 0' before slicing 's[:idx]' or 's[idx + 1:]', because
	indexing with '-1' panics at runtime!
	*/

	sample_file := "audio/footstep.wav"
	fmt.printfln("Starter check: %s is wav=%v", sample_file, strings.has_suffix(sample_file, ".wav"))

	// Inspect path := "textures/player_idle.png":
	// check strings.has_prefix(path, "textures/"), strings.has_suffix(path, ".png"),
	// strings.contains(path, "player"), and locate "." via dot_idx := strings.index(path, ".")
	// Print all four results, and when dot_idx >= 0 print the stem path[:dot_idx].


	// Parse "key=value" config lines without heap allocations:
	// declare cfg := "# comment\nhost=127.0.0.1\nport=9000\n"
	// Loop with strings.split_lines_iterator(&cfg), skip empty lines and lines where
	// strings.has_prefix(line, "#") is true, find "=" with eq_idx := strings.index(line, "="),
	// and when eq_idx >= 0 print key := line[:eq_idx] and val := line[eq_idx + 1:].
}

numeric_and_hex_conversions :: proc() {

	/*
	Odin never throws exceptions on bad text input; 'core:strconv' procedures
	return '(value, ok)' tuples so callers handle malformed input explicitly.

	When we pass a base like '16' to 'strconv.parse_u64(s, 16)', it parses bare
	hexadecimal digits like "DEAD_BEEF" or "ff" directly as base-16 without
	needing a "0x" prefix. Passing base '0' lets Odin auto-detect "0x" (hex),
	"0b" (binary), "0o" (octal), or decimal from the text prefix.
	*/

	hex_val, hex_ok := strconv.parse_u64("FF", 16)
	fmt.printfln("Starter hex FF -> %d (ok=%v)", hex_val, hex_ok)

	// Parse hexadecimal strings with strconv.parse_u64:
	// parse "DEADBEEF" with base 16, parse "0x1A2B" with base 0, and try parsing
	// invalid "0xZZ" (expect ok == false). Notice what happens if you pass "0xFF"
	// with base 16 instead of base 0 ('0x' fails when base is locked to 16!).


	// Parse floats and booleans, then format an int into a stack buffer:
	// parse "3.1415" using strconv.parse_f64 and "true" using strconv.parse_bool.
	// Then declare num_buf: [32]u8 and format -4096 with strconv.itoa(num_buf[:], -4096)
	// printing all results.


	// Combine iterators and strconv on a multi-line asset manifest:
	// declare manifest := "sword:0x0010:2.5\nshield:0x002A:4.0\nbad_row:ZZ:1.0"
	// Loop lines with strings.split_lines_iterator(&manifest), split fields on ":"
	// using strings.split_iterator, parse the hex ID with strconv.parse_u64(..., 0)
	// and weight with strconv.parse_f64, skipping rows where any parse returns ok == false.
}

main :: proc() {

	fmt.println("=== 1. Zero-alloc slicing and iterators ===")
	zero_alloc_slicing_and_iterators()

	fmt.println("\n=== 2. Predicates and substring search ===")
	predicates_and_substring_search()

	fmt.println("\n=== 3. Numeric and hex conversions ===")
	numeric_and_hex_conversions()
}
