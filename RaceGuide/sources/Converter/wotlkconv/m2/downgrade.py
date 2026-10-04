"""Turning a modern M2 into one the 3.3.5a client will load.

The work splits into four kinds of change:

**Container.**  Unwrap ``MD21`` and drop every sibling chunk, because 3.3.5a
reads a flat MD20 and stops at the header.

**Re-externalised data.**  Legion moved bones, sequences and attachments into a
``.skel`` file and every asset reference into a FileDataID.  Both have to come
back inline -- the skeleton merged into the model, the IDs resolved to paths
through the community listfile.

**Struct layout.**  ``M2Sequence``, ``M2Camera`` and ``M2Particle`` changed
shape after Wrath and are mapped field by field.

**Feature clamping.**  Blend modes, flag bits, emitter shapes and texture types
that postdate 3.3.5a are folded onto the nearest thing the old client renders,
and every such fold is recorded on the :class:`~wotlkconv.report.FileResult` so
the user knows what changed.
"""

from __future__ import annotations

import math
import os

from ..limits import (
    M2_BLEND_MODE_FALLBACK,
    M2_BONE_FLAG_MASK,
    M2_DEFAULT_FOV,
    M2_EMITTER_TYPES_SUPPORTED,
    M2_GLOBAL_FLAG_MASK,
    M2_MATERIAL_FLAG_MASK,
    M2_MAX_BLEND_MODE,
    M2_MAX_PARTICLE_BLEND_MODE,
    M2_MAX_SKIN_PROFILES,
    M2_MAX_TEXTURE_TYPE,
    M2_PACKED_GRAVITY_SCALE,
    M2_PARTICLE_FLAG_COMPRESSED_GRAVITY,
    M2_PARTICLE_FLAG_MASK,
    M2_PARTICLE_FLAG_MULTI_TEXTURE,
    M2_SEQUENCE_FLAG_MASK,
    M2_SOFT_MAX_BONES,
    M2_VERSION,
    M2_VERSION_NEWEST_KNOWN,
)
from ..listfile import Listfile, normalise, placeholder_path
from ..options import Options, UnresolvedPolicy
from ..report import FileResult
from ..resolve import AssetSource
from . import schemas
from .model import (
    SEQUENCE_ALIAS_FLAG,
    SEQUENCE_EMBEDDED_FLAG,
    SEQUENCE_EMBEDDED_FLAGS,
    M2Model,
    external_sequences,
)
from .skel import Skeleton, load_skeleton_chain
from .types import Track, mark_external

#: Chunks whose loss is worth telling the user about, and why.
NOTABLE_DROPPED_CHUNKS = {
    "PFID": "physics rig (.phys) -- 3.3.5a has no model physics",
    "PABC": "parent animation blacklist",
    "PADC": "parent animation data",
    "PSBC": "parent sequence bounds",
    "PEDC": "parent event data",
    "LDV1": "level-of-detail data",
    "TXAC": "per-texture animation coefficients",
    "EXPT": "extended particle properties",
    "EXP2": "extended particle properties v2",
    "WFV1": "waterfall shader parameters",
    "WFV2": "waterfall shader parameters",
    "WFV3": "waterfall shader parameters",
    "PGD1": "particle geoset assignment",
    "DETL": "extended light definitions",
    "NERF": "alpha-fade curve",
    "EDGF": "edge-fade parameters",
    "DBOC": "dynamic bounding-object data",
    "AFRA": "animation frame ranges",
    "RPID": "recursive particle model references",
    "GPID": "geometry particle model references",
}


# ---------------------------------------------------------------------------
# Skeleton merge
# ---------------------------------------------------------------------------
def merge_skeleton(model: M2Model, skel: Skeleton, result: FileResult) -> None:
    """Fold a ``.skel``'s contents back into the model, Wrath-style."""
    if skel.bones and not model.bones:
        model.bones = skel.bones
        model.key_bone_lookup = skel.key_bone_lookup
        model.bones_from_skeleton = True
    if skel.sequences and not model.sequences:
        model.sequences = skel.sequences
        model.sequence_lookups = skel.sequence_lookups
        model.sequence_schema = skel.sequence_schema
        model.global_loops = skel.global_loops or model.global_loops
        # The model's own tracks -- colours, texture animation, particles --
        # are indexed by these sequences too, but were read before they were
        # known, so an external sub-array came out of the model at an offset
        # into its .anim.
        external = external_sequences(model.sequences, chunked=True)
        if external:
            for track in model.own_tracks():
                mark_external(track, external)
    if skel.attachments and not model.attachments:
        model.attachments = skel.attachments
        model.attachment_lookup = skel.attachment_lookup
        model.attachments_from_skeleton = True
    if skel.anim_file_ids and not model.anim_file_ids:
        model.anim_file_ids = skel.anim_file_ids
    result.info(
        "m2.skeleton.merged",
        f"merged external skeleton: {len(skel.bones)} bones, "
        f"{len(skel.sequences)} sequences, {len(skel.attachments)} attachments",
        bones=len(skel.bones), sequences=len(skel.sequences),
    )


