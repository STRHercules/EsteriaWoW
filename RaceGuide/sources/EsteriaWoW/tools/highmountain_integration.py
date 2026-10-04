"""Generate Race46 rendering, DBC and matched archive stages from verified Highmountain inputs."""

import argparse
import itertools
import json
import shutil
import struct
import os
import subprocess
from datetime import datetime
from pathlib import Path

from PIL import Image
from wotlkconv.m2 import parse_skin, write_md20
from wotlkconv.m2.skin import write_skin

import highmountain_appearance as codec
import highmountain_race_pack as h
import retroported_race_pack as p
import skyborne_visual_pack as v

RACE = 46


def image(key):
    data = p.Blp.parse(h.art_path(key).read_bytes()).decode_level(0)
    return Image.frombytes("RGBA", (data.width, data.height), bytes(data.data))


def paletted_compositor(bitmap):
    """Native quantization with the proven indexed character-compositor header and mip layout."""
    rgb = Image.frombytes("RGBA", (bitmap.width, bitmap.height), bytes(bitmap.data)).convert("RGB")
    quantized = rgb.quantize(colors=256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    palette = quantized.getpalette()[:768]
    palette.extend([0] * (768 - len(palette)))
    colors = [tuple(palette[i:i + 3]) for i in range(0, 768, 3)]

    class Mapper:
        def map_image(self, rgba):
            pixels = Image.frombytes("RGBA", (len(rgba) // 4, 1), bytes(rgba)).convert("RGB")
            return pixels.quantize(palette=quantized, dither=Image.Dither.NONE).tobytes()

    return p._encode_wotlk_paletted(bitmap, colors, Mapper())


def emit(key, art, *, compositor=False):
    path = h.art_path(key)
    path.parent.mkdir(parents=True, exist_ok=True)
    bitmap = p.BlpImage(art.width, art.height, bytearray(art.tobytes()))
    if compositor:
        path.write_bytes(paletted_compositor(bitmap))
        return key
    levels = bitmap.mip_chain()
    payloads = [Image.frombytes("RGBA", (l.width, l.height), bytes(l.data)).tobytes("raw", "BGRA") for l in levels]
    path.write_bytes(p.Blp.from_images(levels, compression=3, alpha_type=8, alpha_size=8,
                                      payloads=payloads).serialize())
    return key


def prepare_rendering():
    discovery = p.load_json(h.ROOT / "reports/discovery.json")
    profiles = codec.codec()
    materials = {m["ID"]: m for m in discovery["linked"]["ChrCustomizationMaterial"]}
    textures = {t["MaterialResourcesID"]: t["FileDataID"] for t in discovery["texture_files"]}
    files = {a["file_data_id"]: "custom\\highmountain\\" + a["path"] for a in discovery["file_assets"]}
    geometry = {r["ID"]: r for r in discovery["linked"]["ChrCustomizationGeoset"]}
    records = []
    render = {}
    for gender, sex in enumerate(("male", "female")):
        prof = profiles[sex]
        opts = {o["label"]: o for o in prof["options"]}
        indices = {c["ID"]: (i, j) for i, o in enumerate(prof["options"]) for j, c in enumerate(o["choices"])}
        root = f"{h.PREFIX}\\{sex}"

        def material(choice, target, related=0):
            hits = [e for e in discovery["elements"] if e["ChrCustomizationChoiceID"] == choice
                    and e["RelatedChrCustomizationChoiceID"] == related
                    and materials.get(e["ChrCustomizationMaterialID"], {}).get("ChrModelTextureTargetID") == target]
            if len(hits) > 1:
                raise ValueError(f"Ambiguous material {choice}/{target}/{related}")
            if not hits:
                return None
            return files[textures[materials[hits[0]["ChrCustomizationMaterialID"]]["MaterialResourcesID"]]]

        def record(kind, target, value, selectors=(), path=""):
            selectors = [i | (j << 16) for i, j in selectors]
            if len(selectors) > 3:
                raise ValueError("Material/geometry selector capacity exceeded")
            records.append(struct.pack("<7I", gender, kind, target, value,
                                       *(selectors + [0xffffffff] * (3 - len(selectors))))
                           + path.encode().ljust(128, b"\0"))

        # Related geometry rows must precede unconditional fallbacks for the same group.
        geo_rows = []
        used_groups = set()
        for option in prof["options"]:
            for choice in option["choices"]:
                for e in choice["elements"]:
                    if not e["ChrCustomizationGeosetID"]:
                        continue
                    g = geometry[e["ChrCustomizationGeosetID"]]
                    selectors = [indices[choice["ID"]]]
                    related = e["RelatedChrCustomizationChoiceID"]
                    if related:
                        if related not in indices:
                            raise ValueError("Missing dependent geometry choice")
                        selectors.append(indices[related])
                    geo_rows.append((len(selectors), g, selectors))
                    used_groups.add(g["GeosetType"])
        for _, g, selectors in sorted(geo_rows, key=lambda r: -r[0]):
            record(0, g["GeosetType"], g["GeosetType"] * 100 + g["GeosetID"], selectors)
        for group in used_groups:
            record(0, group, group * 100)
        for group, value in ((22, 2201), (32, 3201), (51, 5101)):
            if group not in used_groups:
                record(0, group, value)
        # Eye atlas and eyesight are independent of the optional additive glow sprite.
        for eye, style, sight in itertools.product(range(26), range(3), range(4)):
            choice = opts["Eye Color"]["choices"][eye]
            style_choice = opts["Eye Style"]["choices"][style]
            key = material(choice["ID"], 25, style_choice["ID"]) or material(choice["ID"], 25)
            if not key:
                raise ValueError(f"Unresolved eye palette: {sex}/{eye}/{style}")
            if sight:
                sheet = image(key)
                overlay = image(material(opts["Eyesight"]["choices"][sight]["ID"], 44))
                sheet.alpha_composite(overlay.resize(sheet.size, Image.Resampling.LANCZOS))
                key = emit(f"{root}\\eyes{eye}_{style}_{sight}.blp", sheet)
            selectors = [indices[choice["ID"]], indices[style_choice["ID"]],
                         indices[opts["Eyesight"]["choices"][sight]["ID"]]]
            record(1, 5, 0, selectors, key)
        for color, marking in itertools.product(opts["Horn Color"]["choices"], opts["Horn Markings"]["choices"]):
            key = material(color["ID"], 10, marking["ID"]) or material(marking["ID"], 10)
            if not key:
                raise ValueError(f"Missing horn palette: {sex}/{color['ID']}/{marking['ID']}")
            record(1, 6, 0, [indices[color["ID"]], indices[marking["ID"]]], key)
        section_art = {}
        for skin, paint, color in itertools.product(range(9), range(4), range(3)):
            skin_choice = opts["Skin Color"]["choices"][skin]
            body = image(material(skin_choice["ID"], 1))
            overlay = None
            if paint:
                overlay = image(material(opts["Body Paint Color"]["choices"][color]["ID"], 16,
                                         opts["Body Paint"]["choices"][paint]["ID"]))
                body.alpha_composite(overlay.resize(body.size, Image.Resampling.LANCZOS))
            encoded = skin + 9 * (paint + 4 * color)
            section_art[str(encoded)] = {"body": emit(f"{root}\\body{encoded}.blp",
                                                     body.crop((0, 0, 512, 512)), compositor=True),
                "extra": material(skin_choice["ID"], 2), "faces": [],
                "pelvis": material(skin_choice["ID"], 13), "torso": material(skin_choice["ID"], 14)}
            for face, face_choice in enumerate(opts["Face"]["choices"]):
                key = material(face_choice["ID"], 5, skin_choice["ID"])
                if not key:
                    raise ValueError(f"Missing skin/face: {sex}/{skin}/{face}")
                sheet = image(key)
                if overlay:
                    sheet.alpha_composite(overlay.crop((512, 0, 1024, 512)).resize(sheet.size))
                sheet = sheet.resize((256, 192), Image.Resampling.LANCZOS)
                lower = emit(f"{root}\\facelower{face}_{encoded}.blp",
                             sheet.crop((0, 64, 256, 192)), compositor=True)
                upper = emit(f"{root}\\faceupper{face}_{encoded}.blp",
                             sheet.crop((0, 0, 256, 64)), compositor=True)
                section_art[str(encoded)]["faces"].append((lower, upper))
        path = h.art_path(f"{root}\\highmountaintauren{sex}.m2")
        model = v.read_player_model(path)
        skin = parse_skin(path.with_name(path.stem + "00.skin").read_bytes())
        source_types = p.load_json(h.ROOT / "integration/preparation.json")["models"][sex][
            "texture_types_before_downgrade"]
        # Restore TXID eye binding, hide unusable extra passes, and retain ordinary armor geosets.
        for i, texture in enumerate(model.textures):
            original = source_types[i]
            if original == 19:
                texture.update(type=5, filename="")
            elif original in (11, 15, 16, 17, 18, 20):
                neutral = Image.new("RGBA", (4, 4), (255, 255, 255, 255))
                texture.update(type=0, filename=emit(f"{root}\\neutral.blp", neutral))
        model.replacable_texture_lookup = [65535] * 16
        for i, texture in enumerate(model.textures):
            if texture["type"]:
                model.replacable_texture_lookup[texture["type"]] = i
        # Actual eyeballs use one opaque UV0 sample in Wrath; preserve group17's separate glow material.
        eye_slot = next(i for i, texture in enumerate(model.textures) if texture["type"] == 5)
        eye_material = len(model.materials)
        model.materials.append({"flags": 4, "blending_mode": 0})
        for i, raw in enumerate(skin.batches):
            slots = model.texture_combos[v.u16(raw, 16):v.u16(raw, 16) + v.u16(raw, 14)]
            if not any(model.textures[j]["type"] == 5 for j in slots):
                continue
            batch = bytearray(raw)
            v.patch16(batch, 0, 0)
            v.patch16(batch, 10, eye_material)
            v.patch16(batch, 14, 1)
            v.patch16(batch, 16, len(model.texture_combos))
            v.patch16(batch, 18, 0)
            model.texture_combos.append(eye_slot)
            model.texture_coord_combos[0] = 0
            skin.batches[i] = bytes(batch)
        vertices = bytearray(model.vertices)
        transformed = set()
        for batch in skin.batches:
            slots = model.texture_combos[v.u16(batch, 16):v.u16(batch, 16) + v.u16(batch, 14)]
            if [model.textures[i]["type"] for i in slots] != [1]:
                continue
            mesh = skin.submeshes[v.u16(batch, 4)]
            for vertex in skin.vertices[v.u16(mesh, 4):v.u16(mesh, 4) + v.u16(mesh, 6)]:
                if vertex in transformed:
                    continue
                u, y = struct.unpack_from("<2f", vertices, vertex * 48 + 32)
                struct.pack_into("<2f", vertices, vertex * 48 + 32,
                                 u * 2 if u <= .5 else u - .5, y if u <= .5 else .625 + .375 * y)
                transformed.add(vertex)
        model.vertices = bytes(vertices)
        path.write_bytes(write_md20(model))
        path.with_name(path.stem + "00.skin").write_bytes(write_skin(skin))
        render[sex] = {"sections": section_art, "model": str(path), "geoset_groups": sorted(used_groups)}
        print(sex, "render assets prepared", flush=True)
    (h.STAGE / "EsteriaHighmountain.bin").write_bytes(
        struct.pack("<3I", 0x314D4845, 1, len(records)) + b"".join(records))
    h.save(h.ROOT / "integration/rendering.json", render)
    return render


def replace_rows(name, data, rows, pool=None):
    table = p.RawWdbc(data)
    layout = p.WDBC_LAYOUTS[name]
    kept = [r for r in table.records if p._value(r, layout.race_offset, layout.race_width) != RACE]
    if name != "CharacterFacialHairStyles" and {p._value(r, 0) for r in kept} & {p._value(r, 0) for r in rows}:
        raise ValueError(f"{name} allocation collision")
    return table.build(kept + rows, bytes(pool) if pool is not None else table.strings)


def tables(client=p.CLIENT_DEFAULT):
    render = p.load_json(h.ROOT / "integration/rendering.json")
    manifest = p.load_manifest("highmountain")
    allocation = p.load_json(p.ALLOCATION_PATH)
    storm = p.Storm(p.DLL_DEFAULT)
    names = ("ChrRaces", "CreatureModelData", "CreatureDisplayInfo", "CharSections", "CharHairGeosets",
             "CharHairTextures", "CharacterFacialHairStyles", "BarberShopStyle", "CharBaseInfo", "CharStartOutfit",
             "NameGen", "Spell")
    t = {n: p._read_archive_entry(storm, client / p.GLOBAL_ARCHIVE_REL, p.DBC_ROOT + n + ".dbc") for n in names}
    for n in ("CreatureModelData", "CreatureDisplayInfo"):
        t[n] = p._merge_model_table(n, t[n], manifest, allocation)
    t["ChrRaces"] = p._merge_chr_races(t["ChrRaces"], manifest, allocation)
    t["CharBaseInfo"] = p._build_char_base_info(t["CharBaseInfo"], manifest)
    t["CharStartOutfit"] = p._build_char_start_outfit(t["CharStartOutfit"], manifest, allocation)
    t["NameGen"] = p._clone_namegen(t["NameGen"], manifest, allocation)
    t["CharHairTextures"] = p._clone_race_rows("CharHairTextures", t["CharHairTextures"], manifest, allocation)
    pool, rows = bytearray(p.RawWdbc(t["CharSections"]).strings), []
    hair, facial = [], []
    next_id = 590000
    for gender, sex in enumerate(("male", "female")):
        def add(kind, style, color, paths):
            nonlocal next_id
            row = struct.pack("<10I", next_id, RACE, gender, kind, 0, 0, 0, 1 if kind == 1 else 17, style, color)
            for field, key in zip((4, 5, 6), paths):
                row = p._set_string(row, field, pool, key or "")
            rows.append(row)
            next_id += 1

        for color, art in render[sex]["sections"].items():
            add(0, 0, int(color), (art["body"], art["extra"]))
            add(4, 0, int(color), (art["pelvis"], art["torso"]))
            for face, paths in enumerate(art["faces"]):
                add(1, face, int(color), paths)
        # Logical geometry/material choices are handled by the native catalog.
        add(2, 0, 0, ())
        add(3, 0, 0, (render[sex]["sections"]["0"]["extra"],))
        hair.append(struct.pack("<6I", 450300 + gender, RACE, gender, 0, 0, 0))
        facial.append(struct.pack("<8I", RACE, gender, 0, 0, 0, 0, 0, 0))
    t["CharSections"] = replace_rows("CharSections", t["CharSections"], rows, pool)
    t["CharHairGeosets"] = replace_rows("CharHairGeosets", t["CharHairGeosets"], hair)
    t["CharacterFacialHairStyles"] = replace_rows("CharacterFacialHairStyles", t["CharacterFacialHairStyles"], facial)
    # Standard barber entries keep the base field rows; independent Highmountain controls are native.
    t["BarberShopStyle"] = p._clone_race_rows("BarberShopStyle", t["BarberShopStyle"], manifest, allocation)
    return t


def gui():
    path = h.art_path(p.GLUE_ROOT + "CharacterCreate.lua")
    text = path.read_text(encoding="utf-8")
    text = text.replace('return CharacterCreate.selectedRaceID == 47 or ',
                        'return CharacterCreate.selectedRaceID == 46 or CharacterCreate.selectedRaceID == 47 or ')
    text = text.replace('for i=6,12 do', 'for i=6,23 do').replace('for i=1,12 do', 'for i=1,23 do')
    text = text.replace('local value,count = CycleCharCustomization("EA_GET",i);',
                        'local value,count,label = CycleCharCustomization("EA_GET",i);')
    text = text.replace('(CharacterCreate.selectedRaceID == 47 and EA_MECH_LABELS[i]',
                        '(CharacterCreate.selectedRaceID == 46 and (label or "") '
                        'or CharacterCreate.selectedRaceID == 47 and EA_MECH_LABELS[i]')
    text = text.replace('frame:SetPoint("CENTER", parent, "CENTER", 900, CharacterCreate.selectedRaceID',
                        'frame:SetPoint("CENTER", parent, "CENTER", CharacterCreate.selectedRaceID == 46 '
                        'and (visibleRow >= 11 and 1040 or 740) or 900, CharacterCreate.selectedRaceID')
    text = text.replace('CharacterCreate.selectedRaceID == 47 and 240-visibleRow*34 or 220-visibleRow*38',
                        'CharacterCreate.selectedRaceID == 46 and 240-(visibleRow%11)*36 '
                        'or CharacterCreate.selectedRaceID == 47 and 240-visibleRow*34 or 220-visibleRow*38')
    text = text.replace('    RandomizeCharCustomization();',
                        '    if CharacterCreate.selectedRaceID == 46 then CycleCharCustomization("EA_RANDOM",1);\n'
                        '    else RandomizeCharCustomization(); end')
    from luaparser import ast
    ast.parse(text)
    path.write_text(text, encoding="utf-8", newline="\n")


def build(client=p.CLIENT_DEFAULT):
    h.glue(client)
    gui()
    t = tables(client)
    storm = p.Storm(p.DLL_DEFAULT)
    assets = {"\\".join(f.relative_to(h.SOURCE).parts): f.read_bytes() for f in h.SOURCE.rglob("*") if f.is_file()}
    assets.update({"\\".join(f.relative_to(h.ART).parts): f.read_bytes() for f in h.ART.rglob("*") if f.is_file()})
    updates = {**assets, **{p.DBC_ROOT + n + ".dbc": data for n, data in t.items()}}
    report = {"race": RACE, "assets": len(assets), "source_hashes": {}, "stage_hashes": {}}
    for rel in (p.GLOBAL_ARCHIVE_REL, p.LOCALE_ARCHIVE_REL, p.ASSET_ARCHIVE_REL):
        target = h.STAGE / "pack" / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        report["source_hashes"][str(rel)] = p.sha256(client / rel)
        print("COMPACT", rel, flush=True)
        shutil.copy2(client / rel, target)
        storm.replace_archive_entries(target, assets if rel == p.ASSET_ARCHIVE_REL else updates)
        compressed = target.with_suffix(".compressed-next.MPQ")
        p.rebuild_archive_streaming(storm, target, compressed, compress=True)
        if compressed.stat().st_size >= 0x80000000:
            raise ValueError("Classic reader archive exceeds 2 GiB: " + str(rel))
        os.replace(compressed, target)
        report["stage_hashes"][str(rel)] = p.sha256(target)
    server = h.STAGE / "server-dbc"
    server.mkdir(exist_ok=True)
    for name in p.SERVER_DBC_TABLES:
        (server / (name + ".dbc")).write_bytes(t[name])
    # Append only the Highmountain geometry; all existing race profiles and skin arrays are preserved.
    baseline = (client / "EsteriaAppearanceGeometry.bin").read_bytes()
    magic, version, count = struct.unpack_from("<3I", baseline)
    extra = b""
    for sex in ("male", "female"):
        key = f"{h.PREFIX}\\{sex}\\highmountaintauren{sex}.m2"
        skin = h.art_path(key[:-3] + "00.skin").read_bytes()
        extra += key.encode().ljust(128, b"\0") + struct.pack("<I", len(skin)) + skin
    (h.STAGE / "EsteriaAppearanceGeometry.bin").write_bytes(struct.pack("<3I", magic, version, count + 2)
                                                           + baseline[12:] + extra)
    report["tables"] = list(t)
    report["companion_hashes"] = {name: p.sha256(h.STAGE / name) for name in
        ("Wow.exe", "EsteriaAppearance.dll", "EsteriaAppearance.bin", "EsteriaAppearanceGeometry.bin",
         "EsteriaAppearanceMaterials.bin", "EsteriaHighmountain.bin")}
    h.save(h.STAGE / "build-report.json", report)
    return report


def validate(client=p.CLIENT_DEFAULT):
    from wotlkconv.m2 import parse_m2
    from luaparser import ast

    report = p.load_json(h.STAGE / "build-report.json")
    storm = p.Storm(p.DLL_DEFAULT)
    for name in report["tables"]:
        key = p.DBC_ROOT + name + ".dbc"
        a = p._read_archive_entry(storm, h.STAGE / "pack" / p.GLOBAL_ARCHIVE_REL, key)
        b = p._read_archive_entry(storm, h.STAGE / "pack" / p.LOCALE_ARCHIVE_REL, key)
        if a != b:
            raise ValueError("Root/locale DBC mismatch: " + name)
        t = p.RawWdbc(a)
        if name not in ("CharBaseInfo", "CharacterFacialHairStyles"):
            ids = [p._value(r, 0) for r in t.records]
            if len(set(ids)) != len(ids):
                raise ValueError("Duplicate DBC IDs: " + name)
        if name in p.SERVER_DBC_TABLES and a != (h.STAGE / "server-dbc" / (name + ".dbc")).read_bytes():
            raise ValueError("Server DBC mismatch: " + name)
        if name in p.WDBC_LAYOUTS:
            layout = p.WDBC_LAYOUTS[name]
            old = p.RawWdbc(p._read_archive_entry(storm, client / p.GLOBAL_ARCHIVE_REL, key))
            excluded = {RACE}
            if name in ("CreatureModelData", "CreatureDisplayInfo"):
                excluded = set(p.load_json(p.ALLOCATION_PATH)["race_allocations"]["highmountain"][name].values())
            before = [r for r in old.records if p._value(r, layout.race_offset, layout.race_width) not in excluded]
            after = [r for r in t.records if p._value(r, layout.race_offset, layout.race_width) not in excluded]
            if before != after:
                raise ValueError("Unrelated race rows changed: " + name)
    for rel in (p.GLOBAL_ARCHIVE_REL, p.LOCALE_ARCHIVE_REL, p.ASSET_ARCHIVE_REL):
        stage = h.STAGE / "pack" / rel
        for name in ("CharacterCreate.lua", "CharacterInfo.lua", "GlueStrings.lua", "GlueParent.lua",
                     "ECS_Schema.lua", "ECS_Integrate.lua"):
            key = p.GLUE_ROOT + name
            data = p._read_archive_entry(storm, stage, key)
            if data != h.art_path(key).read_bytes():
                raise ValueError("Staged GlueXML differs: " + name)
            ast.parse(data.decode())
        for sex in ("male", "female"):
            key = f"{h.PREFIX}\\{sex}\\highmountaintauren{sex}.m2"
            data = p._read_archive_entry(storm, stage, key)
            if data != h.art_path(key).read_bytes():
                raise ValueError("Staged player model differs")
            model = parse_m2(data)
            skin = parse_skin(p._read_archive_entry(storm, stage, key[:-3] + "00.skin"))
            if model.vertex_count > 65535 or len(skin.vertices) > 65535:
                raise ValueError("Player vertex budget exceeded")
            for mesh in skin.submeshes:
                start = v.u16(mesh, 8) | v.u16(mesh, 2) << 16
                if start + v.u16(mesh, 10) > len(skin.indices) or v.u16(mesh, 12) > 75:
                    raise ValueError("Invalid player mesh")
            for texture in model.textures:
                if texture["type"] >= 11:
                    raise ValueError("Unsupported replaceable material")
                if texture["type"] == 0 and texture["filename"]:
                    p.Blp.parse(p._read_archive_entry(storm, stage, texture["filename"]))
    sections = p.RawWdbc(p._read_archive_entry(storm, h.STAGE / "pack" / p.GLOBAL_ARCHIVE_REL,
                                              p.DBC_ROOT + "CharSections.dbc"))
    paths = {p._string(sections.strings, p._value(r, offset)).decode()
             for r in sections.records if p._value(r, 4) == RACE for offset in (16, 20, 24)} - {""}
    handle = storm.open_archive(h.STAGE / "pack" / p.ASSET_ARCHIVE_REL)
    try:
        for key in paths:
            p.Blp.parse(storm.read(handle, key), key)
    finally:
        storm.dll.SFileCloseArchive(handle)
    if (h.STAGE / "EsteriaAppearance.bin").read_bytes() != (client / "EsteriaAppearance.bin").read_bytes():
        raise ValueError("Existing native codecs changed")
    material_name = "EsteriaAppearanceMaterials.bin"
    if (h.STAGE / material_name).read_bytes() != (client / material_name).read_bytes():
        raise ValueError("Existing native materials changed")
    return {"verified": True, "race": RACE, "appearance_paths": len(paths)}


def refresh_glue():
    h.glue()
    gui()
    report = p.load_json(h.STAGE / "build-report.json")
    updates = {p.GLUE_ROOT + n: h.art_path(p.GLUE_ROOT + n).read_bytes() for n in
               ("CharacterCreate.lua", "CharacterInfo.lua", "GlueStrings.lua", "GlueParent.lua",
                "ECS_Schema.lua", "ECS_Integrate.lua")}
    storm = p.Storm(p.DLL_DEFAULT)
    for rel in (p.GLOBAL_ARCHIVE_REL, p.LOCALE_ARCHIVE_REL, p.ASSET_ARCHIVE_REL):
        path = h.STAGE / "pack" / rel
        if p.sha256(path) != report["stage_hashes"][str(rel)]:
            raise ValueError("Archive stage changed before GlueXML refresh")
        storm.replace_archive_entries(path, updates)
        report["stage_hashes"][str(rel)] = p.sha256(path)
    report["companion_hashes"] = {name: p.sha256(h.STAGE / name) for name in report["companion_hashes"]}
    h.save(h.STAGE / "build-report.json", report)


def refresh_assets():
    report = p.load_json(h.STAGE / "build-report.json")
    paths = list(p.load_json(h.ROOT / "integration/txid-dependencies.json")["added"])
    paths.extend(f"{h.PREFIX}\\{sex}\\highmountaintauren{sex}.m2" for sex in ("male", "female"))
    updates = {key: h.art_path(key).read_bytes() for key in paths}
    storm = p.Storm(p.DLL_DEFAULT)
    for rel in (p.GLOBAL_ARCHIVE_REL, p.LOCALE_ARCHIVE_REL, p.ASSET_ARCHIVE_REL):
        stage = h.STAGE / "pack" / rel
        if p.sha256(stage) != report["stage_hashes"][str(rel)]:
            raise ValueError("Archive changed before asset refresh")
        storm.replace_archive_entries(stage, updates)
        for key, data in updates.items():
            if p._read_archive_entry(storm, stage, key) != data:
                raise ValueError("Asset refresh readback mismatch")
        report["stage_hashes"][str(rel)] = p.sha256(stage)
    report["companion_hashes"] = {name: p.sha256(h.STAGE / name) for name in report["companion_hashes"]}
    h.save(h.STAGE / "build-report.json", report)


def install(client=p.CLIENT_DEFAULT):
    import mechagnome_race_pack as db
    import expanded_appearance_pack as native

    checks = validate(client)
    processes = subprocess.check_output(["tasklist", "/FO", "CSV", "/NH"], text=True).lower()
    if "wow.exe" in processes or "eclipse.exe" in processes:
        raise RuntimeError("Close WoW/Eclipse before installing Highmountain")
    report = p.load_json(h.STAGE / "build-report.json")
    prior = p.load_json(native.STAGE / "last-install.json")
    if p.sha256(client / "Wow.exe") != prior["installed_hashes"]["Wow.exe"]:
        raise ValueError("Client executable differs from the verified native installation")
    if db.sql("SELECT COUNT(*) FROM characters WHERE race=46;", "acore_characters").strip() != "0":
        raise ValueError("Existing Highmountain characters require an explicit appearance migration")
    files = {rel: h.STAGE / "pack" / rel for rel in
             (p.GLOBAL_ARCHIVE_REL, p.LOCALE_ARCHIVE_REL, p.ASSET_ARCHIVE_REL)}
    files.update({Path(name): h.STAGE / name for name in report["companion_hashes"]})
    for rel, staged in files.items():
        expected = report["stage_hashes"].get(str(rel), report["companion_hashes"].get(str(rel)))
        if p.sha256(staged) != expected:
            raise ValueError("Staged install file hash differs: " + str(rel))
        if str(rel) in report["source_hashes"] and p.sha256(client / rel) != report["source_hashes"][str(rel)]:
            raise ValueError("Client archive stage is stale: " + str(rel))
    tables = ("playercreateinfo", "player_race_stats", "playercreateinfo_item", "playercreateinfo_action",
              "player_totem_model", "custom_race_start_spell", "custom_race_start_skill")
    for name in tables:
        field = "RaceID" if name == "player_totem_model" else "race"
        if db.sql(f"SELECT COUNT(*) FROM `{name}` WHERE `{field}`=46;").strip() != "0":
            raise ValueError("Existing Highmountain startup rows: " + name)
    if db.sql("SHOW COLUMNS FROM characters LIKE 'extraAppearance';", "acore_characters").strip():
        raise ValueError("Extended appearance schema already exists; inspect prior installation first")
    backup = Path("C:/Users/Zach/.codex/backups") / ("highmountain-" + datetime.now().strftime("%Y%m%d-%H%M%S"))
    backup.mkdir(parents=True)
    before = {}
    for rel in files:
        live = client / rel
        if live.exists():
            target = backup / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(live, target)
            before[str(rel)] = p.sha256(live)
            if p.sha256(target) != before[str(rel)]:
                raise RuntimeError("Client backup verification failed")
    for name in p.SERVER_DBC_TABLES:
        live = p.SERVER_DBC_ROOT / (name + ".dbc")
        target = backup / "server-dbc" / live.name
        target.parent.mkdir(exist_ok=True)
        shutil.copy2(live, target)
        if p.sha256(target) != p.sha256(live):
            raise RuntimeError("Server DBC backup verification failed")
    rollback = "START TRANSACTION;\n" + "\n".join(
        f"DELETE FROM `{name}` WHERE `{'RaceID' if name == 'player_totem_model' else 'race'}`=46;"
        for name in tables) + "\nCOMMIT;\n"
    (backup / "rollback-world.sql").write_text(rollback, encoding="utf-8", newline="\n")
    (backup / "rollback-characters.sql").write_text(
        "-- Stop worldserver and restore its previous image before dropping this column.\n"
        "ALTER TABLE `characters` DROP COLUMN `extraAppearance`;\n", encoding="utf-8", newline="\n")
    world = p.ROOT / "data/sql/updates/pending_db_world/rev_20261001006000000.sql"
    characters = p.ROOT / "data/sql/updates/pending_db_characters/rev_20261001006000000.sql"
    db.sql(characters.read_text(encoding="utf-8"), "acore_characters")
    try:
        db.sql("START TRANSACTION;\n" + world.read_text(encoding="utf-8") + "\nCOMMIT;")
        for rel, staged in files.items():
            target = client / rel
            temporary = target.with_suffix(target.suffix + ".highmountain-next")
            shutil.copy2(staged, temporary)
            if p.sha256(temporary) != p.sha256(staged):
                raise RuntimeError("Install copy hash mismatch")
            os.replace(temporary, target)
        for name in p.SERVER_DBC_TABLES:
            source = h.STAGE / "server-dbc" / (name + ".dbc")
            target = p.SERVER_DBC_ROOT / source.name
            shutil.copy2(source, target)
            if p.sha256(source) != p.sha256(target):
                raise RuntimeError("Installed server DBC hash mismatch")
    except Exception:
        for rel in files:
            if (backup / rel).exists():
                shutil.copy2(backup / rel, client / rel)
            elif (client / rel).exists():
                (client / rel).unlink()
        for name in p.SERVER_DBC_TABLES:
            shutil.copy2(backup / "server-dbc" / (name + ".dbc"), p.SERVER_DBC_ROOT / (name + ".dbc"))
        db.sql(rollback)
        db.sql((backup / "rollback-characters.sql").read_text(), "acore_characters")
        raise
    report.update(backup=str(backup), before_hashes=before, validation=checks,
                  installed_hashes={str(rel): p.sha256(client / rel) for rel in files})
    h.save(backup / "install-report.json", report)
    h.save(h.STAGE / "last-install.json", report)
    prior["installed_hashes"].update(report["installed_hashes"])
    prior["latest_highmountain_backup"] = str(backup)
    h.save(native.STAGE / "last-install.json", prior)
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("prepare", "build", "refresh-glue", "refresh-assets",
                                             "validate", "install"))
    args = parser.parse_args()
    result = {"prepare": prepare_rendering, "build": build, "refresh-glue": refresh_glue,
              "refresh-assets": refresh_assets, "validate": validate, "install": install}[args.command]()
    print(json.dumps(result if args.command in ("validate", "install") else
                     {"stage_generated": True, "command": args.command}, indent=2))
