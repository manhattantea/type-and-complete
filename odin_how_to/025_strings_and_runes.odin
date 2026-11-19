// odin run 025_strings_and_runes.odin -file

package main

import "core:fmt"

/*
In Odin, a 'string' is a lightweight 16-byte value header (data: [^]u8, len: int)
carrying a pointer and a byte length rather than a null-terminated C array.
Reading len(s) is an O(1) field lookup returning the exact byte count (not the
Unicode character count), and string bytes are immutable so literals can live
safely in read-only memory.

Odin gives you three distinct text types:
'string' is an immutable UTF-8 byte slice, 'rune' is a single 32-bit Unicode
codepoint (such as 'A' or 'Ω'), and 'cstring' is a null-terminated pointer used
strictly at C library boundaries.

This file is split into three small sections called from main at the bottom so
you can read top to bottom and run the program at any point.
*/

string_headers_and_raw_literals :: proc() {

	/*
	Double-quoted strings process escape sequences like '\n' and '\t', whereas
	raw string literals wrapped in backticks treat backslashes literally and
	can span multiple lines without extra escaping—ideal for Windows file paths,
	regular expressions, and embedded multi-line SQL or config blocks.

	Because every 'string' value is just a 16-byte (data, len) descriptor,
	size_of(string) is always 16 bytes on 64-bit targets regardless of whether
	the text is 3 bytes or 3 megabytes long.
	*/

	// Native UTF-8 string and backtick raw string literal starters:

	greeting: string = "Hellope, Odin!"
	raw_hint := `C:\Odin\bin`
	fmt.printfln("greeting = %q (bytes: %v, header: %vB) | raw_hint = %v", greeting, len(greeting), size_of(string), raw_hint)

	// Declare raw_path using a backtick raw string literal for C:\Program Files\Odin
	// and print it with both %v and %#v.


	// Declare a multi-line raw string literal named config_block spanning three
	// lines (such as a small key=value config or SQL query) using backticks,
	// then print both config_block and len(config_block).


	// Try uncommenting the line below to see Odin enforce string immutability at
	// compile time:
	// greeting[0] = 'J'
}

slicing_aliasing_and_transmute :: proc() {

	/*
	Slicing a string with s[start:end] builds a brand-new 16-byte header
	pointing directly into the existing bytes with zero heap allocation and zero
	copying. You can inspect the underlying [^]u8 byte pointer with raw_data(s),
	or reinterpret the string header as a []u8 byte slice with transmute([]u8)s
	(because string and []u8 share the exact same memory layout). Never write
	into a transmuted []u8 backed by a read-only string literal.

	Suppose label := "OdinLang". Taking head := label[0:4] produces "Odin" with
	raw_data(head) == raw_data(label) and len(head) == 4 without allocating.
	*/

	// Inspecting the underlying byte pointer of a starter string:

	base_text := "Systems Programming"
	fmt.printfln("base_text = %q (raw_data: %p)", base_text, raw_data(base_text))

	// Slice the first 7 bytes of base_text (base_text[0:7]) into sub_text.
	// Print sub_text and evaluate raw_data(base_text) == raw_data(sub_text) to
	// confirm both share the exact same starting memory address (zero copy!).


	// Slice tail_text := base_text[8:] and verify raw_data(tail_text) != raw_data(base_text)
	// because tail_text starts 8 bytes further into the same buffer.


	// Reinterpret base_text as a byte slice using raw_bytes := transmute([]u8)base_text
	// Print len(raw_bytes) alongside the first three raw ASCII byte numbers
	// using raw_bytes[:3].
}

runes_utf8_decoding_and_cstring :: proc() {

	/*
	Because len(s) and s[i] operate on raw UTF-8 bytes, multi-byte characters
	take more than 1 byte: suppose text := "Aα🚀". Here 'A' takes 1 byte at
	offset 0, 'α' takes 2 bytes at offset 1, and '🚀' takes 4 bytes at offset 3,
	so len(text) is 7 bytes even though the string holds only 3 characters.

	When you loop with 'for codepoint, byte_idx in text', Odin decodes each
	full UTF-8 'rune' and hands you both the 32-bit codepoint and its starting
	byte offset. For C APIs that expect a trailing '\0', 'cstring' stores a
	null-terminated pointer, and string(c_str) walks until '\0' to build an
	Odin string.
	*/

	// Single 32-bit Unicode rune starter:

	omega_rune: rune = 'Ω'
	fmt.printfln("omega_rune = %c (codepoint: U+%04X, size: %vB)", omega_rune, u32(omega_rune), size_of(rune))

	// Declare utf8_text := "Aα🚀". Print len(utf8_text) (expected: 7 bytes) and
	// its first raw byte utf8_text[0] (expected: 65). Then loop over runes using:
	// for codepoint, byte_idx in utf8_text
	// Count the decoded runes into rune_count, print each byte_idx and
	// codepoint (%c and U+%04X via u32(codepoint)), and compare len(utf8_text)
	// against rune_count afterward.


	// Contrast indexing a multi-byte character directly by byte: print
	// utf8_text[1] as a hex byte ("0x%02X") and verify it is only the leading
	// UTF-8 byte of 'α' rather than a whole character.


	// Declare c_label: cstring = "Hello from C" (string literals are secretly
	// null-terminated in read-only memory so cstring initializes directly).
	// Convert it to an Odin string via odin_label := string(c_label) and print
	// both odin_label and len(odin_label).
}

main :: proc() {

	fmt.println("=== 1. String headers and raw literals ===")
	string_headers_and_raw_literals()

	fmt.println("\n=== 2. Slicing, aliasing, and transmute ===")
	slicing_aliasing_and_transmute()

	fmt.println("\n=== 3. Runes, UTF-8 decoding, and cstring ===")
	runes_utf8_decoding_and_cstring()
}
