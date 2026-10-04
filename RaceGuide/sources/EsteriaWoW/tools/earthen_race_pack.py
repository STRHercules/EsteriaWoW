"""Reproduce Earthen 48/49 from the pinned Retail graph and current Esteria merge base."""

import argparse
import hashlib
import itertools
import json
import os
import shutil
import struct
import subprocess
import sys
import urllib.request
from datetime import datetime
from pathlib import Path

from PIL import Image
from wotlkconv.blp import convert_blp
from wotlkconv.casc import CascStorage, KeyRing, blte
from wotlkconv.casc.cdn import CdnSource, blte_header_md5
from wotlkconv.casc.config import config_path, parse_config
from wotlkconv.m2 import parse_m2, parse_skin, write_md20
from wotlkconv.m2.skin import write_skin
from wotlkconv.options import Options

import highmountain_complete_tracks as tracks
import highmountain_integration as rendering
import highmountain_race_pack as h
import race_portrait_pack as portraits
import retroported_race_pack as p
import skyborne_visual_pack as v

ROOT = Path(r"G:\RetroPorterWork\earthen")
SOURCE = ROOT / "output/patch-root"
ART = ROOT / "integration/patch-root"
STAGE = Path(r"C:\Users\Zach\.codex\tmp\earthen")
PROJECT = h.PROJECT
CACHE = PROJECT / "sources/retail/races/earthen"
PREFIX = "custom\\earthen\\native"
RACES = (48, 49)
MODELS = {"male": 5548261, "female": 5548259}
LABELS = ("Skin Color", "Face", "Hair Style", "Hair Color", "Beard Style", "Gem Color", "Eye Color",
          "Eyesight", "Eyebrows", "Belt", "Right Shoulder", "Left Shoulder", "Torso", "Arms", "Legs", "Hands")
# Packet order: skin, face, hair style, hair color, facial hair, extension byte.
GROUPS = (("Skin Color", "Gem Color"), ("Face", "Eyesight", "Eyebrows"),
          ("Hair Style", "Right Shoulder", "Torso"), ("Hair Color", "Eye Color"),
          ("Beard Style", "Left Shoulder", "Legs"), ("Arms", "Hands", "Belt"))
LORE = ("Forged by the titans from living stone, the earthen have broken free of their ancient edicts. "
        "They venture beyond Khaz Algar with curiosity and resolve, choosing their own paths in Azeroth.")


def path(root, key):
    return root.joinpath(*p.PureWindowsPath(key).parts)


def save(target, value):
    h.save(target, value)


def audit(discovery=None):
    d = discovery or p.load_json(ROOT / "reports/discovery.json")
    if set(d["race_ids"]) != {84, 85} or {m["ID"] for m in d["models"]} != {195, 196}:
        raise ValueError("Earthen Retail identity changed")
    requirements = {r["ID"]: r for r in d["requirements"]}
    result = {"retail_race_ids": [84, 85], "target_race_ids": RACES, "sexes": {}, "omitted": []}
    for sex, model_id in (("male", 195), ("female", 196)):
        options = {o["Name_lang"]: o for o in d["options"] if o["ChrModelID"] == model_id}
        profile = {"options": [], "descriptors": [], "capacities": [], "requirements": []}
        for label in LABELS:
            option = options[label]
            choices = sorted((c for c in d["choices"] if c["ChrCustomizationOptionID"] == option["ID"]),
                             key=lambda c: (c["OrderIndex"], c["ID"]))
            kept = [c for c in choices if requirements.get(c["ChrCustomizationReqID"], {}).get("ReqType") == 3]
            if not kept:
                raise ValueError(f"No ordinary player choices for {sex}/{label}")
            profile["options"].append({"label": label, "id": option["ID"], "choices": [{**c,
                "elements": [e for e in d["elements"] if e["ChrCustomizationChoiceID"] == c["ID"]]} for c in kept]})
        for field, labels in enumerate(GROUPS):
            factor = 1
            for label in labels:
                count = len(profile["options"][LABELS.index(label)]["choices"])
                profile["descriptors"].append((LABELS.index(label), field, count, factor))
                factor *= count
            if factor > 256:
                raise ValueError(f"{sex} appearance byte {field} exceeds capacity: {factor}")
            profile["capacities"].append(factor)
        profile["descriptors"] = [tuple(row[1:]) for row in sorted(profile["descriptors"])]
        result["sexes"][sex] = profile
        kept_ids = {c["ID"] for o in profile["options"] for c in o["choices"]}
        result["omitted"].extend({"sex": sex, "option": o["Name_lang"], "choice": c["ID"],
            "requirement": c["ChrCustomizationReqID"]} for o in options.values() for c in d["choices"]
            if c["ChrCustomizationOptionID"] == o["ID"] and c["ID"] not in kept_ids)
    save(ROOT / "integration/customization-audit.json", result)
    return result


