"""Little-endian binary reading/writing helpers shared by every format module.

Everything Blizzard ships is little-endian, so the helpers here hard-code that
rather than carrying an endianness parameter around.
"""

from __future__ import annotations

import struct
from collections.abc import Iterable, Sequence

from .errors import TruncatedFileError

_U8 = struct.Struct("<B")
_I8 = struct.Struct("<b")
_U16 = struct.Struct("<H")
_I16 = struct.Struct("<h")
_U32 = struct.Struct("<I")
_I32 = struct.Struct("<i")
_U64 = struct.Struct("<Q")
_F32 = struct.Struct("<f")


class Reader:
    """Cursor over an immutable byte buffer.

    Offsets in M2/WMO files are absolute file offsets, so a Reader is normally
    created once for the whole file and ``seek``-ed around rather than sliced.
    """

    __slots__ = ("data", "name", "pos")

    def __init__(self, data: bytes, name: str = "<memory>", pos: int = 0):
        self.data = data
        self.pos = pos
        self.name = name

    # -- cursor ---------------------------------------------------------
    def __len__(self) -> int:
        return len(self.data)

    def seek(self, pos: int) -> Reader:
        self.pos = pos
        return self

    def skip(self, count: int) -> Reader:
        self.pos += count
        return self

    def at(self, pos: int) -> Reader:
        """Return an independent cursor over the same buffer."""
        return Reader(self.data, self.name, pos)

    def eof(self) -> bool:
        return self.pos >= len(self.data)

    def _need(self, count: int) -> int:
        start = self.pos
        end = start + count
        if start < 0 or end > len(self.data):
            raise TruncatedFileError(
                f"{self.name}: wanted {count} bytes at offset {start}, "
                f"file is {len(self.data)} bytes"
            )
        self.pos = end
        return start

    # -- scalars --------------------------------------------------------
    def u8(self) -> int:
        return _U8.unpack_from(self.data, self._need(1))[0]

    def i8(self) -> int:
        return _I8.unpack_from(self.data, self._need(1))[0]

    def u16(self) -> int:
        return _U16.unpack_from(self.data, self._need(2))[0]

    def i16(self) -> int:
        return _I16.unpack_from(self.data, self._need(2))[0]

    def u32(self) -> int:
        return _U32.unpack_from(self.data, self._need(4))[0]

    def i32(self) -> int:
        return _I32.unpack_from(self.data, self._need(4))[0]

    def u64(self) -> int:
        return _U64.unpack_from(self.data, self._need(8))[0]

    def f32(self) -> float:
        return _F32.unpack_from(self.data, self._need(4))[0]

    # -- aggregates -----------------------------------------------------
    def bytes(self, count: int) -> bytes:
        start = self._need(count)
        return self.data[start : start + count]

    def magic(self) -> str:
        """Read a 4CC as stored, without reversing."""
        return self.bytes(4).decode("latin-1")

    def unpack(self, fmt: str):
        s = struct.Struct("<" + fmt)
        return s.unpack_from(self.data, self._need(s.size))

    def array(self, fmt: str, count: int) -> tuple:
        s = struct.Struct("<" + fmt * count)
        return s.unpack_from(self.data, self._need(s.size))

    def u16s(self, count: int) -> list[int]:
        return list(self.array("H", count)) if count else []

    def u32s(self, count: int) -> list[int]:
        return list(self.array("I", count)) if count else []

    def f32s(self, count: int) -> list[float]:
        return list(self.array("f", count)) if count else []

    def vec3(self) -> tuple[float, float, float]:
        return self.unpack("fff")  # type: ignore[return-value]

    def cstring_at(self, offset: int, max_len: int | None = None) -> str:
        """Read a NUL-terminated latin-1 string at an absolute offset."""
        end = self.data.find(b"\0", offset)
        if end < 0:
            end = len(self.data)
        if max_len is not None:
            end = min(end, offset + max_len)
        return self.data[offset:end].decode("latin-1")


class Writer:
    """Append-only byte builder with in-place patching.

    M2 and WMO writing is inherently two-pass: a struct is emitted with
    placeholder offsets, its payload is appended later, and the placeholder is
    patched once the payload's position is known.
    """

    __slots__ = ("buf",)

    def __init__(self) -> None:
        self.buf = bytearray()

    def __len__(self) -> int:
        return len(self.buf)

    def tell(self) -> int:
        return len(self.buf)

    def getvalue(self) -> bytes:
        return bytes(self.buf)

    # -- scalars --------------------------------------------------------
    def u8(self, v: int) -> None:
        self.buf += _U8.pack(v & 0xFF)

    def i8(self, v: int) -> None:
        self.buf += _I8.pack(v)

    def u16(self, v: int) -> None:
        self.buf += _U16.pack(v & 0xFFFF)

    def i16(self, v: int) -> None:
        self.buf += _I16.pack(v)

    def u32(self, v: int) -> None:
        self.buf += _U32.pack(v & 0xFFFFFFFF)

    def i32(self, v: int) -> None:
        self.buf += _I32.pack(v)

    def f32(self, v: float) -> None:
        self.buf += _F32.pack(v)

    # -- aggregates -----------------------------------------------------
    def raw(self, data: bytes | bytearray | memoryview) -> None:
        self.buf += data

    def magic(self, tag: str) -> None:
        """Write a 4CC exactly as given (callers pass the on-disk spelling)."""
        data = tag.encode("latin-1")
        if len(data) != 4:
            raise ValueError(f"magic must be 4 bytes, got {tag!r}")
        self.buf += data

    def pack(self, fmt: str, *values) -> None:
        self.buf += struct.pack("<" + fmt, *values)

    def array(self, fmt: str, values: Sequence) -> None:
        if values:
            self.buf += struct.pack("<" + fmt * len(values), *values)

    def u16s(self, values: Iterable[int]) -> None:
        self.array("H", list(values))

    def u32s(self, values: Iterable[int]) -> None:
        self.array("I", list(values))

    def f32s(self, values: Iterable[float]) -> None:
        self.array("f", list(values))

    def vec3(self, v: Sequence[float]) -> None:
        self.pack("fff", v[0], v[1], v[2])

    def zeros(self, count: int) -> None:
        self.buf += b"\0" * count

    def align(self, boundary: int = 4, pad: int = 0) -> int:
        """Pad to ``boundary`` and return the new position."""
        rem = len(self.buf) % boundary
        if rem:
            self.buf += bytes([pad]) * (boundary - rem)
        return len(self.buf)

    # -- patching -------------------------------------------------------
    def reserve(self, count: int) -> int:
        """Reserve ``count`` zero bytes and return their start offset."""
        pos = len(self.buf)
        self.buf += b"\0" * count
        return pos

    def patch_u32(self, pos: int, value: int) -> None:
        _U32.pack_into(self.buf, pos, value & 0xFFFFFFFF)

    def patch_u16(self, pos: int, value: int) -> None:
        _U16.pack_into(self.buf, pos, value & 0xFFFF)

    def patch_bytes(self, pos: int, data: bytes) -> None:
        self.buf[pos : pos + len(data)] = data
