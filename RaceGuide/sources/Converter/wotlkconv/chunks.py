"""Generic IFF-style chunk handling.

Every chunked Blizzard format uses the same physical layout::

    char     magic[4]
    uint32   size
    uint8    data[size]

The catch is the spelling of ``magic``.  ADT/WDT/WMO store it byte-reversed
("REVM" for ``MVER``), while the M2 chunk table introduced in Legion stores it
in reading order ("MD21").  Rather than hard-coding a guess per format, a
:class:`ChunkReader` can be told which convention to use, or asked to work it
out from a set of names it expects to see.
"""

from __future__ import annotations

import dataclasses
from collections.abc import Iterable, Iterator, Sequence

from .binio import Reader
from .errors import MalformedFileError, TruncatedFileError


@dataclasses.dataclass(slots=True)
class Chunk:
    """One chunk, with its payload kept as a view into the parent buffer."""

    name: str            # logical name, e.g. "MVER"
    raw_name: str        # exactly the four bytes on disk
    offset: int          # file offset of the payload (after the 8-byte header)
    size: int
    data: bytes

    def reader(self, name: str | None = None) -> Reader:
        return Reader(self.data, name or self.name)


def reverse_magic(magic: str) -> str:
    return magic[::-1]


def _logical(raw: str, reverse: bool) -> str:
    return raw[::-1] if reverse else raw


def detect_reversal(data: bytes, known: Iterable[str]) -> bool:
    """Decide whether magics in ``data`` are stored byte-reversed.

    ``known`` is the set of logical chunk names the caller expects; the first
    chunk in the file is matched against it in both orientations.
    """
    if len(data) < 4:
        raise TruncatedFileError("buffer too short to contain a chunk header")
    known = {k.upper() for k in known}
    raw = data[:4].decode("latin-1")
    if raw.upper() in known:
        return False
    if raw[::-1].upper() in known:
        return True
    # Neither matches: fall back to the ADT/WMO convention, which is what most
    # unrecognised chunked files use.
    return True


class ChunkReader:
    """Sequential reader over a chunked buffer."""

    def __init__(self, data: bytes, *, reverse: bool = True,
                 name: str = "<memory>", start: int = 0):
        self.data = data
        self.reverse = reverse
        self.name = name
        self.start = start

    @classmethod
    def auto(cls, data: bytes, known: Iterable[str], *, name: str = "<memory>",
             start: int = 0) -> ChunkReader:
        return cls(data, reverse=detect_reversal(data[start:], known),
                   name=name, start=start)

    def __iter__(self) -> Iterator[Chunk]:
        data = self.data
        pos = self.start
        end = len(data)
        while pos + 8 <= end:
            raw = data[pos : pos + 4].decode("latin-1")
            size = int.from_bytes(data[pos + 4 : pos + 8], "little")
            body = pos + 8
            if body + size > end:
                # Blizzard occasionally ships a final chunk whose size runs past
                # EOF by a few bytes; clamp instead of refusing the whole file.
                if body >= end:
                    raise MalformedFileError(
                        f"{self.name}: chunk {raw!r} at {pos} claims {size} bytes "
                        f"but the file ends at {end}"
                    )
                size = end - body
            yield Chunk(_logical(raw, self.reverse), raw, body, size,
                        data[body : body + size])
            pos = body + size



class ChunkWriter:
    """Builds a chunked file, writing magics in the requested orientation."""

    def __init__(self, *, reverse: bool = True):
        self.reverse = reverse
        self.buf = bytearray()

    def add(self, name: str, payload: bytes | bytearray | memoryview) -> None:
        if len(name) != 4:
            raise ValueError(f"chunk name must be 4 characters, got {name!r}")
        raw = name[::-1] if self.reverse else name
        self.buf += raw.encode("latin-1")
        self.buf += len(payload).to_bytes(4, "little")
        self.buf += payload

    def extend(self, chunks: Sequence[tuple[str, bytes]]) -> None:
        for name, payload in chunks:
            self.add(name, payload)

    def getvalue(self) -> bytes:
        return bytes(self.buf)

    def __len__(self) -> int:
        return len(self.buf)


def report_unknown(result, seen: Iterable[str], known: Iterable[str],
                   what: str, code: str) -> list[str]:
    """Report chunks the converter has no knowledge of at all.

    Each converter already names the post-Wrath chunks it deliberately drops.
    This covers the other case: a chunk in neither list, which is either
    something Blizzard added after this tool was written or something nobody
    documented.  Dropping it is still the only option, but doing so without
    saying which chunk it was hides the one thing that would explain a tile or
    a model that does not look right.
    """
    known = set(known)
    extra = sorted({name for name in seen if name not in known})
    if extra:
        result.lossy(code,
                     f"dropped {len(extra)} {what} chunk(s) this tool does not "
                     f"recognise, so what they carried is unknown: "
                     + ", ".join(extra),
                     chunks=extra)
    return extra
