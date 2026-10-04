"""WDT -- the per-map tile index.

Small file, but terrain is unusable without it: ``MAIN`` says which of the
64x64 tiles exist, and ``MPHD`` says how the client should read the ADTs it
finds. BfA added ``MAID``, which names every tile's files by FileDataID; 3.3.5a
derives those names from the map name instead, so ``MAID`` is dropped.

A map that is one big WMO (a dungeon, usually) places it with a single
``MODF`` entry.  Since BfA that entry names the WMO by FileDataID and ``MWMO``
is left out, which 3.3.5a cannot follow, so the name is looked up and written
back -- the same repair terrain tiles get, see :mod:`.placements`.

One flag matters more than the rest. ``MPHD.flags & 0x4`` ("big alpha") tells
the client that ``MCAL`` holds 8-bit alpha maps rather than 4-bit ones.
Cataclysm and later always write the 8-bit form, so a converted map needs that
bit set or every terrain texture blend comes out wrong -- the converter sets it
and says so.
"""

from __future__ import annotations

import struct
import time

from ..chunks import Chunk, ChunkReader, ChunkWriter, report_unknown
from ..errors import MalformedFileError, UnsupportedFormatError
from ..limits import ADT_VERSION
from ..listfile import Listfile
from ..options import Options
from ..report import FileResult, Status
from .placements import WMOS, rebuild_placements, restrict_placements

MPHD_SIZE = 32
MAIN_SIZE = 64 * 64 * 8

#: MPHD flag bits 3.3.5a understands.
FLAG_GLOBAL_WMO = 0x0001
FLAG_ADT_HAS_MCCV = 0x0002
FLAG_ADT_HAS_BIG_ALPHA = 0x0004
FLAG_DOODAD_REFS_SORTED = 0x0008
WDT_FLAG_MASK = 0x000F

#: Post-Wrath chunks, with what each one carries.
MODERN_CHUNKS = {
    "MAID": "per-tile FileDataIDs for the ADT, texture and minimap files",
    "MANM": "map animation data",
    "MPL2": "point lights",
    "MPL3": "point lights",
    "MSLK": "light skybox references",
    "MTEX": "map-wide texture list",
    "MLTA": "light animations",
    "MWDR": "doodad references",
    "MWDS": "doodad sets",
    "MPLT": "legacy point lights",
}

KNOWN = {"MVER", "MPHD", "MAIN", "MWMO", "MODF"} | set(MODERN_CHUNKS)


def parse_wdt(data: bytes, name: str = "<wdt>") -> dict[str, Chunk]:
    if len(data) < 8:
        raise MalformedFileError(f"{name}: file is only {len(data)} bytes")
    chunks: dict[str, Chunk] = {}
    for chunk in ChunkReader.auto(data, KNOWN, name=name):
        chunks.setdefault(chunk.name, chunk)
    if "MPHD" not in chunks or "MAIN" not in chunks:
        raise UnsupportedFormatError(
            f"{name}: not a WDT (no MPHD/MAIN chunk)")
    return chunks


def _name_offsets(names: bytes) -> bytes:
    """An MWID-style offset table for a WDT's MWMO, which has none."""
    offsets = bytearray()
    at = 0
    for name in names.rstrip(b"\0").split(b"\0"):
        offsets += struct.pack("<I", at)
        at += len(name) + 1
    return bytes(offsets)


