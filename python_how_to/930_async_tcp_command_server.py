# python 930_async_tcp_command_server.py

# This capstone builds a concurrent loopback TCP command server and multi-client
# self-test in one file using Python's cooperative asyncio streams API:
# asyncio.start_server and asyncio.open_connection.
#
# ServerStats holds shared server-wide counters across every connected client.
# Notice @dataclass(slots=True) keeps this shared state compact and explicit
# instead of hiding counters inside module-level global variables.

import asyncio
from dataclasses import dataclass


@dataclass(slots=True)
class ServerStats:
    commands_handled: int = 0
    total_connections: int = 0


def protocol_framing_and_backpressure() -> None:

    # Three networking realities govern every real-world asyncio TCP server:
    #
    # TCP is an unframed byte stream, not a message queue.
    #     Suppose a client writes b"PING\n" and b"ADD 15 27\n" back to back.
    #     The OS kernel may deliver both commands in one recv() chunk
    #     (b"PING\nADD 15 27\n"), or split the first command into b"PI" followed
    #     by b"NG\n". Calling await reader.readline() buffers incoming bytes
    #     across recv calls and yields cleanly at each '\n', returning b""
    #     (empty bytes) when the peer closes the socket (EOF).
    #
    # writer.write(data) is synchronous—it only appends bytes into an in-memory
    # user-space buffer without yielding to the event loop! If a fast producer
    # writes continuously to a slow reader without calling await writer.drain(),
    # that buffer grows without bound. Pairing writer.write(...) with
    # await writer.drain() pauses the coroutine whenever the buffer crosses its
    # high-water mark, giving you automatic TCP backpressure.
    #
    # Why can multiple concurrent clients update ServerStats without a Lock?
    # Because asyncio runs on a single OS thread and switches coroutines ONLY at
    # explicit 'await' points! Incrementing stats.commands_handled += 1 inside
    # synchronous handle_command executes from start to finish without any other
    # coroutine interleaving mid-update.

    starter_stats = ServerStats()
    sample_wire = b"PING\nADD 15 27\n"
    print(f"Starter stats={starter_stats}, framed lines={sample_wire.decode('utf-8').splitlines()}")

    # Define def handle_command(raw_line: str, stats: ServerStats) -> tuple[str, bool]:
    # to parse one newline-terminated command and return (reply_line, should_close):
    # - Strip whitespace with line = raw_line.strip().
    # - If not line, return ("ERR empty command\n", False).
    # - Split parts = line.split(maxsplit=1) and set cmd = parts[0].upper().
    # - Handle four valid commands (incrementing stats.commands_handled += 1 on
    #   each valid command before building its reply):
    #   - "PING" -> return ("PONG\n", False).
    #   - "ADD" -> parse parts[1].split() into exactly two integers a, b. If
    #     len(parts) < 2, len(tokens) != 2, or int() raises ValueError, return
    #     ("ERR usage: ADD <a> <b>\n", False) without incrementing stats.
    #     Otherwise increment stats.commands_handled += 1 and return
    #     (f"{a + b}\n", False).
    #   - "STATS" -> increment stats.commands_handled += 1 and return
    #     (f"COMMANDS {stats.commands_handled}\n", False).
    #   - "QUIT" -> increment stats.commands_handled += 1 and return
    #     ("BYE\n", True).
    # - For any other command, return (f"ERR unknown command: {cmd}\n", False).


    # Unit-test handle_command purely in memory before opening any sockets:
    # create local_stats = ServerStats() and verify:
    # - handle_command("PING\n", local_stats) == ("PONG\n", False)
    # - handle_command("ADD 15 27\n", local_stats) == ("42\n", False)
    # - handle_command("ADD bad\n", local_stats) == ("ERR usage: ADD <a> <b>\n", False)
    # - handle_command("STATS\n", local_stats) == ("COMMANDS 3\n", False)
    # - handle_command("QUIT\n", local_stats) == ("BYE\n", True)
    # Print local_stats to confirm commands_handled == 4.


