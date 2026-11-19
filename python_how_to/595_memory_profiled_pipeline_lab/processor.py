# 595_memory_profiled_pipeline_lab/processor.py

from collections.abc import Iterable, Iterator

from pool import PacketBuffer, PacketPool


# Streaming raw chunks through a generator (Iterator[int]) keeps memory O(1):
# processing 1,000 or 10,000,000 chunks never materializes a list of
# PacketBuffer objects in RAM.
#
# When a caller stops iterating early (with break or gen.close()), Python
# injects GeneratorExit right at the suspended yield line! Wrapping buffer
# usage in try: ... finally: pool.release(buf) guarantees the borrowed
# PacketBuffer returns to pool even on early exit or exceptions.
#
#     Suppose buf = pool.acquire() runs BEFORE try:, then yield buf.checksum
#     suspends inside try:.
#     Calling gen.close() triggers GeneratorExit at yield, runs finally:, and
#     returns buf to pool; if acquire() itself raises RuntimeError, finally:
#     never tries to release an unacquired buffer.


def compute_checksum(buf: PacketBuffer) -> int:

    return sum(buf.payload) & 0xFFFFFFFF


# Define def process_packets(raw_chunks: Iterable[bytes], pool: PacketPool) -> Iterator[int]:
# Loop over seq_id, chunk in enumerate(raw_chunks):
# Acquire buf = pool.acquire() BEFORE entering try:, then inside try: set
# buf.id = seq_id, copy bytes into the existing bytearray in place using
# slice assignment buf.payload[:] = chunk, compute buf.checksum = compute_checksum(buf),
# and yield buf.checksum. In finally:, call pool.release(buf).
