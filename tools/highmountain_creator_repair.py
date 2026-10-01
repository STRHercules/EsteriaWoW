"""Repair Race46 material access and repack its installed archive payloads for the classic reader."""

import argparse
import hashlib
import json
import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

import highmountain_integration as integration
import highmountain_race_pack as h
import retroported_race_pack as p

STAGE = h.STAGE / "creator-repair"
RELATIVES = (p.GLOBAL_ARCHIVE_REL, p.LOCALE_ARCHIVE_REL, p.ASSET_ARCHIVE_REL)


def paletted_compositor(bitmap):
    """Use Pillow's native quantizer, with the working indexed BLP header/mip contract."""
    return integration.paletted_compositor(bitmap)


def prepare():
    STAGE.mkdir(parents=True, exist_ok=True)
    updates = {}
    digest_cache = {}
    storm = p.Storm(p.DLL_DEFAULT)
    original = storm.open_archive(p.CLIENT_DEFAULT / p.GLOBAL_ARCHIVE_REL)
    try:
        for sex in ("male", "female"):
            root = h.art_path(f"{h.PREFIX}\\{sex}")
            paths = sorted([*root.glob("body*.blp"), *root.glob("faceupper*.blp"), *root.glob("facelower*.blp")])
            for i, path in enumerate(paths, 1):
                key = "\\".join(path.relative_to(h.ART).parts)
                bitmap = p.Blp.parse(storm.read(original, key)).decode_level(0)
                digest = hashlib.sha256(bytes(bitmap.data)).digest()
                if digest not in digest_cache:
                    digest_cache[digest] = paletted_compositor(bitmap)
                converted = digest_cache[digest]
                updates[key] = converted
                path.write_bytes(converted)
                if i % 100 == 0:
                    print("COMPOSITOR", sex, i, len(paths), flush=True)
    finally:
        storm.dll.SFileCloseArchive(original)
    report = {"source_hashes": {}, "stage_hashes": {}, "compositor_entries": len(updates),
              "unique_compositor_palettes": len(digest_cache), "archives": {}}
    for relative in RELATIVES:
        live = p.CLIENT_DEFAULT / relative
        source = STAGE / "source" / relative
        source.parent.mkdir(parents=True, exist_ok=True)
        report["source_hashes"][str(relative)] = p.sha256(live)
        shutil.copy2(live, source)
        storm.replace_archive_entries(source, updates)
        # Recompress every entry while retaining all unrelated bytes and archive precedence.
        target = STAGE / "pack" / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        print("COMPRESS", relative, flush=True)
        p.rebuild_archive_streaming(storm, source, target, compress=True)
        size = target.stat().st_size
        if size >= 0x80000000:
            raise ValueError(f"Classic reader archive still exceeds 2 GiB: {relative} ({size})")
        before = storm.open_archive(source)
        after = storm.open_archive(target)
        try:
            entries = [name for name, *_ in storm.list_files(before)
                       if name.casefold() not in ("(listfile)", "(attributes)")]
            for name in entries:
                if storm.read(before, name) != storm.read(after, name):
                    raise ValueError("Compressed readback differs: " + name)
            report["archives"][str(relative)] = {"bytes": size, "verified_entries": len(entries)}
        finally:
            storm.dll.SFileCloseArchive(before)
            storm.dll.SFileCloseArchive(after)
        report["stage_hashes"][str(relative)] = p.sha256(target)
    report["companion_hashes"] = {name: p.sha256(h.STAGE / name) for name in ("Wow.exe", "EsteriaAppearance.dll")}
    h.save(STAGE / "build-report.json", report)
    return report


