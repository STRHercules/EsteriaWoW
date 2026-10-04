"""Terrain tiles.

Cataclysm split each ADT into four files -- ``Zone_32_48.adt`` for heights,
``_tex0`` for texture layers, ``_obj0`` for doodad and WMO placements, plus LOD
variants.  3.3.5a reads one monolithic tile with an ``MCIN`` index, which
Cataclysm dropped because it no longer needed it.

Merging them back means walking all 256 map chunks in lockstep across the three
files, reassembling each ``MCNK`` from pieces that now live in different
places, and recomputing every offset:

* ``MCNK`` sub-chunk offsets are relative to the start of the chunk *including*
  its 8-byte header, so they all move.
* ``MCRD`` (doodad refs) and ``MCRW`` (WMO refs) concatenate back into a single
  ``MCRF``, with the two counts written into the chunk header.
* ``MCIN`` has to be built from scratch.
* ``MHDR``'s offsets, which are relative to the start of its own payload, are
  rewritten to match the new layout.
* Doodad and WMO placements that name their asset by FileDataID get the name
  tables back (:mod:`.placements`), because 3.3.5a can only follow a name.
* Liquid instances are re-encoded in the vertex formats 3.3.5a reads
  (:mod:`.mh2o`).

Cataclysm's high-resolution 8x8 hole mask is folded down to the 4x4 mask Wrath
renders, and the chunks that only exist after Wrath are dropped.

One detail of ``MCIN`` has two readings.  Each entry gives the file offset of
an ``MCNK`` and a size, and the size is either the chunk's payload or that
payload plus the 8-byte chunk header.  The offset is unambiguous -- it points
at the header -- so a reader that seeks there and then trusts the chunk's own
size field, as the client does, cannot be misled either way; only a tool that
takes ``MCIN``'s size as the extent of the chunk can be.  For that reader the
header-inclusive value is the safe one: it spans the whole chunk, where the
payload-only value would stop 8 bytes short and cut off the end of the last
sub-chunk.  So that is the default.  It is not left as a guess, though: point
``--reference-adt`` at any genuine 3.3.5a tile and the convention is read off
it directly, by comparing each entry's size against the size the chunk itself
declares.
"""

from __future__ import annotations

import dataclasses
import pathlib
import struct
import time
from collections.abc import Callable

from ..chunks import Chunk, ChunkReader, ChunkWriter, report_unknown
from ..errors import MalformedFileError, UnsupportedFormatError
from ..limits import ADT_MCNK_COUNT, ADT_VERSION
from ..listfile import Listfile, normalise, placeholder_path
from ..options import Options, UnresolvedPolicy
from ..report import FileResult, Status
from .layers import limit_layers, remap_predominant
from .mh2o import LiquidTypes, convert_mh2o
from .placements import (
    DOODADS,
    WMOS,
    choose_doodad_sets,
    rebuild_placements,
    remap_references,
    restrict_placements,
)

MCNK_HEADER_SIZE = 128
MCIN_ENTRY_SIZE = 16
MHDR_SIZE = 64

#: How much an MCIN entry's size field covers.  See the module docstring.
MCIN_SIZE_WITH_HEADER = "chunk"
MCIN_SIZE_PAYLOAD_ONLY = "payload"

#: MCNK.flags bit meaning "the 8 bytes at 0x14 are an 8x8 hole mask".
MCNK_FLAG_HIGH_RES_HOLES = 0x10000
#: Where a split root keeps that mask: the MCVT/MCNR offset words it no
#: longer needs.  (Checked against 24,832 Northrend and Outland chunks whose
#: folded mask equals the 3.3.5a tile's own.)
HIGH_RES_HOLES_OFFSET = 0x14
MCNK_FLAG_HAS_MCSH = 0x1
MCNK_FLAG_HAS_MCCV = 0x40
#: MTXF bits 3.3.5a reads: "use the cube map, skip specular and height".
MTXF_WRATH_FLAGS = 0x1
MTXP_ENTRY_SIZE = 16
SPECULAR_SUFFIX = "_s.blp"

#: MCNK sub-chunks 3.3.5a reads, in emission order.
SUBCHUNK_ORDER = ("MCVT", "MCCV", "MCNR", "MCLY", "MCRF", "MCSH", "MCAL",
                  "MCLQ", "MCSE")

