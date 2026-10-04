"""Repair Earthen backgrounds, belt selection and native gameplay appearance without server/data migration."""

import argparse
import json
import os
import shutil
import struct
import subprocess
from datetime import datetime
from pathlib import Path

from luaparser import ast
from wotlkconv.m2 import parse_m2, parse_skin
from wotlkconv.m2.skin import write_skin

import earthen_race_pack as e

STAGE = e.STAGE / "touchups"
RELATIVES = (e.p.GLOBAL_ARCHIVE_REL, e.p.LOCALE_ARCHIVE_REL, e.p.ASSET_ARCHIVE_REL)


def patch_glue(name, text):
    if name == "GlueParent.lua" and '["EARTHENHORDE"] = true,' not in text:
        anchor = '["HIGHMOUNTAINTAUREN"] = true,'
        if text.count(anchor) != 1:
            raise ValueError("Horde background anchor changed")
        text = text.replace(anchor, anchor + '\n        ["EARTHENHORDE"] = true,', 1)
    if name == "CharacterCreate.lua" and 'local earthenChoiceText' not in text:
        anchor = '            _G["CharacterCustomizationButtonFrame"..i.."Text"]:SetText('
        addition = '''            local earthenChoiceText = nil;
            if (CharacterCreate.selectedRaceID == 48 or CharacterCreate.selectedRaceID == 49) and label == "Belt" then
                earthenChoiceText = value == 0 and "  None" or "  Gem";
            end
'''
        if text.count(anchor) != 1:
            raise ValueError("Native control label anchor changed")
        text = text.replace(anchor, addition + anchor, 1)
        old = '..(count and "  "..(value+1).."/"..count or "")'
        if text.count(old) != 1:
            raise ValueError("Native value-label anchor changed")
        text = text.replace(old, '..(earthenChoiceText or (count and "  "..(value+1).."/"..count or ""))', 1)
    ast.parse(text)
    return text


def prepare():
    prior = e.p.load_json(e.STAGE / "last-install.json")
    report = {"source_hashes": {}, "stage_hashes": {}, "companion_hashes": {}, "updates": [], "models": {}}
    storm = e.p.Storm(e.p.DLL_DEFAULT)
    # Read the verified offline copies while the user keeps WoW open for diagnosis.
    for relative in RELATIVES:
        digest = e.p.sha256(e.p.CLIENT_DEFAULT / relative)
        if digest != prior["installed_hashes"][str(relative)]:
            raise ValueError("Live archive differs from its receipt: " + str(relative))
        if e.p.sha256(e.STAGE / "pack" / relative) != digest:
            raise ValueError("Offline archive differs from live: " + str(relative))
        report["source_hashes"][str(relative)] = digest
    updates = {}
    for name in ("GlueParent.lua", "CharacterCreate.lua"):
        key = e.p.GLUE_ROOT + name
        text = e.p._read_archive_entry(storm, e.STAGE / "pack" / e.p.LOCALE_ARCHIVE_REL, key).decode()
        updates[key] = patch_glue(name, text).encode()
    for sex in ("male", "female"):
        root = f"{e.PREFIX}\\{sex}\\earthendwarf{sex}"
        model = parse_m2(e.p._read_archive_entry(storm, e.STAGE / "pack" / e.p.GLOBAL_ARCHIVE_REL, root + ".m2"))
        key = root + "00.skin"
        skin = parse_skin(e.p._read_archive_entry(storm, e.STAGE / "pack" / e.p.GLOBAL_ARCHIVE_REL, key))
        changed = []
        for index, mesh in enumerate(skin.submeshes):
            if e.v.u16(mesh, 0) != 1805:
                continue
            batches = [b for b in skin.batches if e.v.u16(b, 4) == index]
            slots = [model.textures[i]["type"] for b in batches for i in
                     model.texture_combos[e.v.u16(b, 16):e.v.u16(b, 16) + e.v.u16(b, 14)]]
            if slots != [9, 0]:
                continue  # Preserve the ordinary body/armor mesh with the same source geoset ID.
            mesh = bytearray(mesh)
            e.v.patch16(mesh, 0, 4105)
            skin.submeshes[index] = bytes(mesh)
            changed.append(index)
        if len(changed) != 1:
            raise ValueError("Expected one Gem belt collection mesh per gender")
        updates[key] = write_skin(skin)
        report["models"][sex] = {"belt_mesh": changed[0], "old_geoset": 1805, "new_geoset": 4105}
    geometry = bytearray((e.p.CLIENT_DEFAULT / "EsteriaAppearanceGeometry.bin").read_bytes())
    at = 12
    while at < len(geometry):
        key = bytes(geometry[at:at + 128]).split(b"\0")[0].decode()
        length = struct.unpack_from("<I", geometry, at + 128)[0]
        skin_key = key[:-3] + "00.skin"
        if skin_key in updates:
            assert length == len(updates[skin_key])
            geometry[at + 132:at + 132 + length] = updates[skin_key]
        at += 132 + length
    assert at == len(geometry)
    (STAGE / "EsteriaAppearanceGeometry.bin").write_bytes(geometry)
    catalog = bytearray((e.p.CLIENT_DEFAULT / "EsteriaEarthen.bin").read_bytes())
    changed = 0
    for offset in range(12, len(catalog), 156):
        if struct.unpack_from("<2I", catalog, offset + 4) == (0, 18):
            value = struct.unpack_from("<I", catalog, offset + 12)[0]
            struct.pack_into("<2I", catalog, offset + 8, 41, value + 2300)
            changed += 1
    assert changed == 4
    (STAGE / "EsteriaEarthen.bin").write_bytes(catalog)
    for relative in RELATIVES:
        target = STAGE / "pack" / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(e.STAGE / "pack" / relative, target)
        storm.replace_archive_entries(target, updates)
        for key, data in updates.items():
            assert e.p._read_archive_entry(storm, target, key) == data
        assert target.stat().st_size < 0x80000000
        report["stage_hashes"][str(relative)] = e.p.sha256(target)
    for name in ("EsteriaAppearance.dll", "EsteriaAppearanceGeometry.bin", "EsteriaEarthen.bin"):
        report["source_hashes"][name] = e.p.sha256(e.p.CLIENT_DEFAULT / name)
        report["companion_hashes"][name] = e.p.sha256(STAGE / name)
    report["preserved_exe"] = e.p.sha256(e.p.CLIENT_DEFAULT / "Wow.exe")
    report["updates"] = sorted(updates)
    e.save(STAGE / "build-report.json", report)
    return {"models": report["models"], "updated_entries": len(updates)}