def install():
    processes = subprocess.check_output(["tasklist", "/FO", "CSV", "/NH"], text=True).lower()
    if "wow.exe" in processes or "eclipse.exe" in processes:
        raise RuntimeError("WoW/Eclipse must be closed for the creator repair")
    report = p.load_json(STAGE / "build-report.json")
    prior = p.load_json(h.STAGE / "last-install.json")
    files = {relative: STAGE / "pack" / relative for relative in RELATIVES}
    files.update({Path(name): h.STAGE / name for name in report["companion_hashes"]})
    for relative, source in files.items():
        live = p.CLIENT_DEFAULT / relative
        expected = report["source_hashes"].get(str(relative), prior["installed_hashes"].get(str(relative)))
        if not expected or p.sha256(live) != expected:
            raise ValueError("Installed file changed before repair: " + str(relative))
        expected = report["stage_hashes"].get(str(relative), report["companion_hashes"].get(str(relative)))
        if p.sha256(source) != expected:
            raise ValueError("Staged file changed before repair: " + str(relative))
    backup = Path("C:/Users/Zach/.codex/backups") / (
        "highmountain-creator-" + datetime.now().strftime("%Y%m%d-%H%M%S"))
    backup.mkdir(parents=True)
    for relative in files:
        source = p.CLIENT_DEFAULT / relative
        target = backup / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        if p.sha256(source) != p.sha256(target):
            raise RuntimeError("Repair backup hash mismatch")
    try:
        for relative, source in files.items():
            target = p.CLIENT_DEFAULT / relative
            temporary = target.with_suffix(target.suffix + ".creator-repair-next")
            shutil.copy2(source, temporary)
            if p.sha256(temporary) != p.sha256(source):
                raise RuntimeError("Repair copy hash mismatch")
            os.replace(temporary, target)
            print("INSTALLED", relative, flush=True)
    except Exception:
        for relative in files:
            shutil.copy2(backup / relative, p.CLIENT_DEFAULT / relative)
        raise
    report.update(backup=str(backup), installed_hashes={str(r): p.sha256(p.CLIENT_DEFAULT / r) for r in files})
    h.save(backup / "install-report.json", report)
    h.save(STAGE / "last-install.json", report)
    prior["installed_hashes"].update(report["installed_hashes"])
    prior["latest_creator_repair"] = str(backup)
    h.save(h.STAGE / "last-install.json", prior)
    import expanded_appearance_pack as native
    combined = p.load_json(native.STAGE / "last-install.json")
    combined["installed_hashes"].update(report["installed_hashes"])
    combined["latest_highmountain_creator_backup"] = str(backup)
    h.save(native.STAGE / "last-install.json", combined)
    return report


def refresh_native(name="EsteriaAppearance.dll"):
    if name not in ("EsteriaAppearance.dll", "Wow.exe"):
        raise ValueError("Unexpected native repair target")
    processes = subprocess.check_output(["tasklist", "/FO", "CSV", "/NH"], text=True).lower()
    if "wow.exe" in processes or "eclipse.exe" in processes:
        raise RuntimeError("WoW/Eclipse must be closed for the native refresh")
    report = p.load_json(STAGE / "last-install.json")
    live = p.CLIENT_DEFAULT / name
    if p.sha256(live) != report["installed_hashes"][name]:
        raise ValueError("Installed native file changed before its refresh")
    backup = Path("C:/Users/Zach/.codex/backups") / (
        "highmountain-native-" + datetime.now().strftime("%Y%m%d-%H%M%S"))
    backup.mkdir(parents=True)
    shutil.copy2(live, backup / name)
    if p.sha256(live) != p.sha256(backup / name):
        raise RuntimeError("Helper refresh backup differs")
    temporary = live.with_suffix(live.suffix + ".creator-next")
    shutil.copy2(h.STAGE / name, temporary)
    if p.sha256(temporary) != p.sha256(h.STAGE / name):
        raise RuntimeError("Helper refresh stage differs")
    os.replace(temporary, live)
    digest = p.sha256(live)
    report["installed_hashes"][name] = digest
    report["companion_hashes"][name] = digest
    report["native_refresh_backup"] = str(backup)
    h.save(STAGE / "last-install.json", report)
    build = p.load_json(STAGE / "build-report.json")
    build["companion_hashes"][name] = digest
    h.save(STAGE / "build-report.json", build)
    import expanded_appearance_pack as native
    for path in (h.STAGE / "last-install.json", native.STAGE / "last-install.json"):
        current = p.load_json(path)
        current["installed_hashes"][name] = digest
        current["latest_highmountain_native_backup"] = str(backup)
        h.save(path, current)
    h.save(backup / "install-report.json", report)
    return {"file": name, "sha256": digest, "backup": str(backup)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("prepare", "install", "refresh-helper", "refresh-executable"))
    args = parser.parse_args()
    commands = {"prepare": prepare, "install": install, "refresh-helper": refresh_native,
                "refresh-executable": lambda: refresh_native("Wow.exe")}
    print(json.dumps(commands[args.command](), indent=2))