#: Post-Wrath chunks, with what each one carries.
MODERN_CHUNKS = {
    "MTXP": "texture render parameters (height/parallax scale)",
    "MDID": "diffuse texture FileDataIDs",
    "MHID": "height texture FileDataIDs",
    "MAMP": "global texture amplifier",
    "MBMH": "blend mesh headers",
    "MBBB": "blend mesh bounding boxes",
    "MBNV": "blend mesh vertices",
    "MBMI": "blend mesh indices",
    "MLHD": "LOD header",
    "MLVH": "LOD heightmap",
    "MLVI": "LOD indices",
    "MLLL": "LOD levels",
    "MLND": "LOD quad tree",
    "MLSI": "LOD skirt indices",
    "MLLD": "LOD liquid data",
    "MLMD": "LOD map object definitions",
    "MLMX": "LOD map object extents",
    "MCLV": "per-chunk light values",
    "MCBB": "per-chunk blend batches",
    "MCMT": "per-chunk terrain material ids",
    "MCDD": "per-chunk detail doodad disable mask",
    "MWDR": "doodad set ranges for WMO placements",
    "MWDS": "doodad set lists for WMO placements",
    "MLMB": "per-WMO-placement LOD blend values",
    "MPTX": "predominant-texture factors for layers past the fourth",
    "MTCG": "terrain colour-grading references",
}
#: Modern chunks whose content is carried over in another form, so they are
#: not reported as dropped.
FOLDED_CHUNKS = {"MDID", "MWDR", "MWDS"}

#: MHDR field order; the offsets are written back in this sequence.
#: Everything a 3.3.5a tile is made of, top level and inside an MCNK.  Used to
#: tell a chunk this tool drops on purpose from one it has never seen.
WOTLK_CHUNKS = {
    "MVER", "MHDR", "MCIN", "MTEX", "MMDX", "MMID", "MWMO", "MWID", "MDDF",
    "MODF", "MCNK", "MFBO", "MH2O", "MTXF",
    "MCVT", "MCCV", "MCNR", "MCLY", "MCRF", "MCSH", "MCAL", "MCLQ", "MCSE",
    # the split-file spellings the merge reads and folds away
    "MCRD", "MCRW", "MCMT", "MCDD", "MCBB", "MCLV",
}

MHDR_FIELDS = ("MCIN", "MTEX", "MMDX", "MMID", "MWMO", "MWID", "MDDF",
               "MODF", "MFBO", "MH2O", "MTXF")


@dataclasses.dataclass
class AdtParts:
    """The pieces of one tile, however the user extracted them."""

    root: bytes = b""
    tex0: bytes = b""
    obj0: bytes = b""

    def __bool__(self) -> bool:
        return bool(self.root)


def _collect(data: bytes, name: str) -> tuple[dict[str, list[Chunk]], list[Chunk]]:
    """Split a file into (non-MCNK chunks by name, MCNK chunks in order)."""
    if not data:
        return {}, []
    reader = ChunkReader.auto(data, {"MVER", "MHDR", "MCNK", "MTEX", "MCIN"}, name=name)
    named: dict[str, list[Chunk]] = {}
    mcnks: list[Chunk] = []
    for chunk in reader:
        if chunk.name == "MCNK":
            mcnks.append(chunk)
        else:
            named.setdefault(chunk.name, []).append(chunk)
    return named, mcnks


def _check_version(named: dict[str, list[Chunk]], source: str,
                   res: FileResult, what: str) -> int:
    """MVER has read 18 since Wrath; say so if this file disagrees.

    Nothing downstream branches on it, which is exactly why it is worth
    reading: a file declaring something else is being parsed on an assumption
    nobody checked.
    """
    entries = named.get("MVER")
    if not entries or len(entries[0].data) < 4:
        res.warn("adt.no_version",
                 f"{what} has no readable MVER chunk; it was parsed as "
                 f"version {ADT_VERSION} regardless")
        return 0
    version = struct.unpack_from("<I", entries[0].data, 0)[0]
    if version != ADT_VERSION:
        res.warn("adt.version",
                 f"{what} declares MVER {version}, not the {ADT_VERSION} every "
                 f"build from Wrath onwards writes; it was parsed as "
                 f"{ADT_VERSION} anyway, so check the result",
                 version=version)
    return version


