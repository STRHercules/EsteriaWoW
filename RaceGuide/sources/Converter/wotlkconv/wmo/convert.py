"""WMO downgrade: root file plus every group that belongs to it."""

from __future__ import annotations

import dataclasses
import os
import struct
import time

from ..chunks import ChunkWriter, report_unknown
from ..limits import (
    MODD_SIZE,
    MOGI_SIZE,
    MOHD_SIZE,
    MOLT_SIZE,
    MOMT_SIZE,
    WMO_HEADER_FLAG_MASK,
    WMO_MATERIAL_FLAG_MASK,
    WMO_MAX_BLEND_MODE,
    WMO_MAX_GROUPS,
    WMO_MAX_SHADER,
    WMO_VERSION,
    WMO_VERSION_OLDEST_READABLE,
)
from ..listfile import Listfile, normalise, placeholder_path
from ..options import Options, UnresolvedPolicy
from ..report import FileResult, Status
from ..resolve import AssetSource
from .group import convert_group_parts
from .root import ALL_KNOWN as ALL_KNOWN_ROOT
from .root import MODERN_ROOT_CHUNKS, StringTable, WmoRoot, parse_root, split_string_table

#: MAVG and MAVD entries: position, start and end radius, three colours,
#: flags, doodad set and padding.
AMBIENT_VOLUME_SIZE = 48


@dataclasses.dataclass(slots=True)
class ConvertedAsset:
    filename: str
    data: bytes
    result: FileResult


@dataclasses.dataclass(slots=True)
class GroupAddition:
    """A group the root did not have before, because a split produced it."""

    source_index: int
    bounding_box: tuple
    flags: int
    name: str


def _resolve(file_id: int, kind: str, opts: Options, listfile: Listfile,
             result: FileResult) -> str | None:
    """FileDataID -> in-game path under the configured unresolved policy."""
    path = listfile.path_for(file_id)
    if path is None:
        if opts.unresolved is UnresolvedPolicy.FAIL:
            result.fail("wmo.reference.unresolved",
                        f"no listfile entry for {kind} FileDataID {file_id}",
                        file_id=file_id, kind=kind)
            return None
        if opts.unresolved is UnresolvedPolicy.STRIP:
            result.lossy("wmo.reference.stripped",
                         f"dropped unresolvable {kind} FileDataID {file_id}",
                         file_id=file_id, kind=kind)
            return ""
        path = placeholder_path(file_id, kind)
        result.lossy("wmo.reference.placeholder",
                     f"{kind} FileDataID {file_id} is not in the listfile; "
                     f"pointed it at {path}", file_id=file_id, path=path)
    if opts.path_prefix:
        path = normalise(opts.path_prefix.rstrip("\\/") + "\\" + path)
    return path


