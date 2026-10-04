"""3.3.5a client databases (``.dbc``).

The format is as simple as the modern one is not::

    char   magic[4] = 'WDBC'
    uint32 record_count
    uint32 field_count
    uint32 record_size      == the sum of the field widths
    uint32 string_block_size
    uint8  records[record_count][record_size]
    uint8  strings[string_block_size]

Nearly every field is four bytes, but not all: five of a 3.3.5a client's
tables pack some columns into single bytes (CharBaseInfo, CharStartOutfit,
PowerDisplay, SpellChainEffects, SpellItemEnchantmentCondition), and the
header records only the total.  The definitions' widths reproduce the record
size of every one of a clean client's 245 tables, so a caller that knows the
layout passes ``field_sizes``; without it the four-byte layout is required.
Nothing in the file says whether a field is an int, a float or an offset into
the string block either -- the client knows, and any tool has to be told.

That matters for merging. When new rows are appended to a table the user
already has, this module **keeps the original records and string block byte for
byte and appends to them**. Existing string offsets stay valid, so the merge
needs to know the types only of the fields it actually writes, never of the
ones it copies through. Getting a field type wrong elsewhere in the row cannot
corrupt anything.
"""

from __future__ import annotations

import dataclasses
import struct
from typing import Any

from ..errors import MalformedFileError, UnsupportedFormatError

MAGIC = b"WDBC"
HEADER_SIZE = 20
FIELD_SIZE = 4

#: Field types a mapping can declare for a column it writes.
TYPES = ("int", "uint", "float", "string")


@dataclasses.dataclass
class DbcTable:
    """A parsed ``.dbc``, kept as raw words plus the untouched string block."""

    field_count: int = 0
    record_size: int = 0
    records: list[bytes] = dataclasses.field(default_factory=list)
    strings: bytes = b"\0"
    #: Bytes per field, when not all four.
    field_sizes: list[int] | None = None

    def __len__(self) -> int:
        return len(self.records)

    def _slot(self, index: int) -> tuple[int, int]:
        """``(byte offset, width)`` of field ``index`` within a record."""
        if self.field_sizes is None:
            return index * FIELD_SIZE, FIELD_SIZE
        return sum(self.field_sizes[:index]), self.field_sizes[index]

    @classmethod
    def parse(cls, data: bytes, name: str = "<dbc>",
              field_sizes: list[int] | None = None) -> DbcTable:
        if len(data) < HEADER_SIZE:
            raise MalformedFileError(f"{name}: file is only {len(data)} bytes")
        if data[:4] != MAGIC:
            raise UnsupportedFormatError(
                f"{name}: not a 3.3.5a .dbc (magic {data[:4]!r})")
        record_count, field_count, record_size, string_size = struct.unpack_from(
            "<4I", data, 4)
        if field_sizes is not None and all(s == FIELD_SIZE for s in field_sizes):
            field_sizes = None
        if field_sizes is not None:
            if len(field_sizes) != field_count or sum(field_sizes) != record_size:
                raise MalformedFileError(
                    f"{name}: {field_count} fields in {record_size}-byte records "
                    f"do not match the layout's {len(field_sizes)} fields in "
                    f"{sum(field_sizes)} bytes")
        elif field_count and record_size != field_count * FIELD_SIZE:
            raise MalformedFileError(
                f"{name}: record size {record_size} does not match "
                f"{field_count} four-byte fields")
        start = HEADER_SIZE
        end = start + record_count * record_size
        if end > len(data):
            raise MalformedFileError(
                f"{name}: {record_count} records of {record_size} bytes run "
                f"past the end of the file")
        table = cls(field_count=field_count, record_size=record_size,
                    field_sizes=list(field_sizes) if field_sizes else None)
        table.records = [data[start + i * record_size:
                              start + (i + 1) * record_size]
                         for i in range(record_count)]
        table.strings = data[end : end + string_size] or b"\0"
        return table

    # -- typed access ---------------------------------------------------
    def word(self, row: int, index: int) -> int:
        at, width = self._slot(index)
        return int.from_bytes(self.records[row][at:at + width], "little")

    def value(self, row: int, index: int, kind: str) -> Any:
        at, width = self._slot(index)
        raw = self.records[row][at:at + width]
        if kind == "float":
            return struct.unpack("<f", raw)[0]
        if kind == "int":
            return int.from_bytes(raw, "little", signed=True)
        if kind == "string":
            return self.string_at(int.from_bytes(raw, "little"))
        return int.from_bytes(raw, "little")

    def string_at(self, offset: int) -> str:
        if offset <= 0 or offset >= len(self.strings):
            return ""
        end = self.strings.find(b"\0", offset)
        if end < 0:
            end = len(self.strings)
        return self.strings[offset:end].decode("latin-1")

    def ids(self, index: int = 0) -> list[int]:
        return [self.word(r, index) for r in range(len(self.records))]

    def serialize(self) -> bytes:
        out = bytearray(MAGIC)
        out += struct.pack("<4I", len(self.records), self.field_count,
                           self.record_size, len(self.strings))
        for record in self.records:
            out += record.ljust(self.record_size, b"\0")[:self.record_size]
        out += self.strings
        return bytes(out)


