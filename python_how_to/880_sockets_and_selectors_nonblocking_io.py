# python 880_sockets_and_selectors_nonblocking_io.py

import selectors
import socket


def nonblocking_sockets_and_selector_setup() -> None:

    # Every high-concurrency Python async framework (asyncio, uvicorn, aiohttp)
    # sits on top of two OS primitives exposed in the standard library:
    # - Non-blocking sockets (sock.setblocking(False)): instead of putting the
    #   thread to sleep inside the kernel when no bytes are ready, recv(),
    #   send(), accept(), and connect() return immediately—raising
    #   BlockingIOError whenever the operation cannot complete right away.
    # - Readiness multiplexing (selectors.DefaultSelector): instead of spinning
    #   in a tight polling loop at 100% CPU, register sockets with
    #   DefaultSelector (wrapping epoll on Linux, kqueue on macOS, or select on
    #   Windows). Calling sel.select(timeout=1.0) sleeps cleanly in the kernel
    #   until at least one socket becomes readable (EVENT_READ) or writable
    #   (EVENT_WRITE).
    #
    # Notice one cross-platform detail: on a non-blocking socket,
    # client.connect(("127.0.0.1", port)) immediately raises BlockingIOError
    # (WSAEWOULDBLOCK / EINPROGRESS) while the local TCP handshake completes
    # asynchronously. Catch BlockingIOError and wait for EVENT_WRITE readiness.
    # Also binding to ("127.0.0.1", 0) lets the OS pick a guaranteed-free
    # ephemeral port, which you read back with server.getsockname().

    with selectors.DefaultSelector() as sel:
        print(f"Starter selector backend: {type(sel).__name__}")

        # Inside this with selectors.DefaultSelector() as sel: block, create a
        # non-blocking loopback TCP listener:
        # - server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # - server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # - server.bind(("127.0.0.1", 0)), server.listen(4), server.setblocking(False)
        # - host, port = server.getsockname()
        # - Register sel.register(server, selectors.EVENT_READ, data="accept"),
        #   print the bound port, then unregister and close server in finally:.


def tcp_byte_stream_framing() -> None:

    # The #1 TCP networking bug is assuming one send() equals one recv().
    # TCP is an unstructured byte stream, NOT a message queue!
    #
    #     Suppose a client sends b"HELLO\nPING\n":
    #         The OS kernel may deliver all 11 bytes in one recv(1024) call, OR
    #         deliver b"HEL", then b"LO\nPI", then b"NG\n" across three calls!
    #
    # Robust TCP servers and clients ALWAYS append received chunks into a
    # per-connection bytearray buffer and extract complete frames only when a
    # delimiter (b"\n") or explicit length prefix is completely present.

    inbound = bytearray(b"HEL")
    inbound.extend(b"LO\nPI")
    line, sep, rest = inbound.partition(b"\n")
    print(f"Starter framing split: line={line!r}, sep={sep!r}, rest={rest!r}")

    # Drive a single-threaded selector echo loop over loopback TCP:
    # - Open non-blocking server on ("127.0.0.1", 0) and register EVENT_READ.
    # - Open non-blocking client, call try: client.connect((host, port)) except BlockingIOError: pass,
    #   give it outbound = [b"HEL", b"LO\nPING\n"] (deliberately split mid-frame!)
    #   and inbound = bytearray(), and register EVENT_READ | EVENT_WRITE.
    # - Loop while not done: over sel.select(timeout=1.0):
    #   - On "accept": conn, _ = server.accept(), conn.setblocking(False), and
    #     register conn for EVENT_READ with its own bytearray() buffer.
    #   - On client EVENT_WRITE: pop and send() the next chunk; once outbound is
    #     empty, call sel.modify(client, selectors.EVENT_READ, data=...) so
    #     EVENT_WRITE does not fire continuously on idle loops!
    #   - On EVENT_READ: read chunk = sock.recv(1024) inside try ... except BlockingIOError:.
    #     If chunk == b"", the peer closed cleanly—unregister and close.
    #     Otherwise append to that socket's bytearray and pop frames while
    #     b"\n" in buf via line, _, rest = buf.partition(b"\n").
    #     Server replies conn.sendall(b"ACK:" + line + b"\n"); client collects
    #     replies and sets done = True once [b"ACK:HELLO", b"ACK:PING"] arrive!
    # - Cleanly unregister and close all sockets in finally:.


def partial_send_under_backpressure() -> None:

    # Just as recv(n) may return fewer than n bytes, non-blocking sock.send(data)
    # is NOT guaranteed to transmit all of len(data) in one call! When the OS
    # kernel's TCP send buffer is nearly full (backpressure from a slow peer),
    # send(buf) transmits only k bytes (0 < k < len(buf)) and returns k—or
    # raises BlockingIOError when the send buffer is completely full.
    #
    #     Suppose outbuf = memoryview(b"A" * 1_000_000) and sent = sock.send(outbuf):
    #         If sent == 65_536, you MUST slice outbuf = outbuf[sent:] and keep
    #         EVENT_WRITE armed until len(outbuf) == 0!
    #         Calling sock.sendall() on a non-blocking socket does NOT fix this:
    #         sendall() raises BlockingIOError the instant the kernel buffer fills,
    #         leaving you with no way to know how many bytes were already sent!

    payload = memoryview(b"0123456789")
    remaining = payload[4:]
    print(f"Starter memoryview slice without copying: remaining={bytes(remaining)!r}")

    # Test partial non-blocking sock.send() under real kernel backpressure:
    # - Open a connected socket pair via server/client or socket.socketpair()
    #   (note: on Windows use a loopback server.accept() pair, since
    #   socket.socketpair() may not be available on older builds; loopback works
    #   identically on Windows, macOS, and Linux!).
    # - Set both ends to setblocking(False) and shrink the receiver's buffer
    #   or leave the receiver unread while sending a large payload (e.g.
    #   data = memoryview(b"X" * (2 * 1024 * 1024))) from the sender via
    #   sent = sender.send(pending) inside try ... except BlockingIOError:.
    # - Advance pending = pending[sent:], track total_sent += sent and how many
    #   partial/would-block cycles occurred, and drain from the receiver in the
    #   same DefaultSelector loop (arming EVENT_WRITE on sender only while
    #   len(pending) > 0) until total_received == len(data)!
    # - Assert total_received == 2 * 1024 * 1024 and close both sockets cleanly.


def main() -> None:

    print("=== 1. Non-blocking sockets and DefaultSelector ===")
    nonblocking_sockets_and_selector_setup()

    print("\n=== 2. TCP byte-stream framing across split chunks ===")
    tcp_byte_stream_framing()

    print("\n=== 3. Partial sock.send() under kernel backpressure ===")
    partial_send_under_backpressure()


if __name__ == "__main__":
    main()
