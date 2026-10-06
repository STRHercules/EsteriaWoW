"""Stage the native Character Select wing catalog from the installed Cosmetics visual graph."""

import argparse
import ctypes
import hashlib
import json
import math
import os
import shutil
import struct
import subprocess
from datetime import datetime
from pathlib import Path

from cars_mount_pack import DLL_DEFAULT, H, Storm, Wdbc
from wow_xref import Pe

CLIENT = Path(r"G:\3.3.5a - Dev")
STAGE = Path(r"C:\Users\Zach\.codex\tmp\wings-select")
CATALOG = "EsteriaCosmeticWings.bin"
TABLES = ("Spell", "SkillLineAbility", "SpellVisual", "SpellVisualEffectName", "SpellVisualKitModelAttach")
BAKED = {"SpellVisualEffectName", "SpellVisualKitModelAttach"}


def sha256(path):
    with Path(path).open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def open_readonly(storm, path):
    handle = H()
    if not storm.dll.SFileOpenArchive(str(path), 0, 0x100, ctypes.byref(handle)):
        raise OSError(f"Cannot read client archive: {path} ({ctypes.get_last_error()})")
    return handle


def catalog_records(tables):
    """Resolve only wing state-kit attachments, preserving the effective effect scale."""
    spells = sorted({r[2] for r in tables["SkillLineAbility"].values() if r[1] == 779})
    records = []
    for spell in spells:
        row = tables["Spell"][spell]
        visual = tables["SpellVisual"].get(row[131])
        attachments = [r for r in tables["SpellVisualKitModelAttach"].values()
                       if visual and r[1] == visual[4] and r[3] == 16]
        if not attachments:
            continue
        if len(attachments) != 1 or any(attachments[0][4:]):
            raise ValueError(f"Wing {spell} has an unsupported attachment transform")
        effect, strings = tables["SpellVisualEffectName"][attachments[0][2]]
        end = strings.find(b"\0", effect[2])
        if end < effect[2]:
            raise ValueError(f"Wing {spell} has an invalid effect path")
        model = strings[effect[2]:end].decode("ascii")
        scale = struct.unpack("<f", struct.pack("<I", effect[4]))[0]
        if not model or len(model) >= 260 or not math.isfinite(scale) or not 0 < scale <= 100:
            raise ValueError(f"Wing {spell} has an invalid path or scale")
        records.append(dict(spell=spell, visual=row[131], kit=visual[4], model=model, scale=scale))
    if not records:
        raise ValueError("No Cosmetics wing attachments found")
    return records


def prepare(client=CLIENT, stage=STAGE):
    import mechagnome_race_pack as db

    stage.mkdir(parents=True, exist_ok=True)
    storm = Storm(DLL_DEFAULT)
    tables = {name: {} for name in TABLES}
    sources = {}
    archives = (client / "Data/patch-Z.MPQ", client / "Data/enUS/patch-enUS-Z.MPQ")
    for path in archives:
        handle = open_readonly(storm, path)
        try:
            for name in TABLES:
                blob = storm.read(handle, f"DBFilesClient\\{name}.dbc")
                sources[f"{path.name}:{name}"] = hashlib.sha256(blob).hexdigest()
                dbc = Wdbc(blob)
                tables[name].update({r[0]: (r, dbc.strings) if name == "SpellVisualEffectName" else r
                                     for r in dbc.rows})
        finally:
            storm.dll.SFileCloseArchive(handle)
    path = client / "Data/PATCH-X.MPQ"
    handle = open_readonly(storm, path)
    try:
        manifest = storm.read(handle, "wxl-dbc.manifest").decode("utf-8")
        for entry in manifest.splitlines():
            entry = entry.strip()
            if not entry or entry.startswith("#"):
                continue
            name = entry.replace("\\", "/").rsplit("/", 1)[-1].split(".dbc1-", 1)[0]
            # The installed WXL merger does not merge these baked visual tables.
            if name not in tables or name in BAKED:
                continue
            blob = storm.read(handle, entry.replace("/", "\\"))
            sources[entry] = hashlib.sha256(blob).hexdigest()
            dbc = Wdbc(blob)
            tables[name].update({r[0]: r for r in dbc.rows})
        records = catalog_records(tables)
        for record in records:
            model = record["model"]
            if model.lower().endswith(".mdx"):
                model = model[:-4] + ".m2"
            storm.read(handle, model)  # Fail before staging a catalog with missing wing assets.
    finally:
        storm.dll.SFileCloseArchive(handle)
    group = {int(value) for value in db.sql("SELECT spell_id FROM spell_group WHERE id=9100;").split()}
    by_spell = {r["spell"]: r for r in records}
    if not group or not group <= by_spell.keys():
        raise ValueError(f"Exclusive wing group lacks client visuals: {sorted(group - by_spell.keys())}")
    for line in db.sql("SELECT ID,SpellVisualID_1 FROM spell_dbc WHERE ID IN ("
                       + ",".join(map(str, sorted(group))) + ");").splitlines():
        spell, visual = map(int, line.split())
        if by_spell[spell]["visual"] != visual:
            raise ValueError(f"Server/client wing visual mismatch: {spell}")
    pe = Pe(client / "Wow.exe")
    expected = {
        0x0081F8F0: "558bec8b450885c0", 0x00831630: "558bec81ec8c000000",
        0x008274F0: "568bf18b465c33c9", 0x00824ED0: "568bf18306ff8b06",
    }
    for address, fingerprint in expected.items():
        if pe.read_va(address, len(bytes.fromhex(fingerprint))) != bytes.fromhex(fingerprint):
            raise ValueError(f"Native attachment ABI changed at {address:x}")
    if b"ESTERIA_APPEARANCE_NATIVE_V1\0" not in pe.data:
        raise ValueError("Existing native roster/preview hooks are required")
    blob = struct.pack("<3I", 0x31475743, 1, len(records)) + b"".join(
        struct.pack("<IIf260s", r["spell"], 16, r["scale"], r["model"].encode("ascii")) for r in records)
    (stage / CATALOG).write_bytes(blob)
    # Existing native harnesses resolve appearance catalogs beside their executable.
    for catalog in client.glob("Esteria*.bin"):
        if catalog.name == CATALOG:
            continue
        shutil.copy2(catalog, stage / catalog.name)
        digest = sha256(catalog)
        if sha256(stage / catalog.name) != digest:
            raise ValueError(f"Native test catalog copy mismatch: {catalog.name}")
        sources["native-test:" + catalog.name] = digest
    report = dict(records=records, server_wings=len(group), sources=sources,
                  exe_sha256=sha256(client / "Wow.exe"),
                  helper_before_sha256=sha256(client / "EsteriaAppearance.dll"),
                  catalog_sha256=sha256(stage / CATALOG))
    (stage / "catalog-report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Staged {len(records)} wing visuals; {len(group)} server wing spells verified: {stage / CATALOG}")


