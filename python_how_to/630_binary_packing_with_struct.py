# python 630_binary_packing_with_struct.py

import struct


def endianness_and_alignment_padding() -> None:

    # Python integers are heap-allocated arbitrary-precision objects, not raw
    # 16-bit or 32-bit machine words. Whenever you parse network packets, binary
    # file headers (PNG, WAV, SQLite pages), or C structs, you need exact byte
    # layouts.
    #
    # The struct module packs Python values into bytes and unpacks them back
    # using compact format strings. The very first character controls both byte
    # order (endianness) and C compiler alignment padding:
    # - @ (the default if you omit a prefix!): native byte order, native sizes,
    #   AND native C alignment padding.
    # - = : native byte order, standard sizes, NO alignment padding.
    # - < : little-endian (least-significant byte first, standard on x86/ARM),
    #   standard sizes, NO alignment padding.
    # - > or ! : big-endian / network byte order (most-significant byte first;
    #   ! is an alias for >), standard sizes, NO alignment padding.
    #
    # Common standard format characters:
    # - b / B: signed / unsigned 8-bit int (1 byte)
    # - h / H: signed / unsigned 16-bit int (2 bytes)
    # - i / I: signed / unsigned 32-bit int (4 bytes)
    # - q / Q: signed / unsigned 64-bit int (8 bytes)
    # - f / d: IEEE-754 32-bit float / 64-bit double (4 / 8 bytes)
    # - ?: boolean (1 byte)
    # - Ns: fixed N-byte bytes field (pads short inputs with b"\x00" on pack)
    #
    #     Suppose you lay out format HBI (u16, u8, u32):
    #     With <HBI (packed), bytes are 2 + 1 + 4 = 7 bytes total.
    #     With @HBI (native C alignment), H uses bytes 0..1, B uses byte 2, and
    #     the compiler inserts 1 hidden padding byte at offset 3 so I starts at
    #     4-byte-aligned offset 4..7—making the struct 8 bytes!

    print("calcsize('@HBI') =", struct.calcsize("@HBI"), "| calcsize('<HBI') =", struct.calcsize("<HBI"))

    # Compile PACKET_HDR = struct.Struct("<HBI") (pre-compiling avoids re-parsing
    # the format string on every call). Pack (0xCAFE, 1, 1024) into header_bytes,
    # print header_bytes.hex(" ") and len(header_bytes), then unpack back into
    # magic, version, length = PACKET_HDR.unpack(header_bytes) and print them.


    # Compare little-endian vs network big-endian byte order on the same values:
    # pack (0xCAFE, 1, 1024) with struct.pack("!HBI", 0xCAFE, 1, 1024) and print
    # its .hex(" ") next to header_bytes.hex(" ") to see the reversed byte order.


    # Pack a mixed record with fixed bytes, a boolean, and a float:
    # compile SENSOR_REC = struct.Struct("<4s?f"), pack (b"TMP", True, 21.5)
    # into rec_bytes, unpack it back, and observe the trailing b"\x00" padding
    # byte inside the 4s field (b"TMP\x00").


    # Try uncommenting the line below to see struct.error when 300 overflows B (0..255):
    # struct.pack("<HBI", 0xCAFE, 300, 1024)


def zero_copy_buffers_and_int_bytes() -> None:

    # Packing inside a tight loop with .pack(...) allocates a new bytes object
    # per record. Pre-allocating one mutable bytearray lets you write records
    # directly at chosen offsets with .pack_into(buf, offset, *values), read a
    # single record with .unpack_from(buf, offset), or stream every record lazily
    # with .iter_unpack(buf) (which requires len(buf) to be a multiple of .size).
    #
    #     Suppose hdr = struct.Struct("<HBI") (size 7) and buf = bytearray(14).
    #     hdr.pack_into(buf, 0, 0xCAFE, 1, 128) writes bytes 0..6.
    #     hdr.pack_into(buf, 7, 0xCAFE, 2, 512) writes bytes 7..13.
    #     list(hdr.iter_unpack(buf)) yields [(51966, 1, 128), (51966, 2, 512)].
    #
    # For odd integer widths not covered by struct (like 24-bit RGB values or
    # 128-bit IDs), int itself provides .to_bytes(length, byteorder, signed=...)
    # and int.from_bytes(data, byteorder, signed=...).

    raw_u16 = (0xCAFE).to_bytes(2, byteorder="little")
    print("Starter 0xCAFE little-endian:", raw_u16.hex(" "), "->", hex(int.from_bytes(raw_u16, "little")))

    # Compile PACKET_HDR = struct.Struct("<HBI") and allocate
    # buf = bytearray(PACKET_HDR.size * 2). Pack (0xCAFE, 1, 128) at offset 0
    # and (0xCAFE, 2, 512) at offset PACKET_HDR.size using PACKET_HDR.pack_into.
    # Iterate for magic, version, length in PACKET_HDR.iter_unpack(buf): and
    # print each unpacked record.


    # Read just the second record without slicing or copying buf by calling
    # PACKET_HDR.unpack_from(buf, PACKET_HDR.size) and printing the result.


    # Practice non-standard widths with int.to_bytes / int.from_bytes:
    # encode a 24-bit unsigned color 0x336699 into 3 big-endian bytes and decode
    # it back; then encode -42 into 2 little-endian bytes with signed=True and
    # decode it back with signed=True (and also see what signed=False returns!).


def main() -> None:

    print("=== 1. Endianness, C alignment padding, and struct.Struct ===")
    endianness_and_alignment_padding()

    print("\n=== 2. pack_into, iter_unpack, and arbitrary-width int bytes ===")
    zero_copy_buffers_and_int_bytes()


if __name__ == "__main__":
    main()
