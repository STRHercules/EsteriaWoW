"""Liquid volumes -- ``.wlw``, ``.wlm`` and ``.wlq``.

Retail ships a handful of these beside its maps, and **3.3.5a never loads
them.**  It takes liquid from each terrain tile's ``MCLQ``/``MH2O`` and each
world object's ``MLIQ``; none of its archives contains a liquid volume, and its
executable has no file name pattern that could ask for one (it has the ones for
``.adt`` and ``.wdt``).  So they are recognised -- by signature, since retail's
are unnamed -- and skipped with that reason, never converted or copied.

This module still reads the header, for ``inspect`` and for the report.  The
layout below is proven on every liquid volume in 12.1.0.69814 (106 files) and
MoP Classic 5.5.4 (1): each is exactly ``16 + 360 x blocks + 4 + 76 x
secondary blocks + 1`` bytes, and a version 2 file with no blocks is a valid
21 bytes.  Versions 0 and 1 are not present in any build or client available to
check, so their trailing layout is not enforced.

======  ======  =============================================================
offset  type    field
======  ======  =============================================================
0x00    4s      magic ``*QIL`` (``LIQ*`` reversed; both are accepted)
0x04    u16     version
0x06    u16     unknown -- 1 in every real file
0x08    u16     liquid type: a ``LiquidType`` row id
0x0A    u16     padding
0x0C    u32     block count, then 360-byte blocks
..      u32     secondary block count, then 76-byte blocks
..      u8      trailing byte (version 2)
======  ======  =============================================================
"""

from __future__ import annotations

import dataclasses
import struct

from .errors import MalformedFileError, UnsupportedFormatError

#: The signature, in both byte orders.
LIQUID_MAGICS = (b"LIQ*", b"*QIL")

HEADER = struct.Struct("<4sHHHHI")
BLOCK_SIZE = 360
SECONDARY_BLOCK_SIZE = 76

#: Why no liquid volume goes into a 3.3.5a patch.
SKIP_REASON = ("a liquid volume; 3.3.5a takes its liquid from each terrain "
               "tile's MCLQ/MH2O and each world object's MLIQ, ships no liquid "
               "volumes in any of its archives and has no file name to ask for "
               "one, so it never loads the file")


@dataclasses.dataclass(slots=True)
class LiquidHeader:
    version: int
    liquid_type: int
    blocks: int
    secondary_blocks: int
    #: Bytes after the secondary blocks; 1 in every real version 2 file.
    trailing: int


def parse_header(data: bytes, name: str = "<liquid>") -> LiquidHeader:
    """Read a liquid volume's header and check its blocks fit the file."""
    if len(data) < HEADER.size:
        raise MalformedFileError(
            f"{name}: file is {len(data)} bytes, too short for a liquid header")
    magic, version, _unknown, liquid_type, _pad, blocks = HEADER.unpack_from(data)
    if magic not in LIQUID_MAGICS:
        raise UnsupportedFormatError(
            f"{name}: not a liquid volume -- expected {LIQUID_MAGICS[1]!r}, "
            f"found {magic!r}")
    pos = HEADER.size + blocks * BLOCK_SIZE
    if pos + 4 > len(data):
        raise MalformedFileError(
            f"{name}: {blocks} liquid block(s) of {BLOCK_SIZE} bytes do not fit "
            f"in {len(data)} bytes")
    secondary = struct.unpack_from("<I", data, pos)[0]
    pos += 4 + secondary * SECONDARY_BLOCK_SIZE
    if pos > len(data):
        raise MalformedFileError(
            f"{name}: {secondary} secondary liquid block(s) run past the end "
            f"of the file")
    return LiquidHeader(version, liquid_type, blocks, secondary, len(data) - pos)


def inspect_liquid(data: bytes, source_name: str) -> dict:
    try:
        header = parse_header(data, source_name)
    except (MalformedFileError, UnsupportedFormatError):
        return {"kind": "liquid", "readable": False, "bytes": len(data)}
    return {
        "kind": "liquid",
        "version": header.version,
        "liquid_type": header.liquid_type,
        "blocks": header.blocks,
        "secondary_blocks": header.secondary_blocks,
        "trailing_bytes": header.trailing,
        "loaded_by_wotlk": False,
        "bytes": len(data),
    }
