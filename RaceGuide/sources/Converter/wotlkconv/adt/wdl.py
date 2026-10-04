"""Low-resolution terrain heightmaps.

A ``.wdl`` is what the client draws where the real terrain has not been
streamed in yet -- the far-off hills on the horizon.  One 17x17 grid of
16-bit heights, plus the 16x16 grid that sits between those points, stands in
for each of the map's 64x64 tiles.

That part did not change.  ``MAOF`` still indexes the map, ``MARE`` still
holds the two grids, ``MAHO`` still masks out holes.  What Legion added is a
second, unrelated thing living in the same file: the ``ML*`` chunks, which
carry a real LOD mesh -- vertices, indices, skirts, and their own copies of
the doodad and WMO placements -- for a renderer 3.3.5a does not have.

So converting one is a matter of keeping the three chunks that still mean
something and dropping the rest.  The catch is ``MAOF``: its 4096 entries are
absolute file offsets, so dropping anything ahead of the ``MARE`` blocks moves
every one of them and they all have to be rewritten.  Wrath also expects the
low-detail WMO tables, which Legion stopped writing; empty ones are emitted in
their place so the file has the shape the old client reads.
"""

from __future__ import annotations

import struct
import time

from ..chunks import ChunkReader
from ..errors import MalformedFileError, UnsupportedFormatError
from ..options import Options
from ..report import FileResult, Status

#: 3.3.5a writes 18 here, as it does for ADT and WDT.
WDL_VERSION = 18

#: MAOF is one offset per map tile.
MAOF_SIDE = 64
MAOF_ENTRIES = MAOF_SIDE * MAOF_SIDE

#: MARE is a 17x17 outer grid followed by the 16x16 grid between its points.
MARE_VALUES = 17 * 17 + 16 * 16
MARE_SIZE = MARE_VALUES * 2

#: MAHO is one 16-bit hole mask per row of the inner grid.
MAHO_SIZE = 16 * 2

#: Chunks 3.3.5a reads, in the order it expects them.
WOTLK_CHUNKS = ("MVER", "MWMO", "MWID", "MODF")

#: The Legion LOD mesh, which has no 3.3.5a equivalent, and what each part is.
MODERN_CHUNKS = {
    "MLHD": "LOD mesh header",
    "MLVH": "LOD mesh vertex heights",
    "MLVI": "LOD mesh vertex indices",
    "MLLL": "LOD level table",
    "MLND": "LOD quad tree nodes",
    "MLSI": "LOD skirt indices",
    "MLLD": "LOD liquid data",
    "MLLN": "LOD liquid nodes",
    "MLLV": "LOD liquid vertices",
    "MLLI": "LOD liquid indices",
    "MLMD": "LOD WMO placements",
    "MLMX": "LOD WMO bounds",
    "MLDD": "LOD doodad placements",
    "MLDX": "LOD doodad bounds",
    "MLDL": "LOD doodad levels",
    "MLFD": "LOD level offsets",
    "MBMH": "blend mesh headers",
    "MBBB": "blend mesh bounding boxes",
    "MBNV": "blend mesh vertices",
    "MBMI": "blend mesh indices",
}


def _read_chunks(data: bytes, name: str) -> tuple[dict[str, bytes], list[str]]:
    """Top-level chunks by name, first occurrence wins, plus the order seen."""
    found: dict[str, bytes] = {}
    order: list[str] = []
    for chunk in ChunkReader.auto(data, {"MVER", "MAOF", "MARE"}, name=name):
        order.append(chunk.name)
        found.setdefault(chunk.name, chunk.data)
    return found, order


def _tile_blocks(data: bytes, maof: bytes, name: str,
                 res: FileResult) -> dict[int, tuple[bytes, bytes]]:
    """The ``(MARE, MAHO)`` pair each map tile points at, by tile index.

    MAOF holds absolute offsets to the MARE chunk header; MAHO, when a tile has
    one, follows immediately after.  An offset that does not land on a MARE is
    reported and skipped rather than trusted.
    """
    blocks: dict[int, tuple[bytes, bytes]] = {}
    bad = 0
    for index in range(MAOF_ENTRIES):
        offset = struct.unpack_from("<I", maof, index * 4)[0]
        if not offset:
            continue
        if offset + 8 > len(data):
            bad += 1
            continue
        magic = data[offset:offset + 4]
        size = struct.unpack_from("<I", data, offset + 4)[0]
        if magic not in (b"MARE", b"ERAM") or offset + 8 + size > len(data):
            bad += 1
            continue
        mare = data[offset + 8:offset + 8 + size]
        if len(mare) != MARE_SIZE:
            bad += 1
            continue

        maho = b""
        after = offset + 8 + size
        if after + 8 <= len(data) and data[after:after + 4] in (b"MAHO", b"OHAM"):
            maho_size = struct.unpack_from("<I", data, after + 4)[0]
            if after + 8 + maho_size <= len(data) and maho_size == MAHO_SIZE:
                maho = data[after + 8:after + 8 + maho_size]
        blocks[index] = (mare, maho)

    if bad:
        res.lossy("wdl.tiles.unreadable",
                  f"{bad} of the map's tiles had a heightmap offset that did "
                  f"not lead to a {MARE_SIZE}-byte MARE, so those tiles were "
                  f"left empty; the client draws no distant terrain there",
                  tiles=bad)
    return blocks