def resolve_skeleton(model: M2Model, opts: Options, source: AssetSource | None,
                     result: FileResult) -> bool:
    """Load and merge the model's SKID skeleton. Returns False if unavailable."""
    if not model.skeleton_file_id:
        return True
    skel = None
    if source is not None:
        skel = load_skeleton_chain(source.loader_for(".skel"),
                                   model.skeleton_file_id, model.name or "model")
    if skel is None:
        if model.bones:
            result.warn("m2.skeleton.missing",
                        f"skeleton FileDataID {model.skeleton_file_id} not found, "
                        f"but the model carries its own bones; continuing")
            return True
        if opts.allow_missing_skeleton:
            result.lossy("m2.skeleton.missing",
                         f"skeleton FileDataID {model.skeleton_file_id} not found; "
                         f"the model will have no bones and no animations",
                         skeleton_file_id=model.skeleton_file_id)
            return True
        result.fail("m2.skeleton.missing",
                    f"this model keeps its bones and animations in .skel file "
                    f"{model.skeleton_file_id}, which was not found next to it. "
                    f"Extract the .skel alongside the .m2, or pass "
                    f"--allow-missing-skeleton to emit a static model",
                    skeleton_file_id=model.skeleton_file_id)
        return False
    merge_skeleton(model, skel, result)
    return True


# ---------------------------------------------------------------------------
# References
# ---------------------------------------------------------------------------
def _resolve_reference(file_id: int, kind: str, opts: Options, listfile: Listfile,
                       result: FileResult) -> str | None:
    """FileDataID -> in-game path, honouring the unresolved-reference policy."""
    path = listfile.path_for(file_id)
    if path is None:
        if opts.unresolved is UnresolvedPolicy.FAIL:
            result.fail("m2.reference.unresolved",
                        f"no listfile entry for {kind} FileDataID {file_id}; "
                        f"pass --listfile with a listfile new enough to contain it",
                        file_id=file_id, kind=kind)
            return None
        if opts.unresolved is UnresolvedPolicy.STRIP:
            result.lossy("m2.reference.stripped",
                         f"dropped unresolvable {kind} FileDataID {file_id}",
                         file_id=file_id, kind=kind)
            return ""
        path = placeholder_path(file_id, kind)
        result.lossy("m2.reference.placeholder",
                     f"{kind} FileDataID {file_id} is not in the listfile; "
                     f"pointed it at {path}",
                     file_id=file_id, kind=kind, path=path)
    if opts.path_prefix:
        path = normalise(opts.path_prefix.rstrip("\\/") + "\\" + path)
    return path


#: "Monster skin 1": filled from CreatureDisplayInfo on a creature, empty on
#: anything else -- a texture slot with no file to load.
EMPTY_REPLACEABLE_TEXTURE_TYPE = 11


