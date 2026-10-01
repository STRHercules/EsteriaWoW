"""Prepare and install Race47 using the existing native appearance and MPQ pipeline."""

import argparse
import itertools
import json
import os
import shutil
import struct
import subprocess
from datetime import datetime
from pathlib import Path

from PIL import Image
from wotlkconv.m2 import parse_skin, write_md20
from wotlkconv.m2.skin import write_skin
from wotlkconv.m2.split import _rebuild_skin

import expanded_appearance_pack as native
import race_portrait_pack as portraits
import retroported_race_pack as p
import skyborne_visual_pack as v
import mechagnome_animations as animations

ROOT = Path(r"G:\RetroPorterWork\mechagnome")
SOURCE = ROOT / "output/patch-root"
ART = ROOT / "integration/patch-root"
STAGE = Path("C:/Users/Zach/.codex/tmp/mechagnome")
PREFIX = "custom\\mechagnome\\native"
LABELS = ("Skin Color", "Face", "Hair Style", "Hair Color", "Facial Hair", "Arm Upgrade",
          "Leg Upgrade", "Modification", "Eye Color", "Paint", "Eyesight", "Eye Style")


def source(key):
    return SOURCE.joinpath(*p.PureWindowsPath(key).parts)


def profile(discovery, model):
    options = {o["Name_lang"]: o for o in discovery["options"] if o["ChrModelID"] == model}
    materials = {r["ID"]: r for r in discovery["linked"]["ChrCustomizationMaterial"]}
    textures = {r["MaterialResourcesID"]: r["FileDataID"] for r in discovery["texture_files"]}
    files = {r["file_data_id"]: "custom\\mechagnome\\" + r["path"] for r in discovery["file_assets"]}
    geosets = {r["ID"]: r for r in discovery["linked"]["ChrCustomizationGeoset"]}
    skinned = {r["ID"]: r for r in discovery["linked"]["ChrCustomizationSkinnedModel"]}
    result = {"choices": {}, "omitted": [], "materials": {}, "geometry": {}}
    for label in LABELS:
        choices = sorted((c for c in discovery["choices"] if label in options
                          and c["ChrCustomizationOptionID"] == options[label]["ID"]),
                         key=lambda c: c["OrderIndex"])
        # ReqType 10 is an internal transmog placeholder, not a player customization.
        choices = [c for c in choices if c["ChrCustomizationReqID"] != 10]
        if label == "Skin Color":
            choices = [c for c in choices if c["ChrCustomizationReqID"] == 141]
        result["choices"][label] = choices
        for c in choices:
            elements = [e for e in discovery["elements"] if e["ChrCustomizationChoiceID"] == c["ID"]]
            mapping = {}
            for e in elements:
                material = materials.get(e["ChrCustomizationMaterialID"])
                if material:
                    key = files[textures[material["MaterialResourcesID"]]]
                    if not source(key).is_file():
                        raise FileNotFoundError(f"Missing {label} choice {c['ID']}: {key}")
                    mapping[f"{material['ChrModelTextureTargetID']}:{e['RelatedChrCustomizationChoiceID']}"] = key
            result["materials"][str(c["ID"])] = mapping
            result["geometry"][str(c["ID"])] = sorted({g["GeosetType"] * 100 + g["GeosetID"]
                for e in elements for g in (geosets.get(e["ChrCustomizationGeosetID"]),
                                            skinned.get(e["ChrCustomizationSkinnedModelID"])) if g})
    result["omitted"] = [{"id": c["ID"], "option": o["Name_lang"], "requirement": c["ChrCustomizationReqID"]}
        for o in options.values() for c in discovery["choices"]
        if c["ChrCustomizationOptionID"] == o["ID"] and c not in result["choices"][o["Name_lang"]]]
    return result


def counts(prof):
    return {label: max(1, len(prof["choices"][label])) for label in LABELS}


def descriptors(prof):
    c = counts(prof)
    return ((0x28, c["Skin Color"], 1), (0x2C, c["Face"], 1), (0x34, c["Hair Style"], 1),
            (0x24, c["Hair Color"], 1), (0x2C, c["Facial Hair"], c["Face"]),
            (0x34, c["Arm Upgrade"], c["Hair Style"]),
            (0x34, c["Leg Upgrade"], c["Hair Style"] * c["Arm Upgrade"]),
            (0x30, c["Modification"], 1), (0x24, c["Eye Color"], c["Hair Color"]),
            (0x28, c["Paint"], c["Skin Color"]),
            (0x28, c["Eyesight"], c["Skin Color"] * c["Paint"]),
            (0x30, c["Eye Style"], c["Modification"]))


def material(prof, label, index, target, related=0):
    choice = prof["choices"][label][index]
    return prof["materials"][str(choice["ID"])].get(f"{target}:{related}")


def image(key):
    b = p.Blp.parse(source(key).read_bytes()).decode_level(0)
    return Image.frombytes("RGBA", (b.width, b.height), bytes(b.data))