class DbcBuilder:
    """Builds a ``.dbc``, optionally on top of an existing one.

    Starting from a template keeps that table's records and string block
    untouched; new strings are appended so every offset already in the file
    stays correct.
    """

    def __init__(self, field_count: int, template: DbcTable | None = None,
                 field_sizes: list[int] | None = None):
        if field_count <= 0:
            raise ValueError("a .dbc needs at least one field")
        if field_sizes is not None and all(s == FIELD_SIZE for s in field_sizes):
            field_sizes = None
        if field_sizes is not None and len(field_sizes) != field_count:
            raise ValueError(f"{len(field_sizes)} field sizes for "
                             f"{field_count} fields")
        self.field_count = field_count
        self.field_sizes = list(field_sizes) if field_sizes else None
        self._offsets = ([sum(field_sizes[:i]) for i in range(field_count)]
                         if field_sizes else
                         [i * FIELD_SIZE for i in range(field_count)])
        self.record_size = sum(field_sizes) if field_sizes else field_count * FIELD_SIZE
        self.template = template
        if template is not None:
            if template.field_count != field_count:
                raise MalformedFileError(
                    f"template has {template.field_count} fields but the "
                    f"mapping describes {field_count}; one of them is wrong "
                    f"for this client build")
            if template.record_size != self.record_size:
                raise MalformedFileError(
                    f"template records are {template.record_size} bytes but "
                    f"the layout's fields add up to {self.record_size}")
            self.records: list[bytearray] = [bytearray(r) for r in template.records]
            self._strings = bytearray(template.strings or b"\0")
        else:
            self.records = []
            self._strings = bytearray(b"\0")
        self._string_offsets: dict[str, int] = {}
        self._row_index: dict[int, int] = {}

    # -- strings --------------------------------------------------------
    def intern(self, text: str) -> int:
        """Append a string and return its offset; the empty string is 0."""
        if not text:
            return 0
        hit = self._string_offsets.get(text)
        if hit is not None:
            return hit
        offset = len(self._strings)
        self._strings += text.encode("latin-1", errors="replace") + b"\0"
        self._string_offsets[text] = offset
        return offset

    # -- rows -----------------------------------------------------------
    def index_existing(self, id_index: int = 0) -> None:
        """Note where each existing row's id lives, so rows can be replaced."""
        at, width = self._offsets[id_index], self._width(id_index)
        for position, record in enumerate(self.records):
            if len(record) >= at + width:
                row_id = int.from_bytes(record[at:at + width], "little")
                self._row_index[row_id] = position

    def _width(self, index: int) -> int:
        return self.field_sizes[index] if self.field_sizes else FIELD_SIZE

    def encode(self, values: dict[int, tuple[str, Any]]) -> bytearray:
        """Pack ``{field index: (type, value)}`` into one record."""
        record = bytearray(self.record_size)
        for index, (kind, value) in values.items():
            if index < 0 or index >= self.field_count:
                raise MalformedFileError(
                    f"field index {index} is outside the table's "
                    f"{self.field_count} fields")
            at, width = self._offsets[index], self._width(index)
            if kind in ("float", "string") and width != FIELD_SIZE:
                raise MalformedFileError(
                    f"field {index} is {width} byte(s) wide, which cannot hold "
                    f"a {kind}")
            if kind == "float":
                struct.pack_into("<f", record, at, float(value))
            elif kind == "string":
                struct.pack_into("<I", record, at, self.intern(str(value)))
            else:
                # Same bits either way: a modern unsigned column holding a
                # value past 2^31 lands in a Wrath column the client reads as
                # signed, and a byte column keeps the low byte.
                bits = int(value) & ((1 << (8 * width)) - 1)
                record[at:at + width] = bits.to_bytes(width, "little")
        return record

    def add(self, values: dict[int, tuple[str, Any]], row_id: int | None = None,
            id_index: int = 0, replace: bool = True) -> bool:
        """Append a row, or replace one with the same id. Returns True if new."""
        record = self.encode(values)
        if row_id is None:
            at, width = self._offsets[id_index], self._width(id_index)
            row_id = int.from_bytes(record[at:at + width], "little")
        existing = self._row_index.get(row_id)
        if existing is not None and replace:
            self.records[existing] = record
            return False
        self._row_index[row_id] = len(self.records)
        self.records.append(record)
        return True

    def has(self, row_id: int) -> bool:
        return row_id in self._row_index

    def build(self) -> DbcTable:
        table = DbcTable(field_count=self.field_count,
                         record_size=self.record_size,
                         field_sizes=self.field_sizes)
        table.records = [bytes(r) for r in self.records]
        table.strings = bytes(self._strings)
        return table

    def serialize(self) -> bytes:
        return self.build().serialize()


def inspect_dbc(data: bytes, source_name: str) -> dict:
    table = DbcTable.parse(data, source_name)
    return {
        "kind": "dbc",
        "records": len(table.records),
        "fields": table.field_count,
        "record_size": table.record_size,
        "string_block": len(table.strings),
        "wotlk_compatible": True,
    }