def resolve_textures(model: M2Model, opts: Options, listfile: Listfile,
                     result: FileResult) -> None:
    """Turn TXID FileDataIDs back into the inline filenames 3.3.5a reads."""
    ids = model.texture_file_ids
    resolved = 0
    for i, tex in enumerate(model.textures):
        tex_type = tex.get("type", 0)
        tex["flags"] = tex.get("flags", 0) & 0x3  # wrap-x | wrap-y

        file_id = ids[i] if i < len(ids) else 0
        if tex_type > M2_MAX_TEXTURE_TYPE:
            if file_id or tex.get("filename"):
                result.lossy("m2.texture.type",
                             f"texture {i} uses replaceable type {tex_type}, "
                             f"which 3.3.5a does not know; treated as a "
                             f"hardcoded texture, since it names a file",
                             index=i, type=tex_type)
                tex["type"] = tex_type = 0
            else:
                result.lossy("m2.texture.type",
                             f"texture {i} uses replaceable type {tex_type} "
                             f"(guild emblems, character extras), which 3.3.5a "
                             f"does not know and nothing names a file for; made "
                             f"a replaceable texture 3.3.5a leaves empty",
                             index=i, type=tex_type)
                tex["type"] = tex_type = EMPTY_REPLACEABLE_TEXTURE_TYPE
                continue

        if tex.get("filename"):
            continue
        if tex_type != 0:
            # Types 1..15 are substituted by the client at draw time and never
            # carry a filename in any expansion.
            continue

        if not file_id:
            # A hardcoded texture with an empty name makes the client and
            # Noggit look up a file called "", which does not exist.
            result.lossy("m2.texture.missing",
                         f"texture {i} is a hardcoded texture with neither a "
                         f"filename nor a FileDataID; made a replaceable "
                         f"texture 3.3.5a leaves empty", index=i)
            tex["type"] = EMPTY_REPLACEABLE_TEXTURE_TYPE
            continue
        path = _resolve_reference(file_id, "blp", opts, listfile, result)
        if path is None:
            return
        tex["filename"] = path
        resolved += 1
    if resolved:
        result.info("m2.texture.resolved",
                    f"resolved {resolved} texture FileDataID(s) to paths",
                    count=resolved)


# ---------------------------------------------------------------------------
# Struct downgrades
# ---------------------------------------------------------------------------
def downgrade_sequences(model: M2Model, result: FileResult) -> None:
    if model.sequence_schema is schemas.SEQUENCE_264:
        return
    out = []
    for seq in model.sequences:
        s = dict(seq)
        # Legion split the single blend time into separate in/out halves; the
        # old client has one field, so keep the longer of the two.
        blend_in = s.pop("blend_time_in", 0)
        blend_out = s.pop("blend_time_out", 0)
        s["blend_time"] = max(blend_in, blend_out)
        out.append(s)
    model.sequences = out
    model.sequence_schema = schemas.SEQUENCE_264
    result.info("m2.sequence.blendtime",
                f"folded {len(out)} split blend-in/blend-out time(s) into "
                f"3.3.5a's single blend time")


def downgrade_cameras(model: M2Model, result: FileResult) -> None:
    if model.camera_schema is schemas.CAMERA_264 or not model.cameras:
        model.camera_schema = schemas.CAMERA_264
        return
    out = []
    animated = 0
    for cam in model.cameras:
        c = dict(cam)
        track = c.pop("fov_track", None)
        fov = M2_DEFAULT_FOV
        if track is not None:
            first = track.first_value()
            if first is not None:
                # M2SplineKey<float> is (value, in-tangent, out-tangent).
                fov = first[0] if isinstance(first, tuple) else float(first)
            if track.key_count() > 1:
                animated += 1
        c["fov"] = fov
        out.append(c)
    model.cameras = out
    model.camera_schema = schemas.CAMERA_264
    if animated:
        result.lossy("m2.camera.fov",
                     f"{animated} camera(s) animated their field of view; "
                     f"3.3.5a stores a single value, so the first key was kept",
                     cameras=animated)
    else:
        result.info("m2.camera.fov", "camera FoV tracks flattened to scalars")


def _unpack_gravity(track: Track) -> tuple[Track, int, int]:
    """A packed-vector gravity track as the scalar one 3.3.5a reads.

    Returns the new track, how many keys pulled sideways (which a scalar cannot
    say), and how many sequences were dropped because their keys sit in an
    ``.anim``.  A scalar ``g`` means the vector ``(0, 0, -g)``, so the scalar
    is the negated vertical component of the unpacked vector.
    """
    out = Track(kind="f32", interpolation=track.interpolation,
                global_sequence=track.global_sequence)
    sideways = 0
    in_anim = 0
    for index, (stamps, values) in enumerate(zip(track.timestamps, track.values)):
        if index in track.external:
            in_anim += 1
            out.timestamps.append([])
            out.values.append([])
            continue
        floats = []
        for x, y, z in values:
            dx, dy = x / 128.0, y / 128.0
            vertical = math.sqrt(max(0.0, 1.0 - dx * dx - dy * dy))
            magnitude = z * M2_PACKED_GRAVITY_SCALE
            if magnitude < 0:
                vertical, magnitude = -vertical, -magnitude
            if x or y:
                sideways += 1
            floats.append(-vertical * magnitude)
        out.timestamps.append(list(stamps))
        out.values.append(floats)
    return out, sideways, in_anim


