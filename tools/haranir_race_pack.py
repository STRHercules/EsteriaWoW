"""Stage the complete Haranir player graph without changing the installed clients or server."""

import argparse
import copy
import ctypes
import hashlib
import json
import shutil
import os
import subprocess
import struct
import sys
import urllib.request
from pathlib import Path
from datetime import datetime

from PIL import Image
from wotlkconv.blp import convert_blp
from wotlkconv.casc import CascStorage, KeyRing, blte
from wotlkconv.casc.cdn import CdnSource, blte_header_md5
from wotlkconv.casc.config import config_path, parse_config
from wotlkconv.m2 import parse_m2, parse_skin, write_md20
from wotlkconv.m2.skin import write_skin
from wotlkconv.options import Options

import earthen_race_pack as e

p = e.p
ROOT = Path(r"G:\RetroPorterWork\haranir")
SOURCE = ROOT / "output/patch-root"
ART = ROOT / "integration/patch-root"
STAGE = Path(r"C:\Users\Zach\.codex\tmp\haranir")
PROJECT = e.PROJECT
CACHE = PROJECT / "sources/retail/races/haranir"
PREFIX = "custom\\haranir\\native"
RACES = (50, 51)
MODELS = {"male": 5422149, "female": 5422147}
COLLECTIONS = {"male": 6255032, "female": 6255031}
LORE = ("Ferocious, watchful guardians, the haranir keep an ever-present vigil over the wild domains "
        "of their long-absent Goddess, in hopes that she might one day return.")
path = e.path
save = e.save


def audit():
    d = p.load_json(ROOT / "reports/discovery.json")
    if set(d["race_ids"]) != {86, 91} or {m["ID"] for m in d["models"]} != {200, 201}:
        raise ValueError("Haranir source identity changed")
    requirements = {r["ID"]: r for r in d["requirements"]}
    result = {"retail_race_ids": [86, 91], "target_race_ids": list(RACES), "sexes": {}, "omitted": []}
    for sex, model in (("male", 200), ("female", 201)):
        profile = {"options": [], "requirements": []}
        for option in sorted((o for o in d["options"] if o["ChrModelID"] == model),
                             key=lambda o: (o["OrderIndex"], o["ID"])):
            choices = sorted((c for c in d["choices"] if c["ChrCustomizationOptionID"] == option["ID"]),
                             key=lambda c: (c["OrderIndex"], c["ID"]))
            ordinary = [c for c in choices if requirements.get(c["ChrCustomizationReqID"], {}).get("ReqType") == 3]
            if not ordinary:
                raise ValueError("No playable choices: " + option["Name_lang"])
            profile["options"].append({"label": option["Name_lang"], "id": option["ID"], "choices": [
                {**c, "elements": [r for r in d["elements"] if r["ChrCustomizationChoiceID"] == c["ID"]]}
                for c in ordinary]})
            result["omitted"].extend({"sex": sex, "option": option["Name_lang"], "choice": c["ID"],
                "requirement": c["ChrCustomizationReqID"]} for c in choices if c not in ordinary)
        # Freeze this source-derived eleven-byte layout in codec.json before installing it.
        bins, descriptors = [], [None] * len(profile["options"])
        core = ("Skin Color", "Face", "Hair Style", "Hair Color", "Beard" if sex == "male" else "Eyebrows")
        for label in core:
            index = next(i for i, option in enumerate(profile["options"]) if option["label"] == label)
            count = len(profile["options"][index]["choices"])
            descriptors[index] = (len(bins), count, 1)
            bins.append(count)
        for index, option in sorted(enumerate(profile["options"]), key=lambda row: -len(row[1]["choices"])):
            if descriptors[index] is not None:
                continue
            count = len(option["choices"])
            field = next((i for i, capacity in enumerate(bins) if capacity * count <= 256), len(bins))
            if field == len(bins):
                bins.append(1)
            descriptors[index] = (field, count, bins[field])
            bins[field] *= count
        if len(bins) > 13:
            raise ValueError("Haranir appearance exceeds the five stock bytes plus uint64 extension")
        profile.update(descriptors=descriptors, capacities=bins + [1] * (13 - len(bins)))
        result["sexes"][sex] = profile
    if d["requirement_choices"]:
        raise ValueError("New Haranir eligibility relationships need explicit validation")
    receipt = STAGE / "last-install.json"
    codec_file = ROOT / "integration/codec.json"
    if receipt.exists() and codec_file.exists():
        installed = p.load_json(codec_file)
        for sex, prof in result["sexes"].items():
            if [list(row) for row in prof["descriptors"]] != installed[sex]["descriptors"]:
                raise ValueError("Installed Haranir encoding must not change without an appearance migration")
    save(ROOT / "integration/customization-audit.json", result)
    return result