def _rebuild_materials(root: WmoRoot, opts: Options, listfile: Listfile,
                       result: FileResult) -> tuple[bytes, bytes]:
    """Return (MOTX blob, MOMT blob) with texture references repointed.

    Handles both source shapes: a MOTX string table addressed by byte offset,
    and BfA-era materials that carry FileDataIDs where the offsets used to be.
    """
    momt = root.payload("MOMT")
    count = len(momt) // MOMT_SIZE
    motx_blob = root.payload("MOTX")
    strings = split_string_table(motx_blob) if motx_blob else {}
    uses_file_ids = not motx_blob

    table = StringTable()
    out = bytearray(momt)
    clamped_shader = 0
    clamped_blend = 0
    clamped_flags = 0
    resolved_ids = 0
    promoted = 0

    # texture_1, texture_2, texture_3 live at these offsets in SMOMaterial;
    # 32, between the last two, is the ground type (footstep sounds and
    # effects), which is not a texture at all.
    texture_fields = (12, 24, 36)
    # A modern material says "no texture" with FileDataID 0, but in a string
    # table 0 is the first name.  3.3.5a's own files point an absent texture
    # at an empty entry instead.
    empty = None

    for i in range(count):
        base = i * MOMT_SIZE
        flags, shader, blend = struct.unpack_from("<3I", out, base)

        masked = flags & WMO_MATERIAL_FLAG_MASK
        if masked != flags:
            clamped_flags += 1
        shader_clamped = shader > WMO_MAX_SHADER
        if shader_clamped:
            clamped_shader += 1
            shader = 0  # plain diffuse always renders
        if blend > WMO_MAX_BLEND_MODE:
            clamped_blend += 1
            blend = 2  # alpha
        struct.pack_into("<3I", out, base, masked, shader, blend)

        for field in texture_fields:
            value = struct.unpack_from("<I", out, base + field)[0]
            if value == 0:
                if uses_file_ids:
                    if empty is None:
                        empty = table.add("")
                    struct.pack_into("<I", out, base + field, empty)
                continue
            if uses_file_ids:
                path = _resolve(value, "blp", opts, listfile, result)
                if path is None:
                    return b"", b""
                resolved_ids += 1
            else:
                path = strings.get(value)
                if path is None:
                    # Offsets that do not start a string happen in hand-edited
                    # WMOs; point them at the first texture rather than crash.
                    path = next(iter(strings.values()), "")
                if path and opts.path_prefix:
                    path = normalise(opts.path_prefix.rstrip("\\/") + "\\" + path)
            struct.pack_into("<I", out, base + field,
                             table.add(path) if path else 0)

        if uses_file_ids and shader_clamped:
            # Legion's shader 23 leaves texture_1 empty and keeps its diffuse
            # in texture_2, with further textures in color_3, flags_3 and the
            # runtime words.  Diffuse reads texture_1 only, and 3.3.5a takes
            # those words for a colour and flags.
            first, second = struct.unpack_from("<I", out, base + 12)[0], \
                struct.unpack_from("<I", out, base + 24)[0]
            if first == empty and second != empty:
                struct.pack_into("<I", out, base + 12, second)
                promoted += 1
            out[base + 40:base + MOMT_SIZE] = bytes(MOMT_SIZE - 40)

    if promoted:
        result.lossy("wmo.material.texture_promoted",
                     f"{promoted} material(s) kept their diffuse texture in the "
                     f"second slot for a newer shader; moved it to the first, "
                     f"which the diffuse shader 3.3.5a falls back to reads",
                     materials=promoted)
    if clamped_shader:
        result.lossy("wmo.material.shader",
                     f"{clamped_shader} material(s) used a shader newer than "
                     f"3.3.5a; reset to diffuse", materials=clamped_shader)
    if clamped_blend:
        result.lossy("wmo.material.blend",
                     f"{clamped_blend} material(s) used a blend mode newer than "
                     f"3.3.5a; reset to alpha", materials=clamped_blend)
    if clamped_flags:
        result.info("wmo.material.flags",
                    f"cleared post-Wrath render flags on {clamped_flags} material(s)")
    if resolved_ids:
        result.info("wmo.texture.resolved",
                    f"resolved {resolved_ids} texture FileDataID(s) into a MOTX "
                    f"string table", count=resolved_ids)
    return table.getvalue(), bytes(out)