def emit(key, img, alpha=False):
    out = ART.joinpath(*p.PureWindowsPath(key).parts)
    out.parent.mkdir(parents=True, exist_ok=True)
    rgba = p.BlpImage(img.width, img.height, bytearray(img.tobytes()))
    if alpha:
        levels = rgba.mip_chain()
        payloads = [Image.frombytes("RGBA", (level.width, level.height), bytes(level.data)).tobytes("raw", "BGRA")
                    for level in levels]
        out.write_bytes(p.Blp.from_images(levels, compression=3, alpha_type=8, alpha_size=8,
                                         payloads=payloads).serialize())
    else:
        palette = p.build_palette(rgba.data, 256)
        out.write_bytes(p._encode_wotlk_paletted(rgba, palette, p.PaletteMapper(palette)))
    return key


def prepare_model(sex, prof):
    path = source(f"custom\\mechagnome\\character\\mechagnome\\{sex}\\mechagnome{sex}.m2")
    model = v.read_player_model(path)
    animation_report = animations.inherit(model, sex)
    skin = parse_skin(path.with_name(path.stem + "00.skin").read_bytes())
    # Preserve modern mechanical selectors in groups unused by the native appearance table.
    # The helper sets these groups explicitly; normal equipment continues through stock selectors.
    remap = {2201: 0, 2202: 0, 3201: 0, 3202: 0, 3301: 0, 5101: 0,
             1801: 0, 1804: 0, 2901: 301, 3001: 501}
    keep = [i for i, raw in enumerate(skin.submeshes) if v.u16(raw, 0) not in (5102, 5103)]
    skin = _rebuild_skin(skin, keep, {i: i for i in range(model.vertex_count)})
    collection = source("custom\\mechagnome\\item\\objectcomponents\\collections\\"
                        f"collections_mechagnome_mg_{sex[0]}.m2")
    extra = parse_skin(collection.with_name(collection.stem + "00.skin").read_bytes())
    collection_remap = {**{2900 + i: 300 + i for i in range(1, 5)},
                        **{3000 + i: 500 + i for i in range(1, 3)},
                        **{3100 + i: 1000 + i for i in range(1, 3)},
                        **{2400 + i: 1600 + i for i in range(1, 5)}, 1603: 1803}
    v.append_collection(model, skin, collection,
                        {v.u16(r, 0): collection_remap.get(v.u16(r, 0), v.u16(r, 0)) for r in extra.submeshes})
    # Body/head material atlas follows the same split used for Skyborne.
    vertices = bytearray(model.vertices)
    transformed = set()
    for raw in skin.batches:
        mesh = skin.submeshes[v.u16(raw, 4)]
        slots = model.texture_combos[v.u16(raw, 16):v.u16(raw, 16) + v.u16(raw, 14)]
        types = [model.textures[i]["type"] for i in slots]
        if types == [1]:
            for vertex in skin.vertices[v.u16(mesh, 4):v.u16(mesh, 4) + v.u16(mesh, 6)]:
                if vertex in transformed:
                    continue
                u, y = struct.unpack_from("<2f", vertices, vertex * 48 + 32)
                struct.pack_into("<2f", vertices, vertex * 48 + 32,
                                 u * 2 if u <= .5 else u - .5, y if u <= .5 else .625 + .375 * y)
                transformed.add(vertex)
        if v.u16(mesh, 0) == 1507 and 11 in types:
            batch = bytearray(raw)
            v.patch16(batch, 14, 1)
            skin.batches[skin.batches.index(raw)] = bytes(batch)
    model.vertices = bytes(vertices)
    for raw_index, raw in enumerate(skin.submeshes):
        changed = bytearray(raw)
        v.patch16(changed, 0, remap.get(v.u16(raw, 0), v.u16(raw, 0)))
        skin.submeshes[raw_index] = bytes(changed)
    for texture in model.textures:
        if texture["type"] in (11, 15):
            texture.update(type=5, filename="")
        if texture["type"] == 0 and texture["filename"] and not source(texture["filename"]).is_file():
            raise FileNotFoundError(texture["filename"])
    # Modern eye meshes use TXID materials. Bind their color through native replaceable slot 5.
    eye_slot = len(model.textures)
    model.textures.append({"type": 5, "flags": 0, "filename": ""})
    for index, raw in enumerate(skin.batches):
        geoset = v.u16(skin.submeshes[v.u16(raw, 4)], 0)
        # Group 33 is the actual eyeball. Group 17 is the optional additive glow,
        # with a different UV map and hard material; preserve its source binding.
        if geoset == 0 and any(model.textures[i]["type"] == 5 for i in
                              model.texture_combos[v.u16(raw, 16):v.u16(raw, 16) + v.u16(raw, 14)]):
            batch = bytearray(raw)
            v.patch16(batch, 16, len(model.texture_combos))
            v.patch16(batch, 14, 1)
            v.patch16(batch, 0, 0)
            v.patch16(batch, 10, len(model.materials))
            model.materials.append({"flags": 4, "blending_mode": 0})
            model.texture_combos.append(eye_slot)
            skin.batches[index] = bytes(batch)
    model.replacable_texture_lookup = [65535] * 16
    for i, texture in enumerate(model.textures):
        if texture["type"]:
            model.replacable_texture_lookup[texture["type"]] = i
    skin = v.compact_bone_palettes(model, skin)
    key = f"{PREFIX}\\{sex}\\mechagnome{sex}.m2"
    target = ART.joinpath(*p.PureWindowsPath(key).parts)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(write_md20(model))
    target.with_name(target.stem + "00.skin").write_bytes(write_skin(skin))
    for anim in path.parent.glob(path.stem + "*.anim"):
        shutil.copy2(anim, target.parent / anim.name)
    child_files = {a.name for a in path.parent.glob(path.stem + "*.anim")}
    for anim in (animations.ROOT / sex).glob(path.stem + "*.anim"):
        if anim.name not in child_files:
            shutil.copy2(anim, target.parent / anim.name)
    return {"model_path": key, "vertices": model.vertex_count, "indices": len(skin.indices),
            "geosets": sorted({v.u16(r, 0) for r in skin.submeshes}), "profile": prof,
            "animation_inheritance": animation_report}