def convert_wdt(data: bytes, source_name: str, opts: Options,
                result: FileResult | None = None,
                listfile: Listfile | None = None) -> tuple[bytes, FileResult]:
    """Downgrade a WDT to the 3.3.5a layout."""
    started = time.time()
    listfile = listfile or Listfile()
    res = result or FileResult(source=source_name, kind="wdt")
    res.kind = "wdt"
    res.bytes_in = len(data)

    chunks = parse_wdt(data, source_name)
    modern = sorted(n for n in chunks if n in MODERN_CHUNKS)
    res.source_version = f"WDT, {len(chunks)} chunk kinds"

    mphd = bytearray(chunks["MPHD"].data[:MPHD_SIZE].ljust(MPHD_SIZE, b"\0"))
    flags = struct.unpack_from("<I", mphd, 0)[0]
    masked = flags & WDT_FLAG_MASK
    if masked != flags:
        res.info("wdt.flags",
                 f"cleared post-Wrath map flags "
                 f"0x{flags & ~WDT_FLAG_MASK:08X}")
    if not (masked & FLAG_ADT_HAS_BIG_ALPHA):
        masked |= FLAG_ADT_HAS_BIG_ALPHA
        res.info("wdt.big_alpha",
                 "set the big-alpha map flag: Cataclysm and later always write "
                 "8-bit MCAL alpha maps, and without this bit 3.3.5a reads them "
                 "as 4-bit and the terrain blends come out wrong")
    struct.pack_into("<I", mphd, 0, masked)
    # The words after the flags are a Cata+ FileDataID for the map's texture.
    struct.pack_into("<I", mphd, 4, 0)

    main = chunks["MAIN"].data
    if len(main) < MAIN_SIZE:
        res.warn("wdt.main",
                 f"MAIN is {len(main)} bytes, expected {MAIN_SIZE}; padded")
        main = main.ljust(MAIN_SIZE, b"\0")
    else:
        main = main[:MAIN_SIZE]
    tiles = sum(1 for i in range(0, MAIN_SIZE, 8)
                if struct.unpack_from("<I", main, i)[0] & 1)

    mwmo = chunks["MWMO"].data if "MWMO" in chunks else b""
    modf = chunks["MODF"].data if "MODF" in chunks else b""
    wmos = rebuild_placements(WMOS, mwmo, _name_offsets(mwmo) if mwmo else b"",
                              modf, opts, listfile, res, "wdt.wmo")
    if wmos is None:
        res.elapsed = time.time() - started
        return b"", res
    restricted = restrict_placements(WMOS, wmos, res, "wdt.wmo")
    mwmo, modf = wmos.names, wmos.entries
    if masked & FLAG_GLOBAL_WMO and not mwmo:
        res.warn("wdt.global_wmo",
                 "the map claims a global WMO but carries no MWMO filename to "
                 "load it by")

    mver = chunks.get("MVER")
    if mver is None or len(mver.data) < 4:
        res.warn("wdt.no_version",
                 f"map index has no readable MVER chunk; it was parsed as "
                 f"version {ADT_VERSION} regardless")
    else:
        version = struct.unpack_from("<I", mver.data, 0)[0]
        if version != ADT_VERSION:
            res.warn("wdt.version",
                     f"map index declares MVER {version}, not the "
                     f"{ADT_VERSION} every build from Wrath onwards writes; it "
                     f"was parsed as {ADT_VERSION} anyway, so check the result",
                     version=version)

    report_unknown(res, chunks, KNOWN, "map-index", "wdt.chunks.unknown")

    if modern:
        res.lossy("wdt.chunks.dropped",
                  "dropped chunks with no 3.3.5a equivalent: "
                  + ", ".join(f"{n} ({MODERN_CHUNKS[n]})" for n in modern),
                  chunks=modern)

    cw = ChunkWriter(reverse=True)
    cw.add("MVER", struct.pack("<I", ADT_VERSION))
    cw.add("MPHD", bytes(mphd))
    cw.add("MAIN", main)
    cw.add("MWMO", mwmo)   # always present, often empty
    if modf:
        cw.add("MODF", modf)
    out = cw.getvalue()

    res.bytes_out = len(out)
    res.target_version = f"WDT v{ADT_VERSION}, {tiles} tiles present"
    res.extra["tiles"] = tiles
    if (not modern and not wmos.changed and not restricted
            and res.status is Status.OK):
        res.status = Status.PASSTHROUGH
        res.info("wdt.passthrough", "already a 3.3.5a map index")
    res.elapsed = time.time() - started
    return out, res


def inspect_wdt(data: bytes, source_name: str) -> dict:
    chunks = parse_wdt(data, source_name)
    flags = struct.unpack_from("<I", chunks["MPHD"].data, 0)[0]
    main = chunks["MAIN"].data
    tiles = sum(1 for i in range(0, min(len(main), MAIN_SIZE), 8)
                if struct.unpack_from("<I", main, i)[0] & 1)
    return {
        "kind": "wdt",
        "flags": f"0x{flags:08X}",
        "global_wmo": bool(flags & FLAG_GLOBAL_WMO),
        "big_alpha": bool(flags & FLAG_ADT_HAS_BIG_ALPHA),
        "tiles_present": tiles,
        "chunks": sorted(chunks),
        "modern_chunks": sorted(n for n in chunks if n in MODERN_CHUNKS) or None,
        "wotlk_compatible": not any(n in MODERN_CHUNKS for n in chunks)
                            and bool(flags & FLAG_ADT_HAS_BIG_ALPHA),
    }
