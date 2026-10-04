"""Little-endian bit-field reading.

From Legion onwards a DB2 record is not a struct but a bit stream: a column may
start mid-byte and be any width from 1 to 64 bits, chosen per column to be just
wide enough for the values that table actually holds.
"""

from __future__ import annotations


def read_bits(data: bytes, bit_offset: int, bit_count: int) -> int:
    """Read ``bit_count`` bits starting at ``bit_offset`` as an unsigned int."""
    if bit_count <= 0:
        return 0
    byte_offset = bit_offset >> 3
    shift = bit_offset & 7
    span = (shift + bit_count + 7) >> 3
    chunk = data[byte_offset : byte_offset + span]
    if len(chunk) < span:
        # A final record can end exactly on its last used bit; pad rather than
        # refuse the whole table.
        chunk = bytes(chunk) + b"\0" * (span - len(chunk))
    value = int.from_bytes(chunk, "little")
    return (value >> shift) & ((1 << bit_count) - 1)


def sign_extend(value: int, bit_count: int) -> int:
    """Interpret ``bit_count`` bits of ``value`` as two's complement."""
    if bit_count <= 0 or bit_count >= 64:
        return value
    sign = 1 << (bit_count - 1)
    return (value ^ sign) - sign


def as_float(value: int) -> float:
    """Reinterpret the low 32 bits of an integer as an IEEE-754 float."""
    import struct

    return struct.unpack("<f", (value & 0xFFFFFFFF).to_bytes(4, "little"))[0]