def downgrade_particles(model: M2Model, opts: Options, result: FileResult) -> None:
    if opts.strip_particles and model.particles:
        result.lossy("m2.particle.stripped",
                     f"removed {len(model.particles)} particle emitter(s) "
                     f"(--strip-particles)", count=len(model.particles))
        model.particles = []
        model.particle_schema = schemas.PARTICLE_264
        return

    if not model.particles:
        model.particle_schema = schemas.PARTICLE_264
        return

    multi_texture = 0
    bad_emitter = 0
    clamped_blend = 0
    dropped_flags = 0
    gravity_emitters = gravity_sideways = gravity_in_anim = 0
    out = []
    defaults = schemas.PARTICLE_264.defaults()

    for part in model.particles:
        p = dict(defaults)
        for name, _kind, _off in schemas.PARTICLE_264.layout:
            if name in part:
                p[name] = part[name]

        if "multi_texture_param_x" in part:
            # Cataclysm reused Wrath's particle_type/head_or_tail bytes.
            p["particle_type"] = 0
            p["head_or_tail"] = 0

        flags = part.get("flags", 0)
        if flags & M2_PARTICLE_FLAG_COMPRESSED_GRAVITY and "gravity" in part:
            packed, sideways, in_anim = _unpack_gravity(part["gravity"])
            p["gravity"] = packed
            gravity_emitters += 1
            gravity_sideways += bool(sideways)
            gravity_in_anim += in_anim
        if flags & M2_PARTICLE_FLAG_MULTI_TEXTURE:
            multi_texture += 1
            # The texture field packs three 5-bit indices; keep the first.
            p["texture"] = part.get("texture", 0) & 0x1F
        # The packed-gravity and multi-texture bits are handled above and
        # reported on their own; any other bit past Wrath's is just lost.
        if flags & ~(M2_PARTICLE_FLAG_MASK | M2_PARTICLE_FLAG_COMPRESSED_GRAVITY
                     | M2_PARTICLE_FLAG_MULTI_TEXTURE):
            dropped_flags += 1
        p["flags"] = flags & M2_PARTICLE_FLAG_MASK

        emitter = p.get("emitter_type", 1)
        if emitter not in M2_EMITTER_TYPES_SUPPORTED:
            bad_emitter += 1
            p["emitter_type"] = 1  # plane

        blend = p.get("blending_type", 0)
        if blend > M2_MAX_PARTICLE_BLEND_MODE:
            clamped_blend += 1
            p["blending_type"] = 4  # additive reads best for effect art

        out.append(p)

    model.particles = out
    model.particle_schema = schemas.PARTICLE_264

    if gravity_sideways or gravity_in_anim:
        detail = []
        if gravity_sideways:
            detail.append(f"{gravity_sideways} pulled sideways as well as down, "
                          f"and 3.3.5a's gravity is vertical only, so only the "
                          f"vertical part was kept")
        if gravity_in_anim:
            detail.append(f"{gravity_in_anim} animation(s) kept their gravity keys "
                          f"in an .anim, where they cannot be unpacked, so those "
                          f"animations have none")
        result.lossy("m2.particle.gravity",
                     f"unpacked the vector gravity of {gravity_emitters} "
                     f"emitter(s); " + "; ".join(detail),
                     emitters=gravity_emitters)
    elif gravity_emitters:
        result.info("m2.particle.gravity",
                    f"unpacked the vector gravity of {gravity_emitters} emitter(s) "
                    f"into the plain downward pull 3.3.5a reads",
                    emitters=gravity_emitters)
    if multi_texture:
        result.lossy("m2.particle.multitexture",
                     f"{multi_texture} emitter(s) used Cataclysm multi-texture "
                     f"particles; only the first texture survives",
                     emitters=multi_texture)
    if bad_emitter:
        result.lossy("m2.particle.emitter_type",
                     f"{bad_emitter} emitter(s) used a spline or bone emitter "
                     f"shape, which 3.3.5a lacks; changed to a plane emitter",
                     emitters=bad_emitter)
    if clamped_blend:
        result.lossy("m2.particle.blend",
                     f"{clamped_blend} emitter(s) used a blend mode above "
                     f"3.3.5a's range; clamped to additive", emitters=clamped_blend)
    if dropped_flags:
        result.lossy("m2.particle.flags",
                     f"{dropped_flags} emitter(s) had post-Wrath behaviour flags "
                     f"that were cleared", emitters=dropped_flags)


