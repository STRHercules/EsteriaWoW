"""Compacting and splitting models that outgrew 16-bit indices.

A ``.skin`` addresses the model's vertices through a ``uint16`` array, so no
skin profile -- modern or Wrath -- can reach past vertex 65 535. A model with
more than that is unrenderable by any client, not just the old one, and there
are two reasons it happens:

**Dead vertices.** The model carries geometry no submesh draws. Compacting the
vertex array to what is actually referenced is lossless and usually brings the
model back under the limit on its own, so it is always tried first.

**Genuinely too much geometry.** Then the model is split into several, each
with its own vertex array and skins but sharing the rig, materials and
textures. That produces files nothing references yet, so unlike the WMO case it
is off by default: the user has to place the extra pieces.
"""

from __future__ import annotations

import dataclasses
import struct

from ..limits import M2_MAX_VERTICES
from ..options import Options
from ..report import FileResult
from .model import VERTEX_SIZE, M2Model
from .skin import Skin

#: M2SkinSection field offsets. ``Level`` is not a LOD number: it carries the
#: high 16 bits of ``indexStart``, which is how a skin addresses more than
#: 65 536 triangle indices without widening the field.
SUBMESH_LEVEL = 0x02
#: vertexStart, then vertexCount, indexStart and indexCount follow it.
SUBMESH_VERTEX_START = 0x04
#: M2Batch.skinSectionIndex.
BATCH_SUBMESH_INDEX = 0x04


@dataclasses.dataclass
class ModelPart:
    """One model produced from a compaction or split."""

    model: M2Model
    skins: dict[int, Skin] = dataclasses.field(default_factory=dict)
    #: Appended to the output filename; empty for the first part.
    suffix: str = ""
    vertex_count: int = 0


def referenced_vertices(skins: dict[int, Skin]) -> set[int]:
    """Every model vertex any profile draws."""
    used: set[int] = set()
    for skin in skins.values():
        used.update(skin.vertices)
    return used


def _submesh_range(blob: bytes) -> tuple[int, int, int, int]:
    """(vertexStart, vertexCount, indexStart, indexCount), Level folded in."""
    level = struct.unpack_from("<H", blob, SUBMESH_LEVEL)[0]
    vertex_start, vertex_count, index_start, index_count = struct.unpack_from(
        "<4H", blob, SUBMESH_VERTEX_START)
    return vertex_start, vertex_count, (level << 16) | index_start, index_count


def compact(model: M2Model, skins: dict[int, Skin],
            result: FileResult) -> int:
    """Drop vertices no profile references. Returns how many went.

    Lossless: the geometry that is drawn is untouched, and every skin is
    renumbered to match the smaller array.
    """
    total = model.vertex_count
    used = referenced_vertices(skins)
    if len(used) >= total:
        return 0

    order = sorted(used)
    remap = {old: new for new, old in enumerate(order)}
    blob = model.vertices
    model.vertices = b"".join(blob[i * VERTEX_SIZE:(i + 1) * VERTEX_SIZE]
                              for i in order)
    model.vertex_count = len(order)
    for skin in skins.values():
        skin.vertices = [remap[v] for v in skin.vertices]

    dropped = total - len(order)
    result.info("m2.vertices.compacted",
                f"dropped {dropped} vertex/vertices no submesh draws, leaving "
                f"{len(order)}", dropped=dropped, kept=len(order))
    return dropped


def _plan(skin: Skin, limit: int) -> list[list[int]]:
    """Group submesh indices so each group stays inside ``limit`` vertices."""
    parts: list[list[int]] = []
    current: list[int] = []
    current_vertices: set[int] = set()

    for index, blob in enumerate(skin.submeshes):
        vertex_start, vertex_count, _i0, _i1 = _submesh_range(blob)
        needed = set(skin.vertices[vertex_start:vertex_start + vertex_count])
        if current and len(current_vertices | needed) > limit:
            parts.append(current)
            current, current_vertices = [], set()
        current.append(index)
        current_vertices |= needed
    if current:
        parts.append(current)
    return parts or [[]]


def _rebuild_skin(source: Skin, submesh_indices: list[int],
                  vertex_remap: dict[int, int]) -> Skin:
    """A skin holding only ``submesh_indices``, renumbered for the new model."""
    out = Skin(bone_count_max=source.bone_count_max)
    local: dict[int, int] = {}
    keep_positions: dict[int, int] = {}

    for new_index, submesh_index in enumerate(submesh_indices):
        blob = bytearray(source.submeshes[submesh_index])
        vertex_start, vertex_count, index_start, index_count = _submesh_range(blob)
        keep_positions[submesh_index] = new_index

        new_vertex_start = len(out.vertices)
        for offset in range(vertex_count):
            old_skin_vertex = vertex_start + offset
            model_vertex = source.vertices[old_skin_vertex]
            local[old_skin_vertex] = len(out.vertices)
            out.vertices.append(vertex_remap[model_vertex])
            bone_at = old_skin_vertex * 4
            out.bones += source.bones[bone_at:bone_at + 4] or b"\0\0\0\0"

        new_index_start = len(out.indices)
        for offset in range(index_count):
            # Triangle indices address the skin's whole vertex list, not the
            # submesh's slice of it, so they renumber with the list.
            old = source.indices[index_start + offset]
            out.indices.append(local.get(old, 0))

        struct.pack_into("<H", blob, SUBMESH_LEVEL, new_index_start >> 16)
        struct.pack_into("<4H", blob, SUBMESH_VERTEX_START, new_vertex_start,
                         vertex_count, new_index_start & 0xFFFF, index_count)
        out.submeshes.append(bytes(blob))

    for blob in source.batches:
        submesh_index = struct.unpack_from("<H", blob, BATCH_SUBMESH_INDEX)[0]
        if submesh_index not in keep_positions:
            continue
        record = bytearray(blob)
        struct.pack_into("<H", record, BATCH_SUBMESH_INDEX,
                         keep_positions[submesh_index])
        out.batches.append(bytes(record))
    return out