def acquire():
    """Only missing reachable textures, original player models and face BONE dependencies; no Retail writes."""
    from retroporter.config import DEFAULT
    sys.path.insert(0, str(PROJECT / "src"))
    from raceporter.config import load_project_config
    project = load_project_config(PROJECT)
    d = p.load_json(ROOT / "reports/discovery.json")
    a = audit(d)
    CACHE.mkdir(parents=True, exist_ok=True)
    STAGE.mkdir(parents=True, exist_ok=True)
    inventory = p.load_json(CACHE / "inventory.json") if (CACHE / "inventory.json").exists() else {}
    with_storage = CascStorage.open(DEFAULT.retail_root, product=project.retail_source.product,
                                   locale=project.retail_source.locale.lower(), keys=KeyRing.load(DEFAULT.keys))
    cdn = None
    try:
        storage = with_storage
        pin = {"version": storage.build.version, "build_key": storage.build.build_key,
               "cdn_key": storage.build.cdn_key, "mode": project.retail_source.mode}
        if (CACHE / "build.json").exists() and p.load_json(CACHE / "build.json") != pin:
            raise ValueError("Refusing to switch Earthen's pinned Retail build")
        save(CACHE / "build.json", pin)
        metadata = STAGE / "cdn-metadata"
        config = config_path(metadata / "Data", storage.build.cdn_key)
        if not config.exists():
            key = storage.build.cdn_key
            url = f"https://us.cdn.blizzard.com/{storage.build.cdn_path}/config/{key[:2]}/{key[2:4]}/{key}"
            raw = urllib.request.urlopen(url, timeout=30).read()
            if hashlib.md5(raw).hexdigest() != key:
                raise ValueError("Retail CDN config hash differs")
            config.parent.mkdir(parents=True, exist_ok=True)
            config.write_bytes(raw)
        cdn = CdnSource(metadata, storage.build, project.casc_cache_root / "earthen")
        cdn._indices = DEFAULT.retail_root / "Data/indices"
        values = parse_config(config.read_text())
        cdn._group = cdn._open(values.get("archive-group", [""])[0])
        cdn._loose = cdn._open(values.get("file-index", [""])[0])

        def https(url, offset, size):
            headers = {"Range": f"bytes={offset}-{offset + size - 1}"} if offset is not None else {}
            request = urllib.request.Request(url.replace("http://", "https://", 1), headers=headers)
            with urllib.request.urlopen(request, timeout=45) as response:
                if offset is not None and response.status != 206:
                    raise OSError("CDN ignored the requested byte range")
                return response.read(size + 1)

        cdn.fetch = https

        def read(file_id, extension):
            target = CACHE / f"{file_id}{extension}"
            ckey = storage.root.ckey_for(file_id)
            if not ckey:
                raise ValueError(f"Absent FileDataID in pinned build: {file_id}")
            if target.exists():
                raw = target.read_bytes()
            elif project.retail_source.mode == "local":
                raw = storage.read_file_id(file_id)
            else:
                ekey = storage.encoding.ekey_for(ckey)
                if not ekey:
                    raise ValueError(f"Absent encoding: {file_id}")
                if cdn.locate(ekey) is not None:
                    encoded = cdn.read(ekey, f"Earthen {file_id}")
                else:
                    key = ekey.hex()
                    url = f"https://us.cdn.blizzard.com/{storage.build.cdn_path}/data/{key[:2]}/{key[2:4]}/{key}"
                    encoded = urllib.request.urlopen(url, timeout=45).read(64 * 1024 * 1024 + 1)
                if len(encoded) > 64 * 1024 * 1024 or blte_header_md5(encoded) != ekey:
                    raise ValueError(f"Retail encoding hash/size differs: {file_id}")
                raw = blte.decode(encoded, storage.keys)
            if hashlib.md5(raw).digest() != ckey:
                raise ValueError(f"Retail content key differs: {file_id}")
            if not target.exists():
                target.write_bytes(raw)
            inventory[str(file_id)] = {"file": target.name, "content_key": ckey.hex(),
                                        "sha256": p.sha256(target), "bytes": len(raw)}
            save(CACHE / "inventory.json", inventory)
            return raw

        selected = [e for prof in a["sexes"].values() for o in prof["options"] for c in o["choices"]
                    for e in c["elements"]]
        material_ids = {e["ChrCustomizationMaterialID"] for e in selected}
        material_resources = {m["MaterialResourcesID"] for m in d["linked"]["ChrCustomizationMaterial"]
                              if m["ID"] in material_ids}
        texture_ids = {r["FileDataID"] for r in d["texture_files"] if r["MaterialResourcesID"] in material_resources}
        for asset in d["file_assets"]:
            key = "custom\\earthen\\" + asset["path"]
            if asset["file_data_id"] in texture_ids and not path(SOURCE, key).exists() and not path(ART, key).exists():
                raw = read(asset["file_data_id"], ".blp")
                converted, result = convert_blp(raw, key, Options())
                if not result.ok:
                    raise ValueError(f"Texture conversion failed: {key}")
                target = path(ART, key)
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(converted)
                print("Recovered", asset["file_data_id"], flush=True)
        bone_ids = {e["ChrCustomizationBoneSetID"] for e in selected}
        for bone in d["linked"]["ChrCustomizationBoneSet"]:
            if bone["ID"] in bone_ids:
                read(bone["BoneFileDataID"], ".bone")
        for file_id in MODELS.values():
            read(file_id, ".m2")
        model_inputs = [(MODELS[sex], f"custom\\earthen\\character\\earthendwarf\\earthendwarf{sex}.m2")
                        for sex in ("male", "female")]
        model_inputs.extend((file_id, f"custom\\earthen\\item\\objectcomponents\\collections\\earthenextras_ed_{sex}.m2")
                            for file_id, sex in ((5792408, "m"), (5792407, "f")))
        for file_id, key in model_inputs:
            raw_model = parse_m2(read(file_id, ".m2"))
            converted = parse_m2(path(SOURCE, key).read_bytes())
            for texture, txid in zip(converted.textures, raw_model.texture_file_ids, strict=True):
                key = texture["filename"]
                if texture["type"] != 0 or not key or path(ART, key).exists() or path(SOURCE, key).exists():
                    continue
                if not txid:
                    raise ValueError("Hard material has no source TXID: " + key)
                data, conversion = convert_blp(read(txid, ".blp"), key, Options())
                if not conversion.ok:
                    raise ValueError("Hard material conversion failed: " + key)
                target = path(ART, key)
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data)
                print("Recovered model TXID", txid, flush=True)
        save(ROOT / "integration/source-acquisition.json", {"pin": pin, "inventory": inventory})
    finally:
        if cdn:
            cdn.close()
        with_storage.close()
    return {"source": pin, "cached_dependencies": len(inventory)}


def prepare_portraits():
    storm = p.Storm(p.DLL_DEFAULT)
    template = p._read_archive_entry(storm, p.CLIENT_DEFAULT / p.LOCALE_ARCHIVE_REL, portraits.ICON_TEMPLATE_ENTRY)
    ring = portraits.ring_layer(portraits.decode_client_blp(
        p._read_archive_entry(storm, p.CLIENT_DEFAULT / p.LOCALE_ARCHIVE_REL, portraits.RING_ENTRY)))
    report = {}
    STAGE.mkdir(parents=True, exist_ok=True)
    for faction in ("Alliance", "Horde"):
        token = "Earthen" + ("Horde" if faction == "Horde" else "")
        for sex in ("Male", "Female"):
            picture = portraits.DEFAULT_SOURCE / faction / f"Charactercreate-races_earthen-{sex.lower()}_{faction}.png"
            art = portraits.portrait_bytes(picture, portraits.circular_mask())
            plain = p.encode_portrait(art, template)
            bordered = p.encode_portrait(portraits.compose_race_icon(art, ring), template)
            for root, stem, data in (("Glues\\CharacterCreate", f"UI-CharacterCreate-{token}{sex}", bordered),
                ("Glues\\CharacterSelect", f"ECS-Portrait-{token}{sex}", plain),
                ("CharacterFrame", f"TemporaryPortrait-{sex}-{token}", plain)):
                key = f"Interface\\{root}\\{stem}.blp"
                target = path(ART, key)
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data)
                p.validate_portrait(data, target)
                report[key] = p.sha256(target)
            portraits.compose_race_icon(art, ring).save(STAGE / f"portrait-{faction.lower()}-{sex.lower()}.png")
    save(ROOT / "integration/portraits.json", report)
    return report