def convert_wdl(data: bytes, source_name: str, opts: Options,
                result: FileResult | None = None) -> tuple[bytes, FileResult]:
    """Strip a modern ``.wdl`` back to the three chunks 3.3.5a reads."""
    started = time.time()
    res = result or FileResult(source=source_name, kind="wdl")
    res.kind = "wdl"
    res.bytes_in = len(data)

    found, order = _read_chunks(data, source_name)
    if "MAOF" not in found:
        raise UnsupportedFormatError(
            f"{source_name}: not a .wdl -- no MAOF chunk (found "
            f"{', '.join(order[:6]) or 'nothing'})")
    maof = found["MAOF"]
    if len(maof) < MAOF_ENTRIES * 4:
        raise MalformedFileError(
            f"{source_name}: MAOF is {len(maof)} bytes, not the "
            f"{MAOF_ENTRIES * 4} a 64x64 map needs")

    version = (struct.unpack_from("<I", found["MVER"], 0)[0]
               if len(found.get("MVER", b"")) >= 4 else 0)
    res.source_version = f"WDL v{version}" + (" + LOD mesh" if any(
        n in MODERN_CHUNKS for n in order) else "")
    if version != WDL_VERSION:
        res.warn("wdl.version",
                 f"heightmap declares MVER {version}, not the {WDL_VERSION} "
                 f"every build from Wrath onwards writes; it was parsed as "
                 f"{WDL_VERSION} anyway, so check the result",
                 version=version)

    blocks = _tile_blocks(data, maof, source_name, res)

    modern = [n for n in order if n in MODERN_CHUNKS]
    if modern:
        res.lossy("wdl.chunks.dropped",
                  "dropped the Legion LOD mesh, which 3.3.5a has no renderer "
                  "for: " + ", ".join(f"{n} ({MODERN_CHUNKS[n]})"
                                      for n in sorted(set(modern))),
                  chunks=sorted(set(modern)))
    unknown = [n for n in order
               if n not in MODERN_CHUNKS and n not in WOTLK_CHUNKS
               and n not in ("MAOF", "MARE", "MAHO")]
    if unknown:
        res.lossy("wdl.chunks.unknown",
                  "dropped chunks this tool does not recognise: "
                  + ", ".join(sorted(set(unknown))),
                  chunks=sorted(set(unknown)))

    out = bytearray()

    def add(name: str, payload: bytes) -> int:
        """Append a chunk and return where its header starts."""
        at = len(out)
        out.extend(name[::-1].encode("latin-1"))
        out.extend(struct.pack("<I", len(payload)))
        out.extend(payload)
        return at

    add("MVER", struct.pack("<I", WDL_VERSION))
    # Legion stopped writing the low-detail WMO tables; Wrath still looks for
    # them, so empty ones keep the file the shape the old client reads.
    for name in ("MWMO", "MWID", "MODF"):
        add(name, found.get(name, b""))

    maof_at = add("MAOF", b"\0" * (MAOF_ENTRIES * 4))
    maof_data = maof_at + 8

    for index in sorted(blocks):
        mare, maho = blocks[index]
        struct.pack_into("<I", out, maof_data + index * 4, add("MARE", mare))
        if maho:
            add("MAHO", maho)

    res.target_version = f"WDL v{WDL_VERSION}"
    res.bytes_out = len(out)
    res.extra.update({
        "tiles": len(blocks),
        "holes": sum(1 for _mare, maho in blocks.values() if maho),
        "dropped_chunks": sorted(set(modern)),
    })
    res.info("wdl.converted",
             f"kept the low-resolution heightmap for {len(blocks)} of "
             f"{MAOF_ENTRIES} map tiles")
    if res.status is Status.OK and not modern and not unknown:
        res.status = Status.OK
    res.elapsed = time.time() - started
    return bytes(out), res


def inspect_wdl(data: bytes, source_name: str) -> dict:
    found, order = _read_chunks(data, source_name)
    maof = found.get("MAOF", b"")
    tiles = sum(1 for i in range(min(MAOF_ENTRIES, len(maof) // 4))
                if struct.unpack_from("<I", maof, i * 4)[0])
    return {
        "kind": "wdl",
        "version": (struct.unpack_from("<I", found["MVER"], 0)[0]
                    if len(found.get("MVER", b"")) >= 4 else None),
        "chunks": order,
        "tiles_with_terrain": tiles,
        "lod_mesh": sorted({n for n in order if n in MODERN_CHUNKS}) or None,
        "bytes": len(data),
    }
