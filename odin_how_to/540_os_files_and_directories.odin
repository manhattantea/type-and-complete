// odin run 540_os_files_and_directories.odin -file

package main

import "core:fmt"
import "core:os"
import "core:path/filepath"

/*
Odin separates operating-system file and directory calls ('core:os') from
cross-platform path manipulation ('core:path/filepath').

Reading an entire config or asset file in one shot is convenient, but streaming
a multi-gigabyte log or listing a directory requires explicit OS handles
('os.Handle'). Pairing every open handle or allocated directory listing with
'defer' ensures descriptors and memory are released even on early returns.
*/

whole_file_io_and_cleanup :: proc() {

	/*
	When we call 'os.read_entire_file(path)', Odin opens the file, queries its
	byte size, allocates a matching '[]byte' slice on 'context.allocator', reads
	the bytes, and closes the handle before returning '(data, ok)'.

	    Suppose "note.txt" holds 12 bytes:
	        data, ok := os.read_entire_file("note.txt")
	        if ok {
	            defer delete(data)   // caller owns 'data' and must free it
	            fmt.println(string(data))
	        }

	Use 'os.write_entire_file(path, bytes)' to create or overwrite a file in one
	call, 'os.exists(path)' to probe existence, and 'os.remove(path)' to delete
	temporary files when done.
	*/

	fmt.printfln("Starter check: current directory exists=%v", os.exists("."))

	// Write "Hello from Odin file I/O!\n" to temp_path := "temp_test_note.txt":
	// convert the string literal to bytes with transmute([]u8)payload or
	// transmute([]byte)string("Hello from Odin file I/O!\n"), pass it to
	// os.write_entire_file(temp_path, ...), and register defer os.remove(temp_path)
	// so the file is always deleted when this procedure returns.


	// Verify os.exists(temp_path), read it back via data, ok := os.read_entire_file(temp_path),
	// register defer delete(data) when ok is true, and print string(data).
	// Also try reading "missing_file_123.bin" to confirm ok == false without crashing.
}

chunked_handle_io_and_directories :: proc() {

	/*
	Loading a whole file into RAM breaks down on huge files or partial reads.
	Instead, 'os.open(path)' acquires an OS handle ('os.Handle', plus an
	'os.Error' equal to 'os.ERROR_NONE' on success), and 'os.read(fd, buf[:])'
	fills a caller-supplied stack buffer in fixed chunks with zero heap churn.

	The same handle pattern drives directory listings: open a directory with
	'os.open(".")', call 'entries, err := os.read_dir(dir_handle, -1)' to read
	all entries, and free the returned slice with
	'os.file_info_slice_delete(entries, context.allocator)'.
	*/

	dir_handle, dir_err := os.open(".")
	if dir_err == os.ERROR_NONE {
		defer os.close(dir_handle)
		entries, list_err := os.read_dir(dir_handle, -1, context.allocator)
		if list_err == os.ERROR_NONE {
			defer os.file_info_slice_delete(entries, context.allocator)
			fmt.printfln("Starter dir scan: found %d entries in '.'", len(entries))
		}
	}

	// Stream a file in fixed 64-byte stack chunks using os.open, os.read, and os.close:
	// write ~200 bytes of sample text into chunk_path := "temp_chunks.txt" using
	// os.write_entire_file, open it with fd, open_err := os.open(chunk_path),
	// check open_err == os.ERROR_NONE, and immediately schedule defer os.close(fd).
	// Loop reading into buf: [64]u8 via n, read_err := os.read(fd, buf[:]) while
	// read_err == os.ERROR_NONE && n > 0, print each string(buf[:n]) chunk and
	// accumulate total_bytes += n, then remove chunk_path after closing fd.
	// Note why defer os.close(fd) must run before os.remove(chunk_path): Windows
	// locks open file handles and rejects deleting an unclosed file!


	// Inspect entries from os.read_dir(dir_handle, -1) in detail:
	// loop over entries, print each entry.name, entry.size, and entry.is_dir for
	// the first 5 entries, and count how many entries have ".odin" at the end.
}

cross_platform_path_manipulation :: proc() {

	/*
	Never concatenate file paths with raw "/" or "\\" strings—Windows and POSIX
	use different separators and drive-root rules. 'core:path/filepath' provides:
	- Zero-allocation slice views over the input string: 'filepath.base',
	  'filepath.stem', and 'filepath.ext'.
	- Heap-allocating builders (free with 'defer delete(...)'): 'filepath.dir'
	  and 'filepath.join([]string{...})'.

	    Suppose sample := "odin_how_to/540_os_files_and_directories.odin":
	        filepath.base(sample) -> "540_os_files_and_directories.odin"
	        filepath.stem(sample) -> "540_os_files_and_directories"
	        filepath.ext(sample)  -> ".odin"
	*/

	self_name := filepath.base("odin_how_to/540_os_files_and_directories.odin")
	fmt.printfln("Starter primer base: %s", self_name)

	// Extract all four path parts from sample_path := "odin_how_to/540_os_files_and_directories.odin":
	// dir := filepath.dir(sample_path) (with defer delete(dir)), plus
	// filepath.base(sample_path), filepath.stem(sample_path), and filepath.ext(sample_path).
	// Print all four components clearly.


	// Build a platform-native path using filepath.join:
	// joined := filepath.join([]string{"build", "logs", "session.txt"})
	// Register defer delete(joined), print joined, and verify filepath.stem(joined)
	// and filepath.ext(joined) on the joined result.


	// Synthesis roundtrip: join "." and "temp_roundtrip.dat" with filepath.join,
	// write bytes with os.write_entire_file, open with os.open and verify with os.read
	// into a [32]u8 buffer, close the handle before calling os.remove, and confirm
	// os.exists returns false afterward.
}

main :: proc() {

	fmt.println("=== 1. Whole-file I/O and cleanup ===")
	whole_file_io_and_cleanup()

	fmt.println("\n=== 2. Chunked handle I/O and directories ===")
	chunked_handle_io_and_directories()

	fmt.println("\n=== 3. Cross-platform path manipulation ===")
	cross_platform_path_manipulation()
}
