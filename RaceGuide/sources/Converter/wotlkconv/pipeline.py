"""Batch conversion: discovery, output naming and execution.

The pipeline turns a pile of paths into a list of jobs and runs them.  Two
things make that less trivial than it sounds:

* **Terrain arrives in pieces.**  ``Zone_32_48.adt``, ``_tex0`` and ``_obj0``
  are one logical tile and have to be converted together, so they are grouped
  by base name before any work starts.
* **Extractions are named inconsistently.**  A file dumped by FileDataID has
  no path at all, so with a listfile the output is renamed to the in-game path
  the client will look for.
"""

from __future__ import annotations

import collections
import dataclasses
import os
import struct
import time
from collections.abc import Iterable, Sequence
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from . import detect, log
from .adt import AdtParts, convert_adt, convert_wdl, convert_wdt
from .adt.mh2o import LiquidTypes
from .blp import convert_blp
from .db import DbdIndex, MappingLibrary, convert_db2, find_template
from .errors import ConverterError
from .listfile import Listfile, to_posix
from .m2 import convert_anim, convert_m2, convert_skin
from .minimap import relocated_path
from .options import Options
from .report import FileResult, Report, Status
from .resolve import AssetSource
from .wmo import convert_group, convert_wmo_root
from .wmo.root import parse_root

#: Directory walking opens everything: a patch build needs the sound and
#: interface files as much as the converted art, and files extracted by
#: FileDataID have no meaningful extension to filter on.


@dataclasses.dataclass(slots=True)
class Job:
    """One unit of work: a file to convert, or one to copy through."""

    kind: str
    relpath: str
    source: Path | None = None
    #: Set instead of ``source`` when the bytes come out of a CASC install.
    file_id: int | None = None
    action: str = detect.CONVERT
    #: Extra inputs for a split terrain tile, by piece name ("tex0", "obj0").
    extra: dict[str, Path] = dataclasses.field(default_factory=dict)
    extra_ids: dict[str, int] = dataclasses.field(default_factory=dict)
    #: Files the planner left to this job to convert (skins, animations,
    #: groups).  Any the converter does not produce are reported for it.
    companion_ids: tuple[int, ...] = ()

    def describe(self) -> str:
        pieces = sorted({*self.extra, *self.extra_ids})
        if pieces:
            return f"{self.relpath} (+{', '.join(pieces)})"
        return self.relpath


@dataclasses.dataclass(slots=True)
class Output:
    """One file the pipeline wants to write."""

    path: Path
    data: bytes
    result: FileResult
    #: Further paths the same bytes are written to: the names 3.3.5a looks a
    #: file up by when they differ from where the build keeps it.
    aliases: list[Path] = dataclasses.field(default_factory=list)


def iter_input_files(inputs: Sequence[str | os.PathLike[str]],
                     recursive: bool = True) -> list[tuple[Path, Path]]:
    """Expand paths into (root, file) pairs, where root anchors relative names."""
    out: list[tuple[Path, Path]] = []
    for entry in inputs:
        p = Path(entry)
        if p.is_file():
            out.append((p.parent, p))
        elif p.is_dir():
            walker = os.walk(p) if recursive else [(str(p), [], os.listdir(p))]
            for dirpath, _dirs, files in walker:
                for fn in sorted(files):
                    fp = Path(dirpath) / fn
                    if fp.is_file():
                        out.append((p, fp))
        else:
            log.warn(f"input not found, skipping: {p}")
    return out


#: Chunks that name a file belonging to another asset in the same run.
_COMPANION_CHUNKS = {"SFID", "AFID", "BFID", "SKID", "GFID"}


def _companion_references(kind: str, data: bytes) -> set[int]:
    """FileDataIDs this asset pulls in, so they are not converted twice."""
    return set(_companion_claims(kind, data))


# What a claimed file is to the asset that claims it.  The owner's converter
# writes and reports the first three; nobody writes the rest, so the planner
# has to report them itself or they leave the run unmentioned.
ROLE_SKIN = "skin"              # SFID slot the model converts (00..03)
ROLE_ANIM = "anim"              # AFID entry, the model's own or its skeleton's
ROLE_GROUP = "group"            # GFID slot below MOHD.nGroups
ROLE_SKIN_LOD = "skin-lod"      # SFID slot past num_skin_profiles (_lodNN.skin)
ROLE_SKIN_UNUSED = "skin-unused"  # a profile past the four 3.3.5a reads
ROLE_ANIM_REPEAT = "anim-repeat"  # a second file for an (anim, sub) already taken
ROLE_GROUP_LOD = "group-lod"    # GFID slot past nGroups (_NNN_lodK.wmo)
ROLE_SKELETON = "skeleton"      # SKID / SKPD: merged into the model
ROLE_BONE = "bone"              # BFID: no 3.3.5a equivalent

#: Roles whose file the owning asset's converter emits a result for.
EMITTED_ROLES = {ROLE_SKIN, ROLE_ANIM, ROLE_GROUP}
#: When two assets claim one file in different roles, the stronger one wins:
#: a file one model converts is not "unused" because another only lists it
#: as a LOD.
_ROLE_RANK = {ROLE_SKIN: 3, ROLE_ANIM: 3, ROLE_GROUP: 3, ROLE_SKELETON: 2,
              ROLE_SKIN_LOD: 1, ROLE_SKIN_UNUSED: 1, ROLE_ANIM_REPEAT: 1,
              ROLE_GROUP_LOD: 1, ROLE_BONE: 1}


