"""Serialising an :class:`~wotlkconv.m2.model.M2Model` as a 3.3.5a MD20.

The writer is deliberately version-locked: it only ever emits version 264 with
the flat header 3.3.5a expects, no MD21 wrapper and no sibling chunks.  Layout
is two-pass -- the header is emitted with zeroed ``(count, offset)`` pairs whose
payloads are queued and patched by
:meth:`~wotlkconv.m2.types.DeferredWriter.flush`.
"""

from __future__ import annotations

from ..limits import M2_GLOBAL_FLAG_USE_COMBINER_COMBOS, M2_MAGIC, M2_VERSION
from . import schemas
from .model import VERTEX_SIZE, M2Model
from .types import DeferredWriter, Schema


def _emit_struct_array(w: DeferredWriter, pos: int, schema: Schema,
                       items: list[dict]) -> None:
    """Queue a contiguous array of schema-described structs."""

    def emit(writer: DeferredWriter) -> None:
        for item in items:
            writer.emit_struct(schema, item)

    w.defer(pos, len(items), emit)


def write_md20(model: M2Model, version: int = M2_VERSION,
               sequence_schema: Schema | None = None,
               camera_schema: Schema | None = None,
               particle_schema: Schema | None = None) -> bytes:
    """Serialise ``model`` as a flat MD20 file.

    Defaults produce exactly what 3.3.5a wants.  The schema overrides exist so
    the test suite can round-trip a Legion-shaped body through the same writer
    the converter uses, rather than through a second implementation that could
    drift from it.
    """
    sequence_schema = sequence_schema or schemas.SEQUENCE_264
    camera_schema = camera_schema or schemas.CAMERA_264
    particle_schema = particle_schema or schemas.PARTICLE_264

    w = DeferredWriter(alignment=4)

    w.magic(M2_MAGIC)
    w.u32(version)
    name_pos = w.reserve_array()
    w.u32(model.global_flags)
    loops_pos = w.reserve_array()
    sequences_pos = w.reserve_array()
    sequence_lookups_pos = w.reserve_array()
    bones_pos = w.reserve_array()
    key_bone_lookup_pos = w.reserve_array()
    vertices_pos = w.reserve_array()
    w.u32(model.num_skin_profiles)
    colors_pos = w.reserve_array()
    textures_pos = w.reserve_array()
    texture_weights_pos = w.reserve_array()
    texture_transforms_pos = w.reserve_array()
    replacable_pos = w.reserve_array()
    materials_pos = w.reserve_array()
    bone_combos_pos = w.reserve_array()
    texture_combos_pos = w.reserve_array()
    texture_coord_combos_pos = w.reserve_array()
    texture_weight_combos_pos = w.reserve_array()
    texture_transform_combos_pos = w.reserve_array()
    w.pack("6f", *model.bounding_box)
    w.f32(model.bounding_sphere_radius)
    w.pack("6f", *model.collision_box)
    w.f32(model.collision_sphere_radius)
    collision_indices_pos = w.reserve_array()
    collision_positions_pos = w.reserve_array()
    collision_normals_pos = w.reserve_array()
    attachments_pos = w.reserve_array()
    attachment_lookup_pos = w.reserve_array()
    events_pos = w.reserve_array()
    lights_pos = w.reserve_array()
    cameras_pos = w.reserve_array()
    camera_lookup_pos = w.reserve_array()
    ribbons_pos = w.reserve_array()
    particles_pos = w.reserve_array()

    combiner_pos = None
    if model.global_flags & M2_GLOBAL_FLAG_USE_COMBINER_COMBOS:
        combiner_pos = w.reserve_array()

    # -- payloads, in roughly the order Blizzard's own exporter used ----
    w.write_string_array(name_pos, model.name)
    w.write_array(loops_pos, "u32", model.global_loops)
    _emit_struct_array(w, sequences_pos, sequence_schema, model.sequences)
    w.write_array(sequence_lookups_pos, "u16", model.sequence_lookups)
    _emit_struct_array(w, bones_pos, schemas.BONE, model.bones)
    w.write_array(key_bone_lookup_pos, "u16", model.key_bone_lookup)

    vertex_blob = model.vertices
    vertex_count = len(vertex_blob) // VERTEX_SIZE
    w.defer(vertices_pos, vertex_count, lambda writer: writer.raw(vertex_blob))

    _emit_struct_array(w, colors_pos, schemas.COLOR, model.colors)
    _emit_struct_array(w, textures_pos, schemas.TEXTURE, model.textures)
    _emit_struct_array(w, texture_weights_pos, schemas.TEXTURE_WEIGHT,
                       model.texture_weights)
    _emit_struct_array(w, texture_transforms_pos, schemas.TEXTURE_TRANSFORM,
                       model.texture_transforms)
    w.write_array(replacable_pos, "u16", model.replacable_texture_lookup)
    _emit_struct_array(w, materials_pos, schemas.MATERIAL, model.materials)
    w.write_array(bone_combos_pos, "u16", model.bone_combos)
    w.write_array(texture_combos_pos, "u16", model.texture_combos)
    w.write_array(texture_coord_combos_pos, "u16", model.texture_coord_combos)
    w.write_array(texture_weight_combos_pos, "u16", model.texture_weight_combos)
    w.write_array(texture_transform_combos_pos, "u16", model.texture_transform_combos)
    w.write_array(collision_indices_pos, "u16", model.collision_indices)
    w.write_array(collision_positions_pos, "vec3", model.collision_positions)
    w.write_array(collision_normals_pos, "vec3", model.collision_face_normals)
    _emit_struct_array(w, attachments_pos, schemas.ATTACHMENT, model.attachments)
    w.write_array(attachment_lookup_pos, "u16", model.attachment_lookup)
    _emit_struct_array(w, events_pos, schemas.EVENT, model.events)
    _emit_struct_array(w, lights_pos, schemas.LIGHT, model.lights)
    _emit_struct_array(w, cameras_pos, camera_schema, model.cameras)
    w.write_array(camera_lookup_pos, "u16", model.camera_lookup)
    _emit_struct_array(w, ribbons_pos, schemas.RIBBON, model.ribbons)
    _emit_struct_array(w, particles_pos, particle_schema, model.particles)
    if combiner_pos is not None:
        w.write_array(combiner_pos, "u16", model.texture_combiner_combos)

    w.flush()
    return w.getvalue()
