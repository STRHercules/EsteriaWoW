"""Repair Naga-only waist selection, helmet components, sockets and visibility."""

from __future__ import annotations

import argparse
import ctypes as c
import hashlib
import json
import os
import shutil
import struct
import subprocess
from datetime import datetime
from pathlib import Path, PureWindowsPath

from wotlkconv.m2 import parse_m2, parse_skin

import sirus_naga_pack as n
from cars_mount_pack import H, rewrite_m2_texture_paths

p = n.p
STAGE = n.STAGE / "equipment"
PACKAGE = n.PACKAGE.parent / "equipment-package"
HEAD = "Item\\ObjectComponents\\Head\\"
HIDE_GROUPS = (0, 1, 3, 2, 7, 16, 17)
SOURCE_STEM_ALIASES = {
    "helm_plate_bloodknight_d": "helm_plate_bloodknight_d_02",
    "helm_robe_ahnqiraj_a": "helm_robe_ahnqiraj_a_01",
}


class Source:
    def __init__(self):
        self.storm = p.Storm(p.DLL_DEFAULT)
        self.storm._set("SFileHasFile", [H, c.c_char_p], c.c_bool)
        self.chain = p.ClientFiles(str(n.SOURCE.parent / "Data"), "ruRU").chain
        self.handles = {}
        self.cache = {}
        self.origins = {}

    def read(self, key, required=True):
        folded = key.lower()
        if folded in self.cache:
            return self.cache[folded]
        for path in self.chain:
            if path not in self.handles:
                handle = H()
                if not self.storm.dll.SFileOpenArchive(path, 0, 0x100, c.byref(handle)):
                    raise OSError("Cannot read Sirus archive: " + path)
                self.handles[path] = handle
            handle = self.handles[path]
            if self.storm.dll.SFileHasFile(handle, key.encode()):
                payload = self.storm.read(handle, key)
                self.cache[folded] = payload
                self.origins[folded] = {"archive": path, "sha256": hashlib.sha256(payload).hexdigest()}
                return payload
        if required:
            raise FileNotFoundError("Sirus dependency is absent: " + key)
        return None

    def close(self):
        for handle in self.handles.values():
            self.storm.dll.SFileCloseArchive(handle)


