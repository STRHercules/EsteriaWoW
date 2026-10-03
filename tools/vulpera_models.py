"""Prepare the authored Vulpera mesh, animation graph and source texture layers for Wrath."""

import copy
import hashlib
import struct

from PIL import Image
from wotlkconv.m2 import parse_m2, parse_skin, write_md20
from wotlkconv.m2.skin import write_skin

import haranir_race_pack as h
import vulpera_race_pack as v


def split_atlas(model, skin):
    """Keep Retail's skinExtra square independent of the stock equipment compositor."""
    original = copy.deepcopy(skin)
    vertices = bytearray(model.vertices)
    extra_texture = len(model.textures)
    model.textures.append({"type": 8, "flags": 0, "filename": ""})
    new_indices, new_meshes, new_batches = [], [], []
    changed = set()
    for index, raw in enumerate(original.submeshes):
        batches = [b for b in original.batches if v.e.v.u16(b, 4) == index]
        is_body = any(model.textures[model.texture_combos[v.e.v.u16(b, 16)]]["type"] == 1 for b in batches)
        start = v.e.v.u16(raw, 8) | v.e.v.u16(raw, 2) << 16
        triangles = [original.indices[i:i + 3] for i in range(start, start + v.e.v.u16(raw, 10), 3)]
        groups = {False: [], True: []}
        for triangle in triangles:
            if is_body:
                us = [struct.unpack_from("<f", model.vertices, original.vertices[i] * 48 + 32)[0]
                      for i in triangle]
                if min(us) < .4999 and max(us) > .5001:
                    raise ValueError("Source triangle crosses the two authored atlas squares")
                right = max(us) > .5001
            else:
                right = False
            groups[right].append(triangle)
        for right, tris in groups.items():
            if not tris:
                continue
            mesh = bytearray(raw)
            offset = len(new_indices)
            v.e.v.patch16(mesh, 2, offset >> 16)
            v.e.v.patch16(mesh, 8, offset & 65535)
            v.e.v.patch16(mesh, 10, len(tris) * 3)
            mesh_index = len(new_meshes)
            new_meshes.append(bytes(mesh))
            new_indices.extend(i for triangle in tris for i in triangle)
            if is_body:
                for lookup in {i for triangle in tris for i in triangle}:
                    vertex = original.vertices[lookup]
                    if vertex in changed:
                        continue
                    u, y = struct.unpack_from("<2f", vertices, vertex * 48 + 32)
                    struct.pack_into("<2f", vertices, vertex * 48 + 32, 2 * u - int(right), y)
                    changed.add(vertex)
            for raw_batch in batches:
                batch = bytearray(raw_batch)
                v.e.v.patch16(batch, 4, mesh_index)
                v.e.v.patch16(batch, 6, mesh_index)
                if right:
                    v.e.v.patch16(batch, 16, len(model.texture_combos))
                    model.texture_combos.append(extra_texture)
                new_batches.append(bytes(batch))
    model.vertices = bytes(vertices)
    skin.indices, skin.submeshes, skin.batches = new_indices, new_meshes, new_batches
    return {"body_vertices_remapped": len(changed), "submeshes": len(new_meshes),
            "source_triangles": len(original.indices) // 3, "target_triangles": len(skin.indices) // 3}


def prepare():
    profiles = v.audit()
    discovery = v.p.load_json(v.ROOT / "reports/discovery.json")
    layouts = v.p.load_json(v.ROOT / "reports/texture-layouts.json")
    materials = {r["ID"]: r for r in discovery["linked"]["ChrCustomizationMaterial"]}
    textures = {r["MaterialResourcesID"]: r["FileDataID"] for r in discovery["texture_files"]}
    geosets = {r["ID"]: r for r in discovery["linked"]["ChrCustomizationGeoset"]}
    files = {r["file_data_id"]: "custom\\vulpera\\" + r["path"] for r in discovery["file_assets"]}
    payloads = bytearray(struct.pack("<4I", 0x31544845, 1, 0, 0))
    records, cached, report = [], {}, {}
    v.STAGE.mkdir(parents=True, exist_ok=True)

    def record(gender, kind, target, value, selectors=(), key=""):
        if len(selectors) > 3 or len(key.encode()) >= 128:
            raise ValueError("Vulpera catalog limit")
        selected = [i | j << 16 for i, j in selectors]
        records.append(struct.pack("<7I", gender, kind, target, value,
                       *(selected + [0xffffffff] * (3 - len(selected)))) + key.encode().ljust(128, b"\0"))

    def image(file_id):
        source = v.ROOT / "raw" / f"{file_id}.blp"
        blp = v.p.Blp.parse(source.read_bytes()).decode_level(0)
        return Image.frombytes("RGBA", (blp.width, blp.height), bytes(blp.data))

    def layer(file_id, target, group, gender):
        cache_key = (file_id, target, group, gender)
        if cache_key in cached:
            return cached[cache_key]
        art = image(file_id)
        if target in (1, 16):
            art = art.resize((2048, 1024), Image.Resampling.LANCZOS)
            art = art.crop((1024, 0, 2048, 1024) if group == 4 else (0, 0, 1024, 1024))
            art = art.resize((512, 512), Image.Resampling.LANCZOS)
            if group == 1:
                # Wrath fills its left-bottom slabs through the two face layers, not the body base.
                # Vulpera authored its tail and foot fur there; keep their exact body-atlas UVs.
                art = art.crop((0, 320, 256, 512))
        elif target == 5:
            art = art.resize((512, 512), Image.Resampling.LANCZOS)
        elif target in (13, 14):
            section_type = 5 if target == 13 else 3
            section = next(s for s in layouts["CharComponentTextureSections"]
                           if s["CharComponentTextureLayoutID"] == 145 + gender
                           and s["SectionType"] == section_type)
            canvas = Image.new("RGBA", (512, 512))
            box = [section[n] // 2 for n in ("X", "Y", "Width", "Height")]
            canvas.alpha_composite(art.resize(tuple(box[2:]), Image.Resampling.LANCZOS), tuple(box[:2]))
            art = canvas
        elif target in (25, 44):
            art = art.resize((256, 128), Image.Resampling.LANCZOS)
        else:
            raise ValueError("Unmapped Vulpera material target: " + str(target))
        data = h.lznt1(art.tobytes())
        offset = len(payloads)
        payloads.extend(struct.pack("<3I", art.width, art.height, len(data)) + data)
        cached[cache_key] = offset
        return offset

    for gender, sex in enumerate(("male", "female")):
        profile = profiles[sex]
        indices = {c["ID"]: (i, j) for i, o in enumerate(profile["options"]) for j, c in enumerate(o["choices"])}
        selected = [r for o in profile["options"] for c in o["choices"] for r in c["elements"]
                    if not r["RelatedChrCustomizationChoiceID"] or r["RelatedChrCustomizationChoiceID"] in indices]
        selected.sort(key=lambda r: not r["RelatedChrCustomizationChoiceID"])
        groups = set()
        for element in selected:
            geo = geosets.get(element["ChrCustomizationGeosetID"])
            if not geo or geo["GeosetType"] == 0:
                continue  # The single constant Hair Style has no separate mesh; body geoset0 stays unconditional.
            selectors = [indices[element["ChrCustomizationChoiceID"]]]
            if element["RelatedChrCustomizationChoiceID"]:
                selectors.append(indices[element["RelatedChrCustomizationChoiceID"]])
            group = geo["GeosetType"]
            record(gender, 0, group, group * 100 + geo["GeosetID"], selectors)
            groups.add(group)
        for group in sorted(groups):
            record(gender, 0, group, group * 100)
        for group, value in ((22, 2201), (32, 3202), (33, 3301), (51, 5101)):
            if group not in groups:
                record(gender, 0, group, value)
        material_report = []
        for source_layer in sorted((r for r in layouts["ChrModelTextureLayer"]
                                    if r["CharComponentTextureLayoutsID"] == 145 + gender), key=lambda r: r["Layer"]):
            target = source_layer["ChrModelTextureTargetID"][0]
            for element in selected:
                material = materials.get(element["ChrCustomizationMaterialID"])
                if not material or material["ChrModelTextureTargetID"] != target:
                    continue
                selectors = [indices[element["ChrCustomizationChoiceID"]]]
                if element["RelatedChrCustomizationChoiceID"]:
                    selectors.append(indices[element["RelatedChrCustomizationChoiceID"]])
                file_id = textures[material["MaterialResourcesID"]]
                output_groups = ((0, 1, 4) if target in (1, 16) else (4,) if target == 5
                                 else (3,) if target in (25, 44) else (0,))
                for group in output_groups:
                    blob = layer(file_id, target, group, gender)
                    record(gender, 3, group, blob, selectors, f"{target}:{source_layer['BlendMode']}")
                    material_report.append({"target": target, "group": group, "file_id": file_id,
                                           "selectors": selectors, "offset": blob})
        source = v.path(v.SOURCE, f"custom\\vulpera\\character\\vulpera\\{sex}\\vulpera{sex}.m2")
        model = v.e.v.read_player_model(source)
        skin = parse_skin(source.with_name(source.stem + "00.skin").read_bytes())
        v.e.rebuild_sequence_lookup(model)
        v.e.share_material_defaults(model)
        v.e.tracks.embed(model, source.parent, source.stem)
        raw = parse_m2((v.ROOT / "raw" / f"{v.MODELS[sex]}.m2").read_bytes())
        atlas = split_atlas(model, skin)
        neutral = f"{v.PREFIX}\\{sex}\\neutral.blp"
        # The checked indexed encoder is shared with the preceding race packs.
        old_art = v.e.ART
        try:
            v.e.ART = v.ART
            v.e.emit(neutral, Image.new("RGBA", (4, 4), "white"))
        finally:
            v.e.ART = old_art
        for texture, original in zip(model.textures[:len(raw.textures)], raw.textures, strict=True):
            kind = original["type"]
            if kind == 19:
                texture.update(type=5, filename="")
            elif kind >= 11:
                texture.update(type=0, filename=neutral)
        for i, batch in enumerate(skin.batches):
            batch = bytearray(batch)
            first = model.texture_combos[v.e.v.u16(batch, 16)]
            slot = model.textures[first]["type"]
            v.e.v.patch16(batch, 2, 0)
            v.e.v.patch16(batch, 14, 1)
            if v.e.v.u16(batch, 18) == 65535:
                v.e.v.patch16(batch, 18, 0)
            if slot == 5:
                v.e.v.patch16(batch, 10, len(model.materials))
                model.materials.append({"flags": 4, "blending_mode": 0})
            skin.batches[i] = bytes(batch)
        model.replacable_texture_lookup = [65535] * 16
        for i, texture in enumerate(model.textures):
            if texture["type"]:
                model.replacable_texture_lookup[texture["type"]] = i
        skin = v.e.v.compact_bone_palettes(model, skin)
        key = f"{v.PREFIX}\\{sex}\\vulpera{sex}.m2"
        destination = v.path(v.ART, key)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(write_md20(model))
        destination.with_name(destination.stem + "00.skin").write_bytes(write_skin(skin))
        for texture in model.textures:
            if texture["type"] == 0 and texture["filename"] and not v.path(v.ART, texture["filename"]).exists():
                shutil_source = v.path(v.SOURCE, texture["filename"])
                v.path(v.ART, texture["filename"]).parent.mkdir(parents=True, exist_ok=True)
                v.path(v.ART, texture["filename"]).write_bytes(shutil_source.read_bytes())
        report[sex] = {"model_path": key, "vertices": model.vertex_count, "skin_vertices": len(skin.vertices),
                       "sequences": len(model.sequences), "events": len(model.events), "atlas": atlas,
                       "materials": material_report, "source_attachment11":
                       next(a["position"] for a in raw.attachments if a["id"] == 11)}
        print("PREPARED", sex, model.vertex_count, len(skin.vertices), flush=True)
    struct.pack_into("<I", payloads, 8, len(cached))
    struct.pack_into("<I", payloads, 12, int.from_bytes(hashlib.sha256(payloads[16:]).digest()[:4], "little"))
    (v.STAGE / "EsteriaVulperaTextures.bin").write_bytes(payloads)
    (v.STAGE / "EsteriaVulpera.bin").write_bytes(struct.pack("<3I", 0x314D4845, 1, len(records)) + b"".join(records))
    v.save(v.ROOT / "integration/rendering.json", report)
    return report


if __name__ == "__main__":
    prepare()