def _u32s(payload: bytes) -> list[int]:
    return [int.from_bytes(payload[i:i + 4], "little")
            for i in range(0, len(payload) - len(payload) % 4, 4)]


def _companion_claims(kind: str, data: bytes, read_skeleton=None,
                      slots: list | None = None) -> dict[int, str]:
    """FileDataID -> role, for every file this asset pulls in.

    ``read_skeleton(file_id) -> bytes | None`` lets the claim follow a model's
    ``SKID`` into its ``.skel`` and that file's ``SKPD`` parents: a skeleton's
    AFID animations are converted by every model that merges it, exactly like
    the model's own, and a planner that cannot see them converts each one a
    second time with no model to place its keyframes.
    """
    from .chunks import ChunkReader as _CR
    from .limits import M2_MAX_SKIN_PROFILES

    claims: dict[int, str] = {}

    def claim(file_id: int, role: str, key=None) -> None:
        if file_id and slots is not None and role in EMITTED_ROLES:
            slots.append((role, key, file_id))
        if file_id and _ROLE_RANK[role] > _ROLE_RANK.get(claims.get(file_id), 0):
            claims[file_id] = role

    def anims(payload: bytes, taken: dict) -> None:
        for i in range(len(payload) // 8):
            anim_id = int.from_bytes(payload[i * 8:i * 8 + 2], "little")
            sub_id = int.from_bytes(payload[i * 8 + 2:i * 8 + 4], "little")
            file_id = int.from_bytes(payload[i * 8 + 4:i * 8 + 8], "little")
            first = taken.setdefault((anim_id, sub_id), file_id)
            claim(file_id, ROLE_ANIM if first == file_id else ROLE_ANIM_REPEAT,
                  (anim_id, sub_id))

    if kind not in (detect.M2, detect.WMO_ROOT):
        return claims
    known = {"MD21", "SFID", "AFID", "BFID", "SKID", "TXID", "PFID", "MOHD", "MVER"}
    try:
        chunks = {c.name: c.data for c in _CR.auto(data, known)}
        if kind == detect.M2:
            md21 = chunks.get("MD21", b"")
            views = int.from_bytes(md21[68:72], "little") if len(md21) >= 72 else 0
            ids = _u32s(chunks.get("SFID", b""))
            base = views or len(ids)
            for index, file_id in enumerate(ids):
                claim(file_id, ROLE_SKIN_LOD if index >= base else
                      ROLE_SKIN_UNUSED if index >= M2_MAX_SKIN_PROFILES else
                      ROLE_SKIN, index)
            taken: dict = {}
            anims(chunks.get("AFID", b""), taken)
            for file_id in _u32s(chunks.get("BFID", b"")):
                claim(file_id, ROLE_BONE)
            skeleton = next(iter(_u32s(chunks.get("SKID", b""))), 0)
            seen: set[int] = set()
            own_anims = bool(chunks.get("AFID"))
            while skeleton and skeleton not in seen:
                seen.add(skeleton)
                claim(skeleton, ROLE_SKELETON)
                raw = read_skeleton(skeleton) if read_skeleton else None
                if not raw:
                    break
                skel = {c.name: c.data for c in _CR(raw, reverse=False)}
                # merge_skeleton takes the first AFID found up the chain, and
                # only when the model has none of its own.
                if not own_anims and skel.get("AFID"):
                    anims(skel["AFID"], taken)
                    own_anims = True
                for file_id in _u32s(skel.get("BFID", b"")):
                    claim(file_id, ROLE_BONE)
                parent = skel.get("SKPD", b"")
                skeleton = int.from_bytes(parent[8:12], "little") \
                    if len(parent) >= 12 else 0
        else:
            mohd = chunks.get("MOHD", b"")
            groups = int.from_bytes(mohd[4:8], "little") if len(mohd) >= 8 else 0
            for index, file_id in enumerate(_u32s(chunks.get("GFID", b""))):
                claim(file_id, ROLE_GROUP if index < groups else ROLE_GROUP_LOD,
                      index)
    except Exception:
        return {}
    return claims


#: Planner result for a claimed file its owner does not write:
#: (status, kind, note code, reason).
_UNEMITTED = {
    ROLE_SKIN_LOD: (Status.SKIPPED, detect.SKIN, "plan.skin_lod",
                    ("a Legion LOD skin (listed past the model's skin profiles "
                     "in SFID); 3.3.5a only loads <model>00-03.skin, and "
                     "{owner} writes those")),
    ROLE_SKIN_UNUSED: (Status.SKIPPED, detect.SKIN, "plan.skin_unused",
                       ("skin profile past the four 3.3.5a reads; {owner} "
                        "writes profiles 00-03")),
    ROLE_ANIM_REPEAT: (Status.SKIPPED, detect.ANIM, "plan.anim_repeat",
                       ("a second file for an animation {owner} already "
                        "takes from another FileDataID")),
    ROLE_GROUP_LOD: (Status.SKIPPED, detect.WMO_GROUP, "plan.group_lod",
                     ("a level-of-detail group of {owner}; 3.3.5a renders only "
                      "a world object's base groups, which are converted")),
    ROLE_SKELETON: (Status.MERGED, detect.SKEL, "plan.merged",
                    ("skeleton merged into {owner}: its bones, sequences and "
                     "attachments are written into the model")),
    ROLE_BONE: (Status.SKIPPED, "bone", "plan.bone",
                detect.UNSUPPORTED_EXTENSIONS[".bone"] + " (listed by {owner})"),
}


def _companion_names(kind: str, path: Path) -> set[str]:
    """Sibling filenames the client would glob for this asset."""
    stem = path.stem
    if kind == detect.M2:
        names = {f"{stem}{i:02d}.skin".lower() for i in range(4)}
        return names
    if kind == detect.WMO_ROOT:
        return {f"{stem}_{i:03d}.wmo".lower() for i in range(512)}
    return set()


def _merged(source: str, kind: str, why: str,
            file_id: int | None = None) -> FileResult:
    """Record a file another output already carries, so it is still counted."""
    res = FileResult(source=source, kind=kind, status=Status.MERGED)
    if file_id is None:
        res.info("plan.merged", why)
    else:
        res.info("plan.merged", why, file_id=file_id)
    return res


def plan(inputs: Sequence[str | os.PathLike[str]], recursive: bool = True,
         claim_companions: bool = True, copy_unconverted: bool = True,
         convert_databases: bool = False
         ) -> tuple[list[Job], list[FileResult]]:
    """Classify inputs into jobs, grouping split terrain tiles.

    With ``claim_companions``, files that another job will pull in and rename
    (a model's .skin profiles, a WMO's groups) are dropped from the job list so
    they are not also converted under their original names.
    """
    jobs: list[Job] = []
    skipped: list[FileResult] = []
    adt_groups: dict[tuple[str, str], dict[str, Path]] = {}
    adt_roots: dict[tuple[str, str], Path] = {}

    claimed_ids: set[int] = set()
    claimed_names: set[str] = set()
    pending: list[tuple[Path, Path, str, bytes]] = []

    for root, path in iter_input_files(inputs, recursive):
        try:
            with path.open("rb") as fh:
                head = fh.read(4096)
                rest = fh.read() if claim_companions else b""
        except OSError as exc:
            res = FileResult(source=str(path))
            res.fail("io.read", f"cannot read file: {exc}")
            skipped.append(res)
            continue

        kind = detect.detect(head, str(path))
        rel = os.path.relpath(path, root)
        if claim_companions and kind in (detect.M2, detect.WMO_ROOT):
            claimed_ids |= _companion_references(kind, head + rest)
            claimed_names |= _companion_names(kind, path)

        if kind == detect.ADT:
            base = detect.adt_base_name(str(path))
            key = (str(path.parent), base.lower())
            stem = path.stem.lower()
            part = "root"
            for suffix in detect.SPLIT_ADT_SUFFIXES:
                if stem.endswith(suffix):
                    part = suffix.lstrip("_")
                    break
            adt_groups.setdefault(key, {})[part] = path
            if part == "root":
                adt_roots[key] = Path(root)
            continue

        action, reason = detect.classify(kind, str(path), convert_databases)
        if action == detect.COPY and not copy_unconverted:
            action, reason = detect.SKIP, (
                "3.3.5a reads this format unchanged, but --no-copy-unconverted "
                "was given")
        if action == detect.SKIP:
            res = FileResult(source=rel, kind=kind, status=Status.SKIPPED)
            res.info("detect.skipped", reason)
            skipped.append(res)
            continue

        pending.append((root, path, kind, rel, action, reason))

    for _root, path, kind, rel, action, _reason in pending:
        if claim_companions and kind in (detect.SKIN, detect.ANIM, detect.WMO_GROUP):
            # A claimed companion is not dropped: the asset that references
            # it converts it, under the name the client globs for, and emits
            # its own result. Recording it here as well would count it twice.
            if path.name.lower() in claimed_names:
                log.debug(f"{rel}: converted by the asset that references it")
                continue
            if path.stem.isdigit() and int(path.stem) in claimed_ids:
                log.debug(f"{rel}: converted by the asset that references it "
                          f"(FileDataID {path.stem})")
                continue
        jobs.append(Job(kind=kind, source=path, relpath=rel, action=action))

    for key, parts in sorted(adt_groups.items()):
        root_path = parts.get("root")
        if root_path is None:
            names = ", ".join(p.name for p in parts.values())
            res = FileResult(source=names, kind="adt", status=Status.SKIPPED)
            res.info("adt.no_root",
                     "split terrain pieces with no matching terrain file; "
                     "convert the tile's base .adt alongside them")
            skipped.append(res)
            continue
        anchor = adt_roots.get(key, root_path.parent)
        extra = {k: v for k, v in parts.items() if k in ("tex0", "obj0")}
        jobs.append(Job(kind=detect.ADT, source=root_path,
                        relpath=os.path.relpath(root_path, anchor), extra=extra))
        for part, path in sorted(extra.items()):
            skipped.append(_merged(os.path.relpath(path, anchor), detect.ADT,
                                   f"merged into {root_path.name} as the "
                                   f"tile's _{part} piece"))
        # Pieces the merged tile has no room for still have to be accounted
        # for, or they would leave the run without ever being mentioned.
        for part, path in sorted(parts.items()):
            if part in ("root", "tex0", "obj0"):
                continue
            res = FileResult(source=os.path.relpath(path, anchor),
                             kind=detect.ADT, status=Status.SKIPPED)
            res.info("adt.piece_unused",
                     detect.UNUSED_ADT_PIECES.get(
                         part, f"the _{part} piece has no 3.3.5a equivalent"))
            skipped.append(res)

    return jobs, skipped


def plan_casc(storage, listfile: Listfile, *, include: Sequence[str] = (),
              file_ids: Sequence[int] = (),
              exclude: Sequence[str] = (),
              claim_companions: bool = True, copy_unconverted: bool = True,
              convert_databases: bool = False
              ) -> tuple[list[Job], list[FileResult]]:
    """Choose files to pull out of a CASC install.

    Selection is by in-game path glob, which needs the listfile, or by explicit
    FileDataID, which does not. Files whose path is unknown are reported rather
    than silently missed, because "the listfile is too old" is by far the most
    common reason an extraction comes up short.
    """
    import fnmatch

    jobs: list[Job] = []
    skipped: list[FileResult] = []
    patterns = [normalise_pattern(p) for p in include]
    excludes = [normalise_pattern(p) for p in exclude]

    selected: dict[int, str] = {}
    for file_id in file_ids:
        path = listfile.path_for(file_id) or f"{file_id}.unknown"
        selected[file_id] = path

    if patterns:
        # "**" is the whole build and needs no path to match against, so a file
        # the listfile does not name is still taken -- it just arrives under
        # its FileDataID. Any narrower pattern does need a name.
        take_all = any(p == "**" for p in patterns)
        unnamed = 0
        for file_id in storage.file_ids():
            path = listfile.path_for(file_id)
            if path is None:
                if not take_all:
                    unnamed += 1
                    continue
                selected[file_id] = f"{file_id}.unknown"
                continue
            if not any(fnmatch.fnmatch(path, p) for p in patterns):
                continue
            if any(fnmatch.fnmatch(path, p) for p in excludes):
                continue
            selected[file_id] = path
        if unnamed:
            log.info(f"{unnamed} file(s) in this build have no listfile entry "
                     f"and cannot be matched by path; select them by "
                     f"--fileid, or take the whole build with --include '**'")

    #: FileDataID -> (role, path of the asset that claims it).
    claimed: dict[int, tuple[str, str]] = {}
    #: Output path (lowercase posix) a companion will be written to -> owner.
    companion_names: dict[str, tuple[str, int]] = {}
    companions_of: dict[int, tuple[int, ...]] = {}
    if claim_companions:
        def read_skeleton(skel_id: int) -> bytes | None:
            return storage.try_read_file_id(skel_id)[0]

        for file_id, path in selected.items():
            # An unnamed model claims its companions like a named one; left
            # out, its skins were converted twice and its LOD skins once each.
            if not path.endswith((".m2", ".wmo", ".unknown")):
                continue
            data, why = storage.try_read_file_id(file_id)
            if data is None:
                continue
            kind = detect.detect(data, path)
            slots: list = []
            claims = _companion_claims(kind, data, read_skeleton, slots)
            if not claims:
                continue
            owner = path if not path.endswith(".unknown") else \
                f"unknown\\{file_id}{detect.EXTENSIONS.get(kind, '.bin')}"
            for claimed_id, role in claims.items():
                held = claimed.get(claimed_id)
                if held is None or _ROLE_RANK[role] > _ROLE_RANK[held[0]]:
                    claimed[claimed_id] = (role, owner)
            stem = os.path.splitext(to_posix(owner))[0].lower()
            companions_of[file_id] = tuple(dict.fromkeys(f for _r, _k, f in slots
                                                         if f in selected))
            for role, key, claimed_id in slots:
                if role == ROLE_SKIN:
                    name = f"{stem}{key:02d}.skin"
                elif role == ROLE_ANIM:
                    name = f"{stem}{key[0]:04d}-{key[1]:02d}.anim"
                else:
                    name = f"{stem}_{key:03d}.wmo"
                companion_names.setdefault(name, (owner, claimed_id))

    # A tile's terrain, texture and object files are one job, as on disk.
    adt_pieces: dict[str, dict[str, tuple[int, str]]] = {}

    unreadable: set[str] = set()
    for file_id, path in sorted(selected.items(), key=lambda kv: kv[1]):
        held = claimed.get(file_id)
        if held is not None:
            role, owner = held
            if role in EMITTED_ROLES:
                # The owner converts it and reports it under its output name.
                log.debug(f"skipping {path}: converted as a companion")
                continue
            status, kind, code, reason = _UNEMITTED[role]
            if path.endswith(".unknown"):
                path = f"unknown\\{file_id}{detect.EXTENSIONS.get(kind, '.bin')}"
            res = FileResult(source=path, kind=kind, status=status)
            res.info(code, reason.format(owner=owner), file_id=file_id)
            skipped.append(res)
            continue
        clash = companion_names.get(to_posix(path).lower())
        if clash is not None and clash[1] != file_id:
            # Converting this would write the very path a companion is written
            # to, and whichever worker finishes last wins.
            res = FileResult(source=path, kind="unknown", status=Status.SKIPPED)
            res.info("plan.superseded",
                     f"{clash[0]} writes its own companion (FileDataID "
                     f"{clash[1]}) to this name; this file is not the one it "
                     f"references", file_id=file_id)
            skipped.append(res)
            continue
        # A database's unreleased rows are encrypted in sections of their own,
        # which the reader skips; the rest of the table is still readable.
        data, why = storage.try_read_file_id(
            file_id, zero_encrypted=path.lower().endswith(".db2"))
        if data is None:
            res = FileResult(source=path, kind="unknown", status=Status.SKIPPED)
            res.info("casc.unavailable", why, file_id=file_id)
            skipped.append(res)
            unreadable.add(path.lower())
            continue
        kind = detect.detect(data[:4096], path)
        if path.endswith(".unknown"):
            # No listfile entry: name it by FileDataID and detected type so it
            # still lands somewhere predictable.
            path = f"unknown\\{file_id}{detect.EXTENSIONS.get(kind, '.bin')}"
        action, reason = detect.classify(kind, path, convert_databases)
        if action == detect.COPY and not copy_unconverted:
            action, reason = detect.SKIP, (
                "3.3.5a reads this format unchanged, but --no-copy-unconverted "
                "was given")
        if action == detect.SKIP:
            res = FileResult(source=path, kind=kind, status=Status.SKIPPED)
            res.info("detect.skipped", reason, file_id=file_id)
            skipped.append(res)
            continue

        if kind == detect.ADT:
            base = detect.adt_base_name(path)
            stem = os.path.splitext(os.path.basename(path))[0].lower()
            piece = "root"
            for suffix in detect.SPLIT_ADT_SUFFIXES:
                if stem.endswith(suffix):
                    piece = suffix.lstrip("_")
                    break
            adt_pieces.setdefault(base.lower(), {})[piece] = (file_id, path)
            continue

        jobs.append(Job(kind=kind, relpath=to_posix(path), file_id=file_id,
                        action=action,
                        companion_ids=companions_of.get(file_id, ())))

    for _base, pieces in sorted(adt_pieces.items()):
        root_piece = pieces.get("root")
        if root_piece is None:
            # One result per piece: each is an input of its own.
            for part, (piece_id, piece_path) in sorted(pieces.items()):
                root_path = piece_path[: -len(f"_{part}.adt")] + ".adt"
                res = FileResult(source=piece_path, kind="adt",
                                 status=Status.SKIPPED)
                if root_path.lower() in unreadable:
                    res.info("adt.root_unavailable",
                             f"the tile's base terrain {root_path} is not "
                             f"readable from this install, and a piece is "
                             f"nothing without it", file_id=piece_id)
                else:
                    res.info("adt.no_root",
                             "split terrain piece with no matching terrain "
                             "file; widen the --include glob to take the "
                             "tile's base .adt", file_id=piece_id)
                skipped.append(res)
            continue
        file_id, path = root_piece
        merged_ids = {k: v[0] for k, v in pieces.items()
                      if k in ("tex0", "obj0")}
        jobs.append(Job(kind=detect.ADT, relpath=to_posix(path), file_id=file_id,
                        extra_ids=merged_ids))
        for part in sorted(merged_ids):
            skipped.append(_merged(pieces[part][1], detect.ADT,
                                   f"merged into {path} as the tile's "
                                   f"_{part} piece", pieces[part][0]))
        for part, (piece_id, piece_path) in sorted(pieces.items()):
            if part in ("root", "tex0", "obj0"):
                continue
            res = FileResult(source=piece_path, kind=detect.ADT,
                             status=Status.SKIPPED)
            res.info("adt.piece_unused",
                     detect.UNUSED_ADT_PIECES.get(
                         part, f"the _{part} piece has no 3.3.5a equivalent"),
                     file_id=piece_id)
            skipped.append(res)
    for res in skipped:
        # Every planner result above records the FileDataID it is about.
        res.file_id = next((n.detail["file_id"] for n in res.notes
                            if "file_id" in n.detail), None)
    return jobs, skipped


def normalise_pattern(pattern: str) -> str:
    """Match the way listfile paths are stored: lowercase, backslashes."""
    return pattern.replace("/", "\\").lower()


# ---------------------------------------------------------------------------
# Conversion
# ---------------------------------------------------------------------------
class Converter:
    """Runs jobs and decides where their outputs land."""

    def __init__(self, opts: Options, listfile: Listfile,
                 out_dir: Path, source: AssetSource, storage=None,
                 definitions: DbdIndex | None = None,
                 mappings: MappingLibrary | None = None,
                 aliases: dict[int, set[str]] | None = None):
        self.opts = opts
        self.listfile = listfile
        self.out_dir = Path(out_dir)
        self.source = source
        self.storage = storage
        self.definitions = definitions or DbdIndex(None)
        self.mappings = mappings or MappingLibrary(opts.db_mappings or None)
        #: FileDataID -> extra paths under the output root; see
        #: :meth:`wotlkconv.db.itemdisplay.ItemDisplayResolver.asset_aliases`.
        self.aliases = aliases or {}
        self._liquid_types: LiquidTypes | bool | None = False
        self._doodad_sets: dict[str, list[int] | None] = {}

    def liquid_types(self) -> LiquidTypes | None:
        """The install's liquid types, read once per worker for terrain."""
        if self._liquid_types is False:
            self._liquid_types = None
            if self.storage is not None and self.definitions:
                from .db.tables import TableProvider
                self._liquid_types = LiquidTypes.from_tables(TableProvider(
                    self.definitions, storage=self.storage,
                    listfile=self.listfile))
        return self._liquid_types

    def wmo_doodad_sets(self, path: str) -> list[int] | None:
        """How many doodads each of a world object's doodad sets holds, by its
        in-game path; None when the root cannot be found or read."""
        key = path.lower()
        if key not in self._doodad_sets:
            sizes = None
            file_id = self.listfile.id_for(path)
            data = (self.source.by_file_id(file_id, ".wmo") if file_id
                    else self.source.by_path(path))
            if data:
                try:
                    mods = parse_root(data, path).payload("MODS")
                    sizes = [struct.unpack_from("<I", mods, i * 32 + 24)[0]
                             for i in range(len(mods) // 32)]
                except (ConverterError, struct.error):
                    sizes = None
            self._doodad_sets[key] = sizes
        return self._doodad_sets[key]

    # -- naming ---------------------------------------------------------
    def output_path(self, job: Job) -> Path:
        rel = job.relpath
        stem = Path(rel).stem
        # Only a file dumped to disk by FileDataID is named by its number; a
        # CASC job already carries its listfile path, and "2.blp" in a texture
        # folder is not FileDataID 2 (interface/cinematics/wow_intro_800.avi).
        if (self.opts.name_from_listfile and job.file_id is None
                and stem.isdigit() and self.listfile):
            game_path = self.listfile.path_for(int(stem))
            if game_path:
                rel = to_posix(game_path)
        minimap = relocated_path(rel)
        if minimap is not None:
            # 3.3.5a finds minimap tiles through md5translate.trs; see minimap.py.
            rel = to_posix(minimap)
        if self.opts.flatten:
            rel = os.path.basename(rel)
        return self.out_dir / rel

    # -- work -----------------------------------------------------------
    def read(self, job: Job) -> bytes:
        if job.file_id is not None:
            if self.storage is None:
                raise ConverterError(
                    f"{job.relpath} comes from a CASC install but no storage "
                    f"is open")
            return self.storage.read_file_id(
                job.file_id, zero_encrypted=job.kind == detect.DB2)
        assert job.source is not None
        return job.source.read_bytes()

    def convert(self, job: Job) -> list[Output]:
        outputs = self._convert(job)
        if job.companion_ids:
            produced = {o.result.file_id for o in outputs}
            primary = outputs[0].result
            for fid in job.companion_ids:
                if fid in produced:
                    continue
                res = FileResult(source=f"{job.relpath}#{fid}", kind="companion",
                                 status=Status.SKIPPED, file_id=fid)
                why = ("the asset that references it did not convert"
                       if primary.status in (Status.FAILED, Status.SKIPPED)
                       else "the asset that references it did not produce it")
                res.info("plan.companion_not_produced",
                         f"FileDataID {fid} was left to {job.relpath} to "
                         f"convert, and {why}", file_id=fid)
                outputs.append(Output(outputs[0].path, b"", res))
        return outputs

    def _convert(self, job: Job) -> list[Output]:
        started = time.time()
        target = self.output_path(job)
        result = FileResult(source=job.relpath, kind=job.kind,
                            target=str(target), file_id=job.file_id)
        try:
            data = self.read(job)
        except ConverterError as exc:
            result.status = Status.SKIPPED
            result.info("io.unavailable", str(exc))
            result.elapsed = time.time() - started
            return [Output(target, b"", result)]
        except Exception as exc:
            result.fail("io.read", f"{type(exc).__name__}: {exc}")
            result.elapsed = time.time() - started
            return [Output(target, b"", result)]

        result.bytes_in = len(data)
        if job.source is not None:
            self.source.add_root(job.source.parent)

        if job.action == detect.COPY:
            result.status = Status.PASSTHROUGH
            result.kind = job.kind if job.kind != detect.UNKNOWN else "data"
            result.info("copy.verbatim",
                        "3.3.5a reads this format unchanged; copied into the "
                        "output as-is")
            result.elapsed = time.time() - started
            return [Output(target, data, result)]

        try:
            outputs = self._dispatch(job, data, target, result)
        except ConverterError as exc:
            result.fail(f"{job.kind}.error", str(exc))
            result.elapsed = time.time() - started
            return [Output(target, b"", result)]
        except Exception as exc:
            result.fail(f"{job.kind}.error", f"{type(exc).__name__}: {exc}")
            result.elapsed = time.time() - started
            return [Output(target, b"", result)]

        if result.elapsed == 0.0:
            result.elapsed = time.time() - started
        self._attach_aliases(job, target, outputs)
        return outputs

    def _attach_aliases(self, job: Job, target: Path, outputs: list[Output]) -> None:
        """Also write a file, and anything named after it, under its aliases.

        A model's skins and animations are named after the model, so an alias
        for ``helm_x_hu_m.m2`` carries ``helm_x_hu_m00.skin`` along as
        ``helm_x_hum00.skin``.
        """
        file_id = job.file_id
        if file_id is None and Path(job.relpath).stem.isdigit():
            file_id = int(Path(job.relpath).stem)
        names = self.aliases.get(file_id) if file_id is not None else None
        if not names or not outputs:
            return
        stem = target.stem.lower()
        for alias in sorted(names):
            alias_path = self.out_dir / alias.replace("\\", "/")
            for out in outputs:
                if out.path == target:
                    new = alias_path
                elif (out.path.parent == target.parent
                      and out.path.name.lower().startswith(stem)):
                    new = alias_path.parent / (alias_path.stem
                                               + out.path.name[len(stem):])
                else:
                    continue
                if new != out.path:
                    out.aliases.append(new)
        outputs[0].result.info(
            "io.aliases",
            f"also written as {', '.join(sorted(names))}: the name 3.3.5a's "
            f"databases give it", aliases=sorted(names))

    def _light_bands(self, data: bytes, job: Job, target: Path,
                     result: FileResult, tables) -> list[Output]:
        """LightData has no 3.3.5a table of its own, but it is where the two
        3.3.5a sky tables went; see :mod:`wotlkconv.db.lightbands`."""
        from .db.db2 import parse_db2
        from .db.lightbands import build_light_bands

        parsed = parse_db2(data, job.relpath, self.definitions, "LightData")
        params = tables.get("LightParams")
        if params is None:
            result.warn("db2.light_bands.no_params",
                        "LightParams could not be read, so only params with "
                        "LightData rows get sky bands")
        ints, floats, counts = build_light_bands(
            parsed.rows.values(), params.rows.keys() if params else ())
        result.kind = "db2"
        result.info("db2.light_bands",
                    f"rebuilt LightIntBand ({counts['int_rows']} rows) and "
                    f"LightFloatBand ({counts['float_rows']} rows) for "
                    f"{counts['params']} LightParams from LightData, which "
                    f"replaced them after Wrath", **counts)
        result.lossy("db2.light_bands.constants",
                     "three float bands (celestial glow and two unnamed ones) "
                     "have no LightData column; written as the 1.0, 0.95 and "
                     "1.0 3.3.5a's own tables hold in nearly every key")
        if counts["keys_truncated"]:
            result.lossy("db2.light_bands.keys",
                         f"{counts['keys_truncated']} param(s) had more than "
                         f"16 keys a day; the first 16 were kept",
                         params=counts["keys_truncated"])
        floats_result = FileResult(source=f"{job.relpath}#lightfloatband",
                                   kind="db2", status=result.status,
                                   file_id=job.file_id)
        floats_result.info("db2.light_bands", "LightFloatBand, rebuilt from "
                           "LightData alongside LightIntBand")
        return [Output(target.with_name("lightintband.dbc"), ints, result),
                Output(target.with_name("lightfloatband.dbc"), floats, floats_result)]

    def _dispatch(self, job: Job, data: bytes, target: Path,
                  result: FileResult) -> list[Output]:
        kind = job.kind
        opts = self.opts

        if kind == detect.BLP:
            out, result = convert_blp(data, job.relpath, opts, result)
            return [Output(target, out, result)]

        if kind == detect.SKIN:
            out, result = convert_skin(data, job.relpath, opts, False, result)
            return [Output(target, out, result)]

        if kind == detect.ANIM:
            out, result = convert_anim(data, job.relpath, opts, None, result)
            return [Output(target, out, result)]

        if kind == detect.M2:
            out, result, companions = convert_m2(data, job.relpath, opts,
                                                 self.listfile, self.source, result,
                                                 output_stem=target.stem)
            outputs = [Output(target, out, result)]
            for c in companions:
                if c.result.file_id is None:
                    # A split-off part: another output of this job's input.
                    c.result.file_id = job.file_id
                outputs.append(Output(target.parent / c.filename, c.data, c.result))
            return outputs

        if kind == detect.WMO_ROOT:
            out, result, companions = convert_wmo_root(data, job.relpath, opts,
                                                       self.listfile, self.source,
                                                       result,
                                                       output_stem=target.stem)
            outputs = [Output(target, out, result)]
            for c in companions:
                if c.result.file_id is None:
                    # A split-off part: another output of this job's input.
                    c.result.file_id = job.file_id
                outputs.append(Output(target.parent / c.filename, c.data, c.result))
            return outputs

        if kind == detect.WMO_GROUP:
            out, result = convert_group(data, job.relpath, opts, result)
            return [Output(target, out, result)]

        if kind == detect.DB2:
            from .db.convert import table_name_for

            table = table_name_for(job.relpath)
            template = find_template(opts.db_templates, table)
            from .db.tables import TableProvider

            tables = TableProvider(self.definitions, storage=self.storage,
                                   listfile=self.listfile,
                                   directory=job.source.parent if job.source else None)
            if table.lower() == "lightdata":
                try:
                    return self._light_bands(data, job, target, result, tables)
                finally:
                    tables.clear()
            try:
                out, result = convert_db2(data, job.relpath, opts, self.listfile,
                                          self.definitions, self.mappings,
                                          template, table, result, tables=tables)
            finally:
                tables.clear()
            # 3.3.5a reads .dbc, so the output changes extension.
            return [Output(target.with_suffix(".dbc"), out, result)]

        if kind == detect.WDT:
            out, result = convert_wdt(data, job.relpath, opts, result,
                                      self.listfile)
            return [Output(target, out, result)]

        if kind == detect.WDL:
            out, result = convert_wdl(data, job.relpath, opts, result)
            return [Output(target, out, result)]

        if kind == detect.ADT:
            parts = AdtParts(root=data)
            if opts.merge_split_adt:
                for piece in ("tex0", "obj0"):
                    if piece in job.extra:
                        setattr(parts, piece, job.extra[piece].read_bytes())
                    elif piece in job.extra_ids and self.storage is not None:
                        raw, why = self.storage.try_read_file_id(
                            job.extra_ids[piece])
                        if raw is None:
                            result.warn("adt.piece_unavailable",
                                        f"{piece} piece unavailable: {why}")
                        else:
                            setattr(parts, piece, raw)
            out, result = convert_adt(
                parts, job.relpath, opts, self.listfile, result,
                self.liquid_types(),
                self.storage.__contains__ if self.storage is not None else None,
                self.wmo_doodad_sets)
            return [Output(target, out, result)]

        result.status = Status.SKIPPED
        result.info("detect.unsupported", f"no converter for {kind!r}")
        return [Output(target, b"", result)]

    # -- output ---------------------------------------------------------
    def write(self, outputs: Iterable[Output]) -> None:
        for out in outputs:
            if not out.data or out.result.status is Status.FAILED:
                continue
            out.result.target = str(out.path)
            out.result.bytes_out = len(out.data)
            if self.opts.dry_run:
                continue
            if out.path.exists() and not self.opts.overwrite:
                out.result.warn("io.exists",
                                f"{out.path} already exists; pass --overwrite "
                                f"to replace it")
                continue
            out.path.parent.mkdir(parents=True, exist_ok=True)
            out.path.write_bytes(out.data)
            for alias in out.aliases:
                if alias.exists() and not self.opts.overwrite:
                    continue
                alias.parent.mkdir(parents=True, exist_ok=True)
                alias.write_bytes(out.data)


# ---------------------------------------------------------------------------
# Parallel execution
# ---------------------------------------------------------------------------
_WORKER: dict[str, object] = {}


def _worker_init(opts: Options, listfile_path: str | None, roots: list[str],
                 out_dir: str, casc: dict | None,
                 dbd_dir: str | None = None,
                 aliases: dict[int, set[str]] | None = None) -> None:  # pragma: no cover
    lf = Listfile.load(listfile_path) if listfile_path else Listfile()
    storage = None
    if casc:
        # Each worker opens its own handles; CascStorage is not picklable.
        from .casc import CascStorage, KeyRing
        keys = KeyRing.load(casc["keys"]) if casc.get("keys") else KeyRing()
        storage = CascStorage.open(casc["path"], product=casc.get("product"),
                                   locale=casc.get("locale", "enus"), keys=keys,
                                   cdn_cache=casc.get("cdn_cache"))
    source = AssetSource(lf, roots=roots, casc=storage)
    _WORKER["converter"] = Converter(opts, lf, Path(out_dir), source, storage,
                                     DbdIndex(dbd_dir) if dbd_dir else None,
                                     aliases=aliases)


def _worker_run(job: Job) -> list[Output]:  # pragma: no cover
    converter: Converter = _WORKER["converter"]  # type: ignore[assignment]
    outputs = converter.convert(job)
    converter.write(outputs)
    # Payloads stay in the worker; only the results travel back.
    return [Output(o.path, b"", o.result) for o in outputs]


#: Jobs handed to the pool per worker before waiting on the oldest.  The pool's
#: own ``map`` submits everything at once, which for a whole build is millions
#: of futures held in memory before the first file converts.
SUBMIT_WINDOW_PER_WORKER = 16


def _duration(seconds: float) -> str:
    seconds = int(seconds)
    hours, rest = divmod(seconds, 3600)
    minutes, seconds = divmod(rest, 60)
    if hours:
        return f"{hours}h {minutes:02d}m"
    if minutes:
        return f"{minutes}m {seconds:02d}s"
    return f"{seconds}s"


class Progress:
    """Logs how far a run has got, each time the whole percentage moves on.

    The estimate of time left assumes the rest of the files take as long on
    average as the ones so far; a build's big terrain and model jobs are
    spread through it, so that holds well enough to plan around.
    """

    def __init__(self, total: int, done: int = 0, clock=time.monotonic):
        self.total = total
        self.done = done
        self._clock = clock
        self._started = clock()
        self._start_done = done
        self._shown = self.percent

    @property
    def percent(self) -> int:
        return self.done * 100 // self.total if self.total else 100

    def advance(self, count: int = 1) -> None:
        self.done += count
        if self.percent > self._shown:
            self._shown = self.percent
            log.info(self.describe())

    def describe(self) -> str:
        elapsed = self._clock() - self._started
        text = (f"progress: {self.percent}% ({self.done:,} of {self.total:,} "
                f"files, {_duration(elapsed)} elapsed")
        converted = self.done - self._start_done
        if converted and self.done < self.total:
            left = elapsed * (self.total - self.done) / converted
            text += f", about {_duration(left)} left"
        return text + ")"


def _bounded_map(pool, fn, items: Sequence, window: int):
    """``(index, fn(item))`` in order, with at most ``window`` in flight."""
    pending: collections.deque = collections.deque()
    for index, item in enumerate(items):
        pending.append((index, pool.submit(fn, item)))
        if len(pending) >= window:
            done_index, future = pending.popleft()
            yield done_index, future.result()
    while pending:
        done_index, future = pending.popleft()
        yield done_index, future.result()


def run(jobs: Sequence[Job], opts: Options, listfile: Listfile,
        out_dir: str | os.PathLike[str], roots: Sequence[str] = (),
        listfile_path: str | None = None,
        skipped: Sequence[FileResult] = (),
        storage=None, casc_args: dict | None = None,
        definitions: DbdIndex | None = None,
        spool: str | os.PathLike[str] | None = None,
        aliases: dict[int, set[str]] | None = None) -> Report:
    """Convert every job, in parallel when asked, and collect the results.

    ``spool`` writes each result to that file as it arrives instead of
    holding it; see :class:`Report`.
    """
    report = Report(spool=Path(spool) if spool else None)
    report.extend(skipped)
    out_dir = Path(out_dir)
    progress = Progress(len(jobs))

    finished: set[int] = set()
    if opts.jobs > 1 and len(jobs) > 1:
        try:
            with ProcessPoolExecutor(
                    max_workers=opts.jobs, initializer=_worker_init,
                    initargs=(opts, listfile_path, list(roots), str(out_dir),
                              casc_args,
                              str(definitions.directory)
                              if definitions and definitions.directory else None,
                              aliases)
            ) as pool:
                window = opts.jobs * SUBMIT_WINDOW_PER_WORKER
                for index, outputs in _bounded_map(pool, _worker_run, jobs,
                                                   window):
                    for out in outputs:
                        report.add(out.result)
                    finished.add(index)
                    progress.advance()
            report.close()
            return report
        except Exception as exc:
            # Whatever already came back is reported and written; only the
            # rest is redone, so a worker lost hours in does not restart the
            # build or count its files twice.
            log.warn(f"parallel execution unavailable ({exc}); running the "
                     f"{len(jobs) - len(finished)} unfinished job(s) serially")

    source = AssetSource(listfile, roots=list(roots), casc=storage)
    converter = Converter(opts, listfile, out_dir, source, storage, definitions,
                          aliases=aliases)
    for index, job in enumerate(jobs):
        if index in finished:
            continue
        log.debug(f"converting {job.describe()}")
        outputs = converter.convert(job)
        converter.write(outputs)
        for out in outputs:
            report.add(out.result)
        progress.advance()
    report.close()
    return report
