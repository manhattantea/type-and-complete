// odin run 930_tcp_echo_and_command_server.odin -file

package main

import "core:fmt"
import "core:net"
import "core:strconv"
import "core:strings"
import "core:thread"

/*
Writing a TCP server that tests itself inside one executable avoids port
conflicts and manual telnet sessions. Notice the three-part loopback pattern:
bind 'net.listen_tcp' on 'net.IP4_Loopback' with 'port = 0' so the operating
system chooses any free ephemeral port; query that assigned port with
'net.bound_endpoint(listen_sock)'; then launch the server loop on a background
thread while 'main' dials the port, exchanges commands, and joins the thread so
the process always terminates cleanly.
*/

command_protocol_and_validation :: proc() {

	/*
	Network clients rarely send spotless inputs. Lines may carry trailing
	carriage returns ("\r\n"), extra spaces, missing operands ("ADD 15"),
	non-numeric tokens ("ADD 15 abc"), or extra trailing junk ("ADD 1 2 3").
	Trimming whitespace with 'strings.trim_space(line)' and rejecting malformed
	inputs with clear "ERR ..." replies keeps the protocol predictable.

	When a helper formats a short reply like "PONG\n" or an error message,
	allocating into 'context.temp_allocator' via 'fmt.tprintf' avoids per-reply
	heap frees as long as the server loop calls 'free_all(context.temp_allocator)'
	once each request finishes!
	*/

	sample_line := "  ADD 15 27\r\n"
	trimmed := strings.trim_space(sample_line)
	parsed, ok := strconv.parse_int("27")
	fmt.printfln("Trimmed command: %q (parsed sample operand=%d, ok=%v)", trimmed, parsed, ok)

	// Write a text-command handler at file scope:
	// handle_command :: proc(line: string) -> string
	// Trim whitespace with trimmed := strings.trim_space(line).
	// - Empty line -> return "" (ignore blank lines cleanly).
	// - "PING" -> return "PONG\n".
	// - "QUIT" -> return "BYE\n".
	// - Prefix "ADD" (handle bare "ADD" with no arguments too!): split remaining
	//   tokens with strings.split_iterator(&rest, " "), skip extra spaces, parse
	//   exactly two integers with strconv.parse_int, verify no trailing tokens
	//   remain, and return fmt.tprintf("%d\n", a + b) (or "ERR usage: ADD <a> <b>\n"
	//   if arguments are missing, non-numeric, or too many).
	// - Any other unknown verb or input -> return fmt.tprintf("ERR unknown command: %s\n", trimmed).
}

partial_recv_newline_framing :: proc() {

	/*
	TCP is an unstructured byte stream, not a message queue! Calling
	'net.send_tcp' once with "PING\nADD 2 3\n" does not guarantee the server's
	'net.recv_tcp' sees whole lines. Suppose the kernel delivers "PIN" in the
	first read and "G\nADD 2 3\n" in the second read. If the server naively split
	each raw read buffer directly, "PIN" and "G" would look like two broken
	commands instead of one "PING"!

	To frame lines reliably across arbitrary packet splits, keep an accumulation
	buffer 'rx_buf: [dynamic]u8' for the connection: append each 'buf[:n]' chunk,
	search for '\n' with 'strings.index_byte(string(rx_buf[:]), '\n')', extract
	each complete line up to '\n', and shift any leftover partial bytes to the
	front of 'rx_buf' via 'copy' and 'resize' before calling 'net.recv_tcp' again.
	*/

	// Compare an incomplete chunk ("PIN") against a chunk containing a newline:

	part1 := "PIN"
	part2 := "G\nADD"
	fmt.printfln("Newline index in %q: %d | in %q: %d", part1, strings.index_byte(part1, '\n'), part2, strings.index_byte(part2, '\n'))

	// Write the connection handler at file scope:
	// server_proc :: proc(listen_sock: net.TCP_Socket)
	// Accept one client with client_sock, accept_err := net.accept_tcp(listen_sock)
	// (return early if accept_err != nil), and register defer net.close(client_sock).
	// Maintain rx_buf: [dynamic]u8 (with defer delete(rx_buf)), loop calling
	// n, recv_err := net.recv_tcp(client_sock, buf[:]), break on recv_err != nil || n == 0,
	// call append(&rx_buf, ..buf[:n]), and loop while nl := strings.index_byte(string(rx_buf[:]), '\n'); nl >= 0:
	// extract line := string(rx_buf[:nl]), run reply := handle_command(line),
	// send transmute([]u8)reply with net.send_tcp when len(reply) > 0, shift
	// remaining bytes with copy(rx_buf[:], rx_buf[nl + 1:]) and resize(&rx_buf, len(rx_buf) - (nl + 1)),
	// call free_all(context.temp_allocator), and exit when trimmed line == "QUIT".
}

