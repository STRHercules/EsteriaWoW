"""The root table: FileDataID -> content key.

This is the file that makes FileDataIDs mean anything.  Three shapes exist:

*Pre-8.2* -- a bare sequence of blocks, each ``numRecords, contentFlags,
localeFlags`` followed by ID deltas, content keys and name hashes.

*8.2 and later* -- the same blocks behind a ``TSFM`` header, with name hashes
omitted when the block's content flags say so.  10.1.7 added an explicit
header-size/version prefix, which is detected rather than assumed.

*Header version 2* (11.1 onwards) -- the block header grows to 17 bytes and
reorders: ``numRecords, localeFlags, flags1, flags2, flags3:u8``.  The content
flags this reader needs sit in the first two words (platform and violence bits
in ``flags1``, no-name-hash in ``flags2``); the trailing byte is not
interpreted.

FileDataIDs are stored as deltas: ``id = previous + delta + 1``.

One FileDataID can be listed by several blocks -- per locale, a low-violence
variant beside the normal one, a macOS variant beside the Windows one -- and
the low-violence copy is not reliably listed last.  Blocks are therefore
ranked, and each FileDataID resolves to the best-ranked block that lists it
rather than to whichever came first.
"""

from __future__ import annotations

import struct

from .. import log
from ..errors import MalformedFileError

MAGIC = b"TSFM"

#: Locale bits in a root block's localeFlags.
LOCALE_ALL = 0xFFFFFFFF
LOCALE_EN_US = 0x2
LOCALE_EN_GB = 0x4
LOCALE_NAMES = {
    "enus": 0x2, "engb": 0x4, "krkr": 0x20, "frfr": 0x10, "dede": 0x8,
    "zhcn": 0x40, "eses": 0x80, "zhtw": 0x100, "esmx": 0x200, "ruru": 0x400,
    "ptbr": 0x800, "itit": 0x1000, "ptpt": 0x2000,
}

#: Content flag meaning "this block stores no name hashes".
CONTENT_NO_NAME_HASH = 0x10000000
CONTENT_LOAD_ON_WINDOWS = 0x8
CONTENT_LOAD_ON_MACOS = 0x10
CONTENT_LOW_VIOLENCE = 0x80

#: Size of the header that 10.1.7 put in front of the blocks.
HEADER_SIZE = 0x18


def _rank(content_flags: int, locale_flags: int, locale: int) -> int:
    """Lower is better: the wanted locale, then full violence, then Windows."""
    rank = 0
    if not (locale_flags == LOCALE_ALL or locale_flags & locale
            or locale_flags == 0):
        rank |= 4
    if content_flags & CONTENT_LOW_VIOLENCE:
        rank |= 2
    if (content_flags & CONTENT_LOAD_ON_MACOS
            and not content_flags & CONTENT_LOAD_ON_WINDOWS):
        rank |= 1
    return rank


class RootTable:
    """FileDataID -> content key, resolved for a preferred locale."""

    __slots__ = ("_by_id", "blocks", "truncated", "version")

    def __init__(self) -> None:
        self._by_id: dict[int, bytes] = {}
        self.blocks = 0
        self.truncated = False
        self.version = 0

    def __len__(self) -> int:
        return len(self._by_id)

    def __contains__(self, file_id: int) -> bool:
        return file_id in self._by_id

    def ckey_for(self, file_id: int) -> bytes | None:
        return self._by_id.get(file_id)

    def file_ids(self):
        return self._by_id.keys()

    @classmethod
    def parse(cls, data: bytes, locale: int = LOCALE_EN_US,
              name: str = "<root>") -> RootTable:
        table = cls()
        pos = 0
        block_header = struct.Struct("<III")   # records, content, locale

        if len(data) >= 12 and data[:4] == MAGIC:
            first, second = struct.unpack_from("<II", data, 4)
            if first == HEADER_SIZE and len(data) >= HEADER_SIZE:
                # 10.1.7+: headerSize, version, totalFiles, namedFiles, pad
                _size, table.version, total_files, named_files = \
                    struct.unpack_from("<IIII", data, 4)
                if table.version not in (1, 2):
                    raise MalformedFileError(
                        f"{name}: root header version {table.version} is not "
                        f"one this reader understands (1 or 2)")
                if table.version == 2:
                    block_header = struct.Struct("<IIIIB")
                pos = HEADER_SIZE
            else:
                total_files, named_files = first, second
                pos = 12
            log.debug(f"{name}: MFST root v{table.version}, {total_files} "
                      f"files, {named_files} named")

        # Collect the blocks first, then fill best-ranked first, so that a
        # low-violence or macOS copy listed early cannot shadow the real one.
        found: list[tuple[int, int, int, int]] = []  # rank, order, records, pos
        while pos + block_header.size <= len(data):
            fields = block_header.unpack_from(data, pos)
            pos += block_header.size
            if table.version == 2:
                num_records, locale_flags, flags1, flags2, _flags3 = fields
                content_flags = flags1 | flags2
            else:
                # All unsigned: localeFlags is 0xFFFFFFFF for "every locale",
                # which read as -1 if these were signed.
                num_records, content_flags, locale_flags = fields
            if num_records == 0:
                continue
            keys_end = pos + num_records * 20
            if keys_end > len(data):
                table.truncated = True
                log.warn(f"{name}: root block claims {num_records} records but "
                         f"the file ends first; stopping after "
                         f"{table.blocks} block(s)")
                break
            found.append((_rank(content_flags, locale_flags, locale),
                          len(found), num_records, pos))
            pos = keys_end
            if not (content_flags & CONTENT_NO_NAME_HASH):
                # Name hashes are Jenkins hashes of the in-game path; this tool
                # resolves names through the listfile instead, so skip them.
                pos += num_records * 8
            table.blocks += 1

        by_id = table._by_id
        for _rank_, _order, num_records, start in sorted(found):
            deltas = struct.unpack_from(f"<{num_records}i", data, start)
            keys = start + num_records * 4
            file_id = -1
            for i, delta in enumerate(deltas):
                file_id += delta + 1
                if file_id not in by_id:
                    by_id[file_id] = data[keys + i * 16 : keys + i * 16 + 16]

        if not by_id:
            raise MalformedFileError(f"{name}: root table contains no files")
        return table