def downgrade_ribbons(model: M2Model, opts: Options, result: FileResult) -> None:
    if opts.strip_ribbons and model.ribbons:
        result.lossy("m2.ribbon.stripped",
                     f"removed {len(model.ribbons)} ribbon emitter(s) "
                     f"(--strip-ribbons)", count=len(model.ribbons))
        model.ribbons = []
        return
    touched = 0
    for rib in model.ribbons:
        if rib.get("ribbon_color_index") or rib.get("texture_transform_lookup_index"):
            touched += 1
        # Wrath treats these two bytes as padding; leaving values there makes
        # the client read a colour index that does not exist.
        rib["ribbon_color_index"] = 0
        rib["texture_transform_lookup_index"] = 0
    if touched:
        result.lossy("m2.ribbon.multitexture",
                     f"{touched} ribbon(s) used Cataclysm colour/texture-transform "
                     f"indices; cleared", ribbons=touched)


def clamp_flags(model: M2Model, result: FileResult) -> None:
    """Mask off flag bits that only exist after 3.3.5a."""
    original = model.global_flags
    model.global_flags = original & M2_GLOBAL_FLAG_MASK
    if original != model.global_flags:
        result.info("m2.flags.global",
                    f"cleared post-Wrath global flags "
                    f"0x{original & ~M2_GLOBAL_FLAG_MASK:X}")

    sequences_changed = 0
    for seq in model.sequences:
        f = seq.get("flags", 0)
        masked = f
        if f & SEQUENCE_EMBEDDED_FLAGS and not f & SEQUENCE_ALIAS_FLAG:
            # Legion also says "in the model" with 0x100; Wrath only reads 0x20.
            masked |= SEQUENCE_EMBEDDED_FLAG
        masked &= M2_SEQUENCE_FLAG_MASK
        if masked != f:
            sequences_changed += 1
            seq["flags"] = masked
    if sequences_changed:
        result.info("m2.flags.sequence",
                    f"cleared post-Wrath flag bits on {sequences_changed} "
                    f"sequence(s)", sequences=sequences_changed)

    bones_changed = 0
    for bone in model.bones:
        f = bone.get("flags", 0)
        masked = f & M2_BONE_FLAG_MASK
        if masked != f:
            bones_changed += 1
            bone["flags"] = masked
    if bones_changed:
        result.info("m2.flags.bone",
                    f"cleared post-Wrath flag bits on {bones_changed} bone(s)",
                    bones=bones_changed)

    mats_flags = 0
    mats_blend = 0
    for mat in model.materials:
        f = mat.get("flags", 0)
        masked = f & M2_MATERIAL_FLAG_MASK
        if masked != f:
            mats_flags += 1
            mat["flags"] = masked
        blend = mat.get("blending_mode", 0)
        if blend in M2_BLEND_MODE_FALLBACK:
            mat["blending_mode"] = M2_BLEND_MODE_FALLBACK[blend]
            mats_blend += 1
        elif blend > M2_MAX_BLEND_MODE:
            mat["blending_mode"] = 2  # plain alpha is the safe default
            mats_blend += 1
    if mats_flags:
        result.info("m2.flags.material",
                    f"cleared post-Wrath render flags on {mats_flags} material(s)",
                    materials=mats_flags)
    if mats_blend:
        result.lossy("m2.material.blend",
                     f"{mats_blend} material(s) used a blend mode newer than "
                     f"3.3.5a; mapped to the nearest supported mode",
                     materials=mats_blend)


def strip_optional(model: M2Model, opts: Options, result: FileResult) -> None:
    if opts.strip_cameras and model.cameras:
        result.lossy("m2.camera.stripped",
                     f"removed {len(model.cameras)} camera(s) (--strip-cameras)",
                     count=len(model.cameras))
        model.cameras = []
        model.camera_lookup = []
    if opts.strip_lights and model.lights:
        result.lossy("m2.light.stripped",
                     f"removed {len(model.lights)} light(s) (--strip-lights)",
                     count=len(model.lights))
        model.lights = []