def prepare():
    STAGE.mkdir(parents=True, exist_ok=True)
    report = {"status": "preparing", "assets": {}, "components": [], "missing_source_heads": [],
              "source_hashes": {}, "sockets": {}}
    source = Source()
    assets = {}
    audit = p.load_json(n.STAGE / "helmet-source/head-audit.json")
    current = p.RawWdbc(p._full_table(p.CLIENT_DEFAULT / "Data", "ItemDisplayInfo")[0])
    source_items = p.RawWdbc(source.read("DBFilesClient\\ItemDisplayInfo.dbc"))
    source_by_id = {n.values(row)[0]: row for row in source_items.records}
    visibility = p.RawWdbc(source.read("DBFilesClient\\HelmetGeosetVisData.dbc"))
    hidden = {n.values(row)[0]: [group for group, mask in zip(HIDE_GROUPS, n.values(row)[1:], strict=True)
              if mask & (1 << 12)] for row in visibility.records}
    required = p.load_json(n.STAGE / "helmet-source/current-head-displays.json")
    display_ids = set(required["ids"])
    required_stems = {Path(name).stem.lower() for name in required["models"]}

    def put(key, data):
        name = str(PureWindowsPath(key)).lower()
        if name in assets and assets[name] != data:
            raise ValueError("Conflicting Naga equipment payload: " + name)
        assets[name] = data

    try:
        selected_models = [row for row in audit["models"].values()
                           if Path(row["key"].replace("\\", "/")).stem[:-4].lower() in required_stems]
        for target, stem in SOURCE_STEM_ALIASES.items():
            if target not in required_stems:
                continue
            for entry in audit["models"].values():
                if Path(entry["key"].replace("\\", "/")).stem[:-4].lower() == stem:
                    selected_models.append({**entry, "target_stem": target})
        for entry in selected_models:
            key = entry["key"]
            original = source.read(key)
            empty_source = struct.unpack_from("<I", original, 0x3C)[0] == 0
            if empty_source:
                # Source invisible-helmet placeholders carry an unused, dangling UV lookup.
                normalized = bytearray(original)
                for field in (0x78, 0x80, 0x88, 0x90, 0x98):
                    count, offset = struct.unpack_from("<2I", normalized, field)
                    if count and not offset:
                        struct.pack_into("<I", normalized, field, 0)
                original = bytes(normalized)
            model = parse_m2(original, key)
            if model.version != 264:
                raise ValueError("Unsupported Sirus helmet version: " + key)
            destination = key[:-7] + "_Na" + key[-4:]
            if "target_stem" in entry:
                destination = HEAD + entry["target_stem"] + "_Na" + key[-4:]
            # Keep component geometry intact; isolate hardcoded texture names from other races.
            replacements = {}
            for texture in model.textures:
                if texture["filename"]:
                    target = n.PREFIX + "helm-textures\\" + str(PureWindowsPath(texture["filename"])).lower()
                    put(target, source.read(texture["filename"]))
                    replacements[texture["filename"].encode()] = target
            data = rewrite_m2_texture_paths(original, replacements) if replacements else original
            put(destination, data)
            count = model.num_skin_profiles
            if not count:
                raise ValueError("Helmet has no skin profiles: " + key)
            for lod in range(count):
                source_skin = key[:-3] + f"{lod:02d}.skin"
                data = source.read(source_skin)
                skin = parse_skin(data)
                if any(vertex >= model.vertex_count for vertex in skin.vertices):
                    raise ValueError("Helmet skin references invalid vertices: " + source_skin)
                put(destination[:-3] + f"{lod:02d}.skin", data)
            report["components"].append({"source": key, "target": destination.lower(), "skins": count,
                                         "source_invisible_placeholder": empty_source})
        supported = {Path(row["target"].replace("\\", "/")).stem[:-4].lower()
                     for row in report["components"]}
        report["missing_source_heads"] = sorted(required_stems - supported)
        catalog = (p.CLIENT_DEFAULT / "EsteriaNaga.bin").read_bytes()
        magic, version, count = struct.unpack_from("<3I", catalog)
        if (magic, version, len(catalog)) != (0x314D4845, 1, 12 + count * 156):
            raise ValueError("Naga selection catalog differs")
        records = []
        changed_waists = []
        for i in range(count):
            raw = catalog[12 + i * 156:12 + (i + 1) * 156]
            gender, kind, target, value = struct.unpack_from("<4I", raw)
            if kind == 4:
                continue
            if (kind, target) == (0, 18):
                changed_waists.append(gender)
                raw = raw[:12] + struct.pack("<I", 1800) + raw[16:]
            records.append(raw)
        if sorted(changed_waists) != [0, 1]:
            raise ValueError("Naga waist rules are missing or duplicated")
        hide_records = []
        for raw in current.records:
            row = n.values(raw)
            if row[0] not in display_ids or row[0] not in source_by_id:
                continue
            donor = n.values(source_by_id[row[0]])
            current_name = p._string(current.strings, row[1]).lower()
            donor_name = p._string(source_items.strings, donor[1]).lower()
            if current_name != donor_name:
                report.setdefault("different_source_displays", []).append(row[0])
                continue
            for gender in (0, 1):
                for group in hidden.get(donor[13 + gender], ()):
                    records.append(struct.pack("<7I", gender, 4, row[0], group,
                                               0xffffffff, 0xffffffff, 0xffffffff) + bytes(128))
                    hide_records.append([gender, row[0], group, donor[13 + gender]])
        if len(records) > 16384:
            raise ValueError("Naga selection catalog exceeds its native capacity")
        (STAGE / "EsteriaNaga.bin").write_bytes(struct.pack("<3I", magic, version, len(records)) + b"".join(records))
        for sex, name in (("male", "Snaga_male"), ("female", "Snaga_Female")):
            key = n.PREFIX + sex + "\\" + name.lower() + ".m2"
            original = p._effective_file(p.CLIENT_DEFAULT / "Data", key)[0]
            donor = parse_m2(source.read("character\\NagaSirusHD\\" + sex + "\\" + name + ".m2"))
            restored = donor.attachment_lookup[11]
            if restored >= len(donor.attachments) or donor.attachments[restored]["id"] != 11:
                raise ValueError("Sirus head socket is invalid")
            blob = bytearray(original)
            count, offset = struct.unpack_from("<2I", blob, 0xF8)  # MD20 v264 attachment lookup array.
            if count <= 11 or offset + count * 2 > len(blob):
                raise ValueError("Naga attachment lookup layout is invalid")
            struct.pack_into("<H", blob, offset + 22, restored)
            patched = bytes(blob)
            if patched[:offset + 22] != original[:offset + 22] or patched[offset + 24:] != original[offset + 24:]:
                raise ValueError("A change outside the Naga head socket was introduced")
            model = parse_m2(patched)
            if model.attachment_lookup[11] != restored:
                raise ValueError("Naga socket restoration failed")
            put(key, patched)
            report["sockets"][sex] = {"index": restored, "bone": donor.attachments[restored]["bone"],
                                      "position": donor.attachments[restored]["position"],
                                      "casting_and_geometry_bytes_preserved": True}
        for key, payload in assets.items():
            target = STAGE.joinpath("assets", *PureWindowsPath(key).parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(payload)
        report.update(status="prepared", hide_records=hide_records, waist_geoset=1800,
                      catalog_records=len(records), source_receipts=source.origins,
                      assets={key: hashlib.sha256(data).hexdigest() for key, data in assets.items()})
        pth = STAGE / "prepare-report.json"
        n.save(pth, report)
        print("EQUIPMENT PREPARED", len(report["components"]), "helmet models", len(assets), "assets",
              len(hide_records), "visibility records", "source gaps", report["missing_source_heads"], flush=True)
    finally:
        source.close()


def stage():
    report = p.load_json(STAGE / "prepare-report.json")
    if report["status"] != "prepared" or report["missing_source_heads"]:
        raise ValueError("Naga equipment coverage is incomplete")
    for live in p.CLIENT_DEFAULT.glob("Esteria*.bin"):
        if live.name != "EsteriaNaga.bin":
            shutil.copy2(live, STAGE / live.name)
    source = p.CLIENT_DEFAULT / p.ASSET_ARCHIVE_REL
    target = PACKAGE / p.ASSET_ARCHIVE_REL
    target.parent.mkdir(parents=True, exist_ok=True)
    before = p.sha256(source)
    shutil.copy2(source, target)
    if p.sha256(target) != before:
        raise ValueError("Equipment archive copy differs")
    entries = {}
    for key, expected in report["assets"].items():
        payload = STAGE.joinpath("assets", *PureWindowsPath(key).parts).read_bytes()
        if hashlib.sha256(payload).hexdigest() != expected:
            raise ValueError("Prepared equipment asset changed: " + key)
        entries[key] = payload
    storm = p.Storm(p.DLL_DEFAULT)
    handle = storm.open_archive(target)
    try:
        existing = {name.lower() for name, *_ in storm.list_files(handle)}
        collisions = {key for key in entries if key.startswith(HEAD.lower())} & existing
        if collisions:
            raise ValueError("Naga helmet names already exist: " + str(sorted(collisions)[:3]))
    finally:
        storm.dll.SFileCloseArchive(handle)
    storm.replace_archive_entries(target, entries)
    if target.stat().st_size >= 0x80000000:
        raise ValueError("Equipment archive exceeds the classic client boundary")
    handle = storm.open_archive(target)
    try:
        for key, payload in entries.items():
            if storm.read(handle, key) != payload:
                raise ValueError("Staged equipment readback differs: " + key)
    finally:
        storm.dll.SFileCloseArchive(handle)
    report.update(status="staged", archive_before=before, archive_after=p.sha256(target),
                  catalog_before=p.sha256(p.CLIENT_DEFAULT / "EsteriaNaga.bin"),
                  helper_before=p.sha256(p.CLIENT_DEFAULT / "EsteriaAppearance.dll"),
                  exe_preserved=p.sha256(p.CLIENT_DEFAULT / "Wow.exe"))
    n.save(STAGE / "build-report.json", report)
    print("EQUIPMENT ARCHIVE STAGED", target, len(entries), "verified entries", flush=True)


def verify():
    report = p.load_json(STAGE / "build-report.json")
    if report["status"] != "staged":
        raise ValueError("Equipment stage is incomplete")
    catalog = (STAGE / "EsteriaNaga.bin").read_bytes()
    magic, version, count = struct.unpack_from("<3I", catalog)
    if (magic, version, len(catalog)) != (0x314D4845, 1, 12 + count * 156):
        raise ValueError("Equipment catalog layout differs")
    rows = [struct.unpack_from("<7I", catalog, 12 + i * 156) for i in range(count)]
    waists = [row for row in rows if row[1:3] == (0, 18)]
    if sorted((row[0], row[3]) for row in waists) != [(0, 1800), (1, 1800)]:
        raise ValueError("Equipment still forces the raised waist shell")
    for gender in (0, 1):
        groups = {row[3] for row in rows if row[:3] == (gender, 4, 32028)}
        if not {0, 3}.issubset(groups):
            raise ValueError("Giantstalker's Helmet visibility is incomplete")
    for component in report["components"]:
        key = component["target"]
        if not key.endswith(("_nam.m2", "_naf.m2")):
            raise ValueError("Equipment component has an incorrect Naga suffix: " + key)
        model = parse_m2(STAGE.joinpath("assets", *PureWindowsPath(key).parts).read_bytes(), key)
        if model.version != 264:
            raise ValueError("Equipment model is not native v264")
        for lod in range(component["skins"]):
            skin_key = key[:-3] + f"{lod:02d}.skin"
            skin = parse_skin(STAGE.joinpath("assets", *PureWindowsPath(skin_key).parts).read_bytes())
            if any(vertex >= model.vertex_count for vertex in skin.vertices) or any(
                    index >= len(skin.vertices) for index in skin.indices):
                raise ValueError("Equipment skin index bounds are invalid: " + skin_key)
        for texture in model.textures:
            if texture["filename"] and texture["filename"].lower() not in report["assets"]:
                raise ValueError("Equipment hardcoded texture is absent: " + texture["filename"])
    for sex, socket in report["sockets"].items():
        name = n.PREFIX + sex + "\\snaga_" + sex + ".m2"
        model = parse_m2(STAGE.joinpath("assets", *PureWindowsPath(name).parts).read_bytes())
        if model.attachment_lookup[11] != socket["index"]:
            raise ValueError("Naga head attachment is still disabled")
        ids = {sequence["id"] for sequence in model.sequences}
        if not set(n.CASTS).issubset(ids):
            raise ValueError("Naga casting compatibility was lost")
    if p.sha256(PACKAGE / p.ASSET_ARCHIVE_REL) != report["archive_after"]:
        raise ValueError("Equipment archive changed after readback")
    result = {"status": "passed", "helmet_models": len(report["components"]),
              "asset_count": len(report["assets"]), "visibility_records": len(report["hide_records"]),
              "waist_geoset": 1800, "restored_head_sockets": report["sockets"], "race_id": 54}
    n.save(STAGE / "verification.json", result)
    print("EQUIPMENT VERIFIED", result["helmet_models"], "models", result["asset_count"], "assets", flush=True)


def install():
    verify()
    report = p.load_json(STAGE / "build-report.json")
    native = p.load_json(STAGE / "native-build-receipt.json")
    dll = STAGE / "EsteriaAppearance.dll"
    if native.get("status") != "passed" or p.sha256(dll) != native.get("dll_sha256"):
        raise ValueError("The tested native equipment helper is missing or changed")
    processes = subprocess.check_output(["tasklist", "/FO", "CSV", "/NH"], text=True).lower()
    if any(name in processes for name in ("wow.exe", "eclipse.exe", "mpqeditor.exe")):
        raise RuntimeError("Close WoW, Eclipse and MPQEditor before the checked equipment install")
    files = {str(p.ASSET_ARCHIVE_REL): PACKAGE / p.ASSET_ARCHIVE_REL,
             "EsteriaNaga.bin": STAGE / "EsteriaNaga.bin", "EsteriaAppearance.dll": dll}
    expected = {str(p.ASSET_ARCHIVE_REL): report["archive_before"],
                "EsteriaNaga.bin": report["catalog_before"], "EsteriaAppearance.dll": report["helper_before"]}
    if p.sha256(p.CLIENT_DEFAULT / "Wow.exe") != report["exe_preserved"]:
        raise ValueError("Client executable changed during equipment preparation")
    backup = PACKAGE.parent / "backups" / ("equipment-" + datetime.now().strftime("%Y%m%d-%H%M%S"))
    backup.mkdir(parents=True, exist_ok=False)
    installed = {}
    for name, source in files.items():
        live = p.CLIENT_DEFAULT / name
        if p.sha256(live) != expected[name]:
            raise ValueError("Live client changed since equipment staging: " + name)
        target = backup / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(live, target)
        if p.sha256(target) != expected[name]:
            raise ValueError("Equipment backup hash differs: " + name)
        installed[name] = p.sha256(source)
    report.update(backup=str(backup), before_hashes=expected, installed_hashes=installed)
    n.save(backup / "install-plan.json", report)
    try:
        for name, source in files.items():
            target = p.CLIENT_DEFAULT / name
            temporary = target.with_suffix(target.suffix + ".equipment-next")
            shutil.copy2(source, temporary)
            if p.sha256(temporary) != installed[name]:
                raise ValueError("Equipment install copy differs: " + name)
            os.replace(temporary, target)
        if p.sha256(p.CLIENT_DEFAULT / "Wow.exe") != report["exe_preserved"]:
            raise ValueError("Client executable changed during equipment install")
    except Exception:
        for name in files:
            shutil.copy2(backup / name, p.CLIENT_DEFAULT / name)
        raise
    report.update(status="installed_awaiting_visual_test", race_id=54, server_changes=False)
    n.save(STAGE / "last-install.json", report)
    n.save(backup / "install-report.json", report)
    print("NAGA EQUIPMENT INSTALLED", backup, flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("prepare", "stage", "verify", "install"))
    args = parser.parse_args()
    {"prepare": prepare, "stage": stage, "verify": verify, "install": install}[args.action]()