def _payload(named: dict[str, list[Chunk]], key: str) -> bytes:
    entries = named.get(key)
    return entries[0].data if entries else b""


def mcin_size_convention(data: bytes, name: str = "<adt>") -> tuple[str, str]:
    """Read off a real tile whether MCIN sizes include the chunk header.

    Every entry names an offset and a size, and the chunk sitting at that
    offset declares its own size eight bytes in.  Comparing the two says which
    convention wrote the file, with no interpretation left over.  Returns the
    convention and a sentence about the evidence, or ``("", why not)``.
    """
    reader = ChunkReader.auto(data, {"MVER", "MHDR", "MCNK", "MTEX", "MCIN"},
                              name=name)
    mcin = None
    for chunk in reader:
        if chunk.name == "MCIN":
            mcin = chunk
            break
    if mcin is None:
        return "", (f"{name} has no MCIN, so it is not a 3.3.5a tile "
                    f"(Cataclysm and later dropped the chunk)")

    votes = {MCIN_SIZE_WITH_HEADER: 0, MCIN_SIZE_PAYLOAD_ONLY: 0}
    checked = 0
    for i in range(min(ADT_MCNK_COUNT, len(mcin.data) // MCIN_ENTRY_SIZE)):
        offset, size = struct.unpack_from("<II", mcin.data, i * MCIN_ENTRY_SIZE)
        if not offset or not size or offset + 8 > len(data):
            continue
        declared = struct.unpack_from("<I", data, offset + 4)[0]
        checked += 1
        if size == declared + 8:
            votes[MCIN_SIZE_WITH_HEADER] += 1
        elif size == declared:
            votes[MCIN_SIZE_PAYLOAD_ONLY] += 1

    if not checked:
        return "", f"{name}'s MCIN entries are empty, so they settle nothing"
    winner = max(votes, key=lambda k: votes[k])
    if votes[winner] != checked:
        return "", (f"{name} is inconsistent with itself: of {checked} MCIN "
                    f"entries, {votes[MCIN_SIZE_WITH_HEADER]} include the "
                    f"chunk header in their size and "
                    f"{votes[MCIN_SIZE_PAYLOAD_ONLY]} do not")
    covers = ("the chunk header as well as the payload"
              if winner == MCIN_SIZE_WITH_HEADER else "the payload alone")
    return winner, (f"all {checked} of {name}'s MCIN entries size {covers}")


def _subchunks(data: bytes, reverse: bool, start: int = 0) -> dict[str, bytes]:
    out: dict[str, bytes] = {}
    for chunk in ChunkReader(data, reverse=reverse, start=start):
        out.setdefault(chunk.name, chunk.data)
    return out


def _fold_holes(high: bytes) -> int:
    """Collapse Cataclysm's 8x8 hole mask into Wrath's 4x4 one."""
    low = 0
    for y in range(4):
        for x in range(4):
            block = 0
            for dy in range(2):
                row = high[y * 2 + dy] if y * 2 + dy < len(high) else 0
                for dx in range(2):
                    block |= (row >> (x * 2 + dx)) & 1
            if block:
                low |= 1 << (y * 4 + x)
    return low


def _resolve_textures(named: dict[str, list[Chunk]], opts: Options,
                      listfile: Listfile, result: FileResult,
                      file_exists: Callable[[int], bool] | None = None) -> bytes:
    """Return an MTEX blob, building one from MDID FileDataIDs if needed.

    Legion repointed terrain layers at ``<name>_s.blp``, the diffuse texture
    with a specular mask in its alpha; the plain ``<name>.blp`` 3.3.5a names
    still ships beside it, and is used whenever it does.
    """
    mtex = _payload(named, "MTEX")
    if mtex:
        if not opts.path_prefix:
            return mtex
        rebuilt = bytearray()
        for raw in mtex.split(b"\0"):
            if not raw:
                continue
            path = normalise(opts.path_prefix.rstrip("\\/") + "\\"
                             + raw.decode("latin-1"))
            rebuilt += path.encode("latin-1") + b"\0"
        return bytes(rebuilt)

    mdid = _payload(named, "MDID")
    if not mdid:
        return b""

    ids = struct.unpack_from("<" + "I" * (len(mdid) // 4), mdid, 0)
    blob = bytearray()
    plain = 0
    for file_id in ids:
        path = listfile.path_for(file_id) if file_id else ""
        if path and path.endswith(SPECULAR_SUFFIX):
            plain_path = path[:-len(SPECULAR_SUFFIX)] + ".blp"
            plain_id = listfile.id_for(plain_path)
            if plain_id is not None and (file_exists is None or file_exists(plain_id)):
                path = plain_path
                plain += 1
        if path is None:
            if opts.unresolved is UnresolvedPolicy.FAIL:
                result.fail("adt.texture.unresolved",
                            f"no listfile entry for terrain texture FileDataID "
                            f"{file_id}", file_id=file_id)
                return b""
            path = placeholder_path(file_id, "blp")
            result.lossy("adt.texture.placeholder",
                         f"terrain texture FileDataID {file_id} is not in the "
                         f"listfile; pointed it at {path}", file_id=file_id)
        if path and opts.path_prefix:
            path = normalise(opts.path_prefix.rstrip("\\/") + "\\" + path)
        blob += path.encode("latin-1") + b"\0"
    result.info("adt.texture.resolved",
                f"rebuilt MTEX from {len(ids)} MDID FileDataID(s)", count=len(ids))
    if plain:
        result.info("adt.texture.plain",
                    f"named {plain} terrain texture(s) by their plain diffuse "
                    f"file rather than the _s specular variant retail points "
                    f"at", count=plain)
    return bytes(blob)


def _mtxf_from_mtxp(mtxp: bytes, textures: int) -> bytes:
    """Per-texture flags 3.3.5a reads, from the parameters Cataclysm replaced
    them with; empty when no texture sets one."""
    flags = [struct.unpack_from("<I", mtxp, i * MTXP_ENTRY_SIZE)[0] & MTXF_WRATH_FLAGS
             for i in range(min(textures, len(mtxp) // MTXP_ENTRY_SIZE))]
    if not any(flags):
        return b""
    flags += [0] * (textures - len(flags))
    return struct.pack(f"<{textures}I", *flags)


def _build_mcnk(header: bytes, pieces: dict[str, bytes], reverse: bool,
                result: FileResult, counters: dict[str, int],
                remaps: tuple[dict[int, int] | None, dict[int, int] | None]
                = (None, None), untextured: set[int] = frozenset(),
                big_alpha: bool = True) -> bytes:
    """Reassemble one map chunk with 3.3.5a offsets."""
    hdr = bytearray(header[:MCNK_HEADER_SIZE])
    flags = struct.unpack_from("<I", hdr, 0)[0]

    if flags & MCNK_FLAG_HIGH_RES_HOLES:
        # A split root finds its sub-chunks by walking them, so the MCVT and
        # MCNR offset words at 0x14 are free, and that is where the 8x8 mask
        # lives. 0x40 still holds the low-quality texture map, as in Wrath.
        low = _fold_holes(bytes(hdr[HIGH_RES_HOLES_OFFSET:HIGH_RES_HOLES_OFFSET + 8]))
        struct.pack_into("<H", hdr, 0x3C, low)
        flags &= ~MCNK_FLAG_HIGH_RES_HOLES
        counters["holes"] = counters.get("holes", 0) + 1

    if "MCLY" in pieces:
        limited = limit_layers(pieces["MCLY"], pieces.get("MCAL", b""),
                               untextured, big_alpha)
        if limited is not None:
            pieces = dict(pieces, MCLY=limited.mcly, MCAL=limited.mcal)
            hdr[0x40:0x50] = remap_predominant(bytes(hdr[0x40:0x50]), limited)
            for key in ("untextured", "over_limit", "unreadable"):
                counters[f"layers.{key}"] = (counters.get(f"layers.{key}", 0)
                                             + getattr(limited, key))
            counters["layers.chunks"] = counters.get("layers.chunks", 0) + 1

    layers = len(pieces.get("MCLY", b"")) // 16
    doodad_refs = len(pieces.get("MCRD", b"")) // 4
    object_refs = len(pieces.get("MCRW", b"")) // 4
    mcrf = pieces.get("MCRF")
    if mcrf is None:
        mcrf = pieces.get("MCRD", b"") + pieces.get("MCRW", b"")
    else:
        # A monolithic source already merged them; trust the header's counts.
        doodad_refs = struct.unpack_from("<I", hdr, 0x10)[0]
        object_refs = struct.unpack_from("<I", hdr, 0x38)[0]

    if remaps != (None, None):
        # Placements were dropped, so every later entry moved down a slot.
        refs = list(struct.unpack_from(f"<{len(mcrf) // 4}I", mcrf, 0))
        doodads = remap_references(refs[:doodad_refs], remaps[0])
        objects = remap_references(refs[doodad_refs:doodad_refs + object_refs],
                                   remaps[1])
        doodad_refs, object_refs = len(doodads), len(objects)
        mcrf = struct.pack(f"<{doodad_refs + object_refs}I", *doodads, *objects)

    struct.pack_into("<I", hdr, 0x0C, layers)
    struct.pack_into("<I", hdr, 0x10, doodad_refs)
    struct.pack_into("<I", hdr, 0x38, object_refs)

    body = ChunkWriter(reverse=reverse)
    offsets: dict[str, int] = {}
    sizes: dict[str, int] = {}
    emitted = {"MCRF": mcrf} | {k: v for k, v in pieces.items()
                                if k in SUBCHUNK_ORDER and k != "MCRF"}
    for name in SUBCHUNK_ORDER:
        payload = emitted.get(name)
        if payload is None or (name != "MCRF" and not payload):
            continue
        # Offsets count from the start of the MCNK chunk header, so allow for
        # the 8 bytes of magic+size plus the 128-byte chunk header.
        offsets[name] = 8 + MCNK_HEADER_SIZE + len(body)
        sizes[name] = len(payload) + 8
        body.add(name, payload)

    struct.pack_into("<I", hdr, 0x14, offsets.get("MCVT", 0))
    struct.pack_into("<I", hdr, 0x18, offsets.get("MCNR", 0))
    struct.pack_into("<I", hdr, 0x1C, offsets.get("MCLY", 0))
    struct.pack_into("<I", hdr, 0x20, offsets.get("MCRF", 0))
    struct.pack_into("<I", hdr, 0x24, offsets.get("MCAL", 0))
    struct.pack_into("<I", hdr, 0x28, sizes.get("MCAL", 0))
    struct.pack_into("<I", hdr, 0x2C, offsets.get("MCSH", 0))
    struct.pack_into("<I", hdr, 0x30, sizes.get("MCSH", 0))
    struct.pack_into("<I", hdr, 0x58, offsets.get("MCSE", 0))
    struct.pack_into("<I", hdr, 0x5C, len(pieces.get("MCSE", b"")) // 28)
    struct.pack_into("<I", hdr, 0x60, offsets.get("MCLQ", 0))
    # A chunk with no liquid still declares the empty chunk's 8 header bytes.
    struct.pack_into("<I", hdr, 0x64, sizes.get("MCLQ", 8))
    struct.pack_into("<I", hdr, 0x74, offsets.get("MCCV", 0))
    # Wrath has no MCLV and ignores the last word; Cataclysm used both.
    struct.pack_into("<II", hdr, 0x78, 0, 0)

    # Retail keeps "has shadows" and "has vertex colours" set on chunks whose
    # MCSH and MCCV it no longer ships; the flags follow what is written.
    for name, bit in (("MCSH", MCNK_FLAG_HAS_MCSH), ("MCCV", MCNK_FLAG_HAS_MCCV)):
        flags = flags | bit if name in offsets else flags & ~bit
    struct.pack_into("<I", hdr, 0, flags)

    return bytes(hdr) + body.getvalue()


def _learn_mcin(path: str, res: FileResult) -> tuple[str, str]:
    """Read the MCIN convention off a reference tile, if it can be read."""
    try:
        data = pathlib.Path(path).read_bytes()
    except OSError as exc:
        return "", f"could not read the reference tile {path}: {exc}"
    try:
        return mcin_size_convention(data, pathlib.Path(path).name)
    except (MalformedFileError, UnsupportedFormatError, struct.error) as exc:
        return "", f"could not read {path} as an ADT: {exc}"


def convert_adt(parts: AdtParts, source_name: str, opts: Options,
                listfile: Listfile | None = None,
                result: FileResult | None = None,
                liquid_types: LiquidTypes | None = None,
                file_exists: Callable[[int], bool] | None = None,
                wmo_doodad_sets: Callable[[str], list[int] | None] | None = None
                ) -> tuple[bytes, FileResult]:
    """Merge a tile's pieces into one 3.3.5a ADT.

    ``liquid_types`` (read from the build's LiquidType and LiquidMaterial)
    lets retail liquid be decoded by rule rather than from its block sizes.
    ``file_exists`` says whether a FileDataID is in the build; without it the
    listfile is taken at its word.  ``wmo_doodad_sets`` gives a placed world
    object's doodad count per set, by path, to choose between the sets a
    modern placement shows at once.
    """
    started = time.time()
    res = result or FileResult(source=source_name, kind="adt")
    res.kind = "adt"
    res.bytes_in = len(parts.root) + len(parts.tex0) + len(parts.obj0)
    listfile = listfile or Listfile()

    if not parts.root:
        raise MalformedFileError(f"{source_name}: no terrain (root) ADT supplied")

    mcin_convention = MCIN_SIZE_WITH_HEADER
    if opts.adt_reference:
        learned, why = _learn_mcin(opts.adt_reference, res)
        if learned:
            mcin_convention = learned
            res.info("adt.mcin.learned",
                     f"MCIN entry sizes follow the reference tile: {why}")
        elif why:
            res.warn("adt.mcin.reference_unusable",
                     f"{why}; kept the header-inclusive size, which is safe "
                     f"for a reader that trusts MCIN over the chunk's own "
                     f"header")

    root_named, root_mcnks = _collect(parts.root, source_name)
    tex_named, tex_mcnks = _collect(parts.tex0, source_name + "_tex0")
    obj_named, obj_mcnks = _collect(parts.obj0, source_name + "_obj0")
    reverse = True  # ADT magics are stored byte-reversed

    if "MHDR" not in root_named:
        raise UnsupportedFormatError(f"{source_name}: not an ADT (no MHDR chunk)")
    _check_version(root_named, source_name, res, "terrain tile")
    if not root_mcnks:
        raise MalformedFileError(f"{source_name}: root ADT has no MCNK chunks")

    split_source = bool(parts.tex0 or parts.obj0) or "MTEX" not in root_named
    res.source_version = (f"ADT {'split' if split_source else 'monolithic'}, "
                          f"{len(root_mcnks)} map chunks")

    if len(root_mcnks) != ADT_MCNK_COUNT:
        res.warn("adt.mcnk_count",
                 f"tile has {len(root_mcnks)} map chunks, not {ADT_MCNK_COUNT}",
                 chunks=len(root_mcnks))

    modern = sorted({n for n in (*root_named, *tex_named, *obj_named)
                     if n in MODERN_CHUNKS})

    # -- referenced tables ----------------------------------------------
    def pick(name: str) -> bytes:
        for named in (obj_named, tex_named, root_named):
            payload = _payload(named, name)
            if payload:
                return payload
        return b""

    mtex = _resolve_textures(tex_named or root_named, opts, listfile, res,
                             file_exists)
    if not res.ok:
        res.elapsed = time.time() - started
        return b"", res
    untextured = {i for i, name in enumerate(mtex.split(b"\0")[:-1]) if not name}

    source_liquid = pick("MH2O")
    liquid = convert_mh2o(source_liquid, liquid_types, res) if source_liquid else b""
    tables = {
        "MTEX": mtex,
        "MMDX": pick("MMDX"),
        "MMID": pick("MMID"),
        "MWMO": pick("MWMO"),
        "MWID": pick("MWID"),
        "MDDF": pick("MDDF"),
        "MODF": pick("MODF"),
        "MH2O": liquid,
        "MFBO": pick("MFBO"),
        "MTXF": pick("MTXF") or _mtxf_from_mtxp(pick("MTXP"), mtex.count(b"\0")),
    }

    # -- placements ------------------------------------------------------
    doodads = rebuild_placements(DOODADS, tables["MMDX"], tables["MMID"],
                                 tables["MDDF"], opts, listfile, res,
                                 "adt.doodad")
    wmos = rebuild_placements(WMOS, tables["MWMO"], tables["MWID"],
                              tables["MODF"], opts, listfile, res, "adt.wmo")
    if doodads is None or wmos is None:
        res.elapsed = time.time() - started
        return b"", res
    choose_doodad_sets(wmos, pick("MWDR"), pick("MWDS"), wmo_doodad_sets, res,
                       "adt.wmo")
    restricted = (restrict_placements(DOODADS, doodads, res, "adt.doodad")
                  + restrict_placements(WMOS, wmos, res, "adt.wmo"))
    tables.update(MMDX=doodads.names, MMID=doodads.ids, MDDF=doodads.entries,
                  MWMO=wmos.names, MWID=wmos.ids, MODF=wmos.entries)

    # -- map chunks ------------------------------------------------------
    # Every chunk name the three files carry, top level and inside an MCNK, so
    # one nobody has seen before can be named rather than quietly discarded.
    seen_chunks: set[str] = set(root_named) | set(tex_named) | set(obj_named)
    if root_mcnks or tex_mcnks or obj_mcnks:
        seen_chunks.add("MCNK")

    counters: dict[str, int] = {}
    merged_mcnks: list[bytes] = []
    for index, chunk in enumerate(root_mcnks):
        pieces = _subchunks(chunk.data, reverse, start=MCNK_HEADER_SIZE)
        if index < len(tex_mcnks):
            pieces |= _subchunks(tex_mcnks[index].data, reverse)
        if index < len(obj_mcnks):
            pieces |= _subchunks(obj_mcnks[index].data, reverse)
        seen_chunks |= set(pieces)
        merged_mcnks.append(
            _build_mcnk(chunk.data, pieces, reverse, res, counters,
                        (doodads.remap, wmos.remap), untextured, split_source))

    if counters.get("holes"):
        res.lossy("adt.holes",
                  f"folded the 8x8 hole mask down to 4x4 on "
                  f"{counters['holes']} map chunk(s); 3.3.5a cannot punch "
                  f"sub-quadrant holes", chunks=counters["holes"])
    if counters.get("layers.over_limit"):
        res.lossy("adt.layers.limit",
                  f"dropped {counters['layers.over_limit']} texture layer(s) that "
                  f"showed least, so no map chunk has more than the four 3.3.5a "
                  f"holds", layers=counters["layers.over_limit"])
    if counters.get("layers.untextured"):
        res.lossy("adt.layers.untextured",
                  f"dropped {counters['layers.untextured']} texture layer(s) "
                  f"whose texture has no file (FileDataID 0 in the source)",
                  layers=counters["layers.untextured"])
    if counters.get("layers.unreadable"):
        res.lossy("adt.layers.unreadable",
                  f"dropped {counters['layers.unreadable']} texture layer(s) "
                  f"whose alpha map runs past the end of the chunk's MCAL",
                  layers=counters["layers.unreadable"])

    # -- assemble --------------------------------------------------------
    out = bytearray()
    top = ChunkWriter(reverse=reverse)
    top.add("MVER", struct.pack("<I", ADT_VERSION))
    out += top.getvalue()

    mhdr_source = _payload(root_named, "MHDR")
    mhdr = bytearray(mhdr_source[:MHDR_SIZE].ljust(MHDR_SIZE, b"\0"))
    out += b"RDHM" if reverse else b"MHDR"
    out += struct.pack("<I", MHDR_SIZE)
    mhdr_data_pos = len(out)
    out += bytes(mhdr)

    offsets: dict[str, int] = {}

    def append(name: str, payload: bytes, always: bool = False) -> None:
        if not payload and not always:
            return
        offsets[name] = len(out) - mhdr_data_pos
        out.extend((name[::-1] if reverse else name).encode("latin-1"))
        out.extend(struct.pack("<I", len(payload)))
        out.extend(payload)

    # MCIN is written first but only filled in once the chunks are placed.
    mcin_payload = bytearray(ADT_MCNK_COUNT * MCIN_ENTRY_SIZE)
    append("MCIN", bytes(mcin_payload), always=True)
    mcin_data_pos = len(out) - len(mcin_payload)

    # 3.3.5a seeks to every one of these through MHDR without checking the
    # offset, so each is written even when it is empty.
    for name in ("MTEX", "MMDX", "MMID", "MWMO", "MWID", "MDDF", "MODF"):
        append(name, tables[name], always=True)
    append("MH2O", tables["MH2O"])

    for index, payload in enumerate(merged_mcnks):
        chunk_pos = len(out)
        out.extend(b"KNCM" if reverse else b"MCNK")
        out.extend(struct.pack("<I", len(payload)))
        out.extend(payload)
        if index < ADT_MCNK_COUNT:
            entry_size = len(payload) + (8 if mcin_convention ==
                                         MCIN_SIZE_WITH_HEADER else 0)
            struct.pack_into("<4I", out, mcin_data_pos + index * MCIN_ENTRY_SIZE,
                             chunk_pos, entry_size, 0, 0)

    append("MFBO", tables["MFBO"])
    append("MTXF", tables["MTXF"])

    flags = struct.unpack_from("<I", mhdr, 0)[0]
    if tables["MFBO"]:
        flags |= 0x1
    else:
        flags &= ~0x1
    struct.pack_into("<I", mhdr, 0, flags)
    for i, name in enumerate(MHDR_FIELDS):
        struct.pack_into("<I", mhdr, 4 + i * 4, offsets.get(name, 0))
    out[mhdr_data_pos : mhdr_data_pos + MHDR_SIZE] = mhdr

    report_unknown(res, seen_chunks, WOTLK_CHUNKS | set(MODERN_CHUNKS),
                   "terrain", "adt.chunks.unknown")

    if set(modern) - FOLDED_CHUNKS:
        res.lossy("adt.chunks.dropped",
                  "dropped chunks with no 3.3.5a equivalent: "
                  + ", ".join(f"{n} ({MODERN_CHUNKS[n]})" for n in modern
                              if n not in FOLDED_CHUNKS),
                  chunks=modern)
    if split_source:
        res.warn("adt.big_alpha",
                 "this tile's MCAL alpha maps are the 8-bit Cataclysm form; the "
                 "map's .wdt must have the big-alpha flag (MPHD 0x4) set or "
                 "3.3.5a reads them as 4-bit and every terrain blend is wrong. "
                 "Converting the .wdt in the same run sets it for you")
        res.info("adt.merged",
                 f"merged {'root' if parts.root else ''}"
                 f"{'+tex0' if parts.tex0 else ''}"
                 f"{'+obj0' if parts.obj0 else ''} into one monolithic tile "
                 f"with a rebuilt MCIN index")

    res.bytes_out = len(out)
    res.target_version = f"ADT v{ADT_VERSION} monolithic, {len(merged_mcnks)} map chunks"
    res.extra.update({"map_chunks": len(merged_mcnks),
                      "textures": tables["MTEX"].count(b"\0"),
                      "doodad_placements": len(tables["MDDF"]) // 36,
                      "wmo_placements": len(tables["MODF"]) // 64})
    if (not split_source and not modern and not doodads.changed
            and not wmos.changed and not restricted and liquid == source_liquid
            and not counters.get("layers.chunks") and res.status is Status.OK):
        res.status = Status.PASSTHROUGH
        res.info("adt.passthrough", "already a monolithic 3.3.5a tile")
    res.elapsed = time.time() - started
    return bytes(out), res


def inspect_adt(data: bytes, source_name: str) -> dict:
    named, mcnks = _collect(data, source_name)
    return {
        "kind": "adt",
        "chunks": sorted(named),
        "map_chunks": len(mcnks),
        "split": "MHDR" in named and "MTEX" not in named,
        "modern_chunks": sorted(n for n in named if n in MODERN_CHUNKS) or None,
        "wotlk_compatible": "MCIN" in named and not any(n in MODERN_CHUNKS
                                                        for n in named),
    }
