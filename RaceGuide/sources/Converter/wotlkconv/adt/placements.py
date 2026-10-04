"""Doodad and WMO placements, and the name tables they point into.

A 3.3.5a placement (``MDDF`` for models, ``MODF`` for WMOs) names its asset
indirectly: ``nameId`` indexes ``MMID``/``MWID``, whose entries are offsets
into the ``MMDX``/``MWMO`` string blob.  Battle for Azeroth added a flag that
turns ``nameId`` into a FileDataID instead, and from then on Blizzard wrote
every placement that way and stopped writing the name tables at all.

An old reader has no idea the flag exists.  It takes the FileDataID as an
index into a name table that is empty, which is undefined behaviour in the
client and a crash in Noggit.  So every such entry has its FileDataID looked up
in the listfile, the path is added to a rebuilt name table (once, however many
placements share it), ``nameId`` is pointed at that slot and the flag is
cleared.  Entries that already carry a name index keep pointing at the same
name.

When a FileDataID has no listfile entry the unresolved-reference policy
decides: fail the file, point the placement at a deterministic placeholder, or
drop it.  Dropping a placement moves every later entry down a slot, so the
map chunks' ``MCRF`` references are renumbered to match -- see
:func:`remap_references`.
"""

from __future__ import annotations

import dataclasses
import struct
from collections.abc import Callable

from ..listfile import Listfile, normalise, placeholder_path
from ..options import Options, UnresolvedPolicy
from ..report import FileResult


@dataclasses.dataclass(frozen=True, slots=True)
class PlacementKind:
    """How one placement table is laid out."""

    names: str          # string blob chunk
    ids: str            # offset table chunk
    entries: str        # placement chunk
    entry_size: int
    flags_at: int       # offset of the u16 flags field inside an entry
    file_data_id_flag: int
    asset: str          # what the name refers to, for reports and placeholders
    wrath_flags: int    # the flag bits 3.3.5a defines
    scale_at: int | None = None  # a Legion scale word 3.3.5a reads as padding


#: MDDF: 0x1 biodome, 0x2 shrubbery.  MODF: 0x1 destroyable; Legion put a
#: scale (1024 = 1.0) in what was the entry's padding.
DOODADS = PlacementKind("MMDX", "MMID", "MDDF", 36, 34, 0x40, "m2", 0x3)
WMOS = PlacementKind("MWMO", "MWID", "MODF", 64, 56, 0x8, "wmo", 0x1, 62)


@dataclasses.dataclass(slots=True)
class Placements:
    """A rebuilt placement table with the name table it now indexes."""

    names: bytes
    ids: bytes
    entries: bytes
    #: FileDataID-keyed entries turned into name references.
    resolved: int = 0
    #: Old entry index -> new one, when entries were dropped; otherwise None.
    remap: dict[int, int] | None = None

    @property
    def changed(self) -> bool:
        return bool(self.resolved) or self.remap is not None