def prepare():
    d = p.load_json(ROOT / "reports/discovery.json")
    report = {"race": 47, "labels": LABELS, "sexes": {}}
    for sex, model in (("male", 73), ("female", 74)):
        prof = profile(d, model)
        report["sexes"][sex] = prepare_model(sex, prof)
        root = f"{PREFIX}\\{sex}"
        for skin, choice in enumerate(prof["choices"]["Skin Color"]):
            body = image(material(prof, "Skin Color", skin, 1))
            emit(f"{root}\\body{skin}.blp", body.crop((0, 0, 512, 512)))
            for target, name in ((13, "pelvis"), (14, "torso")):
                key = material(prof, "Skin Color", skin, target)
                if key:
                    emit(f"{root}\\{name}{skin}.blp", image(key))
            for face in range(counts(prof)["Face"]):
                face_key = material(prof, "Face", face, 5, choice["ID"])
                if not face_key:
                    raise ValueError(f"Incomplete Face/Skin mapping: {sex} {face} {choice['ID']}")
                sheet = image(face_key).resize((256, 192), Image.Resampling.LANCZOS)
                emit(f"{root}\\faceupper{face}_{skin}.blp", sheet.crop((0, 0, 256, 64)))
                emit(f"{root}\\facelower{face}_{skin}.blp", sheet.crop((0, 64, 256, 192)))
        print(sex, counts(prof), report["sexes"][sex]["vertices"], flush=True)
    (ROOT / "integration/preparation.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    STAGE.mkdir(parents=True, exist_ok=True)
    (STAGE / "EsteriaAppearance.bin").write_bytes(
        appearance_catalog(report, (p.CLIENT_DEFAULT / "EsteriaAppearance.bin").read_bytes()))
    (STAGE / "EsteriaAppearanceGeometry.bin").write_bytes(
        geometry_catalog(report, (p.CLIENT_DEFAULT / "EsteriaAppearanceGeometry.bin").read_bytes()))
    return report


def appearance_catalog(report, baseline):
    magic, version, n = struct.unpack_from("<3I", baseline)
    stride = 12 + 16 * 144
    if magic != 0x50504145 or version != 2 or len(baseline) != 12 + n * stride:
        raise ValueError("Unexpected native catalog")
    rows = [baseline[12 + i * stride:12 + (i + 1) * stride] for i in range(n)
            if struct.unpack_from("<I", baseline, 12 + i * stride)[0] != 47]
    for gender, sex in enumerate(("male", "female")):
        prof = report["sexes"][sex]["profile"]
        desc = descriptors(prof)
        totals = {}
        row = bytearray(struct.pack("<3I", 47, gender, len(desc)))
        for offset, count, factor in desc:
            totals[offset] = max(totals.get(offset, 0), count * factor)
            row.extend(struct.pack("<4I", offset, count, factor, 0) + bytes(128))
        if any(total > 256 for total in totals.values()):
            raise ValueError(f"Mechagnome appearance byte overflow: {totals}")
        row.extend(bytes((16 - len(desc)) * 144))
        rows.append(bytes(row))
    return struct.pack("<3I", magic, version, len(rows)) + b"".join(rows)


def geometry_catalog(report, baseline):
    magic, version, n = struct.unpack_from("<3I", baseline)
    at, rows = 12, []
    for _ in range(n):
        length = struct.unpack_from("<I", baseline, at + 128)[0]
        row = baseline[at:at + 132 + length]
        if not row[:128].split(b"\0")[0].startswith(PREFIX.encode()):
            rows.append(row)
        at += 132 + length
    if at != len(baseline) or magic != 0x4D474145 or version != 1:
        raise ValueError("Unexpected geometry catalog")
    for sex in ("male", "female"):
        key = report["sexes"][sex]["model_path"]
        path = ART.joinpath(*p.PureWindowsPath(key).parts)
        skin = path.with_name(path.stem + "00.skin").read_bytes()
        rows.append(key.encode().ljust(128, b"\0") + struct.pack("<I", len(skin)) + skin)
    return struct.pack("<3I", magic, version, len(rows)) + b"".join(rows)


def material_catalog(report):
    rows = []
    for gender, sex in enumerate(("male", "female")):
        prof = report["sexes"][sex]["profile"]
        desc = descriptors(prof)
        for eye, style, sight in itertools.product(range(counts(prof)["Eye Color"]), range(3), range(4)):
            related = prof["choices"]["Eye Style"][style]["ID"]
            key = material(prof, "Eye Color", eye, 25, related) or material(prof, "Eye Color", eye, 25)
            if not key:
                raise ValueError(f"Eye material mapping missing: {sex} {eye} {style}")
            combined = image(key)
            if sight:
                overlay = image(material(prof, "Eyesight", sight, 44))
                if overlay.size != combined.size:
                    overlay = overlay.resize(combined.size, Image.Resampling.LANCZOS)
                combined.alpha_composite(overlay)
            target = f"{PREFIX}\\{sex}\\eyes{eye}_{style}_{sight}.blp"
            if sight == 0:
                # Direct material art needs no compositor conversion.
                path = ART.joinpath(*p.PureWindowsPath(target).parts)
                path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source(key), path)
            else:
                emit(target, combined, alpha=True)
            row = bytearray(struct.pack("<3I", 47, gender, 5))
            for index, value in ((8, eye), (11, style), (10, sight)):
                offset, count, factor = desc[index]
                row.extend(struct.pack("<4I", offset, factor, count, value))
            rows.append(bytes(row) + target.encode().ljust(128, b"\0"))
    return struct.pack("<3I", 0x544D4145, 1, len(rows)) + b"".join(rows)


