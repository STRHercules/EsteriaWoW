from __future__ import annotations

import json
from pathlib import Path
import struct

from wotlkconv.m2.model import parse_m2
from wotlkconv.m2.skin import parse_skin, write_skin
from wotlkconv.m2.write import write_md20

from .config import Config


_VERTEX_SIZE = 48
_UV0_OFFSET = 32
_BATCH_SKIN_SECTION = 0x04
_BATCH_TEXTURE_COUNT = 0x0E
_BATCH_TEXTURE_COMBO = 0x10
_SUBMESH_VERTEX_START = 0x04
_SUBMESH_VERTEX_COUNT = 0x06
_EMPTY_LOOKUP = 0xFFFF


def _submesh_vertices(skin, section_index: int) -> set[int]:
    raw = skin.submeshes[section_index]
    vertex_start = struct.unpack_from("<H", raw, _SUBMESH_VERTEX_START)[0]
    vertex_count = struct.unpack_from("<H", raw, _SUBMESH_VERTEX_COUNT)[0]
    return set(skin.vertices[vertex_start:vertex_start + vertex_count])


def _uv_u(vertices: bytes | bytearray, vertex_index: int) -> float:
    return struct.unpack_from("<f", vertices, vertex_index * _VERTEX_SIZE + _UV0_OFFSET)[0]


def _set_uv_u(vertices: bytearray, vertex_index: int, value: float) -> None:
    struct.pack_into("<f", vertices, vertex_index * _VERTEX_SIZE + _UV0_OFFSET, value)