def generate_header():
    """Use the existing constexpr validator/descriptor format unchanged."""
    import highmountain_appearance as codec
    original_codec, original_h = codec.codec, codec.h
    from types import SimpleNamespace
    # Generate in an isolated directory, then give the generated namespace its own identity.
    output = STAGE / "header"
    (output / "src/server/shared").mkdir(parents=True, exist_ok=True)
    try:
        codec.codec = lambda: audit()["sexes"]
        codec.h = SimpleNamespace(p=SimpleNamespace(ROOT=output), ROOT=ROOT, save=save)
        codec.generate()
    finally:
        codec.codec, codec.h = original_codec, original_h
    text = (output / "src/server/shared/HighmountainAppearance.h").read_text()
    text = text.replace("Highmountain", "Earthen").replace("HIGHMOUNTAIN", "EARTHEN")
    text = text.replace("tools/highmountain_appearance.py", "tools/earthen_race_pack.py")
    (p.ROOT / "src/server/shared/EarthenAppearance.h").write_text(text, encoding="utf-8", newline="\n")


def emit(key, art, compositor=False):
    bitmap = p.BlpImage(art.width, art.height, bytearray(art.tobytes()))
    if compositor:
        data = rendering.paletted_compositor(bitmap)
    else:
        levels = bitmap.mip_chain()
        payloads = [Image.frombytes("RGBA", (l.width, l.height), bytes(l.data)).tobytes("raw", "BGRA") for l in levels]
        data = p.Blp.from_images(levels, compression=3, alpha_type=8, alpha_size=8, payloads=payloads).serialize()
    target = path(ART, key)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    return key


def rebuild_sequence_lookup(model):
    model.sequence_lookups = [65535] * (max(s["id"] for s in model.sequences) + 1)
    for index, sequence in enumerate(model.sequences):
        if sequence["variation_index"] == 0:
            model.sequence_lookups[sequence["id"]] = index


def share_material_defaults(model):
    for item in (*model.colors, *model.texture_weights, *model.texture_transforms):
        for track in item.values():
            if hasattr(track, "values") and track.global_sequence < 0 and track.timestamps == [[0]]:
                if len(track.values) == 1 and len(track.values[0]) == 1:
                    track.global_sequence = 0
                    track.external.clear()