async def async_tcp_server_and_concurrent_clients() -> None:

    # Binding ("127.0.0.1", 0) asks the OS kernel to assign any guaranteed-free
    # ephemeral port, eliminating "Address already in use" errors across repeated
    # runs. After server = await asyncio.start_server(...), read the assigned
    # endpoint via host, port = server.sockets[0].getsockname()[:2].
    #
    # Always pair writer.close() with await writer.wait_closed() inside a
    # finally: block so the TCP FIN handshake finishes cleanly before
    # async with server: tears down the listening socket.
    #
    # Testing with asyncio.gather launches multiple client coroutines at once:
    #     Suppose Client A, Client B, and Client C connect concurrently via
    #     await asyncio.gather(run_client(...), run_client(...), run_client(...)).
    #     Each client sends PING, ADD, and QUIT (3 valid commands each = 9 total).
    #     While Client A suspends on await reader.readline(), the event loop
    #     serves Client B and Client C on the same thread. Once all 3 finish, a
    #     4th probe client sends STATS and receives "COMMANDS 10\n", proving
    #     shared state tracked every interleaved connection accurately.

    loop = asyncio.get_running_loop()
    print(f"Starter event loop running={loop.is_running()} (ready for loopback TCP server)")

    # Define async def client_handler(reader: asyncio.StreamReader, writer: asyncio.StreamWriter, stats: ServerStats) -> None:
    # Increment stats.total_connections += 1, then wrap a while True: loop in
    # try ... finally: so socket teardown always runs:
    # - Read raw_bytes = await reader.readline(); if not raw_bytes: break (EOF).
    # - Decode line = raw_bytes.decode("utf-8", errors="replace").
    # - Call reply, should_quit = handle_command(line, stats).
    # - Write writer.write(reply.encode("utf-8")) and apply backpressure via
    #   await writer.drain().
    # - If should_quit: break.
    # - Inside finally:, call writer.close() and await writer.wait_closed().


    # Define a reusable loopback client coroutine:
    # async def run_client(host: str, port: int, exchanges: list[tuple[str, str]]) -> list[str]:
    # Open reader, writer = await asyncio.open_connection(host, port) and wrap
    # the exchange loop in try ... finally: (closing writer and awaiting
    # writer.wait_closed()). For each (req, expected) in exchanges:
    # - Send writer.write(req.encode("utf-8")) and await writer.drain().
    # - Read reply = (await reader.readline()).decode("utf-8").
    # - Assert reply == expected and append reply to a results list.
    # Return results.


    # Define async def run_self_test() -> None: and await it at the end of this
    # section:
    # - Create stats = ServerStats() and start the server on an ephemeral port:
    #   server = await asyncio.start_server(lambda r, w: client_handler(r, w, stats), "127.0.0.1", 0)
    # - Read host, port = server.sockets[0].getsockname()[:2].
    # - Inside async with server:, launch 3 concurrent loopback clients using
    #   await asyncio.gather(
    #       run_client(host, port, [("PING\n", "PONG\n"), ("ADD 15 27\n", "42\n"), ("QUIT\n", "BYE\n")]),
    #       run_client(host, port, [("PING\n", "PONG\n"), ("ADD 10 32\n", "42\n"), ("QUIT\n", "BYE\n")]),
    #       run_client(host, port, [("PING\n", "PONG\n"), ("ADD -5 5\n", "0\n"), ("QUIT\n", "BYE\n")]),
    #   )
    # - After all 3 concurrent clients finish, run one final probe client:
    #   await run_client(host, port, [("STATS\n", "COMMANDS 10\n"), ("QUIT\n", "BYE\n")])
    # - Assert stats.total_connections == 4 and stats.commands_handled == 11,
    #   and print the server endpoint (host, port) plus final stats.


def main() -> None:

    print("=== 1. Protocol framing and backpressure ===")
    protocol_framing_and_backpressure()

    print("\n=== 2. Async TCP server and concurrent multi-client test ===")
    asyncio.run(async_tcp_server_and_concurrent_clients())


if __name__ == "__main__":
    main()