def split_retail_player_atlas(
    m2_data: bytes,
    skin_data: bytes,
    name: str,
    *,
    eye_texture_path: str,
) -> tuple[bytes, bytes, dict]:
    """Adapt a modern two-half player atlas to Wrath's type-1/type-8 contract.

    Modern Mag'har uses one 2048x1024 player atlas.  All body draw batches sample
    the left half and all head draw batches sample the right half.  Wrath HD
    player models already support two independently composed player textures:
    type 1 and type 8.  This transformation keeps the Retail geometry but routes
    the two atlas halves to those two supported slots and normalises each half's
    U coordinates back to 0..1.
    """
    model = parse_m2(m2_data, name)
    skin = parse_skin(skin_data, f"{name}00.skin")

    skin_slots = [i for i, texture in enumerate(model.textures) if texture.get("type") == 1]
    head_slots = [i for i, texture in enumerate(model.textures) if texture.get("type") == 15]
    if len(skin_slots) != 1:
        raise ValueError(f"{name}: expected one Retail player-skin type-1 slot, found {skin_slots}")
    if len(head_slots) != 1:
        raise ValueError(f"{name}: expected one unused Retail type-15 slot for the head, found {head_slots}")
    body_slot = skin_slots[0]
    head_slot = head_slots[0]

    # Repurpose the modern player-extra slot as the HD/Wrath secondary player skin.
    model.textures[head_slot]["type"] = 8
    model.textures[head_slot]["filename"] = ""
    while len(model.replacable_texture_lookup) <= 15:
        model.replacable_texture_lookup.append(_EMPTY_LOOKUP)
    model.replacable_texture_lookup[8] = head_slot
    model.replacable_texture_lookup[15] = _EMPTY_LOOKUP

    head_combo = len(model.texture_combos)
    model.texture_combos.append(head_slot)

    # Converter maps modern unknown player-extra types to empty Wrath type 11.
    # Two of those slots are actively drawn by Mag'har: a secondary unit paired
    # with type 2, and the modern eye material. Drop only the unsupported
    # secondary unit and bind the eye material to a real retroported Retail eye
    # texture. Any remaining type-11 slots are unused and therefore harmless.
    eye_slots: set[int] = set()
    stripped_secondary_batches = 0
    preprocessed_batches: list[bytes] = []
    for raw in skin.batches:
        batch = bytearray(raw)
        texture_count = struct.unpack_from("<H", batch, _BATCH_TEXTURE_COUNT)[0]
        texture_combo = struct.unpack_from("<H", batch, _BATCH_TEXTURE_COMBO)[0]
        slots = model.texture_combos[texture_combo:texture_combo + texture_count]
        types = [model.textures[slot].get("type") for slot in slots]
        if 11 in types:
            if texture_count == 2 and 2 in types:
                primary = next(slot for slot in slots if model.textures[slot].get("type") == 2)
                if slots[0] != primary:
                    single_combo = len(model.texture_combos)
                    model.texture_combos.append(primary)
                    struct.pack_into("<H", batch, _BATCH_TEXTURE_COMBO, single_combo)
                struct.pack_into("<H", batch, _BATCH_TEXTURE_COUNT, 1)
                stripped_secondary_batches += 1
            elif all(model.textures[slot].get("type") == 11 for slot in slots):
                eye_slots.update(slots)
        preprocessed_batches.append(bytes(batch))
    for slot in eye_slots:
        model.textures[slot]["type"] = 0
        model.textures[slot]["filename"] = eye_texture_path

    # Any remaining type-11 slots are now unused after the batch cleanup. Make
    # them benign hardcoded Retail textures anyway so the final runtime model
    # contains no unsupported/empty modern replaceable texture types at all.
    neutralized_slots: list[int] = []
    for slot, texture in enumerate(model.textures):
        if texture.get("type") == 11:
            texture["type"] = 0
            texture["filename"] = eye_texture_path
            neutralized_slots.append(slot)
    for texture_type in range(11, len(model.replacable_texture_lookup)):
        if texture_type != 8:
            model.replacable_texture_lookup[texture_type] = _EMPTY_LOOKUP

    skin.batches = preprocessed_batches

    body_vertices: set[int] = set()
    head_vertices: set[int] = set()
    rewritten_batches = []
    body_batches = 0
    head_batches = 0

    for raw in skin.batches:
        batch = bytearray(raw)
        section_index = struct.unpack_from("<H", batch, _BATCH_SKIN_SECTION)[0]
        texture_count = struct.unpack_from("<H", batch, _BATCH_TEXTURE_COUNT)[0]
        texture_combo = struct.unpack_from("<H", batch, _BATCH_TEXTURE_COMBO)[0]
        slots = model.texture_combos[texture_combo:texture_combo + texture_count]
        if body_slot not in slots:
            rewritten_batches.append(bytes(batch))
            continue
        if texture_count != 1 or slots != [body_slot]:
            raise ValueError(f"{name}: player-skin batch uses unexpected texture run {slots}")

        vertices = _submesh_vertices(skin, section_index)
        u_values = [_uv_u(model.vertices, index) for index in vertices]
        if max(u_values) < 0.5:
            body_vertices.update(vertices)
            body_batches += 1
        elif min(u_values) > 0.5:
            head_vertices.update(vertices)
            head_batches += 1
            struct.pack_into("<H", batch, _BATCH_TEXTURE_COMBO, head_combo)
        else:
            raise ValueError(
                f"{name}: section {section_index} crosses the modern atlas midpoint "
                f"({min(u_values):.6f}..{max(u_values):.6f})"
            )
        rewritten_batches.append(bytes(batch))

    if not body_vertices or not head_vertices:
        raise ValueError(f"{name}: failed to identify both body and head player-skin geometry")
    if body_vertices & head_vertices:
        raise ValueError(f"{name}: body and head player-skin geometry share vertices")

    # These vertices must not be reused by a different material; otherwise the UV
    # rewrite would require vertex duplication instead of an in-place transform.
    other_vertices: set[int] = set()
    for raw in skin.batches:
        section_index = struct.unpack_from("<H", raw, _BATCH_SKIN_SECTION)[0]
        texture_count = struct.unpack_from("<H", raw, _BATCH_TEXTURE_COUNT)[0]
        texture_combo = struct.unpack_from("<H", raw, _BATCH_TEXTURE_COMBO)[0]
        slots = model.texture_combos[texture_combo:texture_combo + texture_count]
        if body_slot not in slots:
            other_vertices.update(_submesh_vertices(skin, section_index))
    if (body_vertices | head_vertices) & other_vertices:
        raise ValueError(f"{name}: player-skin vertices are reused by another material")

    vertices = bytearray(model.vertices)
    for index in body_vertices:
        _set_uv_u(vertices, index, _uv_u(vertices, index) * 2.0)
    for index in head_vertices:
        _set_uv_u(vertices, index, (_uv_u(vertices, index) - 0.5) * 2.0)
    model.vertices = bytes(vertices)
    skin.batches = rewritten_batches

    body_u = [_uv_u(model.vertices, index) for index in body_vertices]
    head_u = [_uv_u(model.vertices, index) for index in head_vertices]
    if min(body_u) < -0.001 or max(body_u) > 1.001 or min(head_u) < -0.001 or max(head_u) > 1.001:
        raise ValueError(f"{name}: transformed player UVs fall outside 0..1")

    report = {
        "body_texture_slot": body_slot,
        "head_texture_slot": head_slot,
        "body_batches": body_batches,
        "head_batches": head_batches,
        "body_vertices": len(body_vertices),
        "head_vertices": len(head_vertices),
        "body_u_range": [min(body_u), max(body_u)],
        "head_u_range": [min(head_u), max(head_u)],
        "eye_texture_slots": sorted(eye_slots),
        "neutralized_texture_slots": neutralized_slots,
        "stripped_secondary_batches": stripped_secondary_batches,
    }
    return write_md20(model), write_skin(skin), report


def prepare_maghar_runtime(config: Config) -> Path:
    source_root = config.work_root / "maghar" / "output" / "patch-root" / "custom" / "maghar" / "character" / "orc"
    output_root = config.work_root / "maghar" / "integration" / "retail-runtime" / "custom" / "maghar" / "character" / "orc"
    output_root.mkdir(parents=True, exist_ok=True)

    report: dict[str, object] = {"schema_version": 1, "source_root": str(source_root), "sexes": {}}
    for sex, stem in (("male", "orcmale_hd"), ("female", "orcfemale_hd")):
        source = source_root / sex
        target = output_root / sex
        target.mkdir(parents=True, exist_ok=True)
        m2, skin, details = split_retail_player_atlas(
            (source / f"{stem}.m2").read_bytes(),
            (source / f"{stem}00.skin").read_bytes(),
            stem,
            eye_texture_path=r"custom\maghar\character\orc\male\orcmale_hd_eye_color_5273683.blp",
        )
        (target / f"{stem}.m2").write_bytes(m2)
        (target / f"{stem}00.skin").write_bytes(skin)
        report["sexes"][sex] = details

    report_path = config.work_root / "maghar" / "integration" / "retail-runtime" / "runtime-report.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report_path