def prepare():
    from wotlkconv.m2.split import _rebuild_skin
    from wotlkconv.m2.downgrade import downgrade_cameras
    from wotlkconv.report import FileResult
    d = p.load_json(ROOT / "reports/discovery.json")
    profiles = audit(d)["sexes"]
    materials = {r["ID"]: r for r in d["linked"]["ChrCustomizationMaterial"]}
    textures = {r["MaterialResourcesID"]: r["FileDataID"] for r in d["texture_files"]}
    files = {r["file_data_id"]: "custom\\earthen\\" + r["path"] for r in d["file_assets"]}
    geosets = {r["ID"]: r for r in d["linked"]["ChrCustomizationGeoset"]}
    skinned = {r["ID"]: r for r in d["linked"]["ChrCustomizationSkinnedModel"]}
    records, report = [], {}

    def material(choice, target, related=0):
        hits = [e for e in d["elements"] if e["ChrCustomizationChoiceID"] == choice
                and e["RelatedChrCustomizationChoiceID"] == related
                and materials.get(e["ChrCustomizationMaterialID"], {}).get("ChrModelTextureTargetID") == target]
        if target == 44 and len(hits) > 1:
            # Female Left also names the hard-bound lens sprite. The iris overlay uses the shared
            # Human eyesight atlas; the lens retains its separate source TXID/material on group51.
            hits = [e for e in hits if "\\human\\" in
                    files[textures[materials[e["ChrCustomizationMaterialID"]]["MaterialResourcesID"]]]]
        if len(hits) != 1:
            raise ValueError(f"Ambiguous/missing Earthen material {choice}/{target}/{related}")
        return files[textures[materials[hits[0]["ChrCustomizationMaterialID"]]["MaterialResourcesID"]]]

    def image(key):
        source = path(ART, key) if path(ART, key).exists() else path(SOURCE, key)
        data = p.Blp.parse(source.read_bytes()).decode_level(0)
        return Image.frombytes("RGBA", (data.width, data.height), bytes(data.data))

    def record(gender, kind, target, value, selectors=(), key=""):
        if len(selectors) > 3:
            raise ValueError("Selection capacity exceeded")
        packed = [i | j << 16 for i, j in selectors]
        records.append(struct.pack("<7I", gender, kind, target, value,
                       *(packed + [0xffffffff] * (3 - len(packed)))) + key.encode().ljust(128, b"\0"))

    for gender, sex in enumerate(("male", "female")):
        prof = profiles[sex]
        opts = {o["label"]: o for o in prof["options"]}
        indices = {c["ID"]: (i, j) for i, o in enumerate(prof["options"]) for j, c in enumerate(o["choices"])}
        root = f"{PREFIX}\\{sex}"
        sections = {}
        for skin, choice in enumerate(opts["Skin Color"]["choices"]):
            body = image(material(choice["ID"], 1))
            sections[str(skin)] = {"body": emit(f"{root}\\body{skin}.blp", body.crop((0, 0, 512, 512)), True),
                                  "faces": []}
            for face, face_choice in enumerate(opts["Face"]["choices"]):
                sheet = image(material(face_choice["ID"], 4, choice["ID"])).resize((256, 192), Image.Resampling.LANCZOS)
                lower = emit(f"{root}\\facelower{face}_{skin}.blp", sheet.crop((0, 64, 256, 192)), True)
                upper = emit(f"{root}\\faceupper{face}_{skin}.blp", sheet.crop((0, 0, 256, 64)), True)
                sections[str(skin)]["faces"].append((lower, upper))
        for label, target, slot in (("Hair Color", 10, 6), ("Gem Color", 16, 9)):
            for choice in opts[label]["choices"]:
                record(gender, 1, slot, 0, [indices[choice["ID"]]], material(choice["ID"], target))
        for eye, sight in itertools.product(range(len(opts["Eye Color"]["choices"])), range(4)):
            choice = opts["Eye Color"]["choices"][eye]
            key = material(choice["ID"], 25)
            if sight:
                art = image(key)
                overlay = image(material(opts["Eyesight"]["choices"][sight]["ID"], 44))
                art.alpha_composite(overlay.resize(art.size, Image.Resampling.LANCZOS))
                key = emit(f"{root}\\eyes{eye}_{sight}.blp", art)
            record(gender, 1, 5, 0, [indices[choice["ID"]], (7, sight)], key)
        # Collection hair shares source group0 with the always-visible body; give it an unused group.
        selected, used_groups = {}, set()
        for i, option in enumerate(prof["options"]):
            for j, choice in enumerate(option["choices"]):
                for element in choice["elements"]:
                    collection = skinned.get(element["ChrCustomizationSkinnedModelID"])
                    geo = collection or geosets.get(element["ChrCustomizationGeosetID"])
                    if not geo:
                        continue
                    group, value = geo["GeosetType"], geo["GeosetType"] * 100 + geo["GeosetID"]
                    if group == 0:
                        if not collection:
                            continue
                        group, value = 40, 4000 + geo["GeosetID"]
                    elif collection and group == 18:
                        # Custom belts use their own selector rather than the equipped waist geoset.
                        group, value = 41, 4100 + geo["GeosetID"]
                    used_groups.add(group)
                    record(gender, 0, group, value, [(i, j)])
                    if collection and geo["GeosetID"]:
                        selected[geo["GeosetType"] * 100 + geo["GeosetID"]] = value
        for group in used_groups:
            record(gender, 0, group, group * 100)
        # No NPC horns/FX. Baseline Earthen head and eyeball are unconditional, matching Highmountain.
        record(gender, 0, 20, 2001)  # Wrath does not select Retail's alternate foot meshes.
        record(gender, 0, 22, 2201)
        source_path = path(SOURCE, f"custom\\earthen\\character\\earthendwarf\\earthendwarf{sex}.m2")
        model = v.read_player_model(source_path)
        raw = parse_m2((CACHE / f"{MODELS[sex]}.m2").read_bytes())
        # Keep source event/material tracks inline; only bones need external ANIM extraction.
        model.events, model.texture_weights, model.texture_transforms = raw.events, raw.texture_weights, raw.texture_transforms
        downgrade_cameras(raw, FileResult(source=str(MODELS[sex]), kind="m2"))
        model.cameras = raw.cameras
        rebuild_sequence_lookup(model)
        for opacity in model.texture_weights:
            opacity["weight"].global_sequence = 0
            opacity["weight"].external.clear()
        tracks.embed(model, source_path.parent, source_path.stem)
        skin = parse_skin(source_path.with_name(source_path.stem + "00.skin").read_bytes())
        vertices = bytearray(model.vertices)
        transformed = set()
        for batch in skin.batches:
            slots = model.texture_combos[v.u16(batch, 16):v.u16(batch, 16) + v.u16(batch, 14)]
            if not slots or model.textures[slots[0]]["type"] != 1:
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
        for i, texture in enumerate(model.textures):
            original = raw.textures[i]["type"]
            if original == 19:
                texture.update(type=5, filename="")
            elif original >= 11:
                texture.update(type=0, filename=emit(f"{root}\\neutral.blp", Image.new("RGBA", (4, 4), "white")))
        eye_slot = next(i for i, t in enumerate(model.textures) if t["type"] == 5)
        eye_material = len(model.materials)
        model.materials.append({"flags": 4, "blending_mode": 0})
        for i, batch in enumerate(skin.batches):
            if v.u16(skin.submeshes[v.u16(batch, 4)], 0) != 3301:
                continue
            batch = bytearray(batch)
            for offset, value in ((0, 0), (10, eye_material), (14, 1), (16, len(model.texture_combos)), (18, 0)):
                v.patch16(batch, offset, value)
            model.texture_combos.append(eye_slot)
            model.texture_coord_combos[0] = 0
            skin.batches[i] = bytes(batch)
        for i, mesh in enumerate(skin.submeshes):
            if v.u16(mesh, 0) in (3201, 3202, 3301):
                mesh = bytearray(mesh)
                v.patch16(mesh, 0, 0)
                skin.submeshes[i] = bytes(mesh)
        # Trim NPC-only collection vertices before using the established bone/mesh merger.
        collection = path(SOURCE, f"custom\\earthen\\item\\objectcomponents\\collections\\earthenextras_ed_{sex[0]}.m2")
        extra = parse_m2(collection.read_bytes())
        extra_skin = parse_skin(collection.with_name(collection.stem + "00.skin").read_bytes())
        keep = [i for i, mesh in enumerate(extra_skin.submeshes) if v.u16(mesh, 0) in selected]
        used = sorted({extra_skin.vertices[k] for i in keep for k in range(v.u16(extra_skin.submeshes[i], 4),
                       v.u16(extra_skin.submeshes[i], 4) + v.u16(extra_skin.submeshes[i], 6))})
        extra_skin = _rebuild_skin(extra_skin, keep, {value: i for i, value in enumerate(used)})
        extra.vertices = b"".join(extra.vertices[i * 48:(i + 1) * 48] for i in used)
        extra.vertex_count = len(used)
        temporary = STAGE / sex / collection.name
        temporary.parent.mkdir(parents=True, exist_ok=True)
        temporary.write_bytes(write_md20(extra))
        temporary.with_name(temporary.stem + "00.skin").write_bytes(write_skin(extra_skin))
        collection_report = v.append_collection(model, skin, temporary, selected)
        share_material_defaults(model)
        model.replacable_texture_lookup = [65535] * 16
        for i, texture in enumerate(model.textures):
            if texture["type"]:
                model.replacable_texture_lookup[texture["type"]] = i
        # ponytail: ten baked morphs exceed the 65535 SKIN budget with all accessories; use a runtime
        # vertex morph implementation before enabling BONE overrides. Keep all sourced face textures now.
        face_report = {"face_textures": 10, "bone_morphs": False,
                       "limitation": "baked face variants plus accessories exceed Wrath SKIN uint16 capacity"}
        skin = v.compact_bone_palettes(model, skin)
        key = f"{root}\\earthendwarf{sex}.m2"
        target = path(ART, key)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(write_md20(model))
        target.with_name(target.stem + "00.skin").write_bytes(write_skin(skin))
        report[sex] = {"sections": sections, "model_path": key, "faces": face_report,
                       "collection": collection_report, "sequences": len(model.sequences), "events": len(model.events)}
        print(sex, face_report, flush=True)
    (STAGE / "EsteriaEarthen.bin").write_bytes(struct.pack("<3I", 0x314D4845, 1, len(records)) + b"".join(records))
    generate_header()
    save(ROOT / "integration/rendering.json", report)
    return {sex: {k: v for k, v in row.items() if k != "sections"} for sex, row in report.items()}