def validate():
    report = e.p.load_json(STAGE / "build-report.json")
    for name in ("TestNativeAppearance.exe", "TestHighmountainMaterials.exe"):
        subprocess.run([str(STAGE / name), str(STAGE / "EsteriaAppearance.dll")], check=True)
    old = (e.p.CLIENT_DEFAULT / "EsteriaEarthen.bin").read_bytes()
    new = (STAGE / "EsteriaEarthen.bin").read_bytes()
    assert len(old) == len(new)
    for offset in range(12, len(old), 156):
        assert old[offset:offset + 8] == new[offset:offset + 8]
        assert old[offset + 16:offset + 156] == new[offset + 16:offset + 156]
        if struct.unpack_from("<2I", old, offset + 4) != (0, 18):
            assert old[offset:offset + 156] == new[offset:offset + 156]
    for key in report["updates"]:
        if key.endswith(".lua"):
            data = e.p._read_archive_entry(e.p.Storm(e.p.DLL_DEFAULT), STAGE / "pack" / e.p.LOCALE_ARCHIVE_REL, key)
            ast.parse(data.decode())
        elif key.endswith(".skin"):
            storm = e.p.Storm(e.p.DLL_DEFAULT)
            receipt = STAGE / "last-install.json"
            base = (Path(e.p.load_json(receipt)["backup"]) if receipt.exists() else e.STAGE / "pack")
            before = parse_skin(e.p._read_archive_entry(storm, base / e.p.GLOBAL_ARCHIVE_REL, key))
            after = parse_skin(e.p._read_archive_entry(storm, STAGE / "pack" / e.p.GLOBAL_ARCHIVE_REL, key))
            assert before.vertices == after.vertices and before.indices == after.indices
            assert before.bones == after.bones and before.batches == after.batches
            changes = 0
            for old_mesh, new_mesh in zip(before.submeshes, after.submeshes, strict=True):
                assert old_mesh[2:] == new_mesh[2:]
                if old_mesh[:2] != new_mesh[:2]:
                    assert e.v.u16(old_mesh, 0) == 1805 and e.v.u16(new_mesh, 0) == 4105
                    changes += 1
            assert changes == 1
    return {"verified": True, "checks": "saved byte regression, both factions, belt-only geometry/catalog changes, Lua, native lifetime"}


