"""Top-level M2 conversion: the model plus everything that travels with it.

A single ``.m2`` is never self-contained.  3.3.5a expects to find
``<model>00.skin`` .. ``<model>03.skin`` and ``<model><anim>-<sub>.anim`` beside
it, whereas a modern extraction names those files by FileDataID (or does not
include them at all).  This module converts the model, then goes looking for
its companions and renames them into the layout the old client globs for.
"""

from __future__ import annotations

import dataclasses
import os
import time

from ..limits import M2_MAX_SKIN_PROFILES, M2_VERSION
from ..listfile import Listfile
from ..options import Options
from ..report import FileResult, Status
from ..resolve import AssetSource
from .anim import convert_anim
from .downgrade import anim_filename, downgrade_model
from .model import SEQUENCE_ALIAS_FLAG, SEQUENCE_EMBEDDED_FLAG, M2Model, parse_m2, tracks_in
from .skin import Skin, downgrade_skin, parse_skin, write_skin
from .split import ModelPart, split_model
from .texcoords import assign_texture_coord_combos
from .write import write_md20


@dataclasses.dataclass(slots=True)
class ConvertedAsset:
    """One output file produced alongside the model."""

    filename: str
    data: bytes
    result: FileResult


def _model_stem(source_name: str, model: M2Model,
                output_stem: str | None = None) -> str:
    """Basename the client will glob companions by.

    3.3.5a derives ``<model>00.skin`` and ``<model><anim>-<sub>.anim`` from the
    model's *filename*, so the companions have to match whatever the model is
    written out as -- not the source filename, and not the name stored inside
    the model.
    """
    if output_stem:
        return output_stem
    stem = os.path.splitext(os.path.basename(source_name))[0]
    if stem.isdigit() and model.name:
        # Input named by FileDataID and no output name given: the model's own
        # name is a better guess than the numeric one.
        stem = os.path.splitext(os.path.basename(model.name.replace("\\", "/")))[0]
    return stem


def _load_skins(model: M2Model, source: AssetSource | None, source_name: str,
                opts: Options, result: FileResult
                ) -> tuple[dict[int, Skin], list[ConvertedAsset]]:
    """Find and parse the model's skin profiles, ready for splitting."""
    skins: dict[int, Skin] = {}
    failures: list[ConvertedAsset] = []
    if source is None:
        return skins, failures

    wanted = min(max(model.num_skin_profiles, len(model.skin_file_ids)),
                 M2_MAX_SKIN_PROFILES)
    src_stem = os.path.splitext(os.path.basename(source_name))[0]
    for index in range(wanted):
        raw = None
        if index < len(model.skin_file_ids):
            raw = source.by_file_id(model.skin_file_ids[index], ".skin")
        if raw is None:
            raw = source.by_path(f"{src_stem}{index:02d}.skin")
        file_id = model.skin_file_ids[index] \
            if index < len(model.skin_file_ids) else None
        if raw is None:
            if file_id and source.casc is not None and file_id in source.casc:
                sub = FileResult(source=f"{src_stem}{index:02d}.skin", kind="skin",
                                 status=Status.SKIPPED, file_id=file_id)
                sub.info("skin.unavailable", "skin profile referenced by the "
                         "model could not be read", file_id=file_id)
                failures.append(ConvertedAsset(sub.source, b"", sub))
            continue
        name = f"{src_stem}{index:02d}.skin"
        try:
            skins[index] = parse_skin(raw, name)
        except Exception as exc:
            sub = FileResult(source=name, kind="skin", file_id=file_id)
            sub.fail("skin.error", f"{type(exc).__name__}: {exc}")
            failures.append(ConvertedAsset(name, b"", sub))

    if not skins and wanted:
        result.warn("m2.skin.missing",
                    "no .skin profiles found next to the model; 3.3.5a will "
                    "not render it without its 00.skin",
                    expected=wanted)
    elif len(skins) < wanted:
        result.info("m2.skin.partial",
                    f"found {len(skins)} of {wanted} skin profile(s)",
                    found=len(skins), expected=wanted)
    return skins, failures