headless_loopback_bind_and_server :: proc() {

	/*
	Putting client and server inside one loopback run makes verification
	completely deterministic. Binding 'net.IP4_Loopback' with 'port = 0' avoids
	"address already in use" failures even if two tests run back to back. Once
	the OS assigns a free ephemeral port, 'net.bound_endpoint(listen_sock)'
	returns the concrete endpoint so the client knows which port to dial, and
	'thread.create_and_start_with_poly_data' hands 'listen_sock' to 'server_proc'
	without manual 'rawptr' casts.
	*/

	endpoint := net.Endpoint{address = net.IP4_Loopback, port = 0}
	pending_server: ^thread.Thread
	fmt.printfln("Loopback endpoint ready: %v (server thread handle nil=%v)", endpoint, pending_server == nil)

	// Bind listen_sock, listen_err := net.listen_tcp(endpoint), return early if
	// listen_err != nil, and register defer net.close(listen_sock).
	// Query the OS-assigned port via bound, bound_err := net.bound_endpoint(listen_sock)
	// (returning on bound_err != nil), print bound, and launch the server loop:
	// srv := thread.create_and_start_with_poly_data(listen_sock, server_proc)
}

client_exchange_and_shutdown :: proc() {

	/*
	On the client side, 'net.send_tcp' accepts a '[]u8' byte slice, so sending a
	string command uses 'transmute([]u8)msg' with zero heap allocations. Notice
	also why reading replies requires checking '(n, recv_err)': suppose the server
	sends "PONG\n" (5 bytes) into your stack buffer 'buf: [256]u8'. Only
	'buf[:n]' holds valid response bytes — the remaining bytes 'buf[n:]' are
	still zeroed or leftover from earlier reads!

	Sending one intentionally split request ("PI" followed by "NG\n") alongside
	a malformed request ("ADD 15 abc\n") and "QUIT\n" verifies both your newline
	framer and your error handling in a single headless run before calling
	'thread.join(srv)' and 'thread.destroy(srv)'.
	*/

	// Preview zero-copy string-to-bytes conversion for net.send_tcp:

	cmd := "PING\n"
	wire_bytes := transmute([]u8)cmd
	fmt.printfln("Wire payload for %q is %d bytes", cmd, len(wire_bytes))

	// Dial bound with client_sock, dial_err := net.dial_tcp(bound) and register
	// defer net.close(client_sock). Exchange these requests in order:
	// - Send "PING\n" and "ADD 15 27\n" via net.send_tcp and print each reply.
	// - Test partial recv framing by sending "PI" in one net.send_tcp call and
	//   "NG\n" in a second net.send_tcp call, confirming one "PONG\n" reply.
	// - Test malformed inputs by sending "ADD\n" and "ADD 15 abc\n" and printing
	//   the "ERR ..." replies without crashing the server loop.
	// - Send "QUIT\n", read "BYE\n", and call thread.join(srv) + thread.destroy(srv).
}

main :: proc() {

	fmt.println("=== 1. Command protocol and malformed-input validation ===")
	command_protocol_and_validation()

	fmt.println("\n=== 2. Partial recv newline framing ===")
	partial_recv_newline_framing()

	fmt.println("\n=== 3. Headless loopback bind and server thread ===")
	headless_loopback_bind_and_server()

	fmt.println("\n=== 4. Client command exchange and clean shutdown ===")
	client_exchange_and_shutdown()
}
