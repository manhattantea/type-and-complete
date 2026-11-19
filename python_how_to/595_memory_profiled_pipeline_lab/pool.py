# 595_memory_profiled_pipeline_lab/pool.py

import weakref


# Normally, every Python class instance carries a per-object __dict__ hash
# table (~104+ bytes of overhead on 64-bit CPython). Defining __slots__ replaces
# __dict__ with fixed descriptor offsets inside the PyObject struct, shrinking
# memory footprint and blocking accidental attribute typos.
#
# Defining __slots__ disables weak-reference support unless "__weakref__" is
# listed explicitly in the tuple. Adding "__weakref__" lets a WeakValueDictionary
# observe pooled buffers without owning strong references that would hide leaks.
#
#     Suppose pool = PacketPool(capacity=4) pre-allocates 4 PacketBuffer objects
#     and registers them in self._weak_registry.
#     While pool is alive, len(weak_reg) is 4; once pool is deleted, all 4
#     weak entries vanish automatically to 0 unless a caller leaked a buffer!


class PacketBuffer:

    __slots__ = ("id", "payload", "checksum", "__weakref__")

    def __init__(self, packet_id: int = 0) -> None:

        self.id: int = packet_id
        self.payload: bytearray = bytearray()
        self.checksum: int = 0

    # Add def reset(self) -> None: on PacketBuffer to reset self.id = 0,
    # call self.payload.clear() (preserving the underlying bytearray heap
    # allocation rather than assigning a new bytearray()), and set
    # self.checksum = 0.


class PacketPool:

    def __init__(self, capacity: int = 4) -> None:

        self._capacity = capacity
        self._free: list[PacketBuffer] = [PacketBuffer() for _ in range(capacity)]
        self._in_use: set[PacketBuffer] = set()
        self._weak_registry: weakref.WeakValueDictionary[int, PacketBuffer] = (
            weakref.WeakValueDictionary({id(b): b for b in self._free})
        )

    # Add def acquire(self) -> PacketBuffer: on PacketPool. If not self._free,
    # raise RuntimeError("PacketPool exhausted"). Otherwise pop
    # buf = self._free.pop(), add buf to self._in_use, and return buf.


    # Add def release(self, buf: PacketBuffer) -> None: on PacketPool. Check
    # membership in self._in_use first so double-release raises
    # ValueError("Buffer is not checked out from this pool"), remove buf from
    # self._in_use, call buf.reset(), and append buf back onto self._free.


    # Add two @property read-only helpers on PacketPool:
    # - @property def in_use_count(self) -> int: returning len(self._in_use)
    # - @property def free_count(self) -> int: returning len(self._free)