def split_names(names: bytes, ids: bytes) -> list[str]:
    """The name each ``MMID``/``MWID`` slot points at, in slot order."""
    out = []
    for i in range(len(ids) // 4):
        offset = struct.unpack_from("<I", ids, i * 4)[0]
        end = names.find(b"\0", offset)
        if offset >= len(names):
            out.append("")
            continue
        out.append(names[offset:end if end >= 0 else len(names)].decode("latin-1"))
    return out


def _resolve(file_id: int, kind: PlacementKind, opts: Options,
             listfile: Listfile, result: FileResult, code: str) -> str | None:
    """FileDataID -> path; "" means drop the placement, None means fail."""
    path = listfile.path_for(file_id)
    if path is None:
        if opts.unresolved is UnresolvedPolicy.FAIL:
            result.fail(f"{code}.unresolved",
                        f"no listfile entry for placed {kind.asset} FileDataID "
                        f"{file_id}", file_id=file_id, kind=kind.asset)
            return None
        if opts.unresolved is UnresolvedPolicy.STRIP:
            result.lossy(f"{code}.stripped",
                         f"dropped a placement of unresolvable {kind.asset} "
                         f"FileDataID {file_id}", file_id=file_id,
                         kind=kind.asset)
            return ""
        path = placeholder_path(file_id, kind.asset)
        result.lossy(f"{code}.placeholder",
                     f"placed {kind.asset} FileDataID {file_id} is not in the "
                     f"listfile; pointed it at {path}", file_id=file_id,
                     kind=kind.asset, path=path)
    path = normalise(path)
    if opts.path_prefix:
        path = normalise(opts.path_prefix.rstrip("\\/") + "\\" + path)
    return path


def rebuild_placements(kind: PlacementKind, names: bytes, ids: bytes,
                       entries: bytes, opts: Options, listfile: Listfile,
                       result: FileResult, code: str) -> Placements | None:
    """Give every placement a name-table index 3.3.5a can follow.

    Returns None when the unresolved policy failed the file.
    """
    count = len(entries) // kind.entry_size
    if len(entries) % kind.entry_size:
        result.warn(f"{code}.truncated",
                    f"{kind.entries} is {len(entries)} bytes, not a whole "
                    f"number of {kind.entry_size}-byte entries; the partial "
                    f"entry at the end was dropped")
    existing = split_names(names, ids)
    by_id = any(struct.unpack_from("<H", entries, i * kind.entry_size
                                   + kind.flags_at)[0] & kind.file_data_id_flag
                for i in range(count))
    if not by_id:
        return Placements(names, ids, entries[:count * kind.entry_size])

    table: list[str] = []
    slots: dict[str, int] = {}

    def intern(path: str) -> int:
        slot = slots.get(path)
        if slot is None:
            slot = slots[path] = len(table)
            table.append(path)
        return slot

    # Name-keyed entries keep their slots: intern the old table first, in order.
    for name in existing:
        table.append(name)
        slots.setdefault(name, len(table) - 1)

    out = bytearray()
    remap: dict[int, int] = {}
    resolved = 0
    for i in range(count):
        entry = bytearray(entries[i * kind.entry_size:(i + 1) * kind.entry_size])
        name_id = struct.unpack_from("<I", entry, 0)[0]
        flags = struct.unpack_from("<H", entry, kind.flags_at)[0]
        if flags & kind.file_data_id_flag:
            path = _resolve(name_id, kind, opts, listfile, result, code)
            if path is None:
                return None
            if not path:
                continue
            struct.pack_into("<I", entry, 0, intern(path))
            struct.pack_into("<H", entry, kind.flags_at,
                             flags & ~kind.file_data_id_flag)
            resolved += 1
        remap[i] = len(out) // kind.entry_size
        out += entry

    blob = bytearray()
    offsets = bytearray()
    for name in table:
        offsets += struct.pack("<I", len(blob))
        blob += name.encode("latin-1") + b"\0"
    result.info(f"{code}.resolved",
                f"named {resolved} {kind.asset} placement(s) that referenced "
                f"their asset by FileDataID, which 3.3.5a cannot follow",
                placements=resolved, names=len(table))
    return Placements(bytes(blob), bytes(offsets), bytes(out), resolved,
                      remap if len(remap) != count else None)


def restrict_placements(kind: PlacementKind, placements: Placements,
                        result: FileResult, code: str) -> int:
    """Clear flag bits 3.3.5a does not define, and the WMO scale it cannot
    apply; returns how many entries changed.

    Later flags mean LOD use, projected textures, liquid already known and the
    like; genuine 3.3.5a tiles leave them, and the scale word, at zero.
    """
    out = bytearray(placements.entries)
    changed = scaled = 0
    for base in range(0, len(out) - kind.entry_size + 1, kind.entry_size):
        touched = False
        flags = struct.unpack_from("<H", out, base + kind.flags_at)[0]
        if flags & ~kind.wrath_flags:
            struct.pack_into("<H", out, base + kind.flags_at, flags & kind.wrath_flags)
            touched = True
        if kind.scale_at is not None:
            scale = struct.unpack_from("<H", out, base + kind.scale_at)[0]
            if scale:
                scaled += scale != 1024
                struct.pack_into("<H", out, base + kind.scale_at, 0)
                touched = True
        changed += touched
    placements.entries = bytes(out)
    if scaled:
        result.lossy(f"{code}.scale",
                     f"{scaled} {kind.asset} placement(s) are scaled, which "
                     f"3.3.5a cannot do; they appear at full size",
                     placements=scaled)
    return changed


#: MODF flag: ``doodadSet`` indexes ``MWDR``, whose range of ``MWDS`` entries
#: lists every doodad set the placement shows (Shadowlands onwards).
MODF_SETS_FROM_MWDS = 0x80
MODF_DOODAD_SET_AT = 58


def choose_doodad_sets(placements: Placements, mwdr: bytes, mwds: bytes,
                       set_sizes: Callable[[str], list[int] | None] | None,
                       result: FileResult, code: str) -> None:
    """Give each WMO placement the single doodad set 3.3.5a can show.

    A modern placement can switch on several sets at once -- a house's
    furniture, its lights and its foliage -- by listing them in ``MWDS``, and
    then ``doodadSet`` holds an index into ``MWDR`` rather than a set.  3.3.5a
    shows set 0 on every placement plus the one ``doodadSet`` names, so of the
    listed sets the one with the most doodads is kept.  Left as it was, the
    ``MWDR`` index reads as an arbitrary set, often one the WMO does not have.

    ``set_sizes`` gives a WMO's doodad count per set, by path; without it the
    first listed set other than 0 is kept.  A plain ``doodadSet`` past the
    WMO's last set is pointed at set 0.
    """
    names = split_names(placements.names, placements.ids)
    out = bytearray(placements.entries)
    chosen = narrowed = out_of_range = 0
    for base in range(0, len(out) - WMOS.entry_size + 1, WMOS.entry_size):
        name_id = struct.unpack_from("<I", out, base)[0]
        flags, doodad_set = struct.unpack_from("<HH", out, base + MODF_DOODAD_SET_AT - 2)
        path = names[name_id] if name_id < len(names) else ""
        sizes = set_sizes(path) if set_sizes is not None and path else None
        if flags & MODF_SETS_FROM_MWDS:
            listed: list[int] = []
            if (doodad_set + 1) * 8 <= len(mwdr):
                begin, end = struct.unpack_from("<II", mwdr, doodad_set * 8)
                listed = [struct.unpack_from("<H", mwds, i * 2)[0]
                          for i in range(begin, end + 1) if (i + 1) * 2 <= len(mwds)]
            extra = [s for s in listed if s and (sizes is None or s < len(sizes))]
            if sizes is not None:
                extra.sort(key=lambda s: -sizes[s])
            pick = extra[0] if extra else 0
            chosen += 1
            narrowed += len(extra) > 1
            struct.pack_into("<HH", out, base + MODF_DOODAD_SET_AT - 2,
                             flags & ~MODF_SETS_FROM_MWDS, pick)
        elif sizes is not None and doodad_set >= max(len(sizes), 1):
            out_of_range += 1
            struct.pack_into("<H", out, base + MODF_DOODAD_SET_AT, 0)
    placements.entries = bytes(out)
    if narrowed:
        result.lossy(f"{code}.doodad_sets",
                     f"{narrowed} wmo placement(s) showed several doodad sets "
                     f"at once; 3.3.5a shows one besides the default, so each "
                     f"keeps its largest", placements=narrowed)
    elif chosen:
        result.info(f"{code}.doodad_sets",
                    f"named the doodad set of {chosen} wmo placement(s) that "
                    f"listed theirs in MWDS", placements=chosen)
    if out_of_range:
        result.lossy(f"{code}.doodad_set_range",
                     f"{out_of_range} wmo placement(s) named a doodad set their "
                     f"world object does not have; pointed them at the default "
                     f"set", placements=out_of_range)


def remap_references(refs: list[int], remap: dict[int, int] | None) -> list[int]:
    """Renumber placement references after entries were dropped."""
    if remap is None:
        return refs
    return [remap[r] for r in refs if r in remap]