def tables():
    render = p.load_json(ROOT / "integration/rendering.json")
    allocation = p.load_json(p.ALLOCATION_PATH)
    manifest = p.load_manifest("earthen")
    storm = p.Storm(p.DLL_DEFAULT)
    names = ("ChrRaces", "CreatureModelData", "CreatureDisplayInfo", "CharSections", "CharHairGeosets",
             "CharacterFacialHairStyles", "BarberShopStyle", "CharBaseInfo", "CharStartOutfit", "NameGen", "Spell")
    result = {n: p._read_archive_entry(storm, p.CLIENT_DEFAULT / p.GLOBAL_ARCHIVE_REL, p.DBC_ROOT + n + ".dbc")
              for n in names}
    for name in ("CreatureModelData", "CreatureDisplayInfo"):
        result[name] = p._merge_model_table(name, result[name], manifest, allocation)
    result["ChrRaces"] = p._merge_chr_races(result["ChrRaces"], manifest, allocation)
    chr_races = p.RawWdbc(result["ChrRaces"])
    records = []
    for row in chr_races.records:
        race = p._value(row, 0)
        if race in RACES:
            for field, value in ((2, 3 if race == 48 else 2), (7, 7 if race == 48 else 1),
                                 (12, 0), (13, 0 if race == 48 else 1)):
                row = p._replace(row, field * 4, 4, value)
        records.append(row)
    result["ChrRaces"] = chr_races.build(records)
    result["CharBaseInfo"] = p._build_char_base_info(result["CharBaseInfo"], manifest)
    result["CharStartOutfit"] = p._build_char_start_outfit(result["CharStartOutfit"], manifest, allocation)
    result["NameGen"] = p._clone_namegen(result["NameGen"], manifest, allocation)
    for name in ("CharStartOutfit", "NameGen"):
        table = p.RawWdbc(result[name])
        layout = p.WDBC_LAYOUTS[name]
        donors = [r for r in table.records if p._value(r, layout.race_offset, layout.race_width) == 48]
        first, last = allocation["race_allocations"]["earthen"][name]
        next_id = max(p._value(r, 0) for r in donors) + 1
        if next_id + len(donors) > last + 1:
            raise ValueError(f"Earthen {name} allocation too small for both factions")
        used_ids = {p._value(r, 0) for r in table.records}
        rows = list(table.records)
        for donor in donors:
            if next_id in used_ids:
                raise ValueError(f"Earthen Horde {name} allocation collision: {next_id}")
            row = p._replace(donor, layout.race_offset, layout.race_width, 49)
            rows.append(p._replace(row, 0, 4, next_id))
            next_id += 1
        result[name] = table.build(rows)
    pool, sections, hair, facial = bytearray(p.RawWdbc(result["CharSections"]).strings), [], [], []
    next_id = allocation["race_allocations"]["earthen"]["CharSections"][0]
    d = p.load_json(ROOT / "reports/discovery.json")
    mat = {m["ID"]: m for m in d["linked"]["ChrCustomizationMaterial"]}
    tex = {t["MaterialResourcesID"]: t["FileDataID"] for t in d["texture_files"]}
    files = {a["file_data_id"]: "custom\\earthen\\" + a["path"] for a in d["file_assets"]}
    profiles = audit(d)["sexes"]
    for race in RACES:
        for gender, sex in enumerate(("male", "female")):
            def add(kind, style, color, paths=()):
                nonlocal next_id
                row = struct.pack("<10I", next_id, race, gender, kind, 0, 0, 0, 1 if kind == 1 else 17, style, color)
                for field, key in zip((4, 5, 6), paths):
                    row = p._set_string(row, field, pool, key or "")
                sections.append(row)
                next_id += 1
            for color, art in render[sex]["sections"].items():
                add(0, 0, int(color), (art["body"], ""))
                add(4, 0, int(color))
                for face, paths in enumerate(art["faces"]):
                    add(1, face, int(color), paths)
            add(2, 0, 0)
            for color, choice in enumerate(profiles[sex]["options"][3]["choices"]):
                elements = [e for e in choice["elements"] if e["ChrCustomizationMaterialID"]
                            and mat[e["ChrCustomizationMaterialID"]]["ChrModelTextureTargetID"] == 10]
                if len(elements) != 1:
                    raise ValueError("Ambiguous hair atlas")
                key = files[tex[mat[elements[0]["ChrCustomizationMaterialID"]]["MaterialResourcesID"]]]
                add(3, 0, color, (key,))
            hair.append(struct.pack("<6I", 450400 + len(hair), race, gender, 0, 0, 0))
            facial.append(struct.pack("<8I", race, gender, 0, 0, 0, 0, 0, 0))

    def replace(name, rows, pool=None):
        table = p.RawWdbc(result[name])
        layout = p.WDBC_LAYOUTS[name]
        kept = [r for r in table.records if p._value(r, layout.race_offset, layout.race_width) not in RACES]
        if name != "CharacterFacialHairStyles" and {p._value(r, 0) for r in kept} & {p._value(r, 0) for r in rows}:
            raise ValueError("Earthen allocation collision: " + name)
        result[name] = table.build(kept + rows, bytes(pool) if pool is not None else table.strings)

    if next_id > allocation["race_allocations"]["earthen"]["CharSections"][1] + 1:
        raise ValueError("Earthen sections allocation exceeded")
    replace("CharSections", sections, pool)
    replace("CharHairGeosets", hair)
    replace("CharacterFacialHairStyles", facial)
    barber = p.RawWdbc(result["BarberShopStyle"])
    bp, rows, next_id = bytearray(barber.strings), [], 453000
    for race in RACES:
        for gender, sex in enumerate(("male", "female")):
            for kind, field in ((0, 2), (2, 4), (3, 0)):
                donors = [r for r in barber.records if p._value(r, 148) == 3
                          and p._value(r, 152) == gender and p._value(r, 4) == kind]
                donor = donors[0] if donors else next(r for r in barber.records if p._value(r, 4) == kind)
                for index in range(profiles[sex]["capacities"][field]):
                    row = p._clone_strings("BarberShopStyle", barber, donor, bp)
                    for offset, value in ((0, next_id), (148, race), (152, gender), (156, index)):
                        row = p._replace(row, offset, 4, value)
                    rows.append(row)
                    next_id += 1
    replace("BarberShopStyle", rows, bp)
    return result


