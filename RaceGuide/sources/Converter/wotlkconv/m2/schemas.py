"""Field schemas for every M2 sub-struct, per format era.

Structs that never changed between 264 and 274 are defined once.  The three
that did change get one schema per era plus a mapping in
:mod:`wotlkconv.m2.downgrade`:

===============  =========================  ============================
struct           264 (Wrath)                272+ (Legion .. TWW)
===============  =========================  ============================
M2Sequence       ``blend_time: u32``        ``blend_time_in/out: u16``
M2Camera         ``fov: f32`` (100 bytes)   ``fov: M2Track`` (116 bytes)
M2Particle       476 bytes                  492 bytes (+multi-texture)
===============  =========================  ============================
"""

from __future__ import annotations

from ..limits import (
    M2_CAMERA_SIZE_LEGION,
    M2_CAMERA_SIZE_WOTLK,
    M2_PARTICLE_SIZE_CATA,
    M2_PARTICLE_SIZE_WOTLK,
)
from .types import Schema

# ---------------------------------------------------------------------------
# Era-independent structs
# ---------------------------------------------------------------------------
BONE = Schema("M2CompBone", [
    ("key_bone_id", ("p", "i")),
    ("flags", ("p", "I")),
    ("parent_bone", ("p", "h")),
    ("submesh_id", ("p", "H")),
    # WotLK calls this uDistToFurthDesc/uZRatioOfChain; Cata+ stores a CRC of
    # the bone name here. Either way it is four opaque bytes.
    ("bone_name_crc", ("p", "I")),
    ("translation", ("trk", "vec3")),
    ("rotation", ("trk", "quat16")),
    ("scale", ("trk", "vec3")),
    ("pivot", ("p", "fff")),
])

TEXTURE = Schema("M2Texture", [
    ("type", ("p", "I")),
    ("flags", ("p", "I")),
    ("filename", ("arr", "char")),
])

MATERIAL = Schema("M2Material", [
    ("flags", ("p", "H")),
    ("blending_mode", ("p", "H")),
])

COLOR = Schema("M2Color", [
    ("color", ("trk", "vec3")),
    ("alpha", ("trk", "fixed16")),
])

TEXTURE_WEIGHT = Schema("M2TextureWeight", [
    ("weight", ("trk", "fixed16")),
])

TEXTURE_TRANSFORM = Schema("M2TextureTransform", [
    ("translation", ("trk", "vec3")),
    ("rotation", ("trk", "quat")),
    ("scaling", ("trk", "vec3")),
])

ATTACHMENT = Schema("M2Attachment", [
    ("id", ("p", "I")),
    ("bone", ("p", "H")),
    ("unknown", ("p", "H")),
    ("position", ("p", "fff")),
    ("animate_attached", ("trk", "u8")),
])

EVENT = Schema("M2Event", [
    ("identifier", ("p", "4s")),
    ("data", ("p", "I")),
    ("bone", ("p", "I")),
    ("position", ("p", "fff")),
    ("enabled", ("trkb",)),
])

LIGHT = Schema("M2Light", [
    ("type", ("p", "H")),
    ("bone", ("p", "h")),
    ("position", ("p", "fff")),
    ("ambient_color", ("trk", "vec3")),
    ("ambient_intensity", ("trk", "f32")),
    ("diffuse_color", ("trk", "vec3")),
    ("diffuse_intensity", ("trk", "f32")),
    ("attenuation_start", ("trk", "f32")),
    ("attenuation_end", ("trk", "f32")),
    ("visibility", ("trk", "u8")),
])

RIBBON = Schema("M2Ribbon", [
    ("ribbon_id", ("p", "I")),
    ("bone_index", ("p", "I")),
    ("position", ("p", "fff")),
    ("texture_indices", ("arr", "u16")),
    ("material_indices", ("arr", "u16")),
    ("color_track", ("trk", "vec3")),
    ("alpha_track", ("trk", "fixed16")),
    ("height_above_track", ("trk", "f32")),
    ("height_below_track", ("trk", "f32")),
    ("edges_per_second", ("p", "f")),
    ("edge_lifetime", ("p", "f")),
    ("gravity", ("p", "f")),
    ("texture_rows", ("p", "H")),
    ("texture_cols", ("p", "H")),
    ("tex_slot_track", ("trk", "u16")),
    ("visibility_track", ("trk", "u8")),
    ("priority_plane", ("p", "h")),
    # Wrath pads these two bytes; Cata+ uses them for multi-texture ribbons.
    ("ribbon_color_index", ("p", "B")),
    ("texture_transform_lookup_index", ("p", "B")),
])

