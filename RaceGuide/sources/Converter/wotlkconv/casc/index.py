"""Local CASC indices -- ``Data/data/*.idx``.

Each ``.idx`` covers one of sixteen buckets and maps the first nine bytes of an
EKey to a position inside a ``data.NNN`` archive.  Which bucket a key lives in
is derived from the key itself, so a lookup only ever has to parse one index
file; they are loaded lazily and cached.

Entry layout (18 bytes)::

    uint8  key[9]        first nine bytes of the EKey
    uint40 position      big-endian: top 10 bits archive number, low 30 offset
    uint32 size          little-endian, the whole archive entry incl. its header
"""

from __future__ import annotations

import dataclasses
import re
import struct
from pathlib import Path

from .. import log
from ..errors import MalformedFileError

#: ``<bucket:02x><version:08x>.idx``
_IDX_NAME = re.compile(r"^([0-9a-fA-F]{2})([0-9a-fA-F]{8})\.idx$")

#: Bytes of the entry header that precedes the BLTE stream in data.NNN.
ARCHIVE_ENTRY_HEADER = 30

KEY_PREFIX_BYTES = 9


def bucket_for(ekey: bytes) -> int:
    """Which ``.idx`` bucket an EKey belongs to."""
    i = 0
    for byte in ekey[:KEY_PREFIX_BYTES]:
        i ^= byte
    return (i & 0xF) ^ (i >> 4)


@dataclasses.dataclass(slots=True)
class IndexEntry:
    archive: int
    offset: int
    size: int


def parse_index(data: bytes, name: str = "<idx>") -> dict[bytes, IndexEntry]:
    """Parse one ``.idx`` file into ``key prefix -> location``."""
    if len(data) < 32:
        raise MalformedFileError(f"{name}: index is only {len(data)} bytes")

    header_hash_size = struct.unpack_from("<I", data, 0)[0]
    (version, _bucket, _extra, entry_size_bytes, entry_offset_bytes,
     entry_key_bytes, archive_offset_bits, _max) = struct.unpack_from(
        "<HBBBBBBQ", data, 8)
    if version != 7:
        raise MalformedFileError(
            f"{name}: index version {version}, this reader handles 7")

    # The entry table header starts at the next 16-byte boundary after the
    # file header.
    pos = (8 + header_hash_size + 0x0F) & ~0x0F
    entries_size = struct.unpack_from("<I", data, pos)[0]
    pos += 8  # size + hash

    stride = entry_key_bytes + entry_offset_bytes + entry_size_bytes
    if stride <= 0:
        raise MalformedFileError(f"{name}: index declares a zero-length entry")
    count = min(entries_size // stride, (len(data) - pos) // stride)

    offset_mask = (1 << archive_offset_bits) - 1
    out: dict[bytes, IndexEntry] = {}
    for _ in range(count):
        key = data[pos : pos + entry_key_bytes]
        raw = int.from_bytes(data[pos + entry_key_bytes:
                                  pos + entry_key_bytes + entry_offset_bytes],
                             "big")
        size = int.from_bytes(
            data[pos + entry_key_bytes + entry_offset_bytes: pos + stride],
            "little")
        pos += stride
        if size == 0:
            continue
        out[key] = IndexEntry(raw >> archive_offset_bits, raw & offset_mask, size)
    return out


class LocalIndex:
    """Lazily-loaded view over every bucket in ``Data/data``."""

    def __init__(self, data_dir: Path):
        self.data_dir = Path(data_dir)
        self._buckets: dict[int, dict[bytes, IndexEntry]] = {}
        self._files = self._newest_per_bucket()

    def _newest_per_bucket(self) -> dict[int, Path]:
        """Installs keep several generations of each bucket; use the newest."""
        newest: dict[int, tuple[int, Path]] = {}
        if not self.data_dir.is_dir():
            return {}
        for path in self.data_dir.glob("*.idx"):
            m = _IDX_NAME.match(path.name)
            if not m:
                continue
            bucket = int(m.group(1), 16)
            version = int(m.group(2), 16)
            if bucket not in newest or version > newest[bucket][0]:
                newest[bucket] = (version, path)
        return {b: p for b, (_v, p) in newest.items()}

    @property
    def bucket_count(self) -> int:
        return len(self._files)

    def _load(self, bucket: int) -> dict[bytes, IndexEntry]:
        cached = self._buckets.get(bucket)
        if cached is not None:
            return cached
        path = self._files.get(bucket)
        if path is None:
            self._buckets[bucket] = {}
            return self._buckets[bucket]
        entries = parse_index(path.read_bytes(), path.name)
        log.debug(f"loaded {len(entries)} entries from {path.name}")
        self._buckets[bucket] = entries
        return entries

    def find(self, ekey: bytes) -> IndexEntry | None:
        prefix = ekey[:KEY_PREFIX_BYTES]
        return self._load(bucket_for(ekey)).get(prefix)

    def total_entries(self) -> int:
        """Load every bucket and count. Only used by ``casc info``."""
        return sum(len(self._load(b)) for b in self._files)