def _rebuild_doodads(root: WmoRoot, opts: Options, listfile: Listfile,
                     result: FileResult) -> tuple[bytes, bytes]:
    """Return (MODN blob, MODD blob) with doodad references repointed."""
    modd = root.payload("MODD")
    count = len(modd) // MODD_SIZE
    modn_blob = root.payload("MODN")
    modi = root.payload("MODI")

    table = StringTable()
    out = bytearray(modd)

    if modn_blob:
        strings = split_string_table(modn_blob)
        fallback = next(iter(strings.values()), "")
        for i in range(count):
            word = struct.unpack_from("<I", out, i * MODD_SIZE)[0]
            name_index, flags = word & 0xFFFFFF, word >> 24
            path = strings.get(name_index, fallback)
            if path and opts.path_prefix:
                path = normalise(opts.path_prefix.rstrip("\\/") + "\\" + path)
            new_index = table.add(path) if path else 0
            struct.pack_into("<I", out, i * MODD_SIZE,
                             (new_index & 0xFFFFFF) | (flags << 24))
        return table.getvalue(), bytes(out)

    if modi:
        # BfA replaced the name table with an array of FileDataIDs, and MODD's
        # nameIndex became an index into it rather than a byte offset.
        ids = list(struct.unpack_from("<" + "I" * (len(modi) // 4), modi, 0))
        paths: list[str] = []
        for file_id in ids:
            path = _resolve(file_id, "m2", opts, listfile, result) if file_id else ""
            if path is None:
                return b"", b""
            paths.append(path)
        for i in range(count):
            word = struct.unpack_from("<I", out, i * MODD_SIZE)[0]
            name_index, flags = word & 0xFFFFFF, word >> 24
            path = paths[name_index] if name_index < len(paths) else ""
            new_index = table.add(path) if path else 0
            struct.pack_into("<I", out, i * MODD_SIZE,
                             (new_index & 0xFFFFFF) | (flags << 24))
        result.info("wmo.doodad.resolved",
                    f"rebuilt MODN from {len(ids)} MODI FileDataID(s)",
                    count=len(ids))
        return table.getvalue(), bytes(out)

    return b"", bytes(out)


def _skybox(root: WmoRoot, opts: Options, listfile: Listfile,
            result: FileResult) -> bytes:
    mosb = root.payload("MOSB")
    if mosb:
        return mosb
    mosi = root.payload("MOSI")
    if len(mosi) >= 4:
        file_id = struct.unpack_from("<I", mosi, 0)[0]
        path = _resolve(file_id, "m2", opts, listfile, result) if file_id else ""
        if path:
            result.info("wmo.skybox.resolved", f"skybox MOSI {file_id} -> {path}")
            blob = path.encode("latin-1") + b"\0"
            while len(blob) % 4:
                blob += b"\0"
            return blob
    return b"\0" * 4


def _ambient_colour(root: WmoRoot, mohd: bytearray, result: FileResult) -> None:
    """Give MOHD the ambient colour retail keeps in its ambient volumes.

    Legion moved a world object's ambient light into ``MAVG`` (global, per
    doodad set) and ``MAVD`` (local volumes), which the client prefers over
    ``MOHD``'s colour; 4,366 retail roots leave that colour black.  3.3.5a
    only reads ``MOHD``, so it gets the default set's global colour, or when
    ``MOHD`` is black and there is no global one, the first volume's.
    """
    def lit(blob: bytes) -> list[bytes]:
        """Entries whose colour is not black: a black one sets nothing."""
        return [e for e in (blob[i:i + AMBIENT_VOLUME_SIZE] for i in
                            range(0, len(blob) - AMBIENT_VOLUME_SIZE + 1,
                                  AMBIENT_VOLUME_SIZE))
                if struct.unpack_from("<I", e, 0x14)[0] & 0xFFFFFF]

    current = struct.unpack_from("<I", mohd, 0x1C)[0]
    entries = lit(root.payload("MAVG"))
    chosen = next((e for e in entries if struct.unpack_from("<H", e, 0x24)[0] == 0),
                  entries[0] if entries else None)
    where = "the global ambient volume"
    if chosen is None and not current & 0xFFFFFF:
        volumes = lit(root.payload("MAVD"))
        if volumes:
            chosen, where = volumes[0], "its first ambient volume"
    if chosen is None:
        return
    colour = struct.unpack_from("<I", chosen, 0x14)[0]
    if colour == current:
        return
    struct.pack_into("<I", mohd, 0x1C, colour)
    if not current & 0xFFFFFF:
        result.info("wmo.ambient",
                    f"took the ambient colour 0x{colour:08X} from {where}; the "
                    f"header's was black, and 3.3.5a reads only the header")


def convert_wmo_root(data: bytes, source_name: str, opts: Options,
                     listfile: Listfile | None = None,
                     source: AssetSource | None = None,
                     result: FileResult | None = None,
                     output_stem: str | None = None
                     ) -> tuple[bytes, FileResult, list[ConvertedAsset]]:
    """Convert a WMO root and, when available, its group files.

    ``output_stem`` is the basename the root will be written as; groups are
    renamed to ``<stem>_000.wmo`` so the client finds them.
    """
    started = time.time()
    res = result or FileResult(source=source_name, kind="wmo")
    res.kind = "wmo"
    res.bytes_in = len(data)
    listfile = listfile or Listfile()

    root = parse_root(data, source_name)
    modern = sorted(n for n in root.chunks if n in MODERN_ROOT_CHUNKS)
    res.source_version = (f"WMO root v{root.version}, {root.n_groups} groups, "
                          f"{len(root.chunks)} chunk kinds")

    if root.version < WMO_VERSION_OLDEST_READABLE:
        # The alpha WMO wraps its groups in a MOMO container and shares almost
        # nothing with v17. Reading it as one would not fail, it would just be
        # wrong, so it is refused instead.
        res.fail("wmo.version.too_old",
                 f"root declares version {root.version}; this tool reads "
                 f"version {WMO_VERSION} and later. Versions below that are a "
                 f"different layout wearing the same magic, and reading one as "
                 f"v{WMO_VERSION} would produce a file that loads and renders "
                 f"nonsense rather than failing",
                 version=root.version)
        res.elapsed = time.time() - started
        return b"", res, []
    if root.version != WMO_VERSION:
        res.warn("wmo.version",
                 f"root declares version {root.version}, newer than the "
                 f"{WMO_VERSION} this tool was written against; it was read as "
                 f"v{WMO_VERSION}, which is right unless a structure changed",
                 version=root.version)
    if root.n_groups > WMO_MAX_GROUPS:
        res.warn("wmo.limit.groups",
                 f"{root.n_groups} groups is far beyond anything 3.3.5a ships; "
                 f"expect long load times", groups=root.n_groups)

    motx, momt = _rebuild_materials(root, opts, listfile, res)
    if not res.ok:
        res.elapsed = time.time() - started
        return b"", res, []
    modn, modd = _rebuild_doodads(root, opts, listfile, res)
    if not res.ok:
        res.elapsed = time.time() - started
        return b"", res, []
    mosb = _skybox(root, opts, listfile, res)

    # -- header ---------------------------------------------------------
    # Groups are converted before the root is written: an oversized group
    # splits into several, and the root has to describe the ones it gained.
    companions, additions = _convert_groups(root, source_name, opts, source, res,
                                            output_stem)

    mogn = bytearray(root.payload("MOGN") or b"\0" * 4)
    mogi = bytearray(root.payload("MOGI"))
    if additions:
        for addition in additions:
            name_offset = len(mogn)
            mogn += addition.name.encode("latin-1") + b"\0"
            while len(mogn) % 4:
                mogn += b"\0"
            entry = bytearray(MOGI_SIZE)
            struct.pack_into("<I", entry, 0, addition.flags)
            struct.pack_into("<6f", entry, 4, *addition.bounding_box)
            struct.pack_into("<i", entry, 28, name_offset)
            mogi += entry
        res.info("wmo.group.added",
                 f"registered {len(additions)} extra group(s) in the root, "
                 f"created by splitting oversized ones",
                 groups=len(additions))

    total_groups = root.n_groups + len(additions)

    mohd = bytearray(root.payload("MOHD")[:MOHD_SIZE])
    # nMaterials: the MOMT entry count, which 3.3.5a and Noggit size the
    # material array from (their own WMOs always agree), not the MOTX names.
    struct.pack_into("<I", mohd, 0, len(momt) // MOMT_SIZE)
    struct.pack_into("<I", mohd, 4, total_groups)
    # A few retail roots declare more lights than MOLT holds; a reader that
    # trusts the header reads the next chunk as lights.
    struct.pack_into("<I", mohd, 12, len(root.payload("MOLT")) // MOLT_SIZE)
    struct.pack_into("<I", mohd, 16, len(split_string_table(modn)) if modn else 0)
    # 1,488 retail roots declare more doodads than MODD holds.
    struct.pack_into("<I", mohd, 20, len(modd) // MODD_SIZE)
    _ambient_colour(root, mohd, res)
    flags = root.header_flags & WMO_HEADER_FLAG_MASK
    struct.pack_into("<I", mohd, 60, flags)
    if root.num_lod:
        res.lossy("wmo.lod",
                  f"dropped {root.num_lod} level(s) of detail; 3.3.5a renders "
                  f"the base geometry only", num_lod=root.num_lod)

    report_unknown(res, root.chunks, ALL_KNOWN_ROOT, "world-object",
                   "wmo.chunks.unknown")

    if modern:
        res.lossy("wmo.chunks.dropped",
                  "dropped root chunks with no 3.3.5a equivalent: "
                  + ", ".join(f"{n} ({MODERN_ROOT_CHUNKS[n]})" for n in modern
                              if n not in ("MODI", "MOSI", "GFID")),
                  chunks=modern)

    # -- rebuild --------------------------------------------------------
    cw = ChunkWriter(reverse=root.reverse_magic)
    cw.add("MVER", struct.pack("<I", WMO_VERSION))
    cw.add("MOHD", bytes(mohd))
    cw.add("MOTX", motx or b"\0" * 4)
    cw.add("MOMT", momt)
    cw.add("MOGN", bytes(mogn))
    cw.add("MOGI", bytes(mogi))
    cw.add("MOSB", mosb)
    for name in ("MOPV", "MOPT", "MOPR", "MOVV", "MOVB", "MOLT", "MODS"):
        cw.add(name, root.payload(name))
    cw.add("MODN", modn or b"\0" * 4)
    cw.add("MODD", modd)
    cw.add("MFOG", root.payload("MFOG"))
    if "MCVP" in root.chunks:
        cw.add("MCVP", root.payload("MCVP"))
    out = cw.getvalue()

    res.bytes_out = len(out)
    res.target_version = f"WMO root v{WMO_VERSION}, {total_groups} groups"
    res.extra.update({"groups": total_groups,
                      "groups_before_split": root.n_groups,
                      "materials": len(momt) // MOMT_SIZE,
                      "doodads": len(modd) // MODD_SIZE})

    if not modern and res.status is Status.OK:
        res.status = Status.PASSTHROUGH
        res.info("wmo.passthrough", "already a 3.3.5a root layout")
    res.elapsed = time.time() - started
    return out, res, companions


def _convert_groups(root: WmoRoot, source_name: str, opts: Options,
                    source: AssetSource | None, result: FileResult,
                    output_stem: str | None = None
                    ) -> tuple[list[ConvertedAsset], list[GroupAddition]]:
    """Convert the group files, renaming them into ``<root>_NNN.wmo``.

    A group too big for 16-bit indices becomes several; the first keeps the
    original number and the rest are appended after every existing group, so
    the numbering the root already uses stays put.
    """
    if source is None or not opts.convert_companions:
        return [], []

    src_stem = os.path.splitext(os.path.basename(source_name))[0]
    stem = output_stem or src_stem
    gfid = root.payload("GFID")
    group_ids = list(struct.unpack_from("<" + "I" * (len(gfid) // 4), gfid, 0)) \
        if gfid else []

    out: list[ConvertedAsset] = []
    additions: list[GroupAddition] = []
    next_number = root.n_groups
    found = 0
    for index in range(root.n_groups):
        raw = None
        group_id = group_ids[index] if index < len(group_ids) else 0
        if group_id:
            raw = source.by_file_id(group_id, ".wmo")
        if raw is None:
            raw = source.by_path(f"{src_stem}_{index:03d}.wmo")
        name = f"{stem}_{index:03d}.wmo"
        if raw is None:
            if group_id and source.casc is not None and group_id in source.casc:
                sub = FileResult(source=name, kind="wmo-group",
                                 status=Status.SKIPPED, file_id=group_id)
                sub.info("wmo.group.unavailable", "group file referenced by "
                         "the root could not be read", file_id=group_id)
                out.append(ConvertedAsset(name, b"", sub))
            continue
        sub = FileResult(source=name, kind="wmo-group", file_id=group_id or None)
        try:
            pieces, sub = convert_group_parts(raw, name, opts, sub)
        except Exception as exc:
            sub.fail("wmo.group.error", f"{type(exc).__name__}: {exc}")
            out.append(ConvertedAsset(name, b"", sub))
            continue
        if not pieces:
            out.append(ConvertedAsset(name, b"", sub))
            continue

        found += 1
        out.append(ConvertedAsset(name, pieces[0].data, sub))
        for piece in pieces[1:]:
            extra_name = f"{stem}_{next_number:03d}.wmo"
            extra = FileResult(source=extra_name, kind="wmo-group",
                               status=sub.status, file_id=sub.file_id)
            extra.info("wmo.group.split_part",
                       f"part {piece.part} of {name}, created because that "
                       f"group had more vertices than 16-bit indices reach")
            extra.bytes_out = len(piece.data)
            out.append(ConvertedAsset(extra_name, piece.data, extra))
            additions.append(GroupAddition(index, piece.bounding_box,
                                           _group_flags(root, index),
                                           f"{stem}_{next_number:03d}"))
            next_number += 1

    if root.n_groups and found == 0:
        result.warn("wmo.group.missing",
                    f"none of the {root.n_groups} group file(s) were found next "
                    f"to the root; the WMO will not render without them",
                    expected=root.n_groups)
    elif found < root.n_groups:
        result.info("wmo.group.partial",
                    f"converted {found} of {root.n_groups} group file(s)",
                    found=found, expected=root.n_groups)
    return out, additions


def _group_flags(root: WmoRoot, index: int) -> int:
    """The MOGI flags of an existing group, for a part cloned from it."""
    mogi = root.payload("MOGI")
    at = index * MOGI_SIZE
    if at + 4 > len(mogi):
        return 0
    return struct.unpack_from("<I", mogi, at)[0]


def inspect_wmo_root(data: bytes, source_name: str) -> dict:
    root = parse_root(data, source_name)
    return {
        "kind": "wmo",
        "version": root.version,
        "groups": root.n_groups,
        "textures": root.n_textures,
        "doodad_names": root.n_doodad_names,
        "doodad_defs": root.n_doodad_defs,
        "header_flags": f"0x{root.header_flags:04X}",
        "num_lod": root.num_lod,
        "chunks": sorted(root.chunks),
        "modern_chunks": sorted(n for n in root.chunks if n in MODERN_ROOT_CHUNKS) or None,
        "wotlk_compatible": not any(n in MODERN_ROOT_CHUNKS for n in root.chunks),
    }
