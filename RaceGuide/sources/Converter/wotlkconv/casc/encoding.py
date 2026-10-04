"""The encoding table: content key -> encoding key.

Everything else in CASC names files by *content* key (the MD5 of the file's
bytes), but the archives are indexed by *encoding* key (the MD5 of the BLTE
stream those bytes are stored as).  The encoding table is the bridge, and it is
itself stored BLTE-encoded and referenced by EKey, which is why the build
config lists both keys for it.

Layout (all multi-byte fields big-endian)::

    char   magic[2] = "EN"
    uint8  version, cKeySize, eKeySize
    uint16 cKeyPageKiB, eKeyPageKiB
    uint32 cKeyPageCount, eKeyPageCount
    uint8  unused
    uint32 especBlockSize
    char   espec[especBlockSize]
    struct { uint8 firstKey[cKeySize]; uint8 pageMd5[16]; } cKeyPageIndex[...]
    uint8  cKeyPages[cKeyPageCount][cKeyPageKiB * 1024]

Each page holds entries of ``uint8 keyCount; uint40 fileSize; cKey; eKey*n``
until a zero ``keyCount`` marks the end of the page.
"""

from __future__ import annotations

import struct

from ..errors import MalformedFileError

MAGIC = b"EN"


class EncodingTable:
    """Content key -> (encoding key, decoded file size)."""

    __slots__ = ("_map", "espec")

    def __init__(self) -> None:
        self._map: dict[bytes, tuple[bytes, int]] = {}
        self.espec: bytes = b""

    def __len__(self) -> int:
        return len(self._map)

    def __contains__(self, ckey: bytes) -> bool:
        return ckey in self._map

    def ekey_for(self, ckey: bytes) -> bytes | None:
        hit = self._map.get(ckey)
        return hit[0] if hit else None

    def size_for(self, ckey: bytes) -> int | None:
        hit = self._map.get(ckey)
        return hit[1] if hit else None

    @classmethod
    def parse(cls, data: bytes, name: str = "<encoding>") -> EncodingTable:
        if len(data) < 22 or data[:2] != MAGIC:
            raise MalformedFileError(
                f"{name}: not an encoding table (magic {data[:2]!r})")
        (version, ckey_size, ekey_size, ckey_page_kib, _ekey_page_kib,
         ckey_page_count, _ekey_page_count, _unused,
         espec_size) = struct.unpack_from(">BBBHHIIBI", data, 2)
        if version != 1:
            raise MalformedFileError(
                f"{name}: encoding version {version}, this reader handles 1")

        table = cls()
        pos = 22
        table.espec = data[pos : pos + espec_size]
        pos += espec_size

        # Skip the page index; the pages themselves carry every key.
        pos += ckey_page_count * (ckey_size + 16)
        page_size = ckey_page_kib * 1024
        entry_head = 1 + 5 + ckey_size

        for _page in range(ckey_page_count):
            end = min(pos + page_size, len(data))
            p = pos
            while p + entry_head <= end:
                key_count = data[p]
                if key_count == 0:
                    break
                file_size = int.from_bytes(data[p + 1 : p + 6], "big")
                ckey = data[p + 6 : p + 6 + ckey_size]
                ekeys_at = p + 6 + ckey_size
                needed = ekeys_at + ekey_size * key_count
                if needed > end:
                    break
                # The first EKey is the one the archives are indexed by; the
                # rest are alternative encodings of the same content.
                table._map[ckey] = (data[ekeys_at : ekeys_at + ekey_size],
                                    file_size)
                p = needed
            pos += page_size
            if pos >= len(data):
                break
        return table