def refresh_native():
    import expanded_appearance_pack as native
    candidate = e.STAGE / "late-fields"
    for test in ("TestNativeAppearance.exe", "TestHighmountainMaterials.exe"):
        subprocess.run([str(candidate / test), str(candidate / "EsteriaAppearance.dll")], check=True)
    processes = subprocess.check_output(["tasklist", "/FO", "CSV", "/NH"], text=True).lower()
    if "wow.exe" in processes or "eclipse.exe" in processes:
        raise RuntimeError("Close WoW/Eclipse before replacing the native helper")
    prior = e.p.load_json(e.STAGE / "last-install.json")
    live = e.p.CLIENT_DEFAULT / "EsteriaAppearance.dll"
    before = e.p.sha256(live)
    assert before == prior["installed_hashes"][live.name]
    backup = Path("C:/Users/Zach/.codex/backups") / ("earthen-native-" + datetime.now().strftime("%Y%m%d-%H%M%S"))
    backup.mkdir(parents=True)
    shutil.copy2(live, backup / live.name)
    assert e.p.sha256(backup / live.name) == before
    preserved = {str(rel): e.p.sha256(e.p.CLIENT_DEFAULT / rel) for rel in (*RELATIVES, Path("Wow.exe"))}
    target = candidate / live.name
    temporary = live.with_suffix(".dll.earthen-next")
    shutil.copy2(target, temporary)
    assert e.p.sha256(temporary) == e.p.sha256(target)
    os.replace(temporary, live)
    after = e.p.sha256(live)
    assert after == e.p.sha256(target)
    assert all(e.p.sha256(e.p.CLIENT_DEFAULT / name) == value for name, value in preserved.items())
    for directory in (e.STAGE, e.h.STAGE, native.STAGE, STAGE):
        receipt = directory / "last-install.json"
        if receipt.exists():
            report = e.p.load_json(receipt)
            report["installed_hashes"][live.name] = after
            report["latest_earthen_native_backup"] = str(backup)
            e.save(receipt, report)
    for directory in (e.STAGE, STAGE):
        shutil.copy2(target, directory / live.name)
    report = {"backup": str(backup), "before_sha256": before, "installed_sha256": after,
              "preserved_hashes": preserved, "checks": "late sanitizer overwrite, both factions, teardown: PASS"}
    e.save(backup / "install-report.json", report)
    e.save(candidate / "last-install.json", report)
    return report


def feet():
    import expanded_appearance_pack as native
    live = e.p.CLIENT_DEFAULT / "EsteriaEarthen.bin"
    before = live.read_bytes()
    magic, version, count = struct.unpack_from("<3I", before)
    assert magic == 0x314D4845 and version == 1 and len(before) == 12 + count * 156
    assert not any(struct.unpack_from("<2I", before, at + 4) == (0, 20)
                   for at in range(12, len(before), 156)), "Foot group already selected"
    extra = b"".join(struct.pack("<7I", gender, 0, 20, 2001, 0xffffffff, 0xffffffff, 0xffffffff) + bytes(128)
                     for gender in (0, 1))
    after = struct.pack("<3I", magic, version, count + 2) + before[12:] + extra
    assert after[12:len(before)] == before[12:]
    for sex in ("male", "female"):
        key = f"{e.PREFIX}\\{sex}\\earthendwarf{sex}00.skin"
        skin = parse_skin(e.path(e.ART, key).read_bytes())
        assert {2001 + i for i in range(8)} <= {e.v.u16(m, 0) for m in skin.submeshes}
    candidate = e.STAGE / "feet"
    candidate.mkdir(exist_ok=True)
    (candidate / live.name).write_bytes(after)
    processes = subprocess.check_output(["tasklist", "/FO", "CSV", "/NH"], text=True).lower()
    if "wow.exe" in processes or "eclipse.exe" in processes:
        raise RuntimeError("Foot selector is staged; close WoW/Eclipse to install it")
    backup = Path("C:/Users/Zach/.codex/backups") / ("earthen-feet-" + datetime.now().strftime("%Y%m%d-%H%M%S"))
    backup.mkdir(parents=True)
    shutil.copy2(live, backup / live.name)
    assert (backup / live.name).read_bytes() == before
    assert live.read_bytes() == before
    temporary = live.with_suffix(".bin.earthen-feet-next")
    temporary.write_bytes(after)
    assert temporary.read_bytes() == after
    os.replace(temporary, live)
    assert live.read_bytes() == after
    digest = e.p.sha256(live)
    for directory in (e.STAGE, e.h.STAGE, native.STAGE, STAGE):
        receipt = directory / "last-install.json"
        if receipt.exists():
            report = e.p.load_json(receipt)
            report["installed_hashes"][live.name] = digest
            report["latest_earthen_feet_backup"] = str(backup)
            e.save(receipt, report)
    for directory in (e.STAGE, STAGE, e.STAGE / "late-fields"):
        shutil.copy2(live, directory / live.name)
    report = {"backup": str(backup), "installed_hash": digest, "both_genders": True,
              "visible_foot_geoset": 2001, "hidden_alternatives": list(range(2002, 2009)),
              "preserved_previous_records": count, "new_records": 2}
    e.save(candidate / "last-install.json", report)
    e.save(backup / "install-report.json", report)
    return report


