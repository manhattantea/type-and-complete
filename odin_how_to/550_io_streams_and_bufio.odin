// odin run 550_io_streams_and_bufio.odin -file

package main

import "core:bufio"
import "core:bytes"
import "core:fmt"
import "core:io"
import "core:strings"

/*
Instead of writing separate parsers for files, sockets, and strings, 'core:io'
defines a unified 'io.Stream' vtable interface ('io.Reader', 'io.Writer',
'io.Seeker'). Any procedure accepting an 'io.Stream' or 'io.Reader' works
identically across files, network connections, in-memory 'bytes.Buffer's, and
read-only 'strings.Reader's.

On top of those raw streams, 'core:bufio' adds buffered scanning
('bufio.Scanner') and buffered batch writes ('bufio.Writer') so small reads
and writes do not hit the OS on every byte.
*/

unified_io_stream_and_bytes_buffer :: proc() {

	/*
	A 'bytes.Buffer' is a growable heap byte array that exposes an 'io.Stream'
	via 'bytes.buffer_to_stream(&buf)'. Calling 'io.write_string(stream, s)'
	dispatches through that stream's procedure pointer and returns
	'(bytes_written, err)'. Always free the buffer with 'defer bytes.buffer_destroy(&buf)'.
	*/

	anchor_buf: bytes.Buffer
	defer bytes.buffer_destroy(&anchor_buf)
	written, write_err := io.write_string(bytes.buffer_to_stream(&anchor_buf), "io.Stream ready")
	fmt.printfln("Starter stream write: %d bytes (err=%v) -> %q", written, write_err, bytes.buffer_to_string(&anchor_buf))

	// Initialize buf: bytes.Buffer explicitly with bytes.buffer_init(&buf, nil)
	// and register defer bytes.buffer_destroy(&buf). Obtain stream := bytes.buffer_to_stream(&buf),
	// write two lines using io.write_string(stream, ...), check the returned byte counts
	// and error, and print bytes.buffer_to_string(&buf).


	// Write a reusable helper procedure at file scope or locally:
	// write_header :: proc(s: io.Stream, title: string) -> io.Error
	// Have it write a formatted banner line using io.write_string(s, ...) and
	// test calling write_header(bytes.buffer_to_stream(&buf), "Session Log").
}

streaming_reads_with_scanner :: proc() {

	/*
	'strings.Reader' wraps an existing immutable 'string' as an 'io.Reader' via
	'strings.to_reader(&r, text)' without copying any bytes.

	When we wrap that reader in 'bufio.Scanner' using
	'bufio.scanner_init(&sc, reader)' (paired with 'defer bufio.scanner_destroy(&sc)'),
	each call to 'bufio.scanner_scan(&sc)' advances to the next newline-delimited
	token and returns 'true' until EOF or error, exposing the line via
	'bufio.scanner_text(&sc)'.
	*/

	anchor_reader: strings.Reader
	anchor_scanner: bufio.Scanner
	bufio.scanner_init(&anchor_scanner, strings.to_reader(&anchor_reader, "line one\nline two"))
	defer bufio.scanner_destroy(&anchor_scanner)
	if bufio.scanner_scan(&anchor_scanner) {
		fmt.printfln("Starter scanner line: %s", bufio.scanner_text(&anchor_scanner))
	}

	// Scan multi-line text line by line:
	// declare multi_line := "alpha\nbeta\ngamma", r: strings.Reader, and sc: bufio.Scanner
	// Initialize sc with bufio.scanner_init(&sc, strings.to_reader(&r, multi_line)),
	// register defer bufio.scanner_destroy(&sc), and loop for bufio.scanner_scan(&sc)
	// printing each 1-based line number and bufio.scanner_text(&sc).


	// Parse a config stream while ignoring blank lines and '#' comments:
	// declare cfg_src := "# header\nhost=127.0.0.1\n\nport=8080\n"
	// Stream it through a fresh strings.Reader and bufio.Scanner, skip lines where
	// len(line) == 0 || strings.has_prefix(line, "#"), and print active key=value lines.


	// Check sc.err after scanning an empty string "" to observe scanner_scan(&sc)
	// immediately returning false with sc.err == nil.
}

buffered_writes_with_bufio_writer :: proc() {

	/*
	Writing 100 tiny strings directly to a file or socket issues 100 expensive
	system calls. 'bufio.Writer' absorbs small writes into an internal scratch
	buffer and only forwards to the underlying 'io.Writer' when the buffer fills
	up or when you explicitly call 'bufio.writer_flush(&w)'.

	    Suppose out_buf holds 0 bytes and 'w' wraps it with bufio.writer_init(&w, wr):
	        bufio.writer_write_string(&w, "hello ")
	        // out_buf is STILL empty (0 bytes) — "hello " sits inside w's buffer!
	        bufio.writer_flush(&w)
	        // now out_buf holds "hello "!

	Convert any 'io.Stream' to an 'io.Writer' with 'wr, ok := io.to_writer(stream)',
	and always pair 'bufio.writer_init(&w, wr)' with 'defer bufio.writer_destroy(&w)'.
	Remember that 'writer_destroy' frees the internal buffer without flushing for
	you, so always flush before reading the destination!
	*/

	// Declare out_buf: bytes.Buffer with defer bytes.buffer_destroy(&out_buf).
	// Convert its stream via: wr, wr_ok := io.to_writer(bytes.buffer_to_stream(&out_buf))
	// When wr_ok is true, initialize w: bufio.Writer with bufio.writer_init(&w, wr)
	// and register defer bufio.writer_destroy(&w). Write three short chunks using
	// bufio.writer_write_string(&w, ...), print len(bytes.buffer_to_string(&out_buf))
	// BEFORE flushing (expected: 0!), call flush_err := bufio.writer_flush(&w),
	// and print the flushed byte count and bytes.buffer_to_string(&out_buf) AFTER.


	// Observe automatic flushing on buffer overflow:
	// create a tiny 16-byte buffered writer via bufio.writer_init(&small_w, wr, 16)
	// over a fresh bytes.Buffer (defer bufio.writer_destroy(&small_w)).
	// Write two 12-byte strings with bufio.writer_write_string, print the destination
	// buffer length before calling bufio.writer_flush(&small_w) to see the first
	// chunk spill automatically, then flush the remaining bytes.


	// Synthesis pipeline: write 4 CSV rows ("id,score\n1,95\n2,88\n3,74\n") through
	// bufio.Writer into a bytes.Buffer, flush it, then feed bytes.buffer_to_string
	// into strings.Reader + bufio.Scanner to read and print every row back.
}

main :: proc() {

	fmt.println("=== 1. Unified io.Stream and bytes.Buffer ===")
	unified_io_stream_and_bytes_buffer()

	fmt.println("\n=== 2. Streaming reads with bufio.Scanner ===")
	streaming_reads_with_scanner()

	fmt.println("\n=== 3. Buffered writes with bufio.Writer ===")
	buffered_writes_with_bufio_writer()
}