def report_version(model: M2Model, result: FileResult) -> None:
    """Say when a model is newer than any layout this tool was written for.

    The M2Sequence struct is 64 bytes in both eras, so the array is walked
    correctly either way and only the blend-time fields could be misread --
    a contained error, but a silent one, so it is named.
    """
    if model.version > M2_VERSION_NEWEST_KNOWN:
        result.warn("m2.version.newer",
                    f"M2 version {model.version} is newer than {M2_VERSION_NEWEST_KNOWN}, "
                    f"the newest this tool has layouts for; it was read with "
                    f"those, which is right unless Blizzard changed a struct "
                    f"since. Cameras and particles are checked as they parse, "
                    f"but a changed M2Sequence would show up as wrong "
                    f"animation blend times",
                    version=model.version)


def report_dropped_chunks(model: M2Model, result: FileResult) -> None:
    dropped: list[str] = []
    unknown: list[str] = []
    for name, size in sorted(model.extra_chunks.items()):
        if name == "SFID.lod":
            if size:
                result.info("m2.lod.dropped",
                            f"dropped {size} Legion LOD skin reference(s); "
                            f"3.3.5a only loads Model00-03.skin", count=size)
            continue
        why = NOTABLE_DROPPED_CHUNKS.get(name)
        if why:
            dropped.append(f"{name} ({why})")
        else:
            # Not a chunk this tool knows to expect: say so, rather than
            # listing it beside the ones that were dropped on purpose.
            dropped.append(f"{name} (unrecognised -- contents unknown)")
            unknown.append(name)
    if model.phys_file_id:
        dropped.append("PFID (physics rig)")
    if dropped:
        result.lossy("m2.chunks.dropped",
                     "dropped chunks with no 3.3.5a equivalent: " + ", ".join(dropped),
                     chunks=sorted(model.extra_chunks))
    if unknown:
        result.lossy("m2.chunks.unknown",
                     f"{len(unknown)} of those are chunks this tool does not "
                     f"recognise at all, so what they carried is unknown: "
                     + ", ".join(sorted(unknown)),
                     chunks=sorted(unknown))


def validate(model: M2Model, opts: Options, result: FileResult) -> None:
    # The vertex limit is checked later, in wotlkconv.m2.split: dropping
    # geometry no submesh draws often brings a model back under it on its own,
    # and that needs the skin profiles, which are loaded after the downgrade.
    if len(model.bones) > M2_SOFT_MAX_BONES:
        msg = (f"{len(model.bones)} bones is above the {M2_SOFT_MAX_BONES} the "
               f"3.3.5a renderer keeps matrix slots for; the model may render "
               f"with collapsed limbs")
        if opts.strict_limits:
            result.fail("m2.limit.bones", msg, bones=len(model.bones))
        else:
            result.lossy("m2.limit.bones", msg, bones=len(model.bones))
    if model.num_skin_profiles > M2_MAX_SKIN_PROFILES:
        result.info("m2.limit.skins",
                    f"clamped {model.num_skin_profiles} skin profiles to "
                    f"{M2_MAX_SKIN_PROFILES}")
        model.num_skin_profiles = M2_MAX_SKIN_PROFILES
    if model.num_skin_profiles == 0 and model.skin_file_ids:
        model.num_skin_profiles = min(len(model.skin_file_ids), M2_MAX_SKIN_PROFILES)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def downgrade_model(model: M2Model, opts: Options, listfile: Listfile,
                    source: AssetSource | None, result: FileResult) -> M2Model:
    """Apply every transformation needed to make ``model`` a 3.3.5a MD20."""
    result.source_version = f"M2 v{model.version}" + (" (chunked)" if model.chunked else "")

    if not resolve_skeleton(model, opts, source, result):
        return model

    resolve_textures(model, opts, listfile, result)
    downgrade_sequences(model, result)
    downgrade_cameras(model, result)
    downgrade_particles(model, opts, result)
    downgrade_ribbons(model, opts, result)
    strip_optional(model, opts, result)
    clamp_flags(model, result)
    report_version(model, result)
    report_dropped_chunks(model, result)
    validate(model, opts, result)

    model.version = M2_VERSION
    result.target_version = f"M2 v{M2_VERSION}"
    return model


def anim_filename(model_path: str, anim_id: int, sub_id: int) -> str:
    """3.3.5a external animation filename: ``<model><anim:04d>-<sub:02d>.anim``."""
    stem = os.path.splitext(os.path.basename(model_path))[0]
    return f"{stem}{anim_id:04d}-{sub_id:02d}.anim"
