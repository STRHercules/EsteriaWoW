"""BLTE -- the block container everything in CASC is wrapped in.

Every file stored in a CASC archive is a BLTE stream: a header listing chunks,
then the chunks themselves, each tagged with how it was encoded.  Decoding is
the first thing that has to work before any of the higher-level tables
(encoding, root) can even be read, because those are BLTE-encoded too.

Chunk modes
-----------
``N`` stored verbatim, ``Z`` zlib, ``4`` LZ4 block, ``F`` a nested BLTE stream,
``E`` encrypted (Salsa20 or ARC4) wrapping one of the others.

Note the header and chunk sizes are **big-endian**, unlike every other Blizzard
format.
"""

from __future__ import annotations

import dataclasses
import struct
import zlib

from ..errors import MalformedFileError, UnsupportedFormatError
from .salsa20 import arc4, salsa20

MAGIC = b"BLTE"


class EncryptedChunkError(UnsupportedFormatError):
    """A chunk is encrypted with a key that was not supplied.

    Blizzard ships unreleased content encrypted; the keys leak (or are
    published) later.  This is normal and is reported per file rather than
    aborting a whole extraction.
    """

    def __init__(self, key_name: int):
        self.key_name = key_name
        super().__init__(
            f"chunk is encrypted with key {key_name:016X}, which was not "
            f"supplied (see --casc-keys)"
        )


@dataclasses.dataclass(slots=True)
class ChunkInfo:
    compressed_size: int
    decompressed_size: int
    checksum: bytes


def _lz4_block_decompress(data: bytes, expected: int) -> bytes:
    """Minimal LZ4 block format decoder.

    Rare in WoW data but not absent, and a pure-Python decoder is 40 lines --
    cheaper than making the whole tool depend on an LZ4 binding.
    """
    out = bytearray()
    pos = 0
    n = len(data)
    while pos < n:
        token = data[pos]
        pos += 1
        literal_len = token >> 4
        if literal_len == 15:
            while pos < n:
                b = data[pos]
                pos += 1
                literal_len += b
                if b != 255:
                    break
        out += data[pos : pos + literal_len]
        pos += literal_len
        if pos >= n:
            break
        if pos + 2 > n:
            raise MalformedFileError("LZ4 block ended mid-offset")
        offset = data[pos] | (data[pos + 1] << 8)
        pos += 2
        if offset == 0:
            raise MalformedFileError("LZ4 block has a zero match offset")
        match_len = token & 0x0F
        if match_len == 15:
            while pos < n:
                b = data[pos]
                pos += 1
                match_len += b
                if b != 255:
                    break
        match_len += 4
        start = len(out) - offset
        if start < 0:
            raise MalformedFileError("LZ4 match reaches before the start of output")
        for i in range(match_len):
            out.append(out[start + i])
    if expected and len(out) != expected:
        raise MalformedFileError(
            f"LZ4 chunk decoded to {len(out)} bytes, expected {expected}")
    return bytes(out)


def _decode_encrypted(payload: bytes, block_index: int, keys, expected: int,
                      zero_missing: bool = False) -> bytes:
    """Unwrap an ``E`` chunk: ``keyNameSize keyName ivSize iv type payload``.

    With ``zero_missing``, a chunk whose key is not known decodes to zeros of
    its declared size instead of failing the whole file.  That is only right
    for a reader that recognises the hole -- a WDC database skips a section
    flagged encrypted whose bytes are zero -- so it is off by default.
    """
    if len(payload) < 1:
        raise MalformedFileError("empty encrypted chunk")
    pos = 0
    key_name_size = payload[pos]
    pos += 1
    if key_name_size != 8:
        raise MalformedFileError(
            f"encrypted chunk has a {key_name_size}-byte key name, expected 8")
    key_name = int.from_bytes(payload[pos : pos + 8], "little")
    pos += 8
    iv_size = payload[pos]
    pos += 1
    iv = bytearray(payload[pos : pos + iv_size])
    pos += iv_size
    enc_type = payload[pos : pos + 1]
    pos += 1

    key = keys.get(key_name) if keys is not None else None
    if key is None:
        if zero_missing and expected:
            return bytes(expected)
        raise EncryptedChunkError(key_name)

    # The IV is mixed with the chunk index so identical plaintext in different
    # chunks does not encrypt identically.
    for i in range(4):
        if i >= len(iv):
            break
        iv[i] ^= (block_index >> (i * 8)) & 0xFF

    body = payload[pos:]
    if enc_type == b"S":
        plain = salsa20(key, bytes(iv), body)
    elif enc_type == b"A":
        plain = arc4(key, bytes(iv), body)
    else:
        raise UnsupportedFormatError(
            f"unknown BLTE encryption type {enc_type!r}")
    return _decode_chunk(plain, block_index, keys, expected, zero_missing)


def _decode_chunk(data: bytes, block_index: int, keys, expected: int,
                  zero_missing: bool = False) -> bytes:
    if not data:
        return b""
    mode = data[0:1]
    body = data[1:]
    if mode == b"N":
        return body
    if mode == b"Z":
        try:
            return zlib.decompress(body)
        except zlib.error as exc:
            raise MalformedFileError(f"zlib chunk failed to inflate: {exc}") from None
    if mode == b"4":
        return _lz4_block_decompress(body, expected)
    if mode == b"F":
        return decode(body, keys, zero_missing)
    if mode == b"E":
        return _decode_encrypted(body, block_index, keys, expected,
                                 zero_missing)
    raise UnsupportedFormatError(f"unknown BLTE chunk mode {mode!r}")


def parse_header(data: bytes) -> tuple[int, list[ChunkInfo]]:
    """Return (offset of the first chunk, chunk table).

    A header size of zero means the whole remainder is one chunk, which is how
    small files are stored.
    """
    if len(data) < 8 or data[:4] != MAGIC:
        raise MalformedFileError(
            f"not a BLTE stream (magic {data[:4]!r})")
    header_size = struct.unpack_from(">I", data, 4)[0]
    if header_size == 0:
        return 8, [ChunkInfo(len(data) - 8, 0, b"")]

    flags = data[8]
    chunk_count = int.from_bytes(data[9:12], "big")
    if flags & 0x0F != 0x0F:
        raise UnsupportedFormatError(f"unexpected BLTE flags 0x{flags:02X}")
    chunks: list[ChunkInfo] = []
    pos = 12
    for _ in range(chunk_count):
        if pos + 24 > len(data):
            raise MalformedFileError("BLTE chunk table runs past end of stream")
        comp, decomp = struct.unpack_from(">II", data, pos)
        chunks.append(ChunkInfo(comp, decomp, data[pos + 8 : pos + 24]))
        pos += 24
    return header_size, chunks


def decode(data: bytes, keys=None, zero_missing: bool = False) -> bytes:
    """Decode a complete BLTE stream.

    ``zero_missing`` turns chunks encrypted with an unknown key into zeros of
    their declared size; see :func:`_decode_encrypted`.
    """
    offset, chunks = parse_header(data)
    out = bytearray()
    pos = offset
    for index, chunk in enumerate(chunks):
        size = chunk.compressed_size
        if size <= 0 or pos + size > len(data):
            size = len(data) - pos
        if size <= 0:
            break
        out += _decode_chunk(data[pos : pos + size], index, keys,
                             chunk.decompressed_size, zero_missing)
        pos += size
    return bytes(out)