def _emit_skins(part: ModelPart, stem: str, opts: Options,
                uses_combiner_combos: bool,
                file_ids: list[int] = ()) -> list[ConvertedAsset]:
    """Downgrade and serialise a part's skin profiles."""
    out: list[ConvertedAsset] = []
    written: dict[int, bytes] = {}
    for index, skin in sorted(part.skins.items()):
        name = f"{stem}{index:02d}.skin"
        sub = FileResult(source=name, kind="skin",
                         file_id=file_ids[index] if index < len(file_ids) else None)
        sub.source_version = (f"SKIN {len(skin.vertices)} verts, "
                              f"{skin.triangle_count} tris, "
                              f"{len(skin.submeshes)} submeshes")
        cached = written.get(id(skin))
        if cached is None:
            if not downgrade_skin(skin, opts, uses_combiner_combos, sub):
                out.append(ConvertedAsset(name, b"", sub))
                continue
            cached = write_skin(skin)
            written[id(skin)] = cached
        sub.bytes_out = len(cached)
        sub.target_version = f"SKIN wotlk {len(skin.vertices)} verts"
        out.append(ConvertedAsset(name, cached, sub))
    return out


def _has_keys(track, index: int) -> bool:
    spans = track.timestamp_spans
    if index < len(spans) and spans[index][0]:
        return True
    return index < len(track.timestamps) and bool(track.timestamps[index])


def _embed_empty_sequences(model: M2Model, stem: str,
                           anims: list[ConvertedAsset],
                           result: FileResult) -> None:
    """Mark sequences with no keyframes anywhere, and no .anim, as embedded.

    Retail leaves many sequences unflagged that no file and no track has data
    for (an item model's idle variants, say).  3.3.5a and Noggit go looking
    for ``<model><id>-<sub>.anim`` for every sequence without the embedded
    flag; with nothing to find, saying the keyframes are in the model --
    where there are none -- is the same animation without the lookup.
    """
    written = {asset.filename.lower() for asset in anims if asset.data}
    tracks = list(tracks_in(model.bones, model.colors, model.texture_weights,
                            model.texture_transforms, model.attachments,
                            model.events, model.lights, model.cameras,
                            model.ribbons, model.particles))
    marked = 0
    for index, seq in enumerate(model.sequences):
        flags = seq.get("flags", 0)
        if flags & (SEQUENCE_EMBEDDED_FLAG | SEQUENCE_ALIAS_FLAG):
            continue
        name = anim_filename(stem + ".m2", seq.get("id", 0),
                             seq.get("variation_index", 0)).lower()
        if name in written or any(_has_keys(t, index) for t in tracks):
            continue
        seq["flags"] = flags | SEQUENCE_EMBEDDED_FLAG
        marked += 1
    if marked:
        result.info("m2.sequence.embedded",
                    f"marked {marked} sequence(s) with no keyframes and no "
                    f".anim as embedded, so nothing looks for a file that does "
                    f"not exist", sequences=marked)


def _collect_anims(model: M2Model, stem: str, source: AssetSource | None,
                   opts: Options, result: FileResult) -> list[ConvertedAsset]:
    """Convert the model's external animations.

    This moves the skeleton tracks' keyframe offsets to wherever each file's
    chunks land, so it has to run before the model is split or written.
    """
    out: list[ConvertedAsset] = []
    if source is None or not model.anim_file_ids:
        return out

    missing = 0
    seen: set[tuple[int, int]] = set()
    for ref in model.anim_file_ids:
        # One file per animation; a repeated entry would relocate twice.
        if (ref.anim_id, ref.sub_anim_id) in seen:
            continue
        if not ref.file_id:
            # Retail lists animations with no file (763 entries across 235
            # models); there is nothing missing to find.
            continue
        seen.add((ref.anim_id, ref.sub_anim_id))
        raw = source.by_file_id(ref.file_id, ".anim")
        name = anim_filename(stem + ".m2", ref.anim_id, ref.sub_anim_id)
        if raw is None:
            missing += 1
            if source.casc is not None and ref.file_id in source.casc:
                sub = FileResult(source=name, kind="anim", status=Status.SKIPPED,
                                 file_id=ref.file_id)
                sub.info("anim.unavailable", "external animation could not be "
                         "read; that sequence will not play", file_id=ref.file_id)
                out.append(ConvertedAsset(name, b"", sub))
            continue
        sub = FileResult(source=name, kind="anim", file_id=ref.file_id)
        try:
            data, sub = convert_anim(raw, name, opts, model, sub,
                                     anim_id=ref.anim_id,
                                     sub_id=ref.sub_anim_id)
        except Exception as exc:
            sub.fail("anim.error", f"{type(exc).__name__}: {exc}")
            out.append(ConvertedAsset(name, b"", sub))
            continue
        out.append(ConvertedAsset(name, data, sub))

    if missing:
        result.warn("m2.anim.missing",
                    f"{missing} of {len(model.anim_file_ids)} external .anim "
                    f"file(s) were not found; those sequences will not play",
                    missing=missing, total=len(model.anim_file_ids))
    return out