def replace_rows(data, name, rows, pool=None):
    table = p.RawWdbc(data)
    layout = p.WDBC_LAYOUTS[name]
    kept = [r for r in table.records if p._value(r, layout.race_offset, layout.race_width) != 47]
    if name != "CharacterFacialHairStyles":
        if {p._value(r, 0) for r in kept} & {p._value(r, 0) for r in rows}:
            raise ValueError(f"{name} allocation collision")
    return table.build([*kept, *rows], bytes(pool) if pool is not None else table.strings)


def tables(client, report):
    manifest = p.load_manifest("mechagnome")
    allocation = p.load_json(p.ALLOCATION_PATH)
    names = ("ChrRaces", "CreatureModelData", "CreatureDisplayInfo", "CharSections", "CharHairGeosets",
             "CharHairTextures", "CharacterFacialHairStyles", "BarberShopStyle", "CharBaseInfo",
             "CharStartOutfit", "NameGen", "Spell")
    storm = p.Storm(p.DLL_DEFAULT)
    result = {name: p._read_archive_entry(storm, client / p.GLOBAL_ARCHIVE_REL, p.DBC_ROOT + name + ".dbc")
              for name in names}
    for name in ("CreatureModelData", "CreatureDisplayInfo"):
        result[name] = p._merge_model_table(name, result[name], manifest, allocation)
    result["ChrRaces"] = p._merge_chr_races(result["ChrRaces"], manifest, allocation)
    result["CharBaseInfo"] = p._build_char_base_info(result["CharBaseInfo"], manifest)
    result["CharStartOutfit"] = p._build_char_start_outfit(result["CharStartOutfit"], manifest, allocation)
    result["NameGen"] = p._clone_namegen(result["NameGen"], manifest, allocation)
    result["CharHairTextures"] = p._clone_race_rows(
        "CharHairTextures", result["CharHairTextures"], manifest, allocation)
    sections = p.RawWdbc(result["CharSections"])
    pool, rows, hair, facial = bytearray(sections.strings), [], [], []
    next_id, hair_id = 520000, 450100
    for gender, sex in enumerate(("male", "female")):
        prof = report["sexes"][sex]["profile"]
        c = counts(prof)
        root = f"{PREFIX}\\{sex}"

        def add(kind, style, color, paths):
            nonlocal next_id
            row = struct.pack("<10I", next_id, 47, gender, kind, 0, 0, 0, 1 if kind == 1 else 17, style, color)
            for field, key in zip((4, 5, 6), paths):
                row = p._set_string(row, field, pool, key or "")
            rows.append(row)
            next_id += 1

        for eyesight, paint, skin in itertools.product(
                range(c["Eyesight"]), range(c["Paint"]), range(c["Skin Color"])):
            encoded = skin + c["Skin Color"] * (paint + c["Paint"] * eyesight)
            add(0, 0, encoded, [f"{root}\\body{skin}.blp", material(prof, "Paint", paint, 2)])
            add(4, 0, encoded, [f"{root}\\pelvis{skin}.blp", f"{root}\\torso{skin}.blp" if gender else ""])
            for beard, face in itertools.product(range(c["Facial Hair"]), range(c["Face"])):
                add(1, face + beard * c["Face"], encoded,
                    [f"{root}\\facelower{face}_{skin}.blp", f"{root}\\faceupper{face}_{skin}.blp"])
        for leg, arm, style in itertools.product(
                range(c["Leg Upgrade"]), range(c["Arm Upgrade"]), range(c["Hair Style"])):
            encoded = style + c["Hair Style"] * (arm + c["Arm Upgrade"] * leg)
            geo = prof["geometry"][str(prof["choices"]["Hair Style"][style]["ID"])][0]
            hair.append(struct.pack("<6I", hair_id, 47, gender, encoded, geo, int(geo == 0)))
            hair_id += 1
            for eye, color in itertools.product(range(c["Eye Color"]), range(c["Hair Color"])):
                add(3, encoded, color + c["Hair Color"] * eye, [material(prof, "Hair Color", color, 10)])
        for eye_style, modification in itertools.product(range(c["Eye Style"]), range(c["Modification"])):
            encoded = modification + c["Modification"] * eye_style
            facial.append(struct.pack("<8I", 47, gender, encoded, 0, 0, 0, 0, 0))
            for eye, color in itertools.product(range(c["Eye Color"]), range(c["Hair Color"])):
                add(2, encoded, color + c["Hair Color"] * eye, [])
    result["CharSections"] = replace_rows(result["CharSections"], "CharSections", rows, pool)
    result["CharHairGeosets"] = replace_rows(result["CharHairGeosets"], "CharHairGeosets", hair)
    result["CharacterFacialHairStyles"] = replace_rows(
        result["CharacterFacialHairStyles"], "CharacterFacialHairStyles", facial)
    barber = p.RawWdbc(result["BarberShopStyle"])
    bp, br, row_id = bytearray(barber.strings), [], 452000
    for gender, sex in enumerate(("male", "female")):
        totals = {}
        for offset, count, factor in descriptors(report["sexes"][sex]["profile"]):
            totals[offset] = max(totals.get(offset, 0), count * factor)
        for kind, count in ((0, totals[0x34]), (2, totals[0x30]), (3, totals[0x28])):
            donors = [r for r in barber.records if p._value(r, 148) == 7 and p._value(r, 152) == gender
                      and p._value(r, 4) == kind]
            donor = donors[0] if donors else next(r for r in barber.records if p._value(r, 4) == kind)
            for index in range(count):
                row = p._clone_strings("BarberShopStyle", barber, donor, bp)
                for offset, value in ((0, row_id), (148, 47), (152, gender), (156, index)):
                    row = p._replace(row, offset, 4, value)
                br.append(row)
                row_id += 1
    result["BarberShopStyle"] = replace_rows(result["BarberShopStyle"], "BarberShopStyle", br, bp)
    return result


