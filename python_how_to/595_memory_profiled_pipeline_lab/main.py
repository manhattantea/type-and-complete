# python 595_memory_profiled_pipeline_lab/main.py

from collections.abc import Iterator
import tracemalloc

from pool import PacketBuffer, PacketPool
from processor import compute_checksum


# This lab combines __slots__ + __weakref__ buffer pooling (pool.py),
# constant-memory generator streaming with try/finally cleanup (processor.py),
# and tracemalloc heap verification (main.py).
#
#     Suppose 1,000 byte chunks flow through PacketPool(capacity=4).
#     Because each chunk reuses one of the 4 pre-allocated PacketBuffer slots
#     and clears its bytearray in place, peak traced heap stays flat and
#     WeakValueDictionary confirms zero leaked buffers at teardown.


def main() -> None:

    print("=== Memory-Profiled Streaming Pipeline Lab ===")
    starter_buf = PacketBuffer(packet_id=1)
    starter_buf.payload.extend(b"ping")
    starter_pool = PacketPool(capacity=2)
    print(
        "Starter check -> checksum:",
        compute_checksum(starter_buf),
        "| weak refs tracked:",
        len(starter_pool._weak_registry),
        "| tracemalloc active:",
        tracemalloc.is_tracing(),
    )

    # Define def generate_chunks(count: int) -> Iterator[bytes]: lazily yielding
    # f"pkt-{i:04d}:payload".encode("ascii") for i in range(count) without
    # building an intermediate list in memory.


    # Finish PacketBuffer.reset(), PacketPool methods (acquire, release,
    # in_use_count, free_count), and processor.process_packets(), then import
    # process_packets from processor.
    # Start tracemalloc.start(), create pool = PacketPool(capacity=4), and save
    # weak_reg = pool._weak_registry so you can assert len(weak_reg) == 4 while
    # the pool is alive.


    # Stream 1,000 chunks via process_packets(generate_chunks(1000), pool),
    # summing yielded checksums into total_checksum and counting processed items.
    # Capture current_bytes, peak_bytes = tracemalloc.get_traced_memory(), stop
    # tracemalloc.stop(), assert processed == 1000, pool.in_use_count == 0, and
    # pool.free_count <= 4, and print processed, total_checksum, current_bytes,
    # and peak_bytes.


    # Verify early-break reclamation and zero leaks:
    # create gen = process_packets(generate_chunks(10), pool), pull one item
    # with next(gen), call gen.close(), and assert pool.in_use_count == 0 to
    # observe finally: pool.release(buf) firing on GeneratorExit. Finally, run
    # del pool and assert len(weak_reg) == 0.


if __name__ == "__main__":
    main()