def acquire():
    """Read only reachable missing textures, source M2s and their authored SKINs from the pinned CDN."""
    from retroporter.config import DEFAULT
    sys.path.insert(0, str(PROJECT / "src"))
    from raceporter.config import load_project_config
    project = load_project_config(PROJECT)
    d = p.load_json(ROOT / "reports/discovery.json")
    profile = audit()
    CACHE.mkdir(parents=True, exist_ok=True)
    STAGE.mkdir(parents=True, exist_ok=True)
    inventory = p.load_json(CACHE / "inventory.json") if (CACHE / "inventory.json").exists() else {}
    storage = CascStorage.open(DEFAULT.retail_root, product=project.retail_source.product,
                               locale=project.retail_source.locale.lower(), keys=KeyRing.load(DEFAULT.keys))
    cdn = None
    try:
        pin = {"version": storage.build.version, "build_key": storage.build.build_key,
               "cdn_key": storage.build.cdn_key, "mode": project.retail_source.mode}
        if (CACHE / "build.json").exists() and p.load_json(CACHE / "build.json") != pin:
            raise ValueError("Refusing to change Haranir's pinned source build")
        save(CACHE / "build.json", pin)
        metadata = STAGE / "cdn-metadata"
        config = config_path(metadata / "Data", storage.build.cdn_key)
        if not config.exists():
            key = storage.build.cdn_key
            url = f"https://us.cdn.blizzard.com/{storage.build.cdn_path}/config/{key[:2]}/{key[2:4]}/{key}"
            raw = urllib.request.urlopen(url, timeout=30).read()
            if hashlib.md5(raw).hexdigest() != key:
                raise ValueError("CDN config key mismatch")
            config.parent.mkdir(parents=True, exist_ok=True)
            config.write_bytes(raw)
        cdn = CdnSource(metadata, storage.build, project.casc_cache_root / "haranir")
        cdn._indices = DEFAULT.retail_root / "Data/indices"
        values = parse_config(config.read_text())
        cdn._group = cdn._open(values.get("archive-group", [""])[0])
        cdn._loose = cdn._open(values.get("file-index", [""])[0])

        def https(url, offset, size):
            headers = {"Range": f"bytes={offset}-{offset + size - 1}"} if offset is not None else {}
            with urllib.request.urlopen(urllib.request.Request(url.replace("http://", "https://", 1),
                                        headers=headers), timeout=45) as response:
                if offset is not None and response.status != 206:
                    raise OSError("CDN ignored the requested range")
                return response.read(size + 1)

        cdn.fetch = https

        def read(file_id, extension):
            target = CACHE / f"{file_id}{extension}"
            ckey = storage.root.ckey_for(file_id)
            if not ckey:
                raise ValueError(f"Absent source FileDataID: {file_id}")
            if target.exists():
                raw = target.read_bytes()
            elif project.retail_source.mode == "local":
                raw = storage.read_file_id(file_id)
            else:
                ekey = storage.encoding.ekey_for(ckey)
                if not ekey:
                    raise ValueError(f"Absent source encoding: {file_id}")
                if cdn.locate(ekey) is not None:
                    encoded = cdn.read(ekey, f"Haranir {file_id}")
                else:
                    key = ekey.hex()
                    url = f"https://us.cdn.blizzard.com/{storage.build.cdn_path}/data/{key[:2]}/{key[2:4]}/{key}"
                    encoded = urllib.request.urlopen(url, timeout=45).read(64 * 1024 * 1024 + 1)
                if len(encoded) > 64 * 1024 * 1024 or blte_header_md5(encoded) != ekey:
                    raise ValueError(f"Encoding key/size mismatch: {file_id}")
                raw = blte.decode(encoded, storage.keys)
            if hashlib.md5(raw).digest() != ckey:
                raise ValueError(f"Content key mismatch: {file_id}")
            if not target.exists():
                target.write_bytes(raw)
            inventory[str(file_id)] = {"file": target.name, "content_key": ckey.hex(),
                "sha256": p.sha256(target), "bytes": len(raw)}
            save(CACHE / "inventory.json", inventory)
            return raw

        selected = [r for prof in profile["sexes"].values() for o in prof["options"] for c in o["choices"]
                    for r in c["elements"]]
        material_ids = {r["ChrCustomizationMaterialID"] for r in selected}
        resources = {m["MaterialResourcesID"] for m in d["linked"]["ChrCustomizationMaterial"]
                     if m["ID"] in material_ids}
        texture_ids = {t["FileDataID"] for t in d["texture_files"] if t["MaterialResourcesID"] in resources}
        for asset in d["file_assets"]:
            key = "custom\\haranir\\" + asset["path"]
            if asset["file_data_id"] not in texture_ids or path(SOURCE, key).exists() or path(ART, key).exists():
                continue
            raw = read(asset["file_data_id"], ".blp")
            converted, result = convert_blp(raw, key, Options())
            if not result.ok:
                raise ValueError("Texture conversion failed: " + key)
            target = path(ART, key)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(converted)
            print("Recovered", asset["file_data_id"], flush=True)
        for table, file_id in (("CharComponentTextureLayouts", 1360262), ("CharComponentTextureSections", 1360263)):
            raw = read(file_id, ".db2")
            target = ROOT / "retail-db2/dbfilesclient" / (table.lower() + ".db2")
            if target.exists() and target.read_bytes() != raw:
                raise ValueError("Texture layout source changed")
            target.write_bytes(raw)
        for file_id in (*MODELS.values(), *COLLECTIONS.values()):
            raw_model = read(file_id, ".m2")
            model = parse_m2(raw_model)
            skin_ids = list(model.skin_file_ids)
            offset = 0
            while offset + 8 <= len(raw_model):
                tag, size = struct.unpack_from("<4sI", raw_model, offset)
                if offset + 8 + size > len(raw_model):
                    raise ValueError("Truncated source chunk")
                if tag == b"SFID":
                    skin_ids = list(struct.unpack_from("<" + "I" * (size // 4), raw_model, offset + 8))
                offset += 8 + size
            for skin_id in skin_ids:
                if skin_id:
                    read(skin_id, ".skin")
            for texture_id in model.texture_file_ids:
                if texture_id:
                    read(texture_id, ".blp")
            print("Source model", file_id, model.vertex_count, "SKINs", skin_ids, flush=True)
        save(ROOT / "integration/source-acquisition.json", {"pin": pin, "inventory": inventory})
    finally:
        if cdn:
            cdn.close()
        storage.close()
    return {"source": pin, "cached_dependencies": len(inventory)}


def generate_header():
    import highmountain_appearance as codec
    from types import SimpleNamespace
    output = STAGE / "header"
    (output / "src/server/shared").mkdir(parents=True, exist_ok=True)
    original_codec, original_h = codec.codec, codec.h
    try:
        codec.codec = lambda: audit()["sexes"]
        codec.h = SimpleNamespace(p=SimpleNamespace(ROOT=output), ROOT=ROOT, save=save)
        codec.generate()
    finally:
        codec.codec, codec.h = original_codec, original_h
    text = (output / "src/server/shared/HighmountainAppearance.h").read_text()
    text = text.replace("Highmountain", "Haranir").replace("HIGHMOUNTAIN", "HARANIR")
    text = text.replace("tools/highmountain_appearance.py", "tools/haranir_race_pack.py")
    text = text.replace("std::array<std::uint8_t, 6>", "std::array<std::uint8_t, 13>")
    text = text.replace("std::array<std::uint16_t, 6>", "std::array<std::uint16_t, 13>")
    text = "\n".join(line.replace(" = {", " =\n        {") if "Capacities = " in line else line
                     for line in text.splitlines()) + "\n"
    helpers = '''    constexpr std::array<std::uint8_t, 13> Fields(std::uint8_t skin, std::uint8_t face,
        std::uint8_t hairStyle, std::uint8_t hairColor, std::uint8_t facialStyle, std::uint64_t extra)
    {
        std::array<std::uint8_t, 13> fields = {skin, face, hairStyle, hairColor, facialStyle};
        for (unsigned i = 0; i < 8; ++i)
            fields[5 + i] = static_cast<std::uint8_t>(extra >> (i * 8));
        return fields;
    }

    constexpr std::uint64_t Extra(std::array<std::uint8_t, 13> const& fields)
    {
        std::uint64_t extra = 0;
        for (unsigned i = 0; i < 8; ++i)
            extra |= std::uint64_t{fields[5 + i]} << (i * 8);
        return extra;
    }

'''
    text = text.replace("    template<class Options, class Requirements>", helpers +
                        "    template<class Options, class Requirements>", 1)
    (p.ROOT / "src/server/shared/HaranirAppearance.h").write_text(text, encoding="utf-8", newline="\n")
    save(ROOT / "integration/codec.json", audit()["sexes"])
    return {"header": "src/server/shared/HaranirAppearance.h", "bytes": 13}


def image(key):
    source = path(ART, key) if path(ART, key).exists() else path(SOURCE, key)
    bitmap = p.Blp.parse(source.read_bytes()).decode_level(0)
    return Image.frombytes("RGBA", (bitmap.width, bitmap.height), bytes(bitmap.data))


def emit(key, art, compositor=False):
    bitmap = p.BlpImage(art.width, art.height, bytearray(art.tobytes()))
    if compositor:
        data = e.rendering.paletted_compositor(bitmap)
    else:
        levels = bitmap.mip_chain()
        payloads = [Image.frombytes("RGBA", (l.width, l.height), bytes(l.data)).tobytes("raw", "BGRA") for l in levels]
        data = p.Blp.from_images(levels, compression=3, alpha_type=8, alpha_size=8, payloads=payloads).serialize()
    target = path(ART, key)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    return key


def lznt1(data):
    native = ctypes.WinDLL("ntdll")
    work, fragment = ctypes.c_ulong(), ctypes.c_ulong()
    if native.RtlGetCompressionWorkSpaceSize(2, ctypes.byref(work), ctypes.byref(fragment)):
        raise OSError("LZNT1 workspace unavailable")
    output, workspace = ctypes.create_string_buffer(len(data) + 4096), ctypes.create_string_buffer(work.value)
    size = ctypes.c_ulong()
    status = native.RtlCompressBuffer(2, data, len(data), output, len(output), 4096,
                                     ctypes.byref(size), workspace)
    if status:
        raise OSError(f"LZNT1 compression failed: {status}")
    compressed = output.raw[:size.value]
    restored, count = ctypes.create_string_buffer(len(data)), ctypes.c_ulong()
    if native.RtlDecompressBuffer(2, restored, len(data), compressed, len(compressed), ctypes.byref(count)):
        raise OSError("LZNT1 round trip failed")
    if count.value != len(data) or restored.raw != data:
        raise ValueError("LZNT1 content mismatch")
    return compressed


def prepare():
    from wotlkconv.m2.split import _rebuild_skin
    from wotlkconv.m2.downgrade import downgrade_cameras
    from wotlkconv.report import FileResult
    from retroporter.config import DEFAULT
    from retroporter.wotlk import load_db2
    d = p.load_json(ROOT / "reports/discovery.json")
    profiles = audit()["sexes"]
    materials = {r["ID"]: r for r in d["linked"]["ChrCustomizationMaterial"]}
    textures = {r["MaterialResourcesID"]: r["FileDataID"] for r in d["texture_files"]}
    files = {r["file_data_id"]: "custom\\haranir\\" + r["path"] for r in d["file_assets"]}
    geosets = {r["ID"]: r for r in d["linked"]["ChrCustomizationGeoset"]}
    skinned = {r["ID"]: r for r in d["linked"]["ChrCustomizationSkinnedModel"]}
    layers = [r for _, r in load_db2(DEFAULT, "haranir", "ChrModelTextureLayer")
              if r["CharComponentTextureLayoutsID"] in (183, 184)]
    records, report = [], {}
    payloads = bytearray(struct.pack("<4I", 0x31544845, 1, 0, 0))
    cached_payloads = {}

    def record(gender, kind, target, value, selectors=(), key=""):
        if len(selectors) > 3 or len(key.encode()) >= 128:
            raise ValueError("Catalog selection/path capacity exceeded")
        selected = [i | j << 16 for i, j in selectors]
        records.append(struct.pack("<7I", gender, kind, target, value,
                       *(selected + [0xffffffff] * (3 - len(selected)))) + key.encode().ljust(128, b"\0"))

    def normalized(file_id, target, group):
        cache_key = (file_id, target, group)
        if cache_key in cached_payloads:
            return cached_payloads[cache_key]
        art = image(files[file_id])
        if target in (1, 2):
            art = art.resize((1024, 512), Image.Resampling.LANCZOS)
            art = art.crop((0, 0, 512, 512)) if group == 0 else art.crop((512, 0, 1024, 512)).resize(
                (256, 192), Image.Resampling.LANCZOS)
        elif group == 0:
            canvas = Image.new("RGBA", (512, 512))
            boxes = {3: (256, 448, 256, 64), 13: (256, 192, 256, 128), 14: (256, 0, 256, 128),
                     20: (0, 0, 512, 512)}
            x, y, width, height = boxes[target]
            canvas.alpha_composite(art.resize((width, height), Image.Resampling.LANCZOS), (x, y))
            art = canvas
        else:
            size = (256, 192) if group == 1 else (256, 128) if group in (3, 8) else (512, 512)
            art = art.resize(size, Image.Resampling.LANCZOS)
        data = lznt1(art.tobytes())
        offset = len(payloads)
        payloads.extend(struct.pack("<3I", art.width, art.height, len(data)) + data)
        cached_payloads[cache_key] = offset
        return offset

    groups = {1: 0, 2: 0, 20: 0, 13: 0, 14: 0, 3: 0, 4: 1, 7: 1, 19: 1,
              10: 2, 11: 2, 25: 3, 44: 3, 16: 4, 17: 5, 38: 6, 15: 7, 36: 8}
    for gender, sex in enumerate(("male", "female")):
        prof = profiles[sex]
        indices = {c["ID"]: (i, j) for i, o in enumerate(prof["options"]) for j, c in enumerate(o["choices"])}
        selected = [r for o in prof["options"] for c in o["choices"] for r in c["elements"]
                    if not r["RelatedChrCustomizationChoiceID"] or r["RelatedChrCustomizationChoiceID"] in indices]
        selected.sort(key=lambda r: not r["RelatedChrCustomizationChoiceID"])
        collection_geosets, used_groups = {}, set()
        for element in selected:
            selectors = [indices[element["ChrCustomizationChoiceID"]]]
            if element["RelatedChrCustomizationChoiceID"]:
                selectors.append(indices[element["RelatedChrCustomizationChoiceID"]])
            collection = skinned.get(element["ChrCustomizationSkinnedModelID"])
            geo = collection or geosets.get(element["ChrCustomizationGeosetID"])
            if geo:
                if collection and geo["CollectionsFileDataID"] != COLLECTIONS[sex]:
                    raise ValueError("Unexpected playable collection model")
                group = geo["GeosetType"]
                source_id = group * 100 + geo["GeosetID"]
                if collection and group == 0:
                    group = 40
                value = group * 100 + geo["GeosetID"]
                record(gender, 0, group, value, selectors)
                used_groups.add(group)
                if collection and geo["GeosetID"]:
                    collection_geosets[source_id] = value
        for group in sorted(used_groups):
            record(gender, 0, group, group * 100)
        # Head fragment and eyeball remain visible; the Nose option selects the authored full face.
        record(gender, 0, 22, 2201)
        root = f"{PREFIX}\\{sex}"
        material_report = []
        for layer in sorted((r for r in layers if r["CharComponentTextureLayoutsID"] == 183 + gender),
                            key=lambda r: r["Layer"]):
            target = layer["ChrModelTextureTargetID"][0]
            if target not in groups:
                continue
            for element in selected:
                mat = materials.get(element["ChrCustomizationMaterialID"])
                if not mat or mat["ChrModelTextureTargetID"] != target:
                    continue
                selectors = [indices[element["ChrCustomizationChoiceID"]]]
                if element["RelatedChrCustomizationChoiceID"]:
                    selectors.append(indices[element["RelatedChrCustomizationChoiceID"]])
                file_id = textures[mat["MaterialResourcesID"]]
                group = groups[target]
                blob = normalized(file_id, target, group)
                record(gender, 3, group, blob, selectors, f"{target}:{layer['BlendMode']}")
                material_report.append({"target": target, "group": group, "file_id": file_id,
                    "selectors": selectors, "layer": layer["Layer"], "blend": layer["BlendMode"], "offset": blob})
                if target == 1:
                    blob = normalized(file_id, target, 1)
                    record(gender, 3, 1, blob, selectors, "1:1")
        source = path(SOURCE, f"custom\\haranir\\character\\harronir\\harronir{sex}.m2")
        model = e.v.read_player_model(source)
        raw = parse_m2((CACHE / f"{MODELS[sex]}.m2").read_bytes())
        model.events = copy.deepcopy(raw.events)
        model.texture_weights = copy.deepcopy(raw.texture_weights)
        model.texture_transforms = copy.deepcopy(raw.texture_transforms)
        downgrade_cameras(raw, FileResult(source=str(MODELS[sex]), kind="m2"))
        model.cameras = raw.cameras
        e.rebuild_sequence_lookup(model)
        e.share_material_defaults(model)
        e.tracks.embed(model, source.parent, source.stem)
        skin = parse_skin(source.with_name(source.stem + "00.skin").read_bytes())
        vertices, changed = bytearray(model.vertices), set()
        for batch in skin.batches:
            combo = model.texture_combos[e.v.u16(batch, 16):e.v.u16(batch, 16) + e.v.u16(batch, 14)]
            if not combo or model.textures[combo[0]]["type"] != 1:
                continue
            mesh = skin.submeshes[e.v.u16(batch, 4)]
            for vertex in skin.vertices[e.v.u16(mesh, 4):e.v.u16(mesh, 4) + e.v.u16(mesh, 6)]:
                if vertex in changed:
                    continue
                u, y = struct.unpack_from("<2f", vertices, vertex * 48 + 32)
                struct.pack_into("<2f", vertices, vertex * 48 + 32,
                                 u * 2 if u <= .5 else u - .5, y if u <= .5 else .625 + .375 * y)
                changed.add(vertex)
        model.vertices = bytes(vertices)
        neutral = emit(f"{root}\\neutral.blp", Image.new("RGBA", (4, 4), "white"))
        replacements = {19: 5, 25: 12, 20: 13}
        for texture, original, texture_id in zip(model.textures, raw.textures, raw.texture_file_ids, strict=True):
            kind = original["type"]
            if kind in replacements:
                texture.update(type=replacements[kind], filename="")
            elif kind >= 11:
                texture.update(type=0, filename=neutral)
            elif not kind and texture["filename"] and not path(SOURCE, texture["filename"]).exists():
                key = texture["filename"]
                data, result = convert_blp((CACHE / f"{texture_id}.blp").read_bytes(), key, Options())
                if not result.ok:
                    raise ValueError("Hard material conversion failed")
                target_file = path(ART, key)
                target_file.parent.mkdir(parents=True, exist_ok=True)
                target_file.write_bytes(data)
        for i, mesh in enumerate(skin.submeshes):
            if e.v.u16(mesh, 0) in (3201, 3301):
                mesh = bytearray(mesh)
                e.v.patch16(mesh, 0, 0)
                skin.submeshes[i] = bytes(mesh)
        cid = COLLECTIONS[sex]
        collection = path(SOURCE, f"custom\\haranir\\models\\item\\unk_exp11_{cid}_hr_{sex[0]}\\{cid}_hr_{sex[0]}.m2")
        extra = parse_m2(collection.read_bytes())
        extra_raw = parse_m2((CACHE / f"{cid}.m2").read_bytes())
        skin_ids = [6433274, 6433275, 6433276, 6433277] if gender == 0 else [6255674, 6255675, 6255676, 6255677]
        native_skins = [parse_skin((CACHE / f"{file_id}.skin").read_bytes()) for file_id in skin_ids]
        # Use the authored second reduced LOD, preserving every accessory style and bone binding.
        lod = 2
        vertex_offset = sum(len(s.vertices) for s in native_skins[:lod])
        lod_skin = native_skins[lod]
        extra.vertices = extra_raw.vertices[vertex_offset * 48:(vertex_offset + len(lod_skin.vertices)) * 48]
        extra.vertex_count = len(lod_skin.vertices)
        for texture, original in zip(extra.textures, extra_raw.textures, strict=True):
            if original["type"] in replacements:
                texture.update(type=replacements[original["type"]], filename="")
        keep = [i for i, mesh in enumerate(lod_skin.submeshes) if e.v.u16(mesh, 0) in collection_geosets]
        used = sorted({lod_skin.vertices[k] for i in keep for k in range(e.v.u16(lod_skin.submeshes[i], 4),
                       e.v.u16(lod_skin.submeshes[i], 4) + e.v.u16(lod_skin.submeshes[i], 6))})
        lod_skin = _rebuild_skin(lod_skin, keep, {value: i for i, value in enumerate(used)})
        extra.vertices = b"".join(extra.vertices[i * 48:(i + 1) * 48] for i in used)
        extra.vertex_count = len(used)
        # Retail's absent UV-combo sentinel is not an index into the converted UV0 table.
        for i, batch in enumerate(lod_skin.batches):
            if e.v.u16(batch, 18) == 65535:
                batch = bytearray(batch)
                e.v.patch16(batch, 18, 0)
                lod_skin.batches[i] = bytes(batch)
        temporary = STAGE / sex / collection.name
        temporary.parent.mkdir(parents=True, exist_ok=True)
        temporary.write_bytes(write_md20(extra))
        temporary.with_name(temporary.stem + "00.skin").write_bytes(write_skin(lod_skin))
        merged = e.v.append_collection(model, skin, temporary, collection_geosets)
        e.share_material_defaults(model)
        # Flatten each material to its sourced first sampler; layered colors are composed by the helper.
        for i, batch in enumerate(skin.batches):
            first = model.texture_combos[e.v.u16(batch, 16)]
            slot = model.textures[first]["type"]
            batch = bytearray(batch)
            e.v.patch16(batch, 2, 0)
            e.v.patch16(batch, 14, 1)
            if e.v.u16(batch, 18) == 65535:
                e.v.patch16(batch, 18, 0)
            if slot == 5:
                e.v.patch16(batch, 10, len(model.materials))
                model.materials.append({"flags": 4, "blending_mode": 0})
            skin.batches[i] = bytes(batch)
        model.replacable_texture_lookup = [65535] * 16
        for i, texture in enumerate(model.textures):
            if texture["type"]:
                model.replacable_texture_lookup[texture["type"]] = i
        skin = e.v.compact_bone_palettes(model, skin)
        key = f"{root}\\harronir{sex}.m2"
        target_file = path(ART, key)
        target_file.parent.mkdir(parents=True, exist_ok=True)
        target_file.write_bytes(write_md20(model))
        target_file.with_name(target_file.stem + "00.skin").write_bytes(write_skin(skin))
        report[sex] = {"model_path": key, "vertices": model.vertex_count, "skin_vertices": len(skin.vertices),
            "sequences": len(model.sequences), "events": len(model.events), "collection": merged,
            "collection_lod": lod, "collection_vertex_offset": vertex_offset, "materials": material_report}
        print("PREPARED", sex, model.vertex_count, len(skin.vertices), "vertices", flush=True)
    struct.pack_into("<I", payloads, 8, len(cached_payloads))
    struct.pack_into("<I", payloads, 12, int.from_bytes(hashlib.sha256(payloads[16:]).digest()[:4], "little"))
    (STAGE / "EsteriaHaranirTextures.bin").write_bytes(payloads)
    (STAGE / "EsteriaHaranir.bin").write_bytes(struct.pack("<3I", 0x314D4845, 1, len(records)) + b"".join(records))
    generate_header()
    save(ROOT / "integration/rendering.json", report)
    return {sex: {k: v for k, v in row.items() if k != "materials"} for sex, row in report.items()}


def portraits():
    art = e.portraits
    storm = p.Storm(p.DLL_DEFAULT)
    template = p._read_archive_entry(storm, p.CLIENT_DEFAULT / p.LOCALE_ARCHIVE_REL, art.ICON_TEMPLATE_ENTRY)
    ring = art.ring_layer(art.decode_client_blp(
        p._read_archive_entry(storm, p.CLIENT_DEFAULT / p.LOCALE_ARCHIVE_REL, art.RING_ENTRY)))
    report = {}
    for faction in ("Alliance", "Horde"):
        token = "Haranir" + ("Horde" if faction == "Horde" else "")
        for sex in ("Male", "Female"):
            source = art.DEFAULT_SOURCE / faction / f"Charactercreate-races_haranir-{sex.lower()}_{faction}.png"
            pixels = art.portrait_bytes(source, art.circular_mask())
            plain = p.encode_portrait(pixels, template)
            bordered = p.encode_portrait(art.compose_race_icon(pixels, ring), template)
            for root, stem, data in (("Glues\\CharacterCreate", f"UI-CharacterCreate-{token}{sex}", bordered),
                ("Glues\\CharacterSelect", f"ECS-Portrait-{token}{sex}", plain),
                ("CharacterFrame", f"TemporaryPortrait-{sex}-{token}", plain)):
                key = f"Interface\\{root}\\{stem}.blp"
                target = path(ART, key)
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data)
                p.validate_portrait(data, target)
                report[key] = p.sha256(target)
            art.compose_race_icon(pixels, ring).save(STAGE / f"portrait-{faction.lower()}-{sex.lower()}.png")
    save(ROOT / "integration/portraits.json", report)
    return report


def restore_standard_labels(text):
    anchor = '    else\n        for i=6,29 do _G["CharacterCustomizationButtonFrame"..i]:Hide(); end'
    replacement = ('    else\n'
        '        CharacterCustomizationButtonFrame1Text:SetText(CHAR_CUSTOMIZATION1_DESC);\n'
        '        CharacterCustomizationButtonFrame2Text:SetText(CHAR_CUSTOMIZATION2_DESC);\n'
        '        for i=6,29 do _G["CharacterCustomizationButtonFrame"..i]:Hide(); end')
    if replacement in text:
        return text
    if text.count(anchor) != 1:
        raise ValueError("Standard picker restoration anchor changed")
    return text.replace(anchor, replacement, 1)


def glue():
    from luaparser import ast
    result = {}
    storm = p.Storm(p.DLL_DEFAULT)
    for name in ("CharacterCreate.lua", "CharacterInfo.lua", "GlueStrings.lua", "GlueParent.lua",
                 "ECS_Schema.lua", "ECS_Integrate.lua"):
        text = p._read_archive_entry(storm, p.CLIENT_DEFAULT / p.LOCALE_ARCHIVE_REL, p.GLUE_ROOT + name).decode()
        if "HARANIR" in text or "Haranir=true" in text:
            raise ValueError("Haranir Glue is already installed; merge from its pre-install base")
        if name == "CharacterCreate.lua":
            text = text.replace('return CharacterCreate.selectedRaceID == 48 or ',
                'return CharacterCreate.selectedRaceID == 50 or CharacterCreate.selectedRaceID == 51 '
                'or CharacterCreate.selectedRaceID == 48 or ', 1)
            text = text.replace('for i=6,23 do', 'for i=6,29 do').replace('for i=1,23 do', 'for i=1,29 do')
            text = text.replace('CharacterCreate.selectedRaceID == 49 then CycleCharCustomization("EA_RANDOM",1);',
                'CharacterCreate.selectedRaceID == 49 or CharacterCreate.selectedRaceID == 50 '
                'or CharacterCreate.selectedRaceID == 51 then CycleCharCustomization("EA_RANDOM",1);', 1)
            anchor = '            local earthenChoiceText = nil;'
            text = text.replace(anchor, '''            if CharacterCreate.selectedRaceID == 50
                or CharacterCreate.selectedRaceID == 51 then
                frame:ClearAllPoints();
                frame:SetPoint("CENTER", parent, "CENTER", visibleRow >= 15 and 1040 or 740,
                    270-(visibleRow%15)*28);
            end
''' + anchor, 1)
            anchor = 'CharacterCreate.selectedRaceID == 49) and (label or "")'
            text = text.replace(anchor, 'CharacterCreate.selectedRaceID == 49 or CharacterCreate.selectedRaceID == 50 '
                'or CharacterCreate.selectedRaceID == 51) and (label or "")', 1)
            text = text.replace('RACE_ICON_TEXTURES = {', 'RACE_ICON_TEXTURES = {\n' + '\n'.join(
                f'    ["{token.upper()}_{sex.upper()}"] = "Interface\\\\Glues\\\\CharacterCreate\\\\'
                f'UI-CharacterCreate-{token}{sex}",' for token in ("Haranir", "HaranirHorde")
                for sex in ("Male", "Female")), 1)
            text = text.replace('["MAGHAR"] = "ORC",', '["MAGHAR"] = "ORC",\n'
                '        ["HARANIR"] = "NIGHTELF",\n        ["HARANIRHORDE"] = "NIGHTELF",', 1)
        elif name == "CharacterInfo.lua":
            text = text.replace('local EXACT_RACE_DATA = {', 'local EXACT_RACE_DATA = {\n'
                '    [50] = { glueString="HARANIR", name="Haranir", faction="Alliance", fileString="Haranir" },\n'
                '    [51] = { glueString="HARANIRHORDE", name="Haranir", faction="Horde", '
                'fileString="HaranirHorde" },', 1)
            for token, donor in (("HARANIR", "NIGHTELF"), ("HARANIRHORDE", "TROLL")):
                text += ('\nlocal haranirInfo = {};\n'
                    f'for key,value in pairs(RaceInfoByFileString.{donor} or {{}}) do haranirInfo[key]=value; end\n'
                    f'haranirInfo.Name="Haranir"; haranirInfo.Description={json.dumps(LORE)};\n'
                    f'RaceInfoByFileString.{token}=haranirInfo;\n')
        elif name == "GlueStrings.lua":
            for token in ("HARANIR", "HARANIRHORDE"):
                text += (f'\n{token}="Haranir"; {token}_MALE={token}; {token}_FEMALE={token};\n'
                    f'RACE_INFO_{token}={json.dumps(LORE)}; RACE_INFO_{token}_FEMALE=RACE_INFO_{token};\n')
        elif name == "GlueParent.lua":
            text = text.replace('["HIGHELF"] = true,', '["HIGHELF"] = true,\n        ["HARANIR"] = true,', 1)
            text = text.replace('["HIGHMOUNTAINTAUREN"] = true,',
                '["HIGHMOUNTAINTAUREN"] = true,\n        ["HARANIRHORDE"] = true,', 1)
        elif name == "ECS_Schema.lua":
            text = text.replace('S.RaceOverride = {', 'S.RaceOverride = {\n'
                '    [50] = { name="Haranir", faction=1, artKey="Haranir" },\n'
                '    [51] = { name="Haranir", faction=2, artKey="HaranirHorde" },', 1)
            text = text.replace('S.PortraitArtKeys = {',
                'S.PortraitArtKeys = {\n    Haranir=true, HaranirHorde=true,', 1)
        else:
            anchor = 'race == 48 or race == 49 or race == 52'
            if anchor not in text:
                raise ValueError("Character Select native identity anchor changed")
            text = text.replace(anchor, 'race == 48 or race == 49 or race == 50 or race == 51 or race == 52', 1)
        if name == "CharacterCreate.lua":
            text = restore_standard_labels(text)
        ast.parse(text)
        key = p.GLUE_ROOT + name
        target = path(ART, key)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8", newline="\n")
        result[key] = text.encode()
    return result


def tables():
    allocation = p.load_json(p.ALLOCATION_PATH)
    manifest = p.load_manifest("haranir")
    storm = p.Storm(p.DLL_DEFAULT)
    names = ("ChrRaces", "CreatureModelData", "CreatureDisplayInfo", "CharSections", "CharHairGeosets",
             "CharacterFacialHairStyles", "BarberShopStyle", "CharBaseInfo", "CharStartOutfit", "NameGen", "Spell")
    result = {n: p._read_archive_entry(storm, p.CLIENT_DEFAULT / p.GLOBAL_ARCHIVE_REL, p.DBC_ROOT + n + ".dbc")
              for n in names}
    for name in ("CreatureModelData", "CreatureDisplayInfo"):
        result[name] = p._merge_model_table(name, result[name], manifest, allocation)
    result["ChrRaces"] = p._merge_chr_races(result["ChrRaces"], manifest, allocation)
    races = p.RawWdbc(result["ChrRaces"])
    rows = []
    for row in races.records:
        race = p._value(row, 0)
        if race in RACES:
            for field, value in ((2, 4 if race == 50 else 116), (7, 7 if race == 50 else 1),
                                 (12, 0), (13, 0 if race == 50 else 1)):
                row = p._replace(row, field * 4, 4, value)
        rows.append(row)
    result["ChrRaces"] = races.build(rows)
    result["CharBaseInfo"] = p._build_char_base_info(result["CharBaseInfo"], manifest)
    result["CharStartOutfit"] = p._build_char_start_outfit(result["CharStartOutfit"], manifest, allocation)
    result["NameGen"] = p._clone_namegen(result["NameGen"], manifest, allocation)
    for name in ("CharStartOutfit", "NameGen"):
        table = p.RawWdbc(result[name])
        layout = p.WDBC_LAYOUTS[name]
        donors = [r for r in table.records if p._value(r, layout.race_offset, layout.race_width) == 50]
        first, last = allocation["race_allocations"]["haranir"][name]
        next_id = max(p._value(r, 0) for r in donors) + 1
        occupied = {p._value(r, 0) for r in table.records}
        if next_id + len(donors) > last + 1:
            raise ValueError("Haranir dual-faction allocation too small: " + name)
        rows = list(table.records)
        for donor in donors:
            if next_id in occupied:
                raise ValueError("Haranir Horde allocation collision: " + name)
            rows.append(p._replace(p._replace(donor, layout.race_offset, layout.race_width, 51), 0, 4, next_id))
            next_id += 1
        result[name] = table.build(rows)
    profiles = audit()["sexes"]
    sections, hairs, facial = [], [], []
    section_pool = bytearray(p.RawWdbc(result["CharSections"]).strings)
    start = allocation["race_allocations"]["haranir"]["CharSections"][0]
    hair_start = allocation["race_allocations"]["haranir"]["CharHairGeosets"][0]
    for race in RACES:
        for gender, sex in enumerate(("male", "female")):
            for kind in range(5):
                row = struct.pack("<10I", start + len(sections), race, gender, kind, 0, 0, 0,
                                  1 if kind == 1 else 17, 0, 0)
                row = p._set_string(row, 4, section_pool, f"{PREFIX}\\{sex}\\neutral.blp" if kind in (0, 3) else "")
                sections.append(row)
            hairs.append(struct.pack("<6I", hair_start + len(hairs), race, gender, 0, 0, 0))
            facial.append(struct.pack("<8I", race, gender, 0, 0, 0, 0, 0, 0))

    def append(name, rows, pool=None):
        table = p.RawWdbc(result[name])
        layout = p.WDBC_LAYOUTS[name]
        if any(p._value(r, layout.race_offset, layout.race_width) in RACES for r in table.records):
            raise ValueError("Haranir data already installed: " + name)
        if name != "CharacterFacialHairStyles" and (
                {p._value(r, 0) for r in table.records} & {p._value(r, 0) for r in rows}):
            raise ValueError("Haranir DBC allocation collision: " + name)
        result[name] = table.build(list(table.records) + rows, bytes(pool) if pool is not None else table.strings)

    append("CharSections", sections, section_pool)
    append("CharHairGeosets", hairs)
    append("CharacterFacialHairStyles", facial)
    barber = p.RawWdbc(result["BarberShopStyle"])
    pool, rows = bytearray(barber.strings), []
    first, last = allocation["race_allocations"]["haranir"]["BarberShopStyle"]
    for race in RACES:
        for gender, sex in enumerate(("male", "female")):
            for kind, field in ((0, 2), (2, 4), (3, 0)):
                donors = [r for r in barber.records if p._value(r, 148) == 4
                          and p._value(r, 152) == gender and p._value(r, 4) == kind]
                donor = donors[0] if donors else next(r for r in barber.records if p._value(r, 4) == kind)
                for index in range(profiles[sex]["capacities"][field]):
                    row = p._clone_strings("BarberShopStyle", barber, donor, pool)
                    for offset, value in ((0, first + len(rows)), (148, race), (152, gender), (156, index)):
                        row = p._replace(row, offset, 4, value)
                    rows.append(row)
    if first + len(rows) > last + 1:
        raise ValueError("Haranir barber allocation too small")
    append("BarberShopStyle", rows, pool)
    return result


def stage():
    t, g = tables(), glue()
    portraits()
    keys = set(p.load_json(ROOT / "integration/portraits.json"))
    for sex in ("male", "female"):
        key = f"{PREFIX}\\{sex}\\harronir{sex}.m2"
        keys.update((key, key[:-3] + "00.skin"))
        model = parse_m2(path(ART, key).read_bytes())
        keys.update(tx["filename"] for tx in model.textures if tx["type"] == 0)
        keys.add(f"{PREFIX}\\{sex}\\neutral.blp")
    assets = {}
    for key in keys - {""}:
        source = path(ART, key) if path(ART, key).is_file() else path(SOURCE, key)
        assets[key] = source.read_bytes()
    updates = {**assets, **g, **{p.DBC_ROOT + n + ".dbc": data for n, data in t.items()}}
    storm = p.Storm(p.DLL_DEFAULT)
    report = {"source_hashes": {}, "stage_hashes": {}, "tables": list(t), "assets": len(assets)}
    for rel in (p.GLOBAL_ARCHIVE_REL, p.LOCALE_ARCHIVE_REL, p.ASSET_ARCHIVE_REL):
        target = STAGE / "pack" / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        report["source_hashes"][str(rel)] = p.sha256(p.CLIENT_DEFAULT / rel)
        shutil.copy2(p.CLIENT_DEFAULT / rel, target)
        if p.sha256(target) != report["source_hashes"][str(rel)]:
            raise ValueError("Haranir merge-base copy differs")
        storm.replace_archive_entries(target, updates)
        if target.stat().st_size >= 0x80000000:
            raise ValueError("Haranir MPQ exceeds the classic reader's 2 GiB boundary")
        report["stage_hashes"][str(rel)] = p.sha256(target)
        print("STAGED", rel, flush=True)
    server = STAGE / "server-dbc"
    server.mkdir(exist_ok=True)
    for name in p.SERVER_DBC_TABLES:
        (server / (name + ".dbc")).write_bytes(t[name])
    prior = (p.CLIENT_DEFAULT / "EsteriaAppearanceGeometry.bin").read_bytes()
    magic, version, count = struct.unpack_from("<3I", prior)
    added = b""
    for sex in ("male", "female"):
        key = f"{PREFIX}\\{sex}\\harronir{sex}.m2"
        skin = path(ART, key[:-3] + "00.skin").read_bytes()
        added += key.encode().ljust(128, b"\0") + struct.pack("<I", len(skin)) + skin
    (STAGE / "EsteriaAppearanceGeometry.bin").write_bytes(
        struct.pack("<3I", magic, version, count + 2) + prior[12:] + added)
    for name in ("EsteriaAppearance.bin", "EsteriaAppearanceMaterials.bin",
                 "EsteriaHighmountain.bin", "EsteriaEarthen.bin"):
        shutil.copy2(p.CLIENT_DEFAULT / name, STAGE / name)
    report["companion_hashes"] = {n: p.sha256(STAGE / n) for n in
        ("EsteriaAppearance.bin", "EsteriaAppearanceGeometry.bin", "EsteriaAppearanceMaterials.bin",
         "EsteriaHighmountain.bin", "EsteriaEarthen.bin", "EsteriaHaranir.bin", "EsteriaHaranirTextures.bin")}
    report["preserved_exe_sha256"] = p.sha256(p.CLIENT_DEFAULT / "Wow.exe")
    report["status"] = "data_staged_native_and_worldserver_build_required"
    save(STAGE / "build-report.json", report)
    return report


WORLD_TABLES = ("playercreateinfo", "player_race_stats", "playercreateinfo_item", "playercreateinfo_action",
                "player_totem_model", "custom_race_start_spell", "custom_race_start_skill")
MIGRATION = p.ROOT / "data/sql/updates/pending_db_world/rev_20261002120000000.sql"
SCHEMA = p.ROOT / "data/sql/updates/pending_db_characters/rev_20261002120000000.sql"


def world_fingerprints():
    import mechagnome_race_pack as db
    result = {}
    for table in WORLD_TABLES:
        field = "RaceID" if table == "player_totem_model" else "race"
        rows = sorted(db.sql(f"SELECT * FROM `{table}` WHERE `{field}` NOT IN (50,51);").splitlines())
        result[table] = hashlib.sha256("\n".join(rows).encode()).hexdigest()
    return result


def preflight():
    import mechagnome_race_pack as db
    processes = subprocess.check_output(["tasklist", "/FO", "CSV", "/NH"], text=True).lower()
    if "wow.exe" in processes or "eclipse.exe" in processes:
        raise RuntimeError("Close WoW/Eclipse before replacing the helper and archives")
    if db.sql("SELECT COUNT(*) FROM characters WHERE race IN (50,51);", "acore_characters").strip() != "0":
        raise ValueError("Existing Haranir characters need an explicit appearance migration")
    for table in WORLD_TABLES:
        field = "RaceID" if table == "player_totem_model" else "race"
        if db.sql(f"SELECT COUNT(*) FROM `{table}` WHERE `{field}` IN (50,51);").strip() != "0":
            raise ValueError("Haranir startup data already exists: " + table)
    for source, database in ((MIGRATION, "acore_world"), (SCHEMA, "acore_characters")):
        if db.sql(f"SELECT COUNT(*) FROM updates WHERE name='{source.name}';", database).strip() != "0":
            raise ValueError("Haranir migration receipt already exists: " + database)


def backup():
    import mechagnome_race_pack as db
    preflight()
    report = p.load_json(STAGE / "build-report.json")
    for test in ("TestNativeAppearance.exe", "TestHighmountainMaterials.exe"):
        subprocess.run([str(STAGE / test), str(STAGE / "EsteriaAppearance.dll")], check=True)
    report["companion_hashes"]["EsteriaAppearance.dll"] = p.sha256(STAGE / "EsteriaAppearance.dll")
    files = {str(rel): str(STAGE / "pack" / rel) for rel in
             (p.GLOBAL_ARCHIVE_REL, p.LOCALE_ARCHIVE_REL, p.ASSET_ARCHIVE_REL)}
    files.update({name: str(STAGE / name) for name in report["companion_hashes"]})
    target = Path("C:/Users/Zach/.codex/backups") / ("haranir-" + datetime.now().strftime("%Y%m%d-%H%M%S"))
    target.mkdir(parents=True)
    before = {}
    for name, source in files.items():
        expected = report["stage_hashes"].get(name, report["companion_hashes"].get(name))
        if p.sha256(Path(source)) != expected:
            raise ValueError("Haranir stage changed: " + name)
        live = p.CLIENT_DEFAULT / name
        if name in report["source_hashes"] and p.sha256(live) != report["source_hashes"][name]:
            raise ValueError("Haranir merge base is stale: " + name)
        before[name] = p.sha256(live) if live.exists() else None
        if live.exists():
            copy = target / name
            copy.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(live, copy)
            if p.sha256(copy) != before[name]:
                raise ValueError("Client rollback copy mismatch: " + name)
    server_before = {}
    for name in p.SERVER_DBC_TABLES:
        live = p.SERVER_DBC_ROOT / (name + ".dbc")
        copy = target / "server-dbc" / live.name
        copy.parent.mkdir(exist_ok=True)
        server_before[name] = p.sha256(live)
        shutil.copy2(live, copy)
        if p.sha256(copy) != server_before[name]:
            raise ValueError("Server rollback copy mismatch: " + name)
    schema = db.sql("SHOW COLUMNS FROM characters LIKE 'extraAppearance';", "acore_characters")
    if schema.split("\t")[1] not in ("tinyint unsigned", "bigint unsigned"):
        raise ValueError("Unexpected appearance extension schema")
    appearance = db.sql("SELECT guid,race,skin,face,hairStyle,hairColor,facialStyle,extraAppearance "
                        "FROM characters ORDER BY guid;", "acore_characters")
    (target / "character-appearance-before.tsv").write_text(appearance, encoding="utf-8")
    rollback = "START TRANSACTION;\n" + "\n".join(
        f"DELETE FROM `{table}` WHERE `{'RaceID' if table == 'player_totem_model' else 'race'}` IN (50,51);"
        for table in WORLD_TABLES) + f"\nDELETE FROM updates WHERE name='{MIGRATION.name}';\nCOMMIT;\n"
    (target / "rollback-world.sql").write_text(rollback, encoding="utf-8", newline="\n")
    old_image = subprocess.check_output(
        ["docker", "inspect", "ac-worldserver", "--format", "{{.Image}}"], text=True).strip()
    old_tag = "acore/ac-wotlk-worldserver:haranir-rollback-" + target.name.removeprefix("haranir-")
    subprocess.run(["docker", "tag", old_image, old_tag], check=True)
    report.update(backup=str(target), files=files, before_hashes=before, server_before_hashes=server_before,
        prior_schema=schema, previous_worldserver_image=old_image, rollback_worldserver_tag=old_tag,
        migration_sha256=p.sha256(MIGRATION), schema_sha256=p.sha256(SCHEMA),
        unrelated_world_hashes=world_fingerprints(),
        character_appearance_sha256=hashlib.sha256(appearance.encode()).hexdigest(),
        status="verified_backups_ready")
    save(target / "install-report.json", report)
    save(STAGE / "install-plan.json", report)
    return {"backup": str(target), "files": len(files), "rollback_image": old_tag}


def install():
    import mechagnome_race_pack as db
    import expanded_appearance_pack as native
    preflight()
    report = p.load_json(STAGE / "install-plan.json")
    rollback = Path(report["backup"])
    if p.sha256(p.CLIENT_DEFAULT / "Wow.exe") != report["preserved_exe_sha256"]:
        raise ValueError("Client executable changed since staging")
    for name, expected in report["before_hashes"].items():
        live = p.CLIENT_DEFAULT / name
        if (p.sha256(live) if live.exists() else None) != expected:
            raise ValueError("Client changed after backup: " + name)
    for name, expected in report["server_before_hashes"].items():
        if p.sha256(p.SERVER_DBC_ROOT / (name + ".dbc")) != expected:
            raise ValueError("Server DBC changed after backup: " + name)
    if p.sha256(MIGRATION) != report["migration_sha256"] or p.sha256(SCHEMA) != report["schema_sha256"]:
        raise ValueError("Haranir migrations changed after backup")
    if world_fingerprints() != report["unrelated_world_hashes"]:
        raise ValueError("Unrelated startup data changed after backup")
    for name, source in report["files"].items():
        if p.sha256(Path(source)) != report["stage_hashes"].get(name, report["companion_hashes"].get(name)):
            raise ValueError("Stage changed after backup: " + name)
    image = subprocess.check_output(
        ["docker", "inspect", "ac-worldserver", "--format", "{{.State.Running}}"], text=True).strip()
    if image != "false":
        raise ValueError("Stop only ac-worldserver before installing the matching schema and files")
    try:
        # MySQL DDL commits separately; retain the widened column on rollback to avoid data truncation.
        for source, database in ((SCHEMA, "acore_characters"), (MIGRATION, "acore_world")):
            digest = hashlib.sha1(source.read_bytes()).hexdigest().upper()
            text = (source.read_text() + f"\nINSERT INTO updates (name,hash,state) VALUES "
                    f"('{source.name}','{digest}','PENDING');")
            if database == "acore_world":
                text = "START TRANSACTION;\n" + text + "\nCOMMIT;\n"
            db.sql(text, database)
        for name, source in report["files"].items():
            target = p.CLIENT_DEFAULT / name
            temporary = target.with_suffix(target.suffix + ".haranir-next")
            shutil.copy2(source, temporary)
            if p.sha256(temporary) != p.sha256(Path(source)):
                raise ValueError("Client installation copy mismatch: " + name)
            os.replace(temporary, target)
            print("INSTALLED", name, flush=True)
        for name in p.SERVER_DBC_TABLES:
            source = STAGE / "server-dbc" / (name + ".dbc")
            target = p.SERVER_DBC_ROOT / source.name
            shutil.copy2(source, target)
            if p.sha256(source) != p.sha256(target):
                raise ValueError("Server DBC installation mismatch: " + name)
        if world_fingerprints() != report["unrelated_world_hashes"]:
            raise ValueError("Haranir installation changed unrelated startup data")
        appearance = db.sql("SELECT guid,race,skin,face,hairStyle,hairColor,facialStyle,extraAppearance "
                            "FROM characters ORDER BY guid;", "acore_characters")
        if hashlib.sha256(appearance.encode()).hexdigest() != report["character_appearance_sha256"]:
            raise ValueError("Existing saved character appearance changed")
    except Exception:
        for name, expected in report["before_hashes"].items():
            if expected is not None:
                shutil.copy2(rollback / name, p.CLIENT_DEFAULT / name)
            else:
                (p.CLIENT_DEFAULT / name).unlink(missing_ok=True)
        for name in p.SERVER_DBC_TABLES:
            shutil.copy2(rollback / "server-dbc" / (name + ".dbc"), p.SERVER_DBC_ROOT / (name + ".dbc"))
        db.sql((rollback / "rollback-world.sql").read_text())
        db.sql(f"DELETE FROM updates WHERE name='{SCHEMA.name}';", "acore_characters")
        raise
    report.update(installed_hashes={name: p.sha256(p.CLIENT_DEFAULT / name) for name in report["files"]},
        installed_server_hashes={name: p.sha256(p.SERVER_DBC_ROOT / (name + ".dbc")) for name in p.SERVER_DBC_TABLES},
        status="installed_awaiting_worldserver_recreation")
    save(STAGE / "last-install.json", report)
    save(rollback / "install-report.json", report)
    prior = p.load_json(native.STAGE / "last-install.json")
    prior["installed_hashes"].update(report["installed_hashes"])
    prior["latest_haranir_backup"] = str(rollback)
    save(native.STAGE / "last-install.json", prior)
    acceptance_file = ROOT / "integration/acceptance.json"
    acceptance = p.load_json(acceptance_file) if acceptance_file.exists() else {}
    acceptance.update(report)
    acceptance["installed"] = True
    save(acceptance_file, acceptance)
    return {"backup": str(rollback), "installed_files": len(report["files"])}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("audit", "acquire", "header", "prepare", "portraits", "stage",
                                         "backup", "install"))
    print(json.dumps({"audit": audit, "acquire": acquire, "header": generate_header,
                      "prepare": prepare, "portraits": portraits, "stage": stage,
                      "backup": backup, "install": install}[parser.parse_args().action](), indent=2))