def gui(text):
    text = text.replace('local EA_LEFT = CharacterCustomization_Left;',
        'local EA_MECH_LABELS = {' + ','.join(json.dumps(s) for s in LABELS)
        + '};\nlocal EA_LEFT = CharacterCustomization_Left;')
    text = text.replace('return CharacterCreate.selectedRaceID == 52 or CharacterCreate.selectedRaceID == 53;',
                        'return CharacterCreate.selectedRaceID == 47 or CharacterCreate.selectedRaceID == 52 '
                        'or CharacterCreate.selectedRaceID == 53;')
    text = text.replace('for i=6,10 do', 'for i=6,12 do')
    text = text.replace('for i=1,10 do', 'for i=1,12 do')
    text = text.replace('EA_LABELS[i]..(count',
                        '(CharacterCreate.selectedRaceID == 47 and EA_MECH_LABELS[i] '
                        'or EA_LABELS[i] or "")..(count')
    text = text.replace('220-visibleRow*38',
                        'CharacterCreate.selectedRaceID == 47 and 240-visibleRow*34 or 220-visibleRow*38')
    if '["MECHAGNOME_MALE"]' not in text:
        text = text.replace('RACE_ICON_TEXTURES = {', 'RACE_ICON_TEXTURES = {\n' + '\n'.join(
            f'    ["MECHAGNOME_{sex.upper()}"] = "Interface\\\\Glues\\\\CharacterCreate\\\\'
            f'UI-CharacterCreate-Mechagnome{sex}",'
            for sex in ("Male", "Female")))
    text = text.replace('["MAGHAR"] = "ORC",', '["MAGHAR"] = "ORC",\n        ["MECHAGNOME"] = "GNOME",')
    return text


def glue(client):
    from luaparser import ast
    storm = p.Storm(p.DLL_DEFAULT)
    result = {}
    for name in ("CharacterCreate.lua", "CharacterInfo.lua", "GlueStrings.lua", "GlueParent.lua",
                 "ECS_Schema.lua", "ECS_Integrate.lua"):
        text = p._read_archive_entry(storm, client / p.LOCALE_ARCHIVE_REL, p.GLUE_ROOT + name).decode()
        if name == "CharacterCreate.lua":
            text = gui(text)
        elif name == "CharacterInfo.lua":
            text = text.replace('local EXACT_RACE_DATA = {', 'local EXACT_RACE_DATA = {\n'
                '    [47] = { glueString = "MECHAGNOME", name = "Mechagnome", '
                'faction = "Alliance", fileString = "Mechagnome" },')
            text += ('\nRaceInfoByFileString.MECHAGNOME = {Name="Mechagnome", '
                     'Description="The clever mechagnomes balance flesh with technology, '
                     'making them innovative allies of the Alliance.", RacialTraits={}};\n')
        elif name == "GlueStrings.lua":
            text += ('\nMECHAGNOME = "Mechagnome";\nMECHAGNOME_MALE = MECHAGNOME;\n'
                     'MECHAGNOME_FEMALE = MECHAGNOME;\nRACE_INFO_MECHAGNOME = '
                     '"The clever mechagnomes balance flesh with technology, '
                     'making them innovative allies of the Alliance.";\n'
                     'RACE_INFO_MECHAGNOME_FEMALE = RACE_INFO_MECHAGNOME;\n')
        elif name == "GlueParent.lua":
            text = text.replace('["HIGHELF"] = true,', '["HIGHELF"] = true,\n        ["MECHAGNOME"] = true,')
        elif name == "ECS_Schema.lua":
            text = text.replace('S.RaceOverride = {',
                'S.RaceOverride = {\n    [47] = { name = "Mechagnome", faction = 1, artKey = "Mechagnome" },')
            text = text.replace('S.PortraitArtKeys = {', 'S.PortraitArtKeys = {\n    Mechagnome = true,')
        else:
            text = text.replace('(race == 45 or race == 52 or race == 53)',
                                '(race == 45 or race == 47 or race == 52 or race == 53)')
        ast.parse(text)
        result[p.GLUE_ROOT + name] = text.encode()
    return result