# ---------------------------------------------------------------------------
# M2Sequence
# ---------------------------------------------------------------------------
_SEQUENCE_HEAD = [
    ("id", ("p", "H")),
    ("variation_index", ("p", "H")),
    ("duration", ("p", "I")),
    ("movespeed", ("p", "f")),
    ("flags", ("p", "I")),
    ("frequency", ("p", "h")),
    ("padding", ("p", "H")),
    ("replay_min", ("p", "I")),
    ("replay_max", ("p", "I")),
]
_SEQUENCE_TAIL = [
    ("bounds_min", ("p", "fff")),
    ("bounds_max", ("p", "fff")),
    ("bounds_radius", ("p", "f")),
    ("variation_next", ("p", "h")),
    ("alias_next", ("p", "H")),
]

SEQUENCE_264 = Schema("M2Sequence@264",
                      [*_SEQUENCE_HEAD, ("blend_time", ("p", "I")), *_SEQUENCE_TAIL])
SEQUENCE_272 = Schema("M2Sequence@272",
                      [*_SEQUENCE_HEAD, ("blend_time_in", ("p", "H")), ("blend_time_out", ("p", "H")), *_SEQUENCE_TAIL])

# ---------------------------------------------------------------------------
# M2Camera
# ---------------------------------------------------------------------------
_CAMERA_CLIP = [
    ("far_clip", ("p", "f")),
    ("near_clip", ("p", "f")),
]
_CAMERA_BODY = [
    ("positions", ("trk", "splinevec3")),
    ("position_base", ("p", "fff")),
    ("target_position", ("trk", "splinevec3")),
    ("target_position_base", ("p", "fff")),
    ("roll", ("trk", "splinef32")),
]
#: Wrath keeps the field of view as a scalar straight after the type (checked
#: against 820 genuine 3.3.5a cameras); Cataclysm dropped it there and
#: appended an animated track instead, in the same units.
CAMERA_264 = Schema("M2Camera@264", [("type", ("p", "I")), ("fov", ("p", "f")), *_CAMERA_CLIP, *_CAMERA_BODY])
CAMERA_272 = Schema("M2Camera@272", [("type", ("p", "I")), *_CAMERA_CLIP, *_CAMERA_BODY, ("fov_track", ("trk", "splinef32"))])

# ---------------------------------------------------------------------------
# M2Particle
# ---------------------------------------------------------------------------
_PARTICLE_HEAD = [
    ("particle_id", ("p", "I")),
    ("flags", ("p", "I")),
    ("position", ("p", "fff")),
    ("bone", ("p", "H")),
    # Cata+ packs three 5-bit texture indices in here when the multi-texture
    # flag (0x10000000) is set.
    ("texture", ("p", "H")),
    ("geometry_model_filename", ("arr", "char")),
    ("recursion_model_filename", ("arr", "char")),
    ("blending_type", ("p", "B")),
    ("emitter_type", ("p", "B")),
    ("particle_color_index", ("p", "H")),
]
_PARTICLE_BODY = [
    ("texture_tile_rotation", ("p", "h")),
    ("texture_dimensions_rows", ("p", "H")),
    ("texture_dimensions_columns", ("p", "H")),
    ("emission_speed", ("trk", "f32")),
    ("speed_variation", ("trk", "f32")),
    ("vertical_range", ("trk", "f32")),
    ("horizontal_range", ("trk", "f32")),
    ("gravity", ("trk", "f32")),
    ("lifespan", ("trk", "f32")),
    ("lifespan_vary", ("p", "f")),
    ("emission_rate", ("trk", "f32")),
    ("emission_rate_vary", ("p", "f")),
    ("emission_area_length", ("trk", "f32")),
    ("emission_area_width", ("trk", "f32")),
    ("z_source", ("trk", "f32")),
    ("color_track", ("ptrk", "vec3")),
    ("alpha_track", ("ptrk", "fixed16")),
    ("scale_track", ("ptrk", "vec2")),
    ("scale_vary", ("p", "ff")),
    ("head_cell_track", ("ptrk", "u16")),
    ("tail_cell_track", ("ptrk", "u16")),
    ("tail_length", ("p", "f")),
    ("twinkle_speed", ("p", "f")),
    ("twinkle_percent", ("p", "f")),
    ("twinkle_scale", ("p", "ff")),
    ("burst_multiplier", ("p", "f")),
    ("drag", ("p", "f")),
    ("base_spin", ("p", "f")),
    ("base_spin_vary", ("p", "f")),
    ("spin", ("p", "f")),
    ("spin_vary", ("p", "f")),
    ("tumble_min", ("p", "fff")),
    ("tumble_max", ("p", "fff")),
    ("wind_vector", ("p", "fff")),
    ("wind_time", ("p", "f")),
    ("follow_speed1", ("p", "f")),
    ("follow_scale1", ("p", "f")),
    ("follow_speed2", ("p", "f")),
    ("follow_scale2", ("p", "f")),
    ("spline_points", ("arr", "vec3")),
    ("enabled_in", ("trk", "u8")),
]