def glue():
    from luaparser import ast
    storm = p.Storm(p.DLL_DEFAULT)
    result = {}
    for name in ("CharacterCreate.lua", "CharacterInfo.lua", "GlueStrings.lua", "GlueParent.lua",
                 "ECS_Schema.lua", "ECS_Integrate.lua"):
        text = p._read_archive_entry(storm, p.CLIENT_DEFAULT / p.LOCALE_ARCHIVE_REL, p.GLUE_ROOT + name).decode()
        if name == "CharacterCreate.lua":
            text = text.replace('return CharacterCreate.selectedRaceID == 46 or ',
                'return CharacterCreate.selectedRaceID == 48 or CharacterCreate.selectedRaceID == 49 '
                'or CharacterCreate.selectedRaceID == 46 or ', 1)
            text = text.replace('CharacterCreate.selectedRaceID == 46 and ',
                '(CharacterCreate.selectedRaceID == 46 or CharacterCreate.selectedRaceID == 48 '
                'or CharacterCreate.selectedRaceID == 49) and ')
            text = text.replace('if CharacterCreate.selectedRaceID == 46 then ',
                'if CharacterCreate.selectedRaceID == 46 or CharacterCreate.selectedRaceID == 48 '
                'or CharacterCreate.selectedRaceID == 49 then ')
            text = text.replace('RACE_ICON_TEXTURES = {', 'RACE_ICON_TEXTURES = {\n' + '\n'.join(
                f'    ["{token.upper()}_{sex.upper()}"] = "Interface\\\\Glues\\\\CharacterCreate\\\\'
                f'UI-CharacterCreate-{token}{sex}",' for token in ("Earthen", "EarthenHorde")
                for sex in ("Male", "Female")), 1)
            text = text.replace('["MAGHAR"] = "ORC",',
                '["MAGHAR"] = "ORC",\n        ["EARTHEN"] = "DWARF",\n        ["EARTHENHORDE"] = "DWARF",', 1)
        elif name == "CharacterInfo.lua":
            text = text.replace('local EXACT_RACE_DATA = {', 'local EXACT_RACE_DATA = {\n'
                '    [48] = { glueString="EARTHEN", name="Earthen", faction="Alliance", fileString="Earthen" },\n'
                '    [49] = { glueString="EARTHENHORDE", name="Earthen", faction="Horde", fileString="EarthenHorde" },', 1)
            for token in ("EARTHEN", "EARTHENHORDE"):
                donor = "DWARF" if token == "EARTHEN" else "ORC"
                text += ('\nlocal earthenInfo = {};\n'
                    f'for key,value in pairs(RaceInfoByFileString.{donor} or {{}}) do earthenInfo[key]=value; end\n'
                    f'earthenInfo.Name="Earthen"; earthenInfo.Description={json.dumps(LORE)};\n'
                    f'RaceInfoByFileString.{token}=earthenInfo;\n')
        elif name == "GlueStrings.lua":
            for token in ("EARTHEN", "EARTHENHORDE"):
                text += (f'\n{token}="Earthen"; {token}_MALE={token}; {token}_FEMALE={token};\n'
                         f'RACE_INFO_{token}={json.dumps(LORE)}; RACE_INFO_{token}_FEMALE=RACE_INFO_{token};\n')
        elif name == "GlueParent.lua":
            text = text.replace('["HIGHELF"] = true,', '["HIGHELF"] = true,\n        ["EARTHEN"] = true,', 1)
            text = text.replace('["HIGHMOUNTAINTAUREN"] = true,',
                '["HIGHMOUNTAINTAUREN"] = true,\n        ["EARTHENHORDE"] = true,', 1)
        elif name == "ECS_Schema.lua":
            text = text.replace('S.RaceOverride = {', 'S.RaceOverride = {\n'
                '    [48] = { name="Earthen", faction=1, artKey="Earthen" },\n'
                '    [49] = { name="Earthen", faction=2, artKey="EarthenHorde" },', 1)
            text = text.replace('S.PortraitArtKeys = {', 'S.PortraitArtKeys = {\n    Earthen=true, EarthenHorde=true,', 1)
        else:
            text = text.replace('(race == 45 or race == 46 or race == 47 or race == 52 or race == 53)',
                '(race == 45 or race == 46 or race == 47 or race == 48 or race == 49 or race == 52 or race == 53)', 1)
        from earthen_touchup import patch_glue
        text = patch_glue(name, text)
        ast.parse(text)
        key = p.GLUE_ROOT + name
        target = path(ART, key)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8", newline="\n")
        result[key] = text.encode()
    return result


