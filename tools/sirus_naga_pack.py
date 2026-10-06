"""Stage and install the checked Sirus Naga replacement for Esteria race 54."""

from __future__ import annotations

import argparse
import copy
import csv
import ctypes
import hashlib
import json
import os
import shutil
import struct
import subprocess
from datetime import datetime
from pathlib import Path, PureWindowsPath

from PIL import Image
from luaparser import ast
from wotlkconv.blp import Blp
from wotlkconv.m2 import parse_m2, parse_skin, write_md20
from wotlkconv.m2.skin import write_skin

import creature_race_pack as c
import earthen_race_pack as e
from haranir_race_pack import lznt1
from lib.clientfs import archive_chain

p = c.p
SOURCE = Path(r"D:\Sirus\_client\World of Warcraft Sirus\Naga_Extract_2026-10-03")
STAGE = Path(r"C:\Users\Zach\.codex\tmp\sirus-naga")
PREFIX = "custom\\naga\\sirus\\"
TABLES = ("CharSections", "CharHairGeosets", "CharacterFacialHairStyles", "BarberShopStyle",
          "CreatureModelData", "AnimationData")
SERVER_TABLES = ("CharSections", "BarberShopStyle", "CreatureModelData")
CASTS = {2: 53, 31: 51, 32: 53, 33: 54}
PACKAGE = Path(r"G:\RetroPorterWork\naga-sirus\package")


def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8", newline="\n")


