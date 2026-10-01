"""Restore Highmountain's full base head and its baked face variants, preserving the installed codec."""

import argparse
import json
import os
import shutil
import struct
import subprocess
from datetime import datetime
from pathlib import Path

from wotlkconv.m2 import parse_skin
from wotlkconv.m2.skin import write_skin

import highmountain_race_pack as h
import retroported_race_pack as p

STAGE = h.STAGE / "head-repair"
RELATIVES = (p.GLOBAL_ARCHIVE_REL, p.LOCALE_ARCHIVE_REL, p.ASSET_ARCHIVE_REL)


def prepare():
    STAGE.mkdir(parents=True, exist_ok=True)
    updates = {}
    report = {"source_hashes": {}, "stage_hashes": {}, "head_meshes": {}}
    for sex in ("male", "female"):
        key = f"{h.PREFIX}\\{sex}\\highmountaintauren{sex}00.skin"
        source = h.art_path(key)
        skin = parse_skin(source.read_bytes())
        changed = 0
        for i, row in enumerate(skin.submeshes):
            if h.v.u16(row, 0) in (3201, 3202):
                row = bytearray(row)
                h.v.patch16(row, 0, 0)
                skin.submeshes[i] = bytes(row)
                changed += 1
        if not changed:
            raise ValueError("Base head repair already applied: " + sex)
        data = write_skin(skin)
        updates[key] = data
        report["head_meshes"][sex] = changed
    catalog = bytearray((p.CLIENT_DEFAULT / "EsteriaHighmountain.bin").read_bytes())
    magic, version, count = struct.unpack_from("<3I", catalog)
    if magic != 0x314D4845 or version != 1 or len(catalog) != 12 + count * 156:
        raise ValueError("Unexpected Highmountain selection catalog")
    face_records = 0
    for index in range(count):
        at = 12 + index * 156
        gender, kind, source = struct.unpack_from("<3I", catalog, at)
        if kind == 2 and source in (3201, 3202):
            struct.pack_into("<I", catalog, at + 8, 0)
            face_records += 1
    if face_records != 9:
        raise ValueError("Expected all five male and four female full-head variants")
    (STAGE / "EsteriaHighmountain.bin").write_bytes(catalog)
    report["face_variant_records"] = face_records
    geometry = bytearray((p.CLIENT_DEFAULT / "EsteriaAppearanceGeometry.bin").read_bytes())
    magic, version, count = struct.unpack_from("<3I", geometry)
    at = 12
    for _ in range(count):
        key = bytes(geometry[at:at + 128]).split(b"\0")[0].decode()
        length = struct.unpack_from("<I", geometry, at + 128)[0]
        skin_key = key[:-3] + "00.skin"
        if skin_key in updates:
            if len(updates[skin_key]) != length:
                raise ValueError("Head visibility repair changed the skin layout")
            geometry[at + 132:at + 132 + length] = updates[skin_key]
        at += 132 + length
    if at != len(geometry):
        raise ValueError("Invalid native geometry catalog length")
    (STAGE / "EsteriaAppearanceGeometry.bin").write_bytes(geometry)
    storm = p.Storm(p.DLL_DEFAULT)
    for relative in RELATIVES:
        live = p.CLIENT_DEFAULT / relative
        stage = STAGE / "pack" / relative
        stage.parent.mkdir(parents=True, exist_ok=True)
        report["source_hashes"][str(relative)] = p.sha256(live)
        shutil.copy2(live, stage)
        storm.replace_archive_entries(stage, updates)
        for key, data in updates.items():
            if p._read_archive_entry(storm, stage, key) != data:
                raise ValueError("Head repair archive readback differs")
        if stage.stat().st_size >= 0x80000000:
            raise ValueError("Head repair exceeds the classic reader boundary")
        report["stage_hashes"][str(relative)] = p.sha256(stage)
    report["companion_hashes"] = {name: p.sha256(STAGE / name) for name in
                                  ("EsteriaHighmountain.bin", "EsteriaAppearanceGeometry.bin")}
    for key, data in updates.items():
        h.art_path(key).write_bytes(data)
    report["entries"] = {key: p.sha256(h.art_path(key)) for key in updates}
    h.save(STAGE / "build-report.json", report)
    return report


def install(backup_label="head"):
    processes = subprocess.check_output(["tasklist", "/FO", "CSV", "/NH"], text=True).lower()
    if "wow.exe" in processes or "eclipse.exe" in processes:
        raise RuntimeError("Close WoW/Eclipse before installing the head repair")
    report = p.load_json(STAGE / "build-report.json")
    prior = p.load_json(h.STAGE / "last-install.json")
    files = {rel: STAGE / "pack" / rel for rel in RELATIVES}
    files.update({Path(name): STAGE / name for name in report["companion_hashes"]})
    for relative, source in files.items():
        expected = report["source_hashes"].get(str(relative), prior["installed_hashes"].get(str(relative)))
        if not expected or p.sha256(p.CLIENT_DEFAULT / relative) != expected:
            raise ValueError("Live file changed before head repair: " + str(relative))
        expected = report["stage_hashes"].get(str(relative), report["companion_hashes"].get(str(relative)))
        if p.sha256(source) != expected:
            raise ValueError("Staged head repair changed")
    backup = Path("C:/Users/Zach/.codex/backups") / (
        "highmountain-" + backup_label + "-" + datetime.now().strftime("%Y%m%d-%H%M%S"))
    backup.mkdir(parents=True)
    for relative in files:
        target = backup / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p.CLIENT_DEFAULT / relative, target)
        if p.sha256(target) != p.sha256(p.CLIENT_DEFAULT / relative):
            raise ValueError("Head repair backup hash mismatch")
    try:
        for relative, source in files.items():
            target = p.CLIENT_DEFAULT / relative
            temporary = target.with_suffix(target.suffix + ".head-next")
            shutil.copy2(source, temporary)
            if p.sha256(source) != p.sha256(temporary):
                raise ValueError("Head repair copy hash mismatch")
            os.replace(temporary, target)
    except Exception:
        for relative in files:
            shutil.copy2(backup / relative, p.CLIENT_DEFAULT / relative)
        raise
    report.update(backup=str(backup), installed_hashes={str(r): p.sha256(p.CLIENT_DEFAULT / r) for r in files})
    h.save(STAGE / "last-install.json", report)
    h.save(backup / "install-report.json", report)
    import expanded_appearance_pack as native
    for path in (h.STAGE / "last-install.json", native.STAGE / "last-install.json"):
        data = p.load_json(path)
        data["installed_hashes"].update(report["installed_hashes"])
        data["latest_highmountain_head_backup"] = str(backup)
        h.save(path, data)
    for relative, source in files.items():
        target = h.STAGE / "pack" / relative if relative in RELATIVES else h.STAGE / relative
        shutil.copy2(source, target)
    main = p.load_json(h.STAGE / "build-report.json")
    main["stage_hashes"].update(report["stage_hashes"])
    main["companion_hashes"].update(report["companion_hashes"])
    h.save(h.STAGE / "build-report.json", main)
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("prepare", "install"))
    args = parser.parse_args()
    print(json.dumps(prepare() if args.command == "prepare" else install(), indent=2))