def build(client=p.CLIENT_DEFAULT):
    report = p.load_json(ROOT / "integration/preparation.json")
    STAGE.mkdir(parents=True, exist_ok=True)
    (STAGE / "EsteriaAppearanceMaterials.bin").write_bytes(material_catalog(report))
    t = tables(client, report)
    storm = p.Storm(p.DLL_DEFAULT)
    template = p._read_archive_entry(storm, client / p.LOCALE_ARCHIVE_REL, portraits.ICON_TEMPLATE_ENTRY)
    ring = portraits.ring_layer(portraits.decode_client_blp(
        p._read_archive_entry(storm, client / p.LOCALE_ARCHIVE_REL, portraits.RING_ENTRY)))
    assets = {"\\".join(f.relative_to(SOURCE).parts): f.read_bytes() for f in SOURCE.rglob("*") if f.is_file()}
    assets.update({"\\".join(f.relative_to(ART).parts): f.read_bytes() for f in ART.rglob("*") if f.is_file()})
    for sex in ("Male", "Female"):
        picture = portraits.DEFAULT_SOURCE / "Alliance" / f"Charactercreate-races_mechagnome-{sex.lower()}.png"
        art = portraits.portrait_bytes(picture, portraits.circular_mask())
        plain = p.encode_portrait(art, template)
        bordered = p.encode_portrait(portraits.compose_race_icon(art, ring), template)
        assets[f"Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-Mechagnome{sex}.blp"] = bordered
        assets[f"Interface\\CharacterFrame\\TemporaryPortrait-{sex}-Mechagnome.blp"] = plain
        assets[f"Interface\\Glues\\CharacterSelect\\ECS-Portrait-Mechagnome{sex}.blp"] = plain
    dbcs = {p.DBC_ROOT + name + ".dbc": data for name, data in t.items()}
    g = glue(client)
    relatives = (p.GLOBAL_ARCHIVE_REL, p.LOCALE_ARCHIVE_REL, p.ASSET_ARCHIVE_REL)
    for rel in relatives:
        destination = STAGE / "pack" / rel
        destination.parent.mkdir(parents=True, exist_ok=True)
        print("COMPACT", rel, flush=True)
        p.rebuild_archive_streaming(storm, client / rel, destination)
        updates = assets if rel == p.ASSET_ARCHIVE_REL else {**assets, **dbcs, **g}
        storm.replace_archive_entries(destination, updates)
    server = STAGE / "server-dbc"
    server.mkdir(exist_ok=True)
    for name in p.SERVER_DBC_TABLES:
        (server / (name + ".dbc")).write_bytes(t[name])
    (STAGE / "EsteriaAppearance.bin").write_bytes(
        appearance_catalog(report, (client / "EsteriaAppearance.bin").read_bytes()))
    (STAGE / "EsteriaAppearanceGeometry.bin").write_bytes(
        geometry_catalog(report, (client / "EsteriaAppearanceGeometry.bin").read_bytes()))
    result = {"source_hashes": {str(r): p.sha256(client / r) for r in relatives},
              "stage_hashes": {str(r): p.sha256(STAGE / "pack" / r) for r in relatives},
              "companion_hashes": {name: p.sha256(STAGE / name) for name in
                  ("EsteriaAppearance.dll", "EsteriaAppearance.bin", "EsteriaAppearanceGeometry.bin",
                   "EsteriaAppearanceMaterials.bin")},
              "tables": list(t), "assets": len(assets),
              "options": {s: counts(r["profile"]) for s, r in report["sexes"].items()}}
    (STAGE / "build-report.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


def validate(client=p.CLIENT_DEFAULT):
    from wotlkconv.m2 import parse_m2

    storm = p.Storm(p.DLL_DEFAULT)
    report = p.load_json(STAGE / "build-report.json")
    for name in report["tables"]:
        key = p.DBC_ROOT + name + ".dbc"
        a = p._read_archive_entry(storm, STAGE / "pack" / p.GLOBAL_ARCHIVE_REL, key)
        b = p._read_archive_entry(storm, STAGE / "pack" / p.LOCALE_ARCHIVE_REL, key)
        if a != b:
            raise ValueError(f"Global/locale mismatch: {name}")
        table = p.RawWdbc(a)
        if name not in ("CharBaseInfo", "CharacterFacialHairStyles"):
            ids = [p._value(row, 0) for row in table.records]
            if len(ids) != len(set(ids)):
                raise ValueError(f"Duplicate {name} ID")
        if name in p.SERVER_DBC_TABLES and a != (STAGE / "server-dbc" / (name + ".dbc")).read_bytes():
            raise ValueError(f"Server mismatch: {name}")
    sections = p.RawWdbc(p._read_archive_entry(storm, STAGE / "pack" / p.GLOBAL_ARCHIVE_REL,
                                              p.DBC_ROOT + "CharSections.dbc"))
    handle = storm.open_archive(STAGE / "pack" / p.ASSET_ARCHIVE_REL)
    try:
        paths = {p._string(sections.strings, p._value(r, field * 4)).decode()
                 for r in sections.records if p._value(r, 4) == 47 for field in (4, 5, 6)} - {""}
        for key in paths:
            p.Blp.parse(storm.read(handle, key), key)
        preparation = p.load_json(ROOT / "integration/preparation.json")
        for sex, row in preparation["sexes"].items():
            key = row["model_path"]
            data = storm.read(handle, key)
            if data != ART.joinpath(*p.PureWindowsPath(key).parts).read_bytes():
                raise ValueError("Staged model differs from prepared model: " + sex)
            model = parse_m2(data)
            skin = parse_skin(storm.read(handle, key[:-3] + "00.skin"))
            if model.vertex_count > 65535 or len(skin.vertices) > 65535:
                raise ValueError("Mechagnome vertex budget exceeded")
            for texture in model.textures:
                if texture["type"] in (11, 15):
                    raise ValueError("Unsupported modern texture slot")
                if texture["type"] == 0 and texture["filename"]:
                    storm.read(handle, texture["filename"])
            for mesh in skin.submeshes:
                start = v.u16(mesh, 8) | v.u16(mesh, 2) << 16
                if start + v.u16(mesh, 10) > len(skin.indices) or v.u16(mesh, 12) > 75:
                    raise ValueError("Invalid mesh indices/bone palette")
            for animation in (4, 5, 13, 16, 26, 38, 69, 96, 97):
                index = model.sequence_lookups[animation]
                if index == 65535 or model.sequences[index]["id"] != animation:
                    raise ValueError(f"Missing or mismatched {sex} animation lookup {animation}")
            for index, sequence in enumerate(model.sequences):
                if not sequence["flags"] & (0x20 | 0x40):
                    stem = key[:-3]
                    entry = f"{stem}{sequence['id']:04d}-{sequence['variation_index']:02d}.anim"
                    if any(index < len(b["rotation"].timestamp_spans)
                           and b["rotation"].timestamp_spans[index][0] for b in model.bones):
                        storm.read(handle, entry)
        for sex in ("Male", "Female"):
            for root, stem in (("Glues\\CharacterCreate", "UI-CharacterCreate-Mechagnome"),
                               ("Glues\\CharacterSelect", "ECS-Portrait-Mechagnome")):
                p.validate_portrait(storm.read(handle, f"Interface\\{root}\\{stem}{sex}.blp"), Path(stem))
    finally:
        storm.dll.SFileCloseArchive(handle)
    # Untouched Skyborne native profiles must remain byte-identical in the combined catalogs.
    current = (client / "EsteriaAppearance.bin").read_bytes()
    combined = (STAGE / "EsteriaAppearance.bin").read_bytes()
    if combined[12:len(current)] != current[12:]:
        raise ValueError("Existing appearance profiles changed")
    return {"race": 47, "appearance_paths": len(paths), "options": report["options"], "verified": True}


def sql(query, database="acore_world"):
    command = ["docker", "exec", "-i", "ac-database", "sh", "-c",
               'MYSQL_PWD="$MYSQL_ROOT_PASSWORD" mysql -uroot --batch --skip-column-names ' + database]
    return subprocess.run(command, input=query, capture_output=True, text=True, check=True).stdout


def install(client=p.CLIENT_DEFAULT, rendering_only=False):
    validate(client)
    processes = subprocess.check_output(["tasklist", "/FO", "CSV", "/NH"], text=True).lower()
    if "wow.exe" in processes or "eclipse.exe" in processes:
        raise RuntimeError("WoW/Eclipse must be closed before replacing their archives/helper")
    report = p.load_json(STAGE / "build-report.json")
    prior = p.load_json(native.STAGE / "last-install.json")
    if p.sha256(client / "Wow.exe") != prior["installed_hashes"]["Wow.exe"]:
        raise ValueError("Executable differs from the verified native installation")
    relatives = (p.GLOBAL_ARCHIVE_REL, p.LOCALE_ARCHIVE_REL, p.ASSET_ARCHIVE_REL)
    files = {rel: STAGE / "pack" / rel for rel in relatives}
    files.update({Path(name): STAGE / name for name in
                  ("EsteriaAppearance.dll", "EsteriaAppearance.bin", "EsteriaAppearanceGeometry.bin",
                   "EsteriaAppearanceMaterials.bin")})
    for rel in relatives:
        if p.sha256(client / rel) != report["source_hashes"][str(rel)]:
            raise ValueError("Stale archive stage: " + str(rel))
        if p.sha256(files[rel]) != report["stage_hashes"][str(rel)]:
            raise ValueError("Archive stage hash changed: " + str(rel))
    for name, digest in report["companion_hashes"].items():
        if p.sha256(STAGE / name) != digest:
            raise ValueError("Native companion stage changed: " + name)
    if rendering_only:
        if p.sha256(client / "EsteriaAppearance.bin") != p.sha256(STAGE / "EsteriaAppearance.bin"):
            raise ValueError("Rendering refresh cannot change the saved appearance codec")
    elif sql("SELECT COUNT(*) FROM characters WHERE race=47;", "acore_characters").strip() != "0":
        raise ValueError("Existing Race47 characters require an explicit appearance migration")
    backup = Path("C:/Users/Zach/.codex/backups") / ("mechagnome-" + datetime.now().strftime("%Y%m%d-%H%M%S"))
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
                raise RuntimeError("Backup hash mismatch: " + str(rel))
    (backup / "server-dbc").mkdir()
    for name in p.SERVER_DBC_TABLES:
        live = p.SERVER_DBC_ROOT / (name + ".dbc")
        shutil.copy2(live, backup / "server-dbc" / live.name)
        if p.sha256(live) != p.sha256(backup / "server-dbc" / live.name):
            raise RuntimeError("Server backup mismatch: " + name)
    db_tables = ("playercreateinfo", "player_race_stats", "playercreateinfo_item", "playercreateinfo_action",
                 "player_totem_model", "custom_race_start_spell", "custom_race_start_skill")
    rollback = []
    if not rendering_only:
        for name in db_tables:
            field = "RaceID" if name == "player_totem_model" else "race"
            existing = sql(f"SELECT COUNT(*) FROM `{name}` WHERE `{field}`=47;")
            if existing.strip() != "0":
                raise ValueError("Existing exact-race startup rows require an explicit migration: " + name)
            rollback.append(f"DELETE FROM `{name}` WHERE `{field}`=47;")
    (backup / "rollback.sql").write_text("START TRANSACTION;\n" + "\n".join(rollback) + "\nCOMMIT;\n", encoding="utf-8")
    migration = p.ROOT / "data/sql/updates/pending_db_world/rev_20261001005000000.sql"
    if not rendering_only:
        sql("START TRANSACTION;\n" + migration.read_text(encoding="utf-8") + "\nCOMMIT;")
    try:
        for rel, staged in files.items():
            target = client / rel
            temporary = target.with_suffix(target.suffix + ".mechagnome-next")
            shutil.copy2(staged, temporary)
            if p.sha256(temporary) != p.sha256(staged):
                raise RuntimeError("Install copy mismatch: " + str(rel))
            os.replace(temporary, target)
            print("INSTALLED", rel, flush=True)
        for name in p.SERVER_DBC_TABLES:
            staged = STAGE / "server-dbc" / (name + ".dbc")
            target = p.SERVER_DBC_ROOT / staged.name
            shutil.copy2(staged, target)
            if p.sha256(staged) != p.sha256(target):
                raise RuntimeError("Server install mismatch: " + name)
    except Exception:
        for rel in files:
            if (backup / rel).exists():
                shutil.copy2(backup / rel, client / rel)
            elif (client / rel).exists():
                (client / rel).unlink()
        for name in p.SERVER_DBC_TABLES:
            shutil.copy2(backup / "server-dbc" / (name + ".dbc"), p.SERVER_DBC_ROOT / (name + ".dbc"))
        sql((backup / "rollback.sql").read_text(encoding="utf-8"))
        raise
    report.update(backup=str(backup), before_hashes=before,
                  installed_hashes={str(rel): p.sha256(client / rel) for rel in files})
    (backup / "install-report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    (STAGE / "last-install.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    prior["installed_hashes"].update(report["installed_hashes"])
    prior["latest_mechagnome_backup"] = str(backup)
    (native.STAGE / "last-install.json").write_text(json.dumps(prior, indent=2) + "\n", encoding="utf-8")
    return report


def refresh(client=p.CLIENT_DEFAULT):
    """Update only this installed port's rendering art/helper, preserving world data."""
    previous = p.load_json(STAGE / "last-install.json")
    for name, digest in previous["installed_hashes"].items():
        if p.sha256(client / name) != digest:
            raise ValueError("Installed Mechagnome files changed before rendering refresh: " + name)
    report = p.load_json(STAGE / "build-report.json")
    storm = p.Storm(p.DLL_DEFAULT)
    assets = {"\\".join(path.relative_to(ART).parts): path.read_bytes() for path in ART.rglob("*")
              if path.is_file() and path.suffix.lower() in (".m2", ".skin", ".anim")}
    for rel in (p.GLOBAL_ARCHIVE_REL, p.LOCALE_ARCHIVE_REL, p.ASSET_ARCHIVE_REL):
        stage = STAGE / "pack" / rel
        report["source_hashes"][str(rel)] = p.sha256(client / rel)
        if p.sha256(stage) != report["stage_hashes"][str(rel)]:
            raise ValueError("Rendering refresh archive differs from the validated stage")
        storm.replace_archive_entries(stage, assets)
        for name, data in assets.items():
            if p._read_archive_entry(storm, stage, name) != data:
                raise ValueError("Rendering refresh readback mismatch: " + name)
        report["stage_hashes"][str(rel)] = p.sha256(stage)
    report["companion_hashes"] = {name: p.sha256(STAGE / name) for name in report["companion_hashes"]}
    (STAGE / "build-report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return install(client, rendering_only=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("prepare", "build", "validate", "install", "refresh"))
    args = parser.parse_args()
    result = {"prepare": prepare, "build": build, "validate": validate,
              "install": install, "refresh": refresh}[args.command]()
    print(json.dumps({"sexes": {s: counts(r["profile"]) for s, r in result["sexes"].items()}}
                     if args.command == "prepare" else result, indent=2))