def stage():
    """Stage the data pack; native/server compilation is a separately authorized step."""
    t = tables()
    g = glue()
    prepare_portraits()
    # Close only the runtime graph. The full conversion includes NPC variants, backgrounds and ANIMs
    # already embedded in the runtime M2; packaging those exceeds the classic MPQ size boundary.
    keys = set(p.load_json(ROOT / "integration/portraits.json"))
    catalog = (STAGE / "EsteriaEarthen.bin").read_bytes()
    for offset in range(12, len(catalog), 156):
        if struct.unpack_from("<I", catalog, offset + 4)[0] == 1:
            keys.add(catalog[offset + 28:offset + 156].split(b"\0")[0].decode())
    sections = p.RawWdbc(t["CharSections"])
    keys.update(p._string(sections.strings, p._value(row, field * 4)).decode()
                for row in sections.records if p._value(row, 4) in RACES for field in (4, 5, 6))
    for sex in ("male", "female"):
        key = f"{PREFIX}\\{sex}\\earthendwarf{sex}.m2"
        keys.update((key, key[:-3] + "00.skin"))
        model = parse_m2(path(ART, key).read_bytes())
        keys.update(t["filename"] for t in model.textures if t["type"] == 0)
    assets = {}
    for key in keys - {""}:
        source = path(ART, key) if path(ART, key).is_file() else path(SOURCE, key)
        assets[key] = source.read_bytes()
    dbcs = {p.DBC_ROOT + n + ".dbc": data for n, data in t.items()}
    storm = p.Storm(p.DLL_DEFAULT)
    relatives = (p.GLOBAL_ARCHIVE_REL, p.LOCALE_ARCHIVE_REL, p.ASSET_ARCHIVE_REL)
    report = {"source_hashes": {}, "stage_hashes": {}, "tables": list(t), "assets": len(assets)}
    for rel in relatives:
        destination = STAGE / "pack" / rel
        destination.parent.mkdir(parents=True, exist_ok=True)
        report["source_hashes"][str(rel)] = p.sha256(p.CLIENT_DEFAULT / rel)
        shutil.copy2(p.CLIENT_DEFAULT / rel, destination)
        if p.sha256(destination) != report["source_hashes"][str(rel)]:
            raise ValueError("Earthen merge-base copy differs: " + str(rel))
        storm.replace_archive_entries(destination, {**assets, **dbcs, **g})
        if destination.stat().st_size >= 0x80000000:
            raise ValueError("Earthen archive exceeds the classic reader boundary")
        report["stage_hashes"][str(rel)] = p.sha256(destination)
        print("STAGED", rel, flush=True)
    server = STAGE / "server-dbc"
    server.mkdir(exist_ok=True)
    for name in p.SERVER_DBC_TABLES:
        (server / (name + ".dbc")).write_bytes(t[name])
    baseline = (p.CLIENT_DEFAULT / "EsteriaAppearanceGeometry.bin").read_bytes()
    magic, version, count = struct.unpack_from("<3I", baseline)
    extra = b""
    for sex in ("male", "female"):
        key = f"{PREFIX}\\{sex}\\earthendwarf{sex}.m2"
        skin = path(ART, key[:-3] + "00.skin").read_bytes()
        extra += key.encode().ljust(128, b"\0") + struct.pack("<I", len(skin)) + skin
    (STAGE / "EsteriaAppearanceGeometry.bin").write_bytes(
        struct.pack("<3I", magic, version, count + 2) + baseline[12:] + extra)
    for name in ("EsteriaAppearance.bin", "EsteriaAppearanceMaterials.bin", "EsteriaHighmountain.bin"):
        shutil.copy2(p.CLIENT_DEFAULT / name, STAGE / name)
    report["companion_hashes"] = {n: p.sha256(STAGE / n) for n in
        ("EsteriaAppearance.bin", "EsteriaAppearanceGeometry.bin", "EsteriaAppearanceMaterials.bin",
         "EsteriaHighmountain.bin", "EsteriaEarthen.bin")}
    report["status"] = "data_staged_native_and_worldserver_build_required"
    save(STAGE / "build-report.json", report)
    return report


def backup_install():
    import expanded_appearance_pack as native
    import mechagnome_race_pack as db
    report = p.load_json(STAGE / "build-report.json")
    if "wow.exe" in subprocess.check_output(["tasklist", "/FO", "CSV", "/NH"], text=True).lower():
        raise RuntimeError("Close WoW before installing its native helper and archives")
    if "eclipse.exe" in subprocess.check_output(["tasklist", "/FO", "CSV", "/NH"], text=True).lower():
        raise RuntimeError("Close Eclipse before replacing its archives")
    prior = p.load_json(native.STAGE / "last-install.json")
    for name in ("Wow.exe", "EsteriaAppearance.dll"):
        if p.sha256(p.CLIENT_DEFAULT / name) != prior["installed_hashes"][name]:
            raise ValueError("Live native file differs from its installation receipt: " + name)
    if db.sql("SELECT COUNT(*) FROM characters WHERE race IN (48,49);", "acore_characters").strip() != "0":
        raise ValueError("Existing Earthen characters require an explicit appearance migration")
    if not db.sql("SHOW COLUMNS FROM characters LIKE 'extraAppearance';", "acore_characters").strip():
        raise ValueError("The existing extended appearance schema is required")
    db_tables = ("playercreateinfo", "player_race_stats", "playercreateinfo_item", "playercreateinfo_action",
                 "player_totem_model", "custom_race_start_spell", "custom_race_start_skill")
    for table in db_tables:
        field = "RaceID" if table == "player_totem_model" else "race"
        if db.sql(f"SELECT COUNT(*) FROM `{table}` WHERE `{field}` IN (48,49);").strip() != "0":
            raise ValueError("Existing Earthen startup data: " + table)
    migration = p.ROOT / "data/sql/updates/pending_db_world/rev_20261001100000000.sql"
    if db.sql(f"SELECT COUNT(*) FROM updates WHERE name='{migration.name}';").strip() != "0":
        raise ValueError("Earthen migration receipt already exists")
    report["companion_hashes"]["EsteriaAppearance.dll"] = p.sha256(STAGE / "EsteriaAppearance.dll")
    files = {str(rel): str(STAGE / "pack" / rel) for rel in
             (p.GLOBAL_ARCHIVE_REL, p.LOCALE_ARCHIVE_REL, p.ASSET_ARCHIVE_REL)}
    files.update({name: str(STAGE / name) for name in report["companion_hashes"]})
    backup = Path("C:/Users/Zach/.codex/backups") / ("earthen-" + datetime.now().strftime("%Y%m%d-%H%M%S"))
    backup.mkdir(parents=True)
    before = {}
    for name, staged in files.items():
        expected = report["stage_hashes"].get(name, report["companion_hashes"].get(name))
        if p.sha256(Path(staged)) != expected:
            raise ValueError("Earthen stage changed: " + name)
        live = p.CLIENT_DEFAULT / name
        if name in report["source_hashes"] and p.sha256(live) != report["source_hashes"][name]:
            raise ValueError("Earthen archive stage is stale: " + name)
        before[name] = p.sha256(live) if live.exists() else None
        if live.exists():
            target = backup / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(live, target)
            if p.sha256(target) != before[name]:
                raise ValueError("Earthen client backup differs: " + name)
    server_before = {}
    for name in p.SERVER_DBC_TABLES:
        live = p.SERVER_DBC_ROOT / (name + ".dbc")
        server_before[name] = p.sha256(live)
        target = backup / "server-dbc" / live.name
        target.parent.mkdir(exist_ok=True)
        shutil.copy2(live, target)
        if p.sha256(target) != server_before[name]:
            raise ValueError("Earthen server DBC backup differs: " + name)
    rollback = "START TRANSACTION;\n" + "\n".join(
        f"DELETE FROM `{table}` WHERE `{'RaceID' if table == 'player_totem_model' else 'race'}` IN (48,49);"
        for table in db_tables) + f"\nDELETE FROM updates WHERE name='{migration.name}';\nCOMMIT;\n"
    (backup / "rollback-world.sql").write_text(rollback, encoding="utf-8", newline="\n")
    old_image = subprocess.check_output(["docker", "inspect", "ac-worldserver", "--format", "{{.Image}}"], text=True).strip()
    old_tag = "acore/ac-wotlk-worldserver:earthen-rollback-" + backup.name.removeprefix("earthen-")
    subprocess.run(["docker", "tag", old_image, old_tag], check=True)
    report.update(backup=str(backup), files=files, before_hashes=before, server_before_hashes=server_before,
                  preserved_exe_sha256=p.sha256(p.CLIENT_DEFAULT / "Wow.exe"),
                  previous_worldserver_image=old_image, rollback_worldserver_tag=old_tag,
                  migration_sha256=p.sha256(migration), status="verified_backups_ready")
    report["unrelated_world_hashes"] = {}
    for table in db_tables:
        field = "RaceID" if table == "player_totem_model" else "race"
        rows = sorted(db.sql(f"SELECT * FROM `{table}` WHERE `{field}` NOT IN (48,49);").splitlines())
        report["unrelated_world_hashes"][table] = hashlib.sha256("\n".join(rows).encode()).hexdigest()
    save(backup / "install-report.json", report)
    save(STAGE / "install-plan.json", report)
    return {"backup": str(backup), "rollback_image": old_tag, "files": len(files)}


