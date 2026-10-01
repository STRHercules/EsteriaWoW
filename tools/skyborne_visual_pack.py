"""Prepare dependency-closed Skyborne art and curated Wrath player models."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import shutil
import struct
from pathlib import Path

from PIL import Image
from wotlkconv.blp.image import Image as BlpImage
from wotlkconv.m2 import parse_m2, parse_skin, write_md20
from wotlkconv.m2.skin import write_skin

import retroported_race_pack as pack

ROOT = Path(r"G:\RetroPorterWork\skyborne")
SOURCE = ROOT / "integration" / "patch-root"
OUTPUT = ROOT / "integration" / "runtime"
PREFIX = "custom\\skyborne\\runtime"


def u16(data, offset):
    return struct.unpack_from("<H", data, offset)[0]


def patch16(data, offset, value):
    if not 0 <= value <= 65535:
        raise ValueError(f"SKIN uint16 overflow: {value}")
    struct.pack_into("<H", data, offset, value)


def path_for(key):
    return SOURCE.joinpath(*pack.PureWindowsPath(key).parts)


def read_player_model(path):
    """Preserve native external ANIM offsets when rewriting an already converted flat MD20."""
    from wotlkconv.m2.downgrade import mark_external

    model = parse_m2(path.read_bytes(), str(path))
    external = {i for i, sequence in enumerate(model.sequences) if not sequence["flags"] & 0x20}
    for track in model.tracks():
        if track.global_sequence < 0:
            mark_external(track, external)
    return model


def profiles(discovery, model_id, expanded=False):
    options = {o["Name_lang"]: o for o in discovery["options"] if o["ChrModelID"] == model_id}
    materials = {m["ID"]: m for m in discovery["linked"]["ChrCustomizationMaterial"]}
    textures = {t["MaterialResourcesID"]: t["FileDataID"] for t in discovery["texture_files"]}
    files = {a["file_data_id"]: "custom\\skyborne\\" + a["path"] for a in discovery["file_assets"]}

    def choices(name):
        return sorted((c for c in discovery["choices"] if c["ChrCustomizationOptionID"] == options[name]["ID"]),
                      key=lambda c: c["OrderIndex"])

    def material(choice, target, related=0):
        rows = [e for e in discovery["elements"] if e["ChrCustomizationChoiceID"] == choice
                and e["RelatedChrCustomizationChoiceID"] == related
                and materials.get(e["ChrCustomizationMaterialID"], {}).get("ChrModelTextureTargetID") == target]
        if len(rows) != 1:
            raise ValueError(f"Ambiguous or absent material: choice={choice}, target={target}, related={related}")
        resource = materials[rows[0]["ChrCustomizationMaterialID"]]["MaterialResourcesID"]
        key = files[textures[resource]]
        if not path_for(key).is_file():
            raise FileNotFoundError(key)
        return key

    faces = choices("Face")[:10 if expanded else 4]
    selected_ids = ((62225, 62226, 62227, 62230, 62231) if model_id == 218
                    else (62208, 62209, 62210, 62213, 62214))
    selected_choices = {choice["ID"]: choice for choice in choices("Skin Color")}
    valid = []
    for choice_id in selected_ids:
        skin = selected_choices[choice_id]
        try:
            entry = {"choice_id": skin["ID"], "body": material(skin["ID"], 1),
                     "faces": [material(f["ID"], 5, skin["ID"]) for f in faces],
                     "pelvis": material(skin["ID"], 13)}
            try:
                entry["torso"] = material(skin["ID"], 14)
            except ValueError:
                entry["torso"] = None
            valid.append(entry)
        except ValueError as exc:
            raise ValueError(f"Incomplete authored Skyborne palette {choice_id}") from exc
    skins = valid
    hair = choices("Hair Color")
    hairs = ([material(choice["ID"], 10) for choice in hair] if expanded else
             [material(hair[round(i * (len(hair) - 1) / 7)]["ID"], 10) for i in range(8)])
    feather = material(choices("Feather Color")[0]["ID"], 19)
    eye = material(choices("Eye Color")[0]["ID"], 25)
    result = {"skins": skins, "hair_textures": hairs, "feather_texture": feather, "eye_texture": eye,
              "face_choices": [f["ID"] for f in faces], "face_bone_morphs_applied": False}
    if expanded:
        result["eye_textures"] = []
        result["eye_choices"] = []
        result["omitted_eye_choices"] = []
        for choice in choices("Eye Color"):
            try:
                texture = material(choice["ID"], 25)
            except (ValueError, FileNotFoundError):
                result["omitted_eye_choices"].append(choice["ID"])
                continue
            result["eye_textures"].append(texture)
            result["eye_choices"].append(choice["ID"])
        result["feather_textures"] = [material(choice["ID"], 19) for choice in choices("Feather Color")]
        geosets = {g["ID"]: g for g in discovery["linked"]["ChrCustomizationGeoset"]}
        result["hair_geosets"] = []
        for name, kind, key in (("Hair Style", 0, "hair_geosets"),
                                ("Ears", 7, "ear_geosets"), ("Facial Hair", 1, "beard_geosets")):
            if name not in options:
                result[key] = [0]
                continue
            result[key] = []
            for choice in choices(name):
                rows = [geosets[e["ChrCustomizationGeosetID"]] for e in discovery["elements"]
                        if e["ChrCustomizationChoiceID"] == choice["ID"] and e["ChrCustomizationGeosetID"]
                        and geosets[e["ChrCustomizationGeosetID"]]["GeosetType"] == kind]
                if len(rows) != 1:
                    raise ValueError(f"{name} choice lacks an unambiguous geometry mapping")
                result[key].append(rows[0]["GeosetID"] + kind * 100)
        skinned = {row["ID"]: row for row in discovery["linked"]["ChrCustomizationSkinnedModel"]}
        feather_choice = choices("Feathers")[1]["ID"]
        feather_by_hair = {e["RelatedChrCustomizationChoiceID"]: skinned[e["ChrCustomizationSkinnedModelID"]]
                           for e in discovery["elements"] if e["ChrCustomizationChoiceID"] == feather_choice
                           and e["ChrCustomizationSkinnedModelID"]}
        result["feather_geosets"] = []
        for choice in choices("Hair Style"):
            mapping = feather_by_hair[choice["ID"]]
            if mapping["GeosetType"] != 40:
                raise ValueError("Unexpected feather collection group")
            result["feather_geosets"].append(4000 + mapping["GeosetID"] if mapping["GeosetID"] else 0)
    return result


def append_collection(model, skin, collection_path, selected, texture_paths=None):
    """Merge selected skinned meshes while preserving their local bone palettes."""
    extra = read_player_model(collection_path)
    extra_skin = parse_skin(collection_path.with_name(collection_path.stem + "00.skin").read_bytes())
    by_crc = {b["bone_name_crc"]: i for i, b in enumerate(model.bones) if b["bone_name_crc"]}
    if len(by_crc) != len(model.bones):
        raise ValueError("Base bone names are missing or ambiguous")
    bone_map = [by_crc[b["bone_name_crc"]] for b in extra.bones]
    if max(bone_map, default=0) > 255:
        raise ValueError("Collection bone index exceeds Wrath vertex storage")
    vertex_base = model.vertex_count
    lookup_base = len(skin.vertices)
    index_base = len(skin.indices)
    combo_base = len(model.bone_combos)
    vertices = bytearray(extra.vertices)
    for i in range(extra.vertex_count):
        for influence in range(4):
            if vertices[i * 48 + 12 + influence]:
                vertices[i * 48 + 16 + influence] = bone_map[vertices[i * 48 + 16 + influence]]
    model.vertices += bytes(vertices)
    model.vertex_count += extra.vertex_count
    if model.vertex_count > 65535 or lookup_base + len(extra_skin.vertices) > 65535:
        raise ValueError("Merged player model exceeds the Wrath vertex budget")
    model.bone_combos.extend(bone_map[i] for i in extra.bone_combos)
    skin.vertices.extend(vertex_base + i for i in extra_skin.vertices)
    skin.indices.extend(lookup_base + i for i in extra_skin.indices)
    skin.bones += extra_skin.bones

    texture_map = {}
    for i, texture in enumerate(extra.textures):
        if texture_paths and texture["type"] in texture_paths:
            texture_map[i] = len(model.textures)
            model.textures.append({"type": 0, "flags": texture["flags"],
                                   "filename": texture_paths[texture["type"]]})
        elif texture["type"] in (6, 7):
            texture_map[i] = next(j for j, t in enumerate(model.textures) if t["type"] == texture["type"])
        else:
            texture_map[i] = len(model.textures)
            model.textures.append(copy.deepcopy(texture))
    texture_base = len(model.texture_combos)
    material_base = len(model.materials)
    color_base = len(model.colors)
    weight_base = len(model.texture_weight_combos)
    transform_base = len(model.texture_transform_combos)
    coordinate_base = len(model.texture_coord_combos)
    model.texture_combos.extend(texture_map[i] for i in extra.texture_combos)
    model.materials.extend(copy.deepcopy(extra.materials))
    model.colors.extend(copy.deepcopy(extra.colors))
    weight_offset = len(model.texture_weights)
    transform_offset = len(model.texture_transforms)
    model.texture_weights.extend(copy.deepcopy(extra.texture_weights))
    model.texture_transforms.extend(copy.deepcopy(extra.texture_transforms))
    model.texture_weight_combos.extend(i + weight_offset if i != 65535 else i for i in extra.texture_weight_combos)
    model.texture_transform_combos.extend(i + transform_offset if i != 65535 else i
                                         for i in extra.texture_transform_combos)
    model.texture_coord_combos.extend(extra.texture_coord_combos)
    mesh_map = {}
    for i, raw in enumerate(extra_skin.submeshes):
        original = u16(raw, 0)
        if original not in selected:
            continue
        submesh = bytearray(raw)
        triangle_start = u16(raw, 8) + (u16(raw, 2) << 16) + index_base
        patch16(submesh, 0, selected[original])
        patch16(submesh, 2, triangle_start >> 16)
        patch16(submesh, 4, u16(raw, 4) + lookup_base)
        patch16(submesh, 8, triangle_start & 65535)
        patch16(submesh, 14, u16(raw, 14) + combo_base)
        patch16(submesh, 18, bone_map[u16(raw, 18)])
        mesh_map[i] = len(skin.submeshes)
        skin.submeshes.append(bytes(submesh))
    for raw in extra_skin.batches:
        if u16(raw, 4) not in mesh_map:
            continue
        batch = bytearray(raw)
        patch16(batch, 4, mesh_map[u16(raw, 4)])
        if u16(raw, 8) != 65535:
            patch16(batch, 8, u16(raw, 8) + color_base)
        for offset, addition in ((10, material_base), (16, texture_base), (18, coordinate_base),
                                 (20, weight_base), (22, transform_base)):
            patch16(batch, offset, u16(raw, offset) + addition)
        skin.batches.append(bytes(batch))
    return {"source": str(collection_path), "bone_bindings": len(bone_map), "meshes": len(mesh_map)}


def compact_bone_palettes(model, source):
    """Give each mesh a native Wrath palette of at most 75 bones, splitting only when needed."""
    from wotlkconv.m2.skin import Skin

    output = Skin(bone_count_max=75)
    model.bone_combos = []
    mesh_map = {}

    def bones(vertex):
        at = vertex * 48
        return {model.vertices[at + 16 + i] for i in range(4) if model.vertices[at + 12 + i]}

    for index, raw in enumerate(source.submeshes):
        start = u16(raw, 8) | u16(raw, 2) << 16
        count = u16(raw, 10)
        groups = []
        triangles = []
        used_bones = set()
        for at in range(start, start + count, 3):
            triangle = [source.vertices[v] for v in source.indices[at:at + 3]]
            needed = set().union(*(bones(v) for v in triangle))
            if triangles and len(used_bones | needed) > 75:
                groups.append((triangles, used_bones))
                triangles, used_bones = [], set()
            triangles.extend(triangle)
            used_bones.update(needed)
        if triangles:
            groups.append((triangles, used_bones))
        mesh_map[index] = []
        for triangles, used_bones in groups:
            palette = sorted(used_bones) or [0]
            local_bones = {bone: i for i, bone in enumerate(palette)}
            vertices = list(dict.fromkeys(triangles))
            first_vertex = len(output.vertices)
            first_index = len(output.indices)
            remap = {vertex: first_vertex + i for i, vertex in enumerate(vertices)}
            submesh = bytearray(raw)
            for offset, value in ((2, first_index >> 16), (4, first_vertex), (6, len(vertices)),
                                  (8, first_index & 65535), (10, len(triangles)),
                                  (12, len(palette)), (14, len(model.bone_combos))):
                patch16(submesh, offset, value)
            output.vertices.extend(vertices)
            for vertex in vertices:
                at = vertex * 48
                output.bones += bytes(local_bones.get(model.vertices[at + 16 + i], 0)
                                      if model.vertices[at + 12 + i] else 0 for i in range(4))
            output.indices.extend(remap[v] for v in triangles)
            model.bone_combos.extend(palette)
            mesh_map[index].append(len(output.submeshes))
            output.submeshes.append(bytes(submesh))
    if len(output.vertices) > 65535:
        raise ValueError("Native bone splitting exceeded the Wrath skin vertex budget")
    for raw in source.batches:
        for index in mesh_map[u16(raw, 4)]:
            batch = bytearray(raw)
            patch16(batch, 4, index)
            output.batches.append(bytes(batch))
    return output


def runtime_model(sex, model_id, collection_id, profile, expanded=False, output_root=None):
    model_path = path_for(f"custom\\skyborne\\models\\creature\\unk_exp00_{model_id}\\{model_id}.m2")
    model = read_player_model(model_path)
    skin = parse_skin(model_path.with_name(model_path.stem + "00.skin").read_bytes())
    replacements = {2001: 901, 2201: 0, 2301: 0, 3202: 0, 3301: 0, 5101: 0}
    keep = [i for i, raw in enumerate(skin.submeshes)
            if u16(raw, 0) < 2000 or u16(raw, 0) in replacements]
    kept_batches = []
    mesh_map = {i: n for n, i in enumerate(keep)}
    body_vertices = set()
    head_vertices = set()
    for raw in skin.batches:
        mesh = u16(raw, 4)
        if mesh not in mesh_map:
            continue
        slots = model.texture_combos[u16(raw, 16):u16(raw, 16) + u16(raw, 14)]
        types = [model.textures[i]["type"] for i in slots]
        if u16(skin.submeshes[mesh], 0) == 0 and types == [7]:
            continue  # The three-vertex material marker is not body geometry.
        if types == [1]:
            submesh = skin.submeshes[mesh]
            for vertex in skin.vertices[u16(submesh, 4):u16(submesh, 4) + u16(submesh, 6)]:
                u = struct.unpack_from("<f", model.vertices, vertex * 48 + 32)[0]
                (head_vertices if u > .5 else body_vertices).add(vertex)
        batch = bytearray(raw)
        patch16(batch, 4, mesh_map[mesh])
        if 11 in types and 2 in types:
            patch16(batch, 14, 1)  # The second unit is a modern cape mask.
        kept_batches.append(bytes(batch))
    if body_vertices & head_vertices or not head_vertices or not body_vertices:
        raise ValueError("Ambiguous body/head atlas vertices")
    vertices = bytearray(model.vertices)
    for index in body_vertices:
        u, v = struct.unpack_from("<2f", vertices, index * 48 + 32)
        struct.pack_into("<2f", vertices, index * 48 + 32, u * 2, v)
    for index in head_vertices:
        u, v = struct.unpack_from("<2f", vertices, index * 48 + 32)
        struct.pack_into("<2f", vertices, index * 48 + 32, u - .5, .625 + .375 * v)
    model.vertices = bytes(vertices)
    skin.submeshes = [bytes(bytearray(raw)) for i, raw in enumerate(skin.submeshes) if i in mesh_map]
    for i, raw in enumerate(skin.submeshes):
        changed = bytearray(raw)
        patch16(changed, 0, replacements.get(u16(raw, 0), u16(raw, 0)))
        skin.submeshes[i] = bytes(changed)
    skin.batches = kept_batches
    collections = []
    collection_path = path_for(
        f"custom\\skyborne\\models\\unknown\\unk_exp00_{collection_id}\\{collection_id}.m2")
    if expanded:
        from wotlkconv.m2.split import _rebuild_skin

        skin = _rebuild_skin(skin, list(range(len(skin.submeshes))),
                             {i: i for i in range(model.vertex_count)})
        extra_skin = parse_skin(collection_path.with_name(collection_path.stem + "00.skin").read_bytes())
        feathers = {u16(row, 0) for row in extra_skin.submeshes if 4000 < u16(row, 0) < 4100}
        for color, texture in enumerate(profile["feather_textures"]):
            selected = {geoset: geoset + color * 100 for geoset in feathers}
            if color == 0:
                selected.update({3401 + i: 201 + i for i in range(4)})
            collections.append(append_collection(model, skin, collection_path, selected, {7: texture}))
    else:
        collections.append(append_collection(model, skin, collection_path, {3401: 201, 3402: 202, 4001: 1601}))
    for texture in model.textures:
        if expanded and texture["type"] == 11:
            texture.update(type=8, filename="")
        elif texture["type"] in (11, 15):
            texture.update(type=0, filename=profile["eye_texture"])
        elif texture["type"] == 7:
            texture.update(type=0, filename=profile["feather_texture"])
    model.replacable_texture_lookup = [65535] * 16
    for i, texture in enumerate(model.textures):
        if texture["type"]:
            model.replacable_texture_lookup[texture["type"]] = i
    # The native character selector compares the whole geoset DWORD, including
    # the index high-word. Keep the curated SKIN below 65536 triangle indices so
    # every level is zero; otherwise bodies read as geosets 65536/131072 and hide.
    from wotlkconv.m2.split import _rebuild_skin

    selected = []
    for index, submesh in enumerate(skin.submeshes):
        geoset = u16(submesh, 0)
        group = geoset // 100
        if group == 17:
            continue  # Modern eyes were already retained in the unconditional group.
        if (expanded or geoset == 0 or 1 <= geoset <= 4
                or (geoset >= 100 and group not in (1, 2, 3, 5, 15, 16))
                or geoset in (201, 202, 501, 502, 503, 1502, 1503, 1504, 1601)):
            selected.append(index)
    skin = _rebuild_skin(skin, selected, {i: i for i in range(model.vertex_count)})
    if expanded:
        skin = compact_bone_palettes(model, skin)
    if not expanded and (len(skin.indices) > 65535 or any(u16(row, 2) for row in skin.submeshes)):
        raise ValueError("Curated SKIN still exceeds native geoset selection limits")
    # Keep the source stem so all external animation filenames remain valid.
    prefix = "custom\\skyborne\\expanded" if expanded else PREFIX
    key = f"{prefix}\\{sex}\\{model_id}.m2"
    target = (output_root or OUTPUT).joinpath(*pack.PureWindowsPath(key).parts)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(write_md20(model))
    target.with_name(target.stem + "00.skin").write_bytes(write_skin(skin))
    for animation in model_path.parent.glob(model_path.stem + "*.anim"):
        shutil.copy2(animation, target.parent / animation.name)
    return {"model_path": key, "vertices": model.vertex_count, "collections": collections,
            "head_vertices": len(head_vertices), "body_vertices": len(body_vertices),
            "triangle_indices": len(skin.indices),
            "animations": len(list(target.parent.glob("*.anim")))}


def bake_appearance(sex, profile, output_root=None, prefix=PREFIX):
    result = []
    for skin_index, skin in enumerate(profile["skins"]):
        source = pack.Blp.parse(path_for(skin["body"]).read_bytes()).decode_level(0)
        if (source.width, source.height) != (1024, 512):
            raise ValueError("Unexpected Skyborne body atlas dimensions")
        body = pack._crop_blp_rgba(source, 0, 0, 512, 512)
        images = [pack.Blp.parse(path_for(key).read_bytes()).decode_level(0) for key in skin["faces"]]
        underwear = {name: pack.Blp.parse(path_for(skin[name]).read_bytes()).decode_level(0)
                     for name in ("pelvis", "torso") if skin[name]}
        palette_source = bytearray(body.data)
        for image in [*images, *underwear.values()]:
            palette_source.extend(image.data)
        palette = pack.build_palette(palette_source, 256)
        mapper = pack.PaletteMapper(palette)
        entries = {f"{prefix}\\{sex}\\body{skin_index:02d}.blp": body}
        entries.update({f"{prefix}\\{sex}\\{name}{skin_index:02d}.blp": image
                        for name, image in underwear.items()})
        for face_index, image in enumerate(images):
            sheet = Image.frombytes("RGBA", (image.width, image.height), bytes(image.data)).resize(
                (256, 192), Image.Resampling.LANCZOS)
            for fragment, box in (("upper", (0, 0, 256, 64)), ("lower", (0, 64, 256, 192))):
                crop = sheet.crop(box)
                entries[f"{prefix}\\{sex}\\face{fragment}{face_index:02d}_{skin_index:02d}.blp"] = BlpImage(
                    crop.width, crop.height, bytearray(crop.tobytes()))
        for key, image in entries.items():
            data = pack._encode_wotlk_paletted(image, palette, mapper)
            path = (output_root or OUTPUT).joinpath(*pack.PureWindowsPath(key).parts)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
            result.append({"path": key, "sha256": hashlib.sha256(data).hexdigest()})
    return result


def prepare():
    discovery = pack.load_json(ROOT / "reports" / "discovery.json")
    output = {"schema_version": 1, "scope": "curated presets", "sexes": {}}
    for sex, model_id, collection_id, chr_model_id in (
        ("male", 7478487, 7845093, 218), ("female", 7478494, 7845092, 219)
    ):
        profile = profiles(discovery, chr_model_id)
        runtime = runtime_model(sex, model_id, collection_id, profile)
        runtime["appearance"] = bake_appearance(sex, profile)
        runtime["profile"] = profile
        output["sexes"][sex] = runtime
    (ROOT / "integration" / "visual-preparation.json").write_text(
        json.dumps(output, indent=2) + "\n", encoding="utf-8")
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("prepare",))
    parser.parse_args()
    result = prepare()
    print(json.dumps({sex: {k: v for k, v in row.items() if k not in ("profile", "appearance")}
                      for sex, row in result["sexes"].items()}, indent=2))
