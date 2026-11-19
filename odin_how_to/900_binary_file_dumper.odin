// odin run 900_binary_file_dumper.odin -file

package main

import "core:fmt"
import "core:os"

/*
A binary hex dumper is one of the most useful diagnostic tools in systems
programming. Whenever a network packet, binary file header, or UTF-8 string
looks wrong, looking at the raw bytes in hexadecimal alongside a printable
ASCII gutter reveals hidden carriage returns, null terminators, endianness
flips, and alignment padding immediately.

Instead of hardcoding a toy byte array, this capstone reads any file from disk
and renders 16 bytes per row in the classic hex-inspector layout:

    00000000  2f 2f 20 6f 64 69 6e 20  72 75 6e 20 39 30 30 5f  |// odin run 900_|

Read top to bottom across the four milestone sections, or scroll to main at the
bottom to run each section in order.
*/

reading_target_bytes :: proc() {

	/*
	Odin passes command-line arguments to your program through 'os.args', a
	slice of strings ('[]string') where 'os.args[0]' is the executable path and
	'os.args[1:]' holds any extra arguments supplied after '--'. When no path
	is passed, defaulting to the source file itself lets the dumper inspect real
	bytes out of the box.

	When we call 'os.read_entire_file(path)', Odin opens the file, measures its
	size, allocates a '[]u8' slice on the heap, reads every byte into it, and
	returns '(bytes, ok)'. Scheduling 'defer delete(bytes)' on the very next
	line guarantees the buffer is freed no matter where the procedure returns.
	*/

	// Live starter read over this Primer file so you can see the byte count:

	default_path := "900_binary_file_dumper.odin"
	if header_bytes, read_err := os.read_entire_file(default_path, context.allocator); read_err == os.ERROR_NONE {
		defer delete(header_bytes)
		preview_len := min(4, len(header_bytes))
		first_byte := header_bytes[0] if len(header_bytes) > 0 else u8(0)
		fmt.printfln("Read %d bytes from %s (first byte=0x%02x, prefix=%v)", len(header_bytes), default_path, first_byte, header_bytes[:preview_len])
	} else {
		fmt.eprintfln("Could not read default file: %s", default_path)
	}

	// Select a target path from os.args using a ternary expression:
	// target := len(os.args) > 1 ? os.args[1] : "900_binary_file_dumper.odin"
	// Read target with os.read_entire_file(target) into (bytes, ok). If !ok,
	// print an error via fmt.eprintfln and return early; otherwise register
	// defer delete(bytes) and print the total file size in bytes.
}

formatting_hex_rows :: proc() {

	/*
	Displaying a raw buffer 16 bytes at a time requires careful slice bounds.
	Suppose 'data' has 20 bytes total. On the first row, 'offset' is 0 and we
	want indices 0..<16. On the second row, 'offset' is 16, so 'offset + 16'
	would be 32 — way past the end of 'data'! Clamping the upper bound with
	'min(offset + 16, len(data))' turns the final row into 'data[16:20]', a
	clean 4-byte tail slice without ever panicking out of bounds.

	Notice also how each row stays visually aligned even when that final row has
	fewer than 16 bytes: for columns 'col' from 0 up to 15, any column with
	'col < len(row)' prints '%02x ' (two lowercase hex digits plus a space),
	while missing columns print three spaces ("   ") so the right-hand ASCII
	gutter lines up vertically down the entire dump. Adding one extra space
	after column 7 splits the 16-byte row into two readable 8-byte halves.
	*/

	// Here is a compact 6-byte row preview showing 8-digit hex offsets and
	// two-digit zero-padded hex bytes:

	sample := [6]u8{0x2F, 0x2F, 0x20, 0x4F, 0x64, 0x69}
	fmt.printf("%08x  ", 0)
	for b in sample {
		fmt.printf("%02x ", b)
	}
	fmt.println()

	// Write a 16-byte chunk loop over a 20-byte test slice (for example,
	// raw := make([]u8, 20) filled with ASCII bytes and defer delete(raw)) so
	// you test both a full 16-byte row and a short 4-byte trailing row:
	// for offset := 0; offset < len(raw); offset += 16
	// Inside the loop, compute row := raw[offset:min(offset + 16, len(raw))]
	// Print the 8-digit offset with fmt.printf("%08x  ", offset), then loop:
	// for col in 0..<16
	// Print fmt.printf("%02x ", row[col]) when col < len(row), or "   " when
	// col >= len(row), and emit an extra space " " right after col == 7.
}

printing_ascii_gutter :: proc() {

	/*
	Raw binary files are full of control bytes such as 0x00 (NUL), 0x0A (line
	feed), 0x0D (carriage return), or 0x1B (terminal escape). Printing those
	bytes directly as characters scrambles terminal output and ruins column
	alignment.

	In ASCII, printable characters live in one contiguous range from space
	(0x20, or ' ') through tilde (0x7E, or '~'). When we write an inclusive
	range check such as '0x20..=0x7E' (or ' '..='~') in Odin, it tests whether
	a byte is safe to display verbatim. Anything outside that range gets
	replaced by '.' so every byte takes exactly one column inside '|...|'.
	*/

	// Compare a printable byte against a newline byte:

	probe := [2]u8{'A', 0x0A}
	for b in probe {
		display := rune(b) if (b >= ' ' && b <= '~') else '.'
		fmt.printfln("Byte 0x%02x renders in gutter as '%c'", b, display)
	}

	// Complete the ASCII gutter for each row from the previous section:
	// Print " |" before iterating over each byte in row with: for b in row
	// Use a switch or range check on b: when b is in ' '..='~', print
	// rune(b) using fmt.printf("%c", rune(b)); otherwise print ".". Close the
	// row with fmt.println("|").
}

building_the_dumper :: proc() {

	/*
	Putting all three pieces into one reusable procedure turns the script into a
	real tool. Keeping a 'max_rows' parameter with a default value ('max_rows := 16')
	prevents accidentally dumping megabytes of output when inspecting large
	files, while allowing callers to pass a higher limit whenever needed.

	Suppose you invoke the compiled program with a file smaller than 16 bytes,
	or with 'max_rows = 0'. Guarding 'if len(data) == 0 || max_rows <= 0' at the
	top of the procedure returns cleanly before touching any slices or printing
	a blank gutter.
	*/

	// Define a file-scope procedure above main with this exact signature:
	// dump_bytes :: proc(data: []u8, max_rows := 16)
	// Inside dump_bytes, guard empty data or max_rows <= 0, track rows := 0,
	// loop while offset < len(data) && rows < max_rows, slice each 16-byte row,
	// print the %08x offset, 16 hex columns with the mid-row gap after col == 7,
	// and the 16-character |...| ASCII gutter.
	//
	// Wire dump_bytes into main (or right here): read os.args[1] when provided
	// (defaulting to "900_binary_file_dumper.odin"), call dump_bytes(bytes, 12),
	// and test dumping a non-text file by passing an executable via '--':
	// odin run 900_binary_file_dumper.odin -file -- .build/some_binary.exe

	fmt.println("Ready to wire dump_bytes(bytes, 12) over any target file.")
}

main :: proc() {

	fmt.println("=== 1. Reading target file bytes ===")
	reading_target_bytes()

	fmt.println("\n=== 2. Formatting 16-byte hex rows ===")
	formatting_hex_rows()

	fmt.println("\n=== 3. Printable ASCII gutter ===")
	printing_ascii_gutter()

	fmt.println("\n=== 4. Full binary dumper assembly ===")
	building_the_dumper()
}