def install(client=CLIENT, stage=STAGE):
    processes = subprocess.check_output(["tasklist", "/FO", "CSV", "/NH"], text=True).lower()
    if "wow.exe" in processes or "eclipse.exe" in processes:
        raise RuntimeError("Close WoW/Eclipse before installing the native helper")
    report = json.loads((stage / "catalog-report.json").read_text(encoding="utf-8"))
    if sha256(client / "Wow.exe") != report["exe_sha256"]:
        raise ValueError("Client executable changed after staging")
    if sha256(client / "EsteriaAppearance.dll") != report["helper_before_sha256"]:
        raise ValueError("Client helper changed after staging")
    if sha256(stage / CATALOG) != report["catalog_sha256"]:
        raise ValueError("Catalog changed after staging")
    for test in ("TestNativeAppearance.exe", "TestHighmountainMaterials.exe", "TestCustomizationChoices.exe",
                 "TestCosmeticWings.exe"):
        subprocess.run([str(stage / test), str(stage / "EsteriaAppearance.dll")], check=True)
    backup = Path(r"C:\Users\Zach\.codex\backups") / (
        "cosmetic-wings-select-" + datetime.now().strftime("%Y%m%d-%H%M%S"))
    backup.mkdir(parents=True)
    report["backup"] = str(backup)
    report["before"] = {}
    for name in ("EsteriaAppearance.dll", CATALOG):
        live = client / name
        report["before"][name] = sha256(live) if live.exists() else None
        if live.exists():
            shutil.copy2(live, backup / name)
            if sha256(backup / name) != report["before"][name]:
                raise ValueError(f"Rollback copy mismatch: {name}")
    (backup / "install-report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    try:
        for name in (CATALOG, "EsteriaAppearance.dll"):
            temporary = client / (name + ".wings-next")
            shutil.copy2(stage / name, temporary)
            if sha256(temporary) != sha256(stage / name):
                raise ValueError(f"Install copy mismatch: {name}")
            os.replace(temporary, client / name)
    except Exception:
        for name, previous in report["before"].items():
            if previous is not None:
                shutil.copy2(backup / name, client / name)
            elif (client / name).exists():
                (client / name).unlink()
        raise
    report["installed"] = {name: sha256(client / name) for name in ("EsteriaAppearance.dll", CATALOG)}
    (backup / "install-report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Installed native helper and wing catalog; verified rollback: {backup}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("prepare", "install"))
    parser.add_argument("--client", type=Path, default=CLIENT)
    parser.add_argument("--stage", type=Path, default=STAGE)
    args = parser.parse_args()
    globals()[args.action](args.client, args.stage)