PARTICLE_264 = Schema(
    "M2Particle@264",
    [*_PARTICLE_HEAD, ("particle_type", ("p", "B")), ("head_or_tail", ("p", "B")), *_PARTICLE_BODY],
)

#: Cata..TWW. The two bytes that were particle_type/head_or_tail became
#: multi-texture parameters, and two 8-byte parameter blocks were appended.
PARTICLE_CATA = Schema(
    "M2Particle@272",
    [*_PARTICLE_HEAD, ("multi_texture_param_x", ("p", "BB")), *_PARTICLE_BODY, ("multi_texture_param0", ("p", "HHHH")), ("multi_texture_param1", ("p", "HHHH"))],
)


def particle_candidates(version: int) -> list[Schema]:
    """Particle schemas to try, most likely first.

    The struct carries no size field, so a model whose emitter layout does not
    match the header version -- which happens with third-party exporters and
    with any version this tool has not seen -- is recovered by trying the other
    era's schema and keeping whichever parses cleanly.
    """
    if version >= 265:
        return [PARTICLE_CATA, PARTICLE_264]
    return [PARTICLE_264, PARTICLE_CATA]


def camera_candidates(version: int) -> list[Schema]:
    if version >= 272:
        return [CAMERA_272, CAMERA_264]
    return [CAMERA_264, CAMERA_272]


def sequence_schema(version: int) -> Schema:
    return SEQUENCE_272 if version >= 272 else SEQUENCE_264


#: Sanity-check the sizes the wire format demands.
_EXPECTED_SIZES = {
    "BONE": (BONE, 88),
    "TEXTURE": (TEXTURE, 16),
    "MATERIAL": (MATERIAL, 4),
    "COLOR": (COLOR, 40),
    "TEXTURE_WEIGHT": (TEXTURE_WEIGHT, 20),
    "TEXTURE_TRANSFORM": (TEXTURE_TRANSFORM, 60),
    "ATTACHMENT": (ATTACHMENT, 40),
    "EVENT": (EVENT, 36),
    "LIGHT": (LIGHT, 156),
    "RIBBON": (RIBBON, 176),
    "SEQUENCE_264": (SEQUENCE_264, 64),
    "SEQUENCE_272": (SEQUENCE_272, 64),
    "CAMERA_264": (CAMERA_264, M2_CAMERA_SIZE_WOTLK),
    "CAMERA_272": (CAMERA_272, M2_CAMERA_SIZE_LEGION),
    "PARTICLE_264": (PARTICLE_264, M2_PARTICLE_SIZE_WOTLK),
    "PARTICLE_CATA": (PARTICLE_CATA, M2_PARTICLE_SIZE_CATA),
}
for _name, (_schema, _size) in _EXPECTED_SIZES.items():
    if _schema.size != _size:  # pragma: no cover - guards against edits
        raise AssertionError(
            f"{_name} schema is {_schema.size} bytes, the format requires {_size}"
        )
del _name, _schema, _size
