"""Stage the ported models' external .anim files from Eunoia into Patch-Y.

`port_race.py` deliberately left these out (`STAGE_ANIMS = False`), but Eunoia's HD
models do carry external sequences (e.g. character\\voidelf\\male\\voidelfmale0060-00.anim),
and the client loads them during model init. Each staged model gets the full set under
its own name so the client never sees a mismatched animation set.
"""

from __future__ import annotations

import argparse
import ctypes
import datetime
import shutil
import sys
import time
from pathlib import Path

REPO = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW")
sys.path.insert(0, str(REPO / ".agents/plans/races-9-port"))
sys.path.insert(0, str(REPO / "tools"))

from cars_mount_pack import DLL_DEFAULT, H, Storm  # noqa: E402
from port_race import RACES  # noqa: E402

EUNOIA = Path(r"G:\Eunoia\Client\data")
ARCHIVES = ("Patch-5.mpq", "Patch-4.mpq", "Patch-9.mpq", "Patch-8.mpq", "patch-I.mpq", "Patch-6.mpq", "Patch-7.mpq")
PATCH_Y = REPO / "3.3.5a - Dev/Data/Patch-Y.MPQ"
BACKUP_ROOT = REPO / "3.3.5a - Dev/Backups"
MAX_INDEX = 1400
MAX_VARIATION = 4
# client-filestring aliases created by stage_filestring_model_aliases.py
ALIASES = {
    "CHARACTER\\Naga_\\male\\kultiranmale": "Character\\KulTiran\\Male\\KulTiranMale",
    "CHARACTER\\Naga_\\Female\\kultiranfemale": "Character\\KulTiran\\Female\\KulTiranFemale",
    "Character\\BloodElf_Dh\\Male\\BloodElfMale_DH": "Character\\Illidari\\Male\\IllidariMale",
    "Character\\BloodElf_Dh\\Female\\BloodElfFemale_DH": "Character\\Illidari\\Female\\IllidariFemale",
}


def read_from_eunoia(storm: Storm, handles: dict, name: str) -> bytes | None:
    for archive in ARCHIVES:
        handle = handles.get(archive)
        if handle is None:
            handle = H()
            if not storm.dll.SFileOpenArchive(str(EUNOIA / archive), 0, 0x100, ctypes.byref(handle)):
                handles[archive] = None
                continue
            handles[archive] = handle
        if handle is None:
            continue
        try:
            return storm.read(handle, name)
        except Exception:
            continue
    return None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    storm = Storm(DLL_DEFAULT)
    handles: dict = {}
    staged: dict[str, bytes] = {}
    started = time.time()

    for spec in RACES:
        for gender in ("male", "female"):
            source_stem, target_stem, *_ = spec[gender]
            found = 0
            for index in range(MAX_INDEX):
                name = f"{source_stem}{index:04d}-00.anim"
                payload = read_from_eunoia(storm, handles, name)
                if payload is None:
                    continue
                found += 1
                stems = [target_stem]
                alias = ALIASES.get(target_stem)
                if alias:
                    stems.append(alias)
                for stem in stems:
                    staged[f"{stem}{index:04d}-00.anim"] = payload
                for variation in range(1, MAX_VARIATION):
                    variant = f"{source_stem}{index:04d}-{variation:02d}.anim"
                    variant_payload = read_from_eunoia(storm, handles, variant)
                    if variant_payload is None:
                        continue
                    for stem in stems:
                        staged[f"{stem}{index:04d}-{variation:02d}.anim"] = variant_payload
            print(f"{spec['name']:<18} {gender:<6} anim files: {found}  (elapsed {time.time() - started:5.1f}s)")

    for handle in handles.values():
        if handle:
            storm.dll.SFileCloseArchive(handle)

    print(f"staged entries: {len(staged)}  total bytes: {sum(len(v) for v in staged.values()):,}")
    if not staged:
        raise SystemExit("nothing found")
    if args.dry_run:
        print("dry run - Patch-Y untouched")
        return

    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = BACKUP_ROOT / f"patch-y-before-race-anims-{stamp}"
    backup.mkdir(parents=True, exist_ok=True)
    shutil.copy2(PATCH_Y, backup / "Patch-Y.MPQ")
    storm.replace_archive_entries(PATCH_Y, staged)
    print(f"Patch-Y updated ({PATCH_Y.stat().st_size:,} bytes), backup {backup}")


if __name__ == "__main__":
    main()