def install():
    import expanded_appearance_pack as native
    validate()
    processes = subprocess.check_output(["tasklist", "/FO", "CSV", "/NH"], text=True).lower()
    if "wow.exe" in processes or "eclipse.exe" in processes:
        raise RuntimeError("Close WoW/Eclipse before installing the checked touchups")
    report = e.p.load_json(STAGE / "build-report.json")
    files = {str(rel): STAGE / "pack" / rel for rel in RELATIVES}
    files.update({name: STAGE / name for name in report["companion_hashes"]})
    backup = Path("C:/Users/Zach/.codex/backups") / ("earthen-touchup-" + datetime.now().strftime("%Y%m%d-%H%M%S"))
    backup.mkdir(parents=True)
    for name, staged in files.items():
        live = e.p.CLIENT_DEFAULT / name
        assert e.p.sha256(live) == report["source_hashes"][name], name
        assert e.p.sha256(staged) == report["stage_hashes"].get(name, report["companion_hashes"].get(name)), name
        target = backup / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(live, target)
        assert e.p.sha256(target) == report["source_hashes"][name], name
    try:
        for name, staged in files.items():
            target = e.p.CLIENT_DEFAULT / name
            temporary = target.with_suffix(target.suffix + ".earthen-touchup-next")
            shutil.copy2(staged, temporary)
            assert e.p.sha256(temporary) == e.p.sha256(staged), name
            os.replace(temporary, target)
    except Exception:
        for name in files:
            shutil.copy2(backup / name, e.p.CLIENT_DEFAULT / name)
        raise
    assert e.p.sha256(e.p.CLIENT_DEFAULT / "Wow.exe") == report["preserved_exe"]
    report.update(backup=str(backup), installed_hashes={name: e.p.sha256(e.p.CLIENT_DEFAULT / name) for name in files})
    e.save(STAGE / "last-install.json", report)
    e.save(backup / "install-report.json", report)
    for directory in (e.STAGE, e.h.STAGE, native.STAGE):
        receipt = directory / "last-install.json"
        if not receipt.exists():
            continue
        prior = e.p.load_json(receipt)
        prior["installed_hashes"].update(report["installed_hashes"])
        prior["latest_earthen_touchup_backup"] = str(backup)
        e.save(receipt, prior)
    for relative in RELATIVES:
        shutil.copy2(STAGE / "pack" / relative, e.STAGE / "pack" / relative)
    for name in report["companion_hashes"]:
        shutil.copy2(STAGE / name, e.STAGE / name)
    storm = e.p.Storm(e.p.DLL_DEFAULT)
    for key in report["updates"]:
        target = e.path(e.ART, key)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(e.p._read_archive_entry(storm, e.p.CLIENT_DEFAULT / e.p.GLOBAL_ARCHIVE_REL, key))
    return {"installed": True, "backup": str(backup), "live_acceptance": "pending"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("prepare", "validate", "install", "refresh-native", "feet"))
    args = parser.parse_args()
    print(json.dumps({"prepare": prepare, "validate": validate, "install": install,
                      "refresh-native": refresh_native, "feet": feet}[args.action](), indent=2))