def values(row):
    return struct.unpack("<" + "I" * (len(row) // 4), row)


def namespace(key):
    parts = PureWindowsPath(key).parts
    if PureWindowsPath(key).is_absolute() or ".." in parts:
        raise ValueError("Unsafe source asset path: " + key)
    return PREFIX + str(PureWindowsPath(*parts)).lower()


class Extracted:
    def __init__(self):
        self.rows = {}
        self.receipts = {}
        data = SOURCE.parent / "Data"
        chain = archive_chain(str(data), "ruRU")
        ranks = {str(Path(path).relative_to(data)).replace("\\", "/").lower(): i
                 for i, path in enumerate(chain)}
        for name in ("manifest.csv", "discovered_from_dbc_manifest.csv", "model_companions_manifest.csv",
                     "supporting_files_manifest.csv", "naga_database_glue_manifest.csv",
                     "race13_linked_tables_manifest.csv"):
            with (SOURCE / name).open(encoding="utf-8-sig", newline="") as source:
                for row in csv.DictReader(source):
                    key = row["MPQPath"].lower()
                    current = self.rows.get(key)
                    if current is None or ranks.get(row["Archive"].lower(), 10000) < ranks.get(
                            current["Archive"].lower(), 10000):
                        self.rows[key] = row

    def read(self, key):
        row = self.rows[key.lower()]
        payload = Path(row["OutputPath"]).read_bytes()
        if hashlib.sha1(payload).hexdigest().upper() != row["SHA1"].upper():
            raise ValueError("Extraction changed: " + row["OutputPath"])
        self.receipts[key.lower()] = {"archive": row["Archive"], "sha256": hashlib.sha256(payload).hexdigest()}
        return payload

    def table(self, name):
        return p.RawWdbc(self.read("DBFilesClient\\" + name + ".dbc"))


def source_profiles(source):
    sections = [values(row) for row in source.table("CharSections").records if values(row)[1] == 13]
    hair = [values(row) for row in source.table("CharHairGeosets").records if values(row)[1] == 13]
    facial = [values(row) for row in source.table("CharacterFacialHairStyles").records if values(row)[0] == 13]
    result = {}
    for gender in (0, 1):
        domains = [sorted({r[9] for r in sections if r[2] == gender and r[3] == 0}),
                   sorted({r[8] for r in sections if r[2] == gender and r[3] == 1}),
                   sorted({r[3] for r in hair if r[2] == gender}),
                   sorted({r[9] for r in sections if r[2] == gender and r[3] == 3}),
                   sorted({r[2] for r in facial if r[1] == gender})]
        if any(domain != list(range(len(domain))) or not domain or len(domain) > 256 for domain in domains):
            raise ValueError("Sirus appearance domains are not dense five-byte choices")
        labels = ("Skin Color", "Face", "Hair Style" if gender else "Crest Style",
                  "Hair Color" if gender else "Eye Color", "Facial Features")
        capacities = [len(domain) for domain in domains]
        result[str(gender)] = {"capacities": capacities, "options": [
            {"label": label, "id": None, "field": i, "count": capacities[i], "factor": 1, "choices": []}
            for i, label in enumerate(labels)]}
    return result


def add_casts(model):
    report = []
    for requested, authored in CASTS.items():
        if any(s["id"] == requested for s in model.sequences):
            raise ValueError("Unexpected existing casting entry: " + str(requested))
        index = next(i for i, s in enumerate(model.sequences) if s["id"] == authored and not s["variation_index"])
        added = copy.deepcopy(model.sequences[index])
        slot = len(model.sequences)
        added.update(id=requested, variation_index=0, variation_next=-1, alias_next=slot,
                     flags=(added["flags"] & ~0x40) | 0x20)
        model.sequences.append(added)
        for track in model.tracks():
            if track.global_sequence >= 0:
                continue
            times = copy.deepcopy(track.timestamps[index]) if index < len(track.timestamps) else []
            keys = copy.deepcopy(track.values[index]) if hasattr(track, "values") and index < len(track.values) else []
            while len(track.timestamps) <= slot:
                track.timestamps.append([])
            track.timestamps[slot] = times
            track.timestamp_spans = [(0, 0)] * len(track.timestamps)
            if hasattr(track, "values"):
                while len(track.values) <= slot:
                    track.values.append([])
                track.values[slot] = keys
                track.value_spans = [(0, 0)] * len(track.values)
            track.external.clear()
        report.append({"id": requested, "source_id": authored, "duration": added["duration"]})
    e.rebuild_sequence_lookup(model)
    return report


def prepare():
    STAGE.mkdir(parents=True, exist_ok=True)
    source = Extracted()
    profiles = source_profiles(source)
    report = {"status": "preparing", "race_id": 54, "profiles": profiles, "models": {}, "source_hashes": {}}
    assets = {}
    sections = source.table("CharSections")
    selected = [values(row) for row in sections.records if values(row)[1] == 13]
    texture_keys = {p._string(sections.strings, off).decode() for row in selected for off in row[4:7] if off}
    for gender, sex in enumerate(("male", "female")):
        stem = "Snaga_Female" if gender else "Snaga_male"
        key = f"character\\NagaSirusHD\\{sex}\\{stem}.m2"
        original = source.read(key)
        path = STAGE / "source-models" / sex / (stem + ".m2")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(original)
        raw = parse_m2(original)
        for sequence in raw.sequences:
            if sequence["flags"] & (0x20 | 0x40):
                continue
            suffix = f"{sequence['id']:04d}-{sequence['variation_index']:02d}.anim"
            path.with_name(stem + suffix).write_bytes(source.read(key[:-3] + suffix))
        model = e.v.read_player_model(path)
        e.tracks.embed(model, path.parent, path.stem)
        expected_tracks = [(copy.deepcopy(track.timestamps), copy.deepcopy(getattr(track, "values", None)))
                           for track in model.tracks()]
        cast_report = add_casts(model)
        for texture in model.textures:
            if texture["filename"]:
                texture_keys.add(texture["filename"])
                texture["filename"] = namespace(texture["filename"])
        skin = parse_skin(source.read(key[:-3] + "00.skin"))
        for i, mesh in enumerate(skin.submeshes):
            if e.v.u16(mesh, 0) == 0:
                changed = bytearray(mesh)
                e.v.patch16(changed, 0, 10000)
                skin.submeshes[i] = bytes(changed)
        skin = e.v.compact_bone_palettes(model, skin)
        if p.load_manifest("naga")["appearance"].get("hide_helm"):
            model.attachment_lookup[11] = 65535
        target_key = PREFIX + sex + "\\" + stem.lower() + ".m2"
        encoded = write_md20(model)
        decoded = parse_m2(encoded)
        if decoded.vertices != raw.vertices:
            raise ValueError("Naga source vertex geometry changed")
        for track_index, (before, track) in enumerate(zip(expected_tracks, decoded.tracks(), strict=True)):
            count = len(raw.sequences)
            if track.global_sequence >= 0:
                count = len(before[0])
            unchanged_times = before[0] == track.timestamps[:len(before[0])]
            unchanged_keys = before[1] is None or before[1] == track.values[:len(before[1])]
            empty_padding = not any(track.timestamps[len(before[0]):count]) and (
                before[1] is None or not any(track.values[len(before[1]):count]))
            if not unchanged_times or not unchanged_keys or not empty_padding:
                raise ValueError(f"Donor track {track_index} {getattr(track, 'kind', 'event')} changed: "
                                 f"times {len(before[0])}/{len(track.timestamps[:count])}, "
                                 f"keys {len(before[1]) if before[1] is not None else None}/"
                                 f"{len(track.values[:count]) if hasattr(track, 'values') else None}")
        assets[target_key] = encoded
        assets[target_key[:-3] + "00.skin"] = write_skin(skin)
        for name, payload in ((target_key, encoded), (target_key[:-3] + "00.skin", write_skin(skin))):
            target = STAGE.joinpath("assets", *PureWindowsPath(name).parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(payload)
        report["models"][sex] = {"path": target_key, "source_path": key, "source_sha256":
            hashlib.sha256(original).hexdigest(), "vertices": model.vertex_count, "bones": len(model.bones),
            "sequences": len(model.sequences), "source_sequences": len(raw.sequences), "casts": cast_report,
            "geosets": sorted({e.v.u16(mesh, 0) for mesh in skin.submeshes}), "all_animations_embedded": True}
        print("PREPARED", sex, model.vertex_count, len(model.sequences), flush=True)
    for key in sorted(texture_keys):
        payload = source.read(key)
        name = namespace(key)
        assets[name] = payload
        target = STAGE.joinpath("assets", *PureWindowsPath(name).parts)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(payload)

    bank = bytearray(struct.pack("<4I", 0x31544845, 1, 0, 0))
    blobs, records = {}, []
    image_cache = {}

    def image(offset):
        key = p._string(sections.strings, offset).decode()
        if key not in image_cache:
            pixels = Blp.parse(source.read(key)).decode_level(0)
            image_cache[key] = Image.frombytes("RGBA", (pixels.width, pixels.height), bytes(pixels.data))
        return image_cache[key].copy()

    def blob(pixels):
        identity = (pixels.size, hashlib.sha256(pixels.tobytes()).hexdigest())
        if identity not in blobs:
            packed = lznt1(pixels.tobytes())
            blobs[identity] = len(bank)
            bank.extend(struct.pack("<3I", *pixels.size, len(packed)) + packed)
        return blobs[identity]

    def record(gender, kind, target, value, selectors=(), path=""):
        if len(path.encode()) >= 128 or len(selectors) > 3:
            raise ValueError("Naga catalog record exceeds native layout")
        fields = [i | value << 16 for i, value in selectors]
        records.append(struct.pack("<7I", gender, kind, target, value,
            *(fields + [0xffffffff] * (3 - len(fields)))) + path.encode().ljust(128, b"\0"))

    for gender in (0, 1):
        rows = [row for row in selected if row[2] == gender]
        for body in (r for r in rows if r[3] == 0):
            color = body[9]
            art = image(body[4])
            if art.size != (512, 512):
                raise ValueError("Unexpected Sirus body atlas dimensions")
            underwear = next(row for row in rows if row[3] == 4 and row[9] == color)
            if underwear[5]:
                torso = image(underwear[5]).resize((256, 128), Image.Resampling.LANCZOS)
                art.alpha_composite(torso, (256, 0))
            record(gender, 3, 0, blob(art), [(0, color)], "1:1")
            face = next(row for row in rows if row[3] == 1 and row[8] == 0 and row[9] == color)
            canvas = Image.new("RGBA", (256, 192))
            canvas.paste(image(face[5]).resize((256, 64), Image.Resampling.LANCZOS), (0, 0))
            canvas.paste(image(face[4]).resize((256, 128), Image.Resampling.LANCZOS), (0, 64))
            record(gender, 3, 1, blob(canvas), [(0, color)], "4:1")
            record(gender, 1, 8, 0, [(0, color)], namespace(p._string(sections.strings, body[5]).decode()))
        for hair in (r for r in rows if r[3] == 3):
            record(gender, 1, 6, 0, [(2, hair[8]), (3, hair[9])],
                   namespace(p._string(sections.strings, hair[4]).decode()))
        record(gender, 2, 0, 10000)
        # The source's 1802 mesh is a rigid equipment shell, not the natural waist.
        record(gender, 0, 18, 1800)
        for row in source.table("CharHairGeosets").records:
            r = values(row)
            if r[1:3] == (13, gender):
                record(gender, 0, 0, r[4], [(2, r[3])])
        for row in source.table("CharacterFacialHairStyles").records:
            r = values(row)
            if r[:2] == (13, gender):
                # Native Wrath orders the beard, sideburn, moustache, eye and face groups this way.
                for group, value in zip((1, 3, 2, 16, 17), r[3:], strict=True):
                    record(gender, 0, group, group * 100 + value, [(4, r[2])])
        print("MATERIALS", gender, len(records), len(blobs), flush=True)
    if len(records) > 16384 or len(blobs) > 4096:
        raise ValueError("Naga appearance exceeds native catalog capacities")
    struct.pack_into("<2I", bank, 8, len(blobs), int.from_bytes(hashlib.sha256(bank[16:]).digest()[:4], "little"))
    (STAGE / "EsteriaNagaTextures.bin").write_bytes(bank)
    (STAGE / "EsteriaNaga.bin").write_bytes(struct.pack("<3I", 0x314D4845, 1, len(records)) + b"".join(records))
    report.update(status="prepared", asset_hashes={key: hashlib.sha256(data).hexdigest()
                  for key, data in assets.items()}, source_receipts=source.receipts, catalog_records=len(records),
                  material_blobs=len(blobs))
    save(STAGE / "prepare-report.json", report)
    manifest = p.load_manifest("naga")
    manifest["runtime_patch_root"] = str(STAGE / "assets")
    for sex, info in report["models"].items():
        manifest["models"][sex]["model_path"] = info["path"]
    manifest["appearance"].update(source="sirus-naga", source_build="Sirus 3.3.5a", profiles=profiles)
    manifest["asset_source"] = {"name": "Sirus", "family": "NagaSirusHD", "race_id": 13,
                                "extraction": str(SOURCE)}
    save(p.manifest_path("naga"), manifest)
    c.header()
    print("PREPARE COMPLETE", STAGE, flush=True)


def merge_table(name, baseline, source, models):
    target = p.RawWdbc(baseline)
    rows, pool = list(target.records), bytearray(target.strings)
    if name == "CreatureModelData":
        manifest = p.load_manifest("naga")
        ids = {manifest["models"][sex]["model_id"]: info["path"] for sex, info in models.items()}
        changed = []
        for row in rows:
            identifier = values(row)[0]
            changed.append(p._set_string(row, 2, pool, ids[identifier]) if identifier in ids else row)
        if sum(values(row)[0] in ids for row in rows) != 2:
            raise ValueError("Existing Naga model IDs are missing")
        return target.build(changed, bytes(pool))
    donor = source.table(name)
    if (target.fields, target.record_size) != (donor.fields, donor.record_size):
        raise ValueError("Sirus table layout differs: " + name)
    if name == "AnimationData":
        existing = {values(row)[0] for row in rows}
        by_id = {values(row)[0]: row for row in donor.records}
        needed = set()
        for info in models.values():
            path = STAGE.joinpath("assets", *PureWindowsPath(info["path"]).parts)
            needed.update(s["id"] for s in parse_m2(path.read_bytes()).sequences)
        queue = list(needed - existing)
        added = set()
        while queue:
            identifier = queue.pop()
            if identifier in existing or identifier in added:
                continue
            if identifier not in by_id:
                raise ValueError("Sirus animation definition is missing: " + str(identifier))
            raw = by_id[identifier]
            row = p._set_string(raw, 1, pool, p._string(donor.strings, values(raw)[1]))
            rows.append(row)
            added.add(identifier)
            queue.append(values(raw)[5])
        return target.build(sorted(rows, key=lambda row: values(row)[0]), bytes(pool))
    race_field = 37 if name == "BarberShopStyle" else 0 if name == "CharacterFacialHairStyles" else 1
    rows = [row for row in rows if values(row)[race_field] != 54]
    next_id = max(values(row)[0] for row in target.records) + 1
    for raw in donor.records:
        if values(raw)[race_field] != 13:
            continue
        row = p._clone_strings(name, donor, raw, pool)
        row = p._replace(row, race_field * 4, 4, 54)
        if name != "CharacterFacialHairStyles":
            row = p._replace(row, 0, 4, next_id)
            next_id += 1
        if name == "CharSections":
            for field in (4, 5, 6):
                value = values(raw)[field]
                if value:
                    row = p._set_string(row, field, pool, namespace(p._string(donor.strings, value).decode()))
        rows.append(row)
    data = target.build(rows, bytes(pool))
    if name == "CharSections":
        from cars_mount_pack import order_charsections_entry
        data = order_charsections_entry("DBFilesClient\\CharSections.dbc", data)
    return data


def geometry_catalog(data, original_models, prepared):
    magic, version, count = struct.unpack_from("<3I", data)
    if (magic, version) != (0x4D474145, 1):
        raise ValueError("Unsupported geometry catalog")
    offset, output, changed = 12, [], []
    for _ in range(count):
        key = data[offset:offset + 128].split(b"\0", 1)[0].decode()
        length = struct.unpack_from("<I", data, offset + 128)[0]
        end = offset + 132 + length
        sex = original_models.get(key.lower())
        if sex is None:
            output.append(data[offset:end])
        else:
            new = prepared["models"][sex]["path"]
            skin = STAGE.joinpath("assets", *PureWindowsPath(new[:-3] + "00.skin").parts).read_bytes()
            output.append(new.encode().ljust(128, b"\0") + struct.pack("<I", len(skin)) + skin)
            changed.append(sex)
        offset = end
    if offset != len(data) or sorted(changed) != ["female", "male"]:
        raise ValueError("Geometry catalog did not contain exactly two Naga models")
    return data[:12] + b"".join(output)


def creator(data):
    text = data.decode("utf-8")
    old = "or CharacterCreate.selectedRaceID == 53;"
    new = "or CharacterCreate.selectedRaceID == 53 or CharacterCreate.selectedRaceID == 54;"
    if new not in text:
        if text.count(old) != 1:
            raise ValueError("Extended creator race predicate changed")
        text = text.replace(old, new, 1)
    old = 'or CharacterCreate.selectedRaceID == 51) and (label or "")'
    new = 'or CharacterCreate.selectedRaceID == 51 or CharacterCreate.selectedRaceID == 54) and (label or "")'
    if new not in text:
        if text.count(old) != 1:
            raise ValueError("Extended creator label predicate changed")
        text = text.replace(old, new, 1)
    ast.parse(text)
    return text.encode("utf-8")


def check_preserved(name, before, after):
    old, new = p.RawWdbc(before), p.RawWdbc(after)
    if not new.strings.startswith(old.strings):
        raise ValueError("Existing DBC string pool changed: " + name)
    if name == "CreatureModelData":
        ids = {120057, 120058}
        original = [row for row in old.records if values(row)[0] not in ids]
    elif name == "AnimationData":
        original = old.records
    else:
        field = 37 if name == "BarberShopStyle" else 0 if name == "CharacterFacialHairStyles" else 1
        original = [row for row in old.records if values(row)[field] != 54]
    available = set(new.records)
    if any(row not in available for row in original):
        raise ValueError("Unrelated DBC rows changed: " + name)
    if name != "CharacterFacialHairStyles" and len({row[:4] for row in new.records}) != len(new.records):
        raise ValueError("Duplicate DBC IDs: " + name)


def stage():
    prepared = p.load_json(STAGE / "prepare-report.json")
    if prepared["status"] != "prepared":
        raise ValueError("Prepare the complete Sirus pack first")
    source = Extracted()
    report = {"status": "staging", "models": prepared["models"], "source_hashes": {}, "stage_hashes": {},
              "server_before": {}, "server_after": {}, "asset_hashes": prepared["asset_hashes"],
              "table_changes": {}, "preserved_exe": p.sha256(p.CLIENT_DEFAULT / "Wow.exe")}
    updates = {}
    old_models = {}
    old_model_table = p.RawWdbc(p._full_table(p.CLIENT_DEFAULT / "Data", "CreatureModelData")[0])
    for sex in ("male", "female"):
        identifier = p.load_manifest("naga")["models"][sex]["model_id"]
        row = next(row for row in old_model_table.records if values(row)[0] == identifier)
        key = p._string(old_model_table.strings, values(row)[2]).decode()
        key = key[:-4] + ".m2" if key.lower().endswith(".mdx") else key
        old_models[key.lower()] = sex
    for name in TABLES:
        baseline = p._full_table(p.CLIENT_DEFAULT / "Data", name)[0]
        after = merge_table(name, baseline, source, prepared["models"])
        check_preserved(name, baseline, after)
        updates[p.DBC_ROOT + name + ".dbc"] = after
        path = STAGE / "client-dbc" / (name + ".dbc")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(after)
        report["table_changes"][name] = {"before_rows": len(p.RawWdbc(baseline).records),
                                        "after_rows": len(p.RawWdbc(after).records)}
    for name in SERVER_TABLES:
        live = p.SERVER_DBC_ROOT / (name + ".dbc")
        baseline = live.read_bytes()
        after = merge_table(name, baseline, source, prepared["models"])
        check_preserved(name, baseline, after)
        target = STAGE / "server-dbc" / live.name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(after)
        report["server_before"][name] = p.sha256(live)
        report["server_after"][name] = p.sha256(target)
    key = p.GLUE_ROOT + "CharacterCreate.lua"
    updates[key] = creator(p._effective_file(p.CLIENT_DEFAULT / "Data", key)[0])
    (STAGE / "CharacterCreate.staged.lua").write_bytes(updates[key])
    geometry = "EsteriaAppearanceGeometry.bin"
    (STAGE / geometry).write_bytes(geometry_catalog((p.CLIENT_DEFAULT / geometry).read_bytes(), old_models, prepared))
    report["companion_hashes"] = {name: p.sha256(STAGE / name) for name in
                                 (geometry, "EsteriaNaga.bin", "EsteriaNagaTextures.bin")}
    for path in p.CLIENT_DEFAULT.glob("Esteria*.bin"):
        if path.name not in report["companion_hashes"]:
            shutil.copy2(path, STAGE / path.name)
    storm = p.Storm(p.DLL_DEFAULT)
    for relative in (p.ASSET_ARCHIVE_REL, p.GLOBAL_ARCHIVE_REL, p.LOCALE_ARCHIVE_REL):
        live = p.CLIENT_DEFAULT / relative
        target = PACKAGE / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        report["source_hashes"][str(relative)] = p.sha256(live)
        shutil.copy2(live, target)
        if p.sha256(target) != report["source_hashes"][str(relative)]:
            raise ValueError("Archive stage copy differs")
        if relative == p.ASSET_ARCHIVE_REL:
            entries = {key: STAGE.joinpath("assets", *PureWindowsPath(key).parts).read_bytes()
                       for key in prepared["asset_hashes"]}
            handle = storm.open_archive(target)
            try:
                names = {name.lower() for name, *_ in storm.list_files(handle)}
                collision = {key.lower() for key in entries} & names
                if collision:
                    raise ValueError("Sirus asset namespace is already occupied: " + str(sorted(collision)[:3]))
            finally:
                storm.dll.SFileCloseArchive(handle)
        else:
            entries = updates
        storm.replace_archive_entries(target, entries)
        if target.stat().st_size >= 0x80000000:
            compact = target.with_suffix(".compact")
            p.rebuild_archive_streaming(storm, target, compact, compress=True)
            os.replace(compact, target)
        if target.stat().st_size >= 0x80000000:
            raise ValueError("Archive exceeds the classic client boundary")
        handle = storm.open_archive(target)
        try:
            for key, payload in entries.items():
                if storm.read(handle, key) != payload:
                    raise ValueError("Staged archive entry differs: " + key)
        finally:
            storm.dll.SFileCloseArchive(handle)
        report["stage_hashes"][str(relative)] = p.sha256(target)
        print("STAGED", relative, target.stat().st_size, flush=True)
    report["status"] = "staged"
    save(STAGE / "build-report.json", report)
    print("STAGE COMPLETE", PACKAGE, flush=True)


def verify():
    report = p.load_json(STAGE / "build-report.json")
    prepared = p.load_json(STAGE / "prepare-report.json")
    if report["status"] != "staged":
        raise ValueError("The archive stage is incomplete")
    bank = (STAGE / "EsteriaNagaTextures.bin").read_bytes()
    magic, version, count, checksum = struct.unpack_from("<4I", bank)
    if (magic, version, count) != (0x31544845, 1, prepared["material_blobs"]) or checksum != int.from_bytes(
            hashlib.sha256(bank[16:]).digest()[:4], "little"):
        raise ValueError("Naga material bank header or checksum differs")
    selectors = (STAGE / "EsteriaNaga.bin").read_bytes()
    magic, version, count = struct.unpack_from("<3I", selectors)
    if (magic, version, len(selectors)) != (0x314D4845, 1, 12 + count * 156):
        raise ValueError("Naga selection catalog layout differs")
    records = [struct.unpack_from("<7I128s", selectors, 12 + i * 156) for i in range(count)]
    decompress = ctypes.WinDLL("ntdll").RtlDecompressBuffer
    decompress.argtypes = [ctypes.c_ushort, ctypes.c_void_p, ctypes.c_ulong, ctypes.c_void_p,
                          ctypes.c_ulong, ctypes.POINTER(ctypes.c_ulong)]
    decompress.restype = ctypes.c_long
    decoded = set()
    for record in records:
        gender, kind, target, value = record[:4]
        capacities = prepared["profiles"][str(gender)]["capacities"]
        for selector in record[4:7]:
            if selector != 0xffffffff and ((selector & 65535) >= 5 or selector >> 16 >= capacities[selector & 65535]):
                raise ValueError("Naga selector exceeds its appearance domain")
        if kind == 1:
            key = record[7].split(b"\0", 1)[0].decode()
            if key not in report["asset_hashes"]:
                raise ValueError("Naga direct material is absent: " + key)
        if kind != 3 or value in decoded:
            continue
        width, height, size = struct.unpack_from("<3I", bank, value)
        if (width, height) != ((512, 512) if target == 0 else (256, 192)) or value + 12 + size > len(bank):
            raise ValueError("Naga material bounds or dimensions differ")
        output = ctypes.create_string_buffer(width * height * 4)
        packed = ctypes.create_string_buffer(bank[value + 12:value + 12 + size])
        got = ctypes.c_ulong()
        if decompress(2, output, len(output), packed, size, ctypes.byref(got)) or got.value != len(output):
            raise ValueError("Naga material decompression failed")
        decoded.add(value)
    if len(decoded) != prepared["material_blobs"]:
        raise ValueError("Naga material bank contains unreachable blobs")
    states = 0
    for gender in (0, 1):
        capacities = prepared["profiles"][str(gender)]["capacities"]
        active = [record for record in records if record[0] == gender]

        def selected(fields):
            return [r for r in active if all(v == 0xffffffff or fields[v & 65535] == v >> 16 for v in r[4:7])]

        for skin in range(capacities[0]):
            rows = selected([skin, 0, 0, 0, 0])
            for kind, target in ((3, 0), (3, 1), (1, 8), (2, 0)):
                if sum(r[1:3] == (kind, target) for r in rows) != 1:
                    raise ValueError("Naga skin has incomplete or ambiguous material/base selections")
            states += 1
        for style in range(capacities[2]):
            for color in range(capacities[3]):
                rows = selected([0, 0, style, color, 0])
                if sum(r[1:3] == (1, 6) for r in rows) != 1 or sum(r[1:3] == (0, 0) for r in rows) != 1:
                    raise ValueError("Naga hair/eye choice has incomplete selections")
                states += 1
        for facial in range(capacities[4]):
            rows = selected([0, 0, 0, 0, facial])
            for group in (1, 3, 2, 16, 17):
                if sum(r[1:3] == (0, group) for r in rows) != 1:
                    raise ValueError("Naga facial choice has incomplete geometry selections")
            states += 1
    for sex, info in prepared["models"].items():
        path = STAGE.joinpath("assets", *PureWindowsPath(info["path"]).parts)
        model = parse_m2(path.read_bytes())
        skin = parse_skin(path.with_name(path.stem + "00.skin").read_bytes())
        if model.version != 264 or len(model.sequences) != info["source_sequences"] + 4:
            raise ValueError("Naga model format or sequence count differs")
        if any(track.external for track in model.tracks()) or any(not s["flags"] & 0x20 for s in model.sequences):
            raise ValueError("Naga model still requires an external animation")
        for requested, authored in CASTS.items():
            a = next(i for i, s in enumerate(model.sequences) if s["id"] == requested)
            b = next(i for i, s in enumerate(model.sequences) if s["id"] == authored and not s["variation_index"])
            for track in model.tracks():
                if track.global_sequence >= 0:
                    continue
                if track.timestamps[a] != track.timestamps[b] or (hasattr(track, "values")
                        and track.values[a] != track.values[b]):
                    raise ValueError("Casting compatibility keys differ from their donor spell tracks")
        if skin.bone_count_max > 75 or any(e.v.u16(mesh, 12) > 75 for mesh in skin.submeshes):
            raise ValueError("Naga skin exceeds the native bone palette limit")
        if any(vertex >= model.vertex_count for vertex in skin.vertices) or any(
                i >= len(skin.vertices) for i in skin.indices):
            raise ValueError("Naga skin index bounds are invalid")
        if any(name not in report["asset_hashes"] for name in (t["filename"] for t in model.textures) if name):
            raise ValueError("Naga model has a missing hardcoded texture")
    for key, expected in report["asset_hashes"].items():
        if p.sha256(STAGE.joinpath("assets", *PureWindowsPath(key).parts)) != expected:
            raise ValueError("Staged Naga asset changed: " + key)
    for key, expected in report["stage_hashes"].items():
        if p.sha256(PACKAGE / key) != expected:
            raise ValueError("Staged archive changed: " + key)
    if p.sha256(p.CLIENT_DEFAULT / "Wow.exe") != report["preserved_exe"]:
        raise ValueError("Client executable changed since staging")
    result = {"status": "passed", "factored_choice_states": states, "material_blobs": len(decoded),
              "asset_count": len(report["asset_hashes"]), "cast_ids": list(CASTS), "race_id": 54}
    save(STAGE / "verification.json", result)
    print("VERIFIED", result, flush=True)


def install():
    import mechagnome_race_pack as db

    verify()
    processes = subprocess.check_output(["tasklist", "/FO", "CSV", "/NH"], text=True).lower()
    if any(name in processes for name in ("wow.exe", "eclipse.exe", "mpqeditor.exe")):
        raise RuntimeError("Close WoW, Eclipse and MPQEditor before replacing the checked Naga pack")
    races = p.RawWdbc(p._full_table(p.CLIENT_DEFAULT / "Data", "ChrRaces")[0])
    race = next(values(row) for row in races.records if values(row)[0] == 54)
    if race[4:6] != (60048, 60049):
        raise ValueError("Existing Naga race/display identity differs from the replacement contract")
    report = p.load_json(STAGE / "build-report.json")
    dll = STAGE / "EsteriaAppearance.dll"
    native = p.load_json(STAGE / "native-build-receipt.json")
    if p.sha256(dll) != native.get("dll_sha256") or p.sha256(
            p.ROOT / "src/server/shared/CreatureAppearance.h") != native.get("header_sha256"):
        raise ValueError("Native helper or shared appearance limits changed after verification")
    image = dll.read_bytes()
    pe = struct.unpack_from("<I", image, 0x3C)[0]
    if native.get("status") != "passed" or image[:2] != b"MZ" or image[pe:pe + 4] != b"PE\0\0" \
            or struct.unpack_from("<H", image, pe + 4)[0] != 0x14C:
        raise ValueError("The checked native appearance helper is not a valid Win32 build")
    for name in ("EsteriaCycle", "EsteriaGeometry", "EsteriaDirectSection", "EsteriaUnitExtra"):
        if name.encode() + b"\0" not in image:
            raise ValueError("Native appearance helper lacks its existing ABI: " + name)
    files = {name: PACKAGE / name for name in report["stage_hashes"]}
    files.update({name: STAGE / name for name in report["companion_hashes"]})
    files["EsteriaAppearance.dll"] = dll
    allowed = {str(p.ASSET_ARCHIVE_REL), str(p.GLOBAL_ARCHIVE_REL), str(p.LOCALE_ARCHIVE_REL),
               "EsteriaAppearanceGeometry.bin", "EsteriaNaga.bin", "EsteriaNagaTextures.bin", "EsteriaAppearance.dll"}
    if set(files) != allowed:
        raise ValueError("Unexpected installation target")
    for name, expected in report["source_hashes"].items():
        if p.sha256(p.CLIENT_DEFAULT / name) != expected:
            raise ValueError("Live archive changed since staging: " + name)
    for name, expected in report["server_before"].items():
        if p.sha256(p.SERVER_DBC_ROOT / (name + ".dbc")) != expected:
            raise ValueError("Server DBC changed since staging: " + name)
    before_image = subprocess.check_output(
        ["docker", "inspect", "ac-worldserver", "--format", "{{.Image}}"], text=True).strip()
    image_tag = subprocess.check_output(
        ["docker", "inspect", "ac-worldserver", "--format", "{{.Config.Image}}"], text=True).strip()
    new_image = subprocess.check_output(
        ["docker", "image", "inspect", image_tag, "--format", "{{.Id}}"], text=True).strip()
    if before_image == new_image:
        raise ValueError("The updated worldserver image has not been built")
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = PACKAGE.parent / "backups" / stamp
    backup.mkdir(parents=True, exist_ok=False)
    before, after = {}, {}
    for name, source in files.items():
        live = p.CLIENT_DEFAULT / name
        target = backup / name
        target.parent.mkdir(parents=True, exist_ok=True)
        before[name] = p.sha256(live)
        shutil.copy2(live, target)
        if p.sha256(target) != before[name]:
            raise ValueError("Client backup hash differs: " + name)
        after[name] = p.sha256(source)
    for name in SERVER_TABLES:
        live = p.SERVER_DBC_ROOT / (name + ".dbc")
        target = backup / "server-dbc" / live.name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(live, target)
        if p.sha256(target) != report["server_before"][name]:
            raise ValueError("Server backup hash differs: " + name)
    report.update(backup=str(backup), before_hashes=before, installed_hashes=after,
                  old_image=before_image, new_image=new_image, image_tag=image_tag)
    save(backup / "install-plan.json", report)
    print("VERIFIED BACKUP", backup, flush=True)
    query = ("SELECT guid,race,gender,skin,face,hairStyle,hairColor,facialStyle,extraAppearance "
             "FROM characters WHERE race=54 ORDER BY guid;")
    subprocess.run(["docker", "compose", "stop", "ac-worldserver"], check=True)
    try:
        characters = db.sql(query, "acore_characters")
        profiles = p.load_json(STAGE / "prepare-report.json")["profiles"]
        for line in characters.splitlines():
            fields = line.split("\t")
            capacities = profiles[fields[2]]["capacities"]
            if any(int(value) >= capacity for value, capacity in zip(fields[3:8], capacities, strict=True)):
                raise ValueError("An existing Naga appearance exceeds the replacement choices")
        for name, source in files.items():
            target = p.CLIENT_DEFAULT / name
            temporary = target.with_suffix(target.suffix + ".naga-next")
            shutil.copy2(source, temporary)
            if p.sha256(temporary) != after[name]:
                raise ValueError("Client install copy differs: " + name)
            os.replace(temporary, target)
        for name in SERVER_TABLES:
            source = STAGE / "server-dbc" / (name + ".dbc")
            target = p.SERVER_DBC_ROOT / source.name
            shutil.copy2(source, target)
            if p.sha256(target) != report["server_after"][name]:
                raise ValueError("Installed server DBC differs: " + name)
        if db.sql(query, "acore_characters") != characters:
            raise ValueError("Existing Naga appearance changed during installation")
        if p.sha256(p.CLIENT_DEFAULT / "Wow.exe") != report["preserved_exe"]:
            raise ValueError("Client executable changed during installation")
    except Exception:
        for name in files:
            shutil.copy2(backup / name, p.CLIENT_DEFAULT / name)
        for name in SERVER_TABLES:
            shutil.copy2(backup / "server-dbc" / (name + ".dbc"), p.SERVER_DBC_ROOT / (name + ".dbc"))
        subprocess.run(["docker", "image", "tag", before_image, image_tag], check=True)
        subprocess.run(["docker", "compose", "up", "-d", "--no-deps", "--no-build", "--pull", "never",
                        "--force-recreate", "ac-worldserver"], check=True)
        raise
    subprocess.run(["docker", "compose", "up", "-d", "--no-deps", "--no-build", "--pull", "never",
                    "--force-recreate", "ac-worldserver"], check=True)
    report.update(status="installed_awaiting_client_visual_test", race_id=54,
                  saved_naga_appearance_sha256=hashlib.sha256(characters.encode()).hexdigest())
    save(STAGE / "last-install.json", report)
    save(backup / "install-report.json", report)
    print("INSTALLED", backup, flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("prepare", "stage", "verify", "install"))
    args = parser.parse_args()
    {"prepare": prepare, "stage": stage, "verify": verify, "install": install}[args.action]()