def _bounds(vertices: bytes) -> tuple[tuple, float]:
    count = len(vertices) // VERTEX_SIZE
    if count == 0:
        return (0.0,) * 6, 0.0
    lo = [float("inf")] * 3
    hi = [float("-inf")] * 3
    for i in range(count):
        x, y, z = struct.unpack_from("<3f", vertices, i * VERTEX_SIZE)
        for axis, value in enumerate((x, y, z)):
            lo[axis] = min(lo[axis], value)
            hi[axis] = max(hi[axis], value)
    centre = [(hi[a] + lo[a]) / 2.0 for a in range(3)]
    radius = max(
        sum((c - v) ** 2 for c, v in zip(centre, corner)) ** 0.5
        for corner in ((lo[0], lo[1], lo[2]), (hi[0], hi[1], hi[2])))
    return tuple(lo) + tuple(hi), radius


def split_model(model: M2Model, skins: dict[int, Skin], opts: Options,
                result: FileResult) -> list[ModelPart]:
    """Compact the model, then split it if it still cannot be indexed."""
    if not skins:
        if model.vertex_count > M2_MAX_VERTICES:
            result.fail("m2.limit.vertices",
                        f"{model.vertex_count} vertices exceeds the "
                        f"{M2_MAX_VERTICES} a .skin can index, and no skin "
                        f"profile was available to work out which of them are "
                        f"actually used",
                        vertices=model.vertex_count)
        return [ModelPart(model, skins, "", model.vertex_count)]

    compact(model, skins, result)
    if model.vertex_count <= M2_MAX_VERTICES:
        return [ModelPart(model, skins, "", model.vertex_count)]

    if not opts.split_oversized_models:
        result.fail("m2.limit.vertices",
                    f"{model.vertex_count} vertices still exceeds the "
                    f"{M2_MAX_VERTICES} a .skin can index after dropping unused "
                    f"geometry. Pass --split-models to break the model into "
                    f"several, or split it in a model editor",
                    vertices=model.vertex_count)
        return []

    base = skins.get(0) or next(iter(skins.values()))
    groups = _plan(base, M2_MAX_VERTICES)
    if len(groups) <= 1:
        return [ModelPart(model, skins, "", model.vertex_count)]

    result.lossy("m2.split",
                 f"{model.vertex_count} vertices exceeds the {M2_MAX_VERTICES} "
                 f"a .skin can index, so the model was split into "
                 f"{len(groups)} files sharing one rig. Nothing references the "
                 f"extra pieces yet -- place them alongside the first",
                 vertices=model.vertex_count, parts=len(groups))
    if len(skins) > 1:
        result.lossy("m2.split.lod",
                     "the split model's level-of-detail profiles were replaced "
                     "with copies of the full-detail one",
                     profiles=len(skins))

    blob = model.vertices
    parts: list[ModelPart] = []
    for number, submesh_indices in enumerate(groups):
        used: list[int] = []
        seen: set[int] = set()
        for submesh_index in submesh_indices:
            vertex_start, vertex_count, _a, _b = _submesh_range(
                base.submeshes[submesh_index])
            for model_vertex in base.vertices[vertex_start:vertex_start + vertex_count]:
                if model_vertex not in seen:
                    seen.add(model_vertex)
                    used.append(model_vertex)
        remap = {old: new for new, old in enumerate(used)}

        piece = dataclasses.replace(model)
        piece.vertices = b"".join(blob[v * VERTEX_SIZE:(v + 1) * VERTEX_SIZE]
                                  for v in used)
        piece.vertex_count = len(used)
        box, radius = _bounds(piece.vertices)
        piece.bounding_box = box
        piece.bounding_sphere_radius = radius
        if number > 0:
            # Everything attached to the model as a whole stays with the first
            # piece, so effects and collision are not emitted several times.
            piece.collision_indices = []
            piece.collision_positions = []
            piece.collision_face_normals = []
            piece.particles = []
            piece.ribbons = []
            piece.lights = []
            piece.cameras = []
            piece.camera_lookup = []
            piece.attachments = []
            piece.attachment_lookup = []
            piece.events = []

        rebuilt = _rebuild_skin(base, submesh_indices, remap)
        piece_skins = dict.fromkeys(sorted(skins), rebuilt)
        parts.append(ModelPart(piece, piece_skins,
                               "" if number == 0 else f"_part{number}",
                               len(used)))
    return parts