def convert_m2(data: bytes, source_name: str, opts: Options,
               listfile: Listfile | None = None,
               source: AssetSource | None = None,
               result: FileResult | None = None,
               output_stem: str | None = None
               ) -> tuple[bytes, FileResult, list[ConvertedAsset]]:
    """Convert one model. Returns (MD20 bytes, result, companion files).

    ``output_stem`` is the basename the model will be written as; companions
    are named to match it so the client finds them.
    """
    started = time.time()
    res = result or FileResult(source=source_name, kind="m2")
    res.kind = "m2"
    res.bytes_in = len(data)
    listfile = listfile or Listfile()

    model = parse_m2(data, source_name)
    already_wotlk = (model.version == M2_VERSION and not model.chunked)

    model = downgrade_model(model, opts, listfile, source, res)
    if not res.ok:
        res.elapsed = time.time() - started
        return b"", res, []

    stem = _model_stem(source_name, model, output_stem)
    companions: list[ConvertedAsset] = []
    skins: dict[int, Skin] = {}
    anims: list[ConvertedAsset] = []
    if opts.convert_companions:
        skins, failures = _load_skins(model, source, source_name, opts, res)
        companions += failures
        anims = _collect_anims(model, stem, source, opts, res)
        _embed_empty_sequences(model, stem, anims, res)

    parts = split_model(model, skins, opts, res)
    if not parts or not res.ok:
        res.elapsed = time.time() - started
        return b"", res, []
    for part in parts:
        assign_texture_coord_combos(part.model, part.skins, res)

    primary = parts[0]
    out = write_md20(primary.model)
    res.bytes_out = len(out)
    res.extra.update({
        "name": model.name,
        "vertices": primary.model.vertex_count,
        "bones": len(model.bones),
        "sequences": len(model.sequences),
        "textures": len(model.textures),
        "particles": len(primary.model.particles),
        "skin_profiles": model.num_skin_profiles,
        "parts": len(parts),
    })

    if opts.convert_companions:
        companions += _emit_skins(primary, stem, opts,
                                  model.uses_combiner_combos,
                                  model.skin_file_ids)
        companions += anims

    for part in parts[1:]:
        name = f"{stem}{part.suffix}"
        sub = FileResult(source=f"{name}.m2", kind="m2", status=res.status)
        sub.info("m2.split.part",
                 f"geometry split out of {stem}.m2 because the model has more "
                 f"vertices than a .skin can index")
        data = write_md20(part.model)
        sub.bytes_out = len(data)
        sub.extra["vertices"] = part.model.vertex_count
        companions.append(ConvertedAsset(f"{name}.m2", data, sub))
        companions += _emit_skins(part, name, opts, model.uses_combiner_combos,
                                  model.skin_file_ids)

    if already_wotlk and res.status is Status.OK:
        res.status = Status.PASSTHROUGH
        res.info("m2.passthrough", "already a version 264 model; rewritten as-is")

    res.elapsed = time.time() - started
    return out, res, companions


def inspect_m2(data: bytes, source_name: str) -> dict:
    model = parse_m2(data, source_name)
    return {
        "kind": "m2",
        "version": model.version,
        "chunked": model.chunked,
        "name": model.name,
        "vertices": model.vertex_count,
        "bones": len(model.bones),
        "sequences": len(model.sequences),
        "textures": len(model.textures),
        "materials": len(model.materials),
        "particles": len(model.particles),
        "ribbons": len(model.ribbons),
        "cameras": len(model.cameras),
        "lights": len(model.lights),
        "skin_profiles": model.num_skin_profiles,
        "texture_file_ids": model.texture_file_ids or None,
        "skin_file_ids": model.skin_file_ids or None,
        "skeleton_file_id": model.skeleton_file_id or None,
        "phys_file_id": model.phys_file_id or None,
        "anim_files": len(model.anim_file_ids) or None,
        "extra_chunks": model.extra_chunks or None,
        "wotlk_compatible": model.version == M2_VERSION and not model.chunked,
    }
