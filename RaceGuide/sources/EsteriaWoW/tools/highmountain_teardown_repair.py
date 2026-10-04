"""Deploy the paired native teardown repair without changing accepted race assets."""

import argparse
import json
import os
import shutil
import subprocess
from datetime import datetime

import highmountain_race_pack as h
import expanded_appearance_pack as native

STAGE = h.STAGE / "teardown-repair"
FILES = ("Wow.exe", "EsteriaAppearance.dll")
PRESERVED = ("Data/patch-Z.MPQ", "Data/enUS/patch-enUS-Z.MPQ", "Data/Patch-R.MPQ",
             "EsteriaAppearance.bin", "EsteriaAppearanceGeometry.bin",
             "EsteriaAppearanceMaterials.bin", "EsteriaHighmountain.bin")


def prepare():
    previous = h.p.load_json(h.STAGE / "last-install.json")
    report = {"source_hashes": {}, "stage_hashes": {}, "preserved_hashes": {}}
    for name in FILES:
        digest = h.p.sha256(h.p.CLIENT_DEFAULT / name)
        if digest != previous["installed_hashes"][name]:
            raise ValueError("Live native file differs from the installation receipt: " + name)
        report["source_hashes"][name] = digest
        report["stage_hashes"][name] = h.p.sha256(STAGE / name)
    for name in PRESERVED:
        report["preserved_hashes"][name] = h.p.sha256(h.p.CLIENT_DEFAULT / name)
    h.save(STAGE / "build-report.json", report)
    return report


def install():
    processes = subprocess.check_output(["tasklist", "/FO", "CSV", "/NH"], text=True).lower()
    if "wow.exe" in processes or "eclipse.exe" in processes:
        raise RuntimeError("Close WoW/Eclipse before replacing the native pair")
    report = h.p.load_json(STAGE / "build-report.json")
    for name in FILES:
        if h.p.sha256(h.p.CLIENT_DEFAULT / name) != report["source_hashes"][name]:
            raise ValueError("Live native file changed: " + name)
        if h.p.sha256(STAGE / name) != report["stage_hashes"][name]:
            raise ValueError("Staged native file changed: " + name)
    for name, digest in report["preserved_hashes"].items():
        if h.p.sha256(h.p.CLIENT_DEFAULT / name) != digest:
            raise ValueError("Accepted asset changed: " + name)
    backup = h.p.Path("C:/Users/Zach/.codex/backups") / (
        "highmountain-teardown-" + datetime.now().strftime("%Y%m%d-%H%M%S"))
    backup.mkdir(parents=True)
    for name in FILES:
        shutil.copy2(h.p.CLIENT_DEFAULT / name, backup / name)
        if h.p.sha256(backup / name) != report["source_hashes"][name]:
            raise ValueError("Native backup differs: " + name)
    try:
        for name in FILES:
            target = h.p.CLIENT_DEFAULT / name
            temporary = target.with_suffix(target.suffix + ".teardown-next")
            shutil.copy2(STAGE / name, temporary)
            if h.p.sha256(temporary) != report["stage_hashes"][name]:
                raise ValueError("Native copy differs: " + name)
            os.replace(temporary, target)
        for name, digest in report["preserved_hashes"].items():
            if h.p.sha256(h.p.CLIENT_DEFAULT / name) != digest:
                raise ValueError("Accepted asset changed during installation: " + name)
    except Exception:
        for name in FILES:
            shutil.copy2(backup / name, h.p.CLIENT_DEFAULT / name)
        raise
    report.update(backup=str(backup), installed_hashes={
        name: h.p.sha256(h.p.CLIENT_DEFAULT / name) for name in FILES})
    h.save(STAGE / "last-install.json", report)
    h.save(backup / "install-report.json", report)
    for directory in (h.STAGE, native.STAGE, h.STAGE / "creator-repair"):
        receipt = directory / "last-install.json"
        current = h.p.load_json(receipt)
        current["installed_hashes"].update(report["installed_hashes"])
        current["latest_highmountain_teardown_backup"] = str(backup)
        if "companion_hashes" in current:
            current["companion_hashes"].update(report["installed_hashes"])
        h.save(receipt, current)
        build = directory / "build-report.json"
        if build.exists():
            current = h.p.load_json(build)
            current.setdefault("companion_hashes", {}).update(report["installed_hashes"])
            h.save(build, current)
    for directory in (h.STAGE, native.STAGE):
        for name in (*FILES, "exe-patch-report.json"):
            shutil.copy2(STAGE / name, directory / name)
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("prepare", "install"))
    args = parser.parse_args()
    print(json.dumps(prepare() if args.command == "prepare" else install(), indent=2))