def install():
    import expanded_appearance_pack as native
    import mechagnome_race_pack as db
    report = p.load_json(STAGE / "install-plan.json")
    backup = Path(report["backup"])
    processes = subprocess.check_output(["tasklist", "/FO", "CSV", "/NH"], text=True).lower()
    if "wow.exe" in processes or "eclipse.exe" in processes:
        raise RuntimeError("Close WoW/Eclipse before installation")
    if p.sha256(p.CLIENT_DEFAULT / "Wow.exe") != report["preserved_exe_sha256"]:
        raise ValueError("Client executable changed after backup")
    for name, digest in report["before_hashes"].items():
        live = p.CLIENT_DEFAULT / name
        if (p.sha256(live) if live.exists() else None) != digest:
            raise ValueError("Live file changed after backup: " + name)
    for name, digest in report["server_before_hashes"].items():
        if p.sha256(p.SERVER_DBC_ROOT / (name + ".dbc")) != digest:
            raise ValueError("Server DBC changed after backup: " + name)
    migration = p.ROOT / "data/sql/updates/pending_db_world/rev_20261001100000000.sql"
    if p.sha256(migration) != report["migration_sha256"]:
        raise ValueError("Earthen migration changed after backup")
    if db.sql("SELECT COUNT(*) FROM characters WHERE race IN (48,49);", "acore_characters").strip() != "0":
        raise ValueError("Earthen character state changed after backup")
    for table, digest in report.get("unrelated_world_hashes", {}).items():
        field = "RaceID" if table == "player_totem_model" else "race"
        rows = sorted(db.sql(f"SELECT * FROM `{table}` WHERE `{field}` NOT IN (48,49);").splitlines())
        if hashlib.sha256("\n".join(rows).encode()).hexdigest() != digest:
            raise ValueError("Unrelated startup data changed after backup: " + table)
    for name, source in report["files"].items():
        expected = report["stage_hashes"].get(name, report["companion_hashes"].get(name))
        if p.sha256(Path(source)) != expected:
            raise ValueError("Stage changed after backup: " + name)
    receipt = hashlib.sha1(migration.read_bytes()).hexdigest().upper()
    try:
        db.sql("START TRANSACTION;\n" + migration.read_text() +
               f"\nINSERT INTO updates (name,hash,state) VALUES ('{migration.name}','{receipt}','PENDING');\nCOMMIT;")
        for name, source in report["files"].items():
            target = p.CLIENT_DEFAULT / name
            temporary = target.with_suffix(target.suffix + ".earthen-next")
            shutil.copy2(source, temporary)
            if p.sha256(temporary) != p.sha256(Path(source)):
                raise ValueError("Client install copy differs: " + name)
            os.replace(temporary, target)
            print("INSTALLED", name, flush=True)
        for name in p.SERVER_DBC_TABLES:
            source = STAGE / "server-dbc" / (name + ".dbc")
            target = p.SERVER_DBC_ROOT / source.name
            shutil.copy2(source, target)
            if p.sha256(source) != p.sha256(target):
                raise ValueError("Server DBC install differs: " + name)
    except Exception:
        for name, digest in report["before_hashes"].items():
            if digest is not None:
                shutil.copy2(backup / name, p.CLIENT_DEFAULT / name)
            else:
                (p.CLIENT_DEFAULT / name).unlink(missing_ok=True)
        for name in p.SERVER_DBC_TABLES:
            shutil.copy2(backup / "server-dbc" / (name + ".dbc"), p.SERVER_DBC_ROOT / (name + ".dbc"))
        db.sql((backup / "rollback-world.sql").read_text())
        raise
    report.update(installed_hashes={name: p.sha256(p.CLIENT_DEFAULT / name) for name in report["files"]},
                  installed_server_hashes={name: p.sha256(p.SERVER_DBC_ROOT / (name + ".dbc"))
                                           for name in p.SERVER_DBC_TABLES},
                  migration_receipt_sha1=receipt, status="installed_awaiting_worldserver_recreation")
    save(STAGE / "last-install.json", report)
    save(backup / "install-report.json", report)
    prior = p.load_json(native.STAGE / "last-install.json")
    prior["installed_hashes"].update(report["installed_hashes"])
    prior["latest_earthen_backup"] = str(backup)
    save(native.STAGE / "last-install.json", prior)
    return {"backup": str(backup), "installed_files": len(report["files"]), "receipt": receipt}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("audit", "acquire", "portraits", "prepare", "stage", "backup", "install"))
    action = parser.parse_args().action
    print(json.dumps({"audit": audit, "acquire": acquire, "portraits": prepare_portraits,
                      "prepare": prepare, "stage": stage, "backup": backup_install, "install": install}[action](), indent=2))
