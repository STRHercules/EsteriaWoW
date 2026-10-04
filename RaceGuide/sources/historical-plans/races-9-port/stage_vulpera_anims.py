"""Stage the donor's Vulpera external animations, which match the model we ship.

`stage_eunoia_vulpera.py` copied Eunoia's HD model, its four `.skin` LODs and the textures,
but not the external `.anim` files. Ours are the older set from `patch-CHA.mpq` and differ in
size and content for all 48 animations per gender (e.g. male `0060-00.anim`: 102,624 bytes vs
the donor's 196,640). The client loads sequences out of those files, so a mismatched set gives
it garbage track data - the crash both times was inside the keyframe search
(`M2.FindTrackKey`, `0x8285EB`, binary search over the key time array with a wild index).

This copies every `<stem>%04d-%02d.anim` the donor has into `Patch-Y`, so the HD model and its
animations come from the same source again.
"""

from __future__ import annotations

import argparse
import ctypes
import datetime
import hashlib
import shutil
import sys
import time
from pathlib import Path

REPO = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW")
sys.path.insert(0, str(REPO / "tools"))

from cars_mount_pack import DLL_DEFAULT, H, Storm  # noqa: E402

DONOR = Path(r"G:\Eunoia\Client\data")
DONOR_ARCHIVES = ("Patch-5.mpq", "Patch-4.mpq", "Patch-9.mpq", "Patch-8.mpq", "patch-I.mpq", "Patch-6.mpq", "Patch-7.mpq")
PATCH_Y = REPO / "3.3.5a - Dev/Data/Patch-Y.MPQ"
BACKUP_ROOT = REPO / "3.3.5a - Dev/Backups"
STEMS = (
    r"character\vulpera\male\vulperamale",
    r"character\vulpera\female\vulperafemale",
)
MAX_INDEX = 1500
MAX_VARIATION = 4


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    storm = Storm(DLL_DEFAULT)
    handles = []
    for name in DONOR_ARCHIVES:
        path = DONOR / name
        if not path.is_file():
            continue
        handle = H()
        if storm.dll.SFileOpenArchive(str(path), 0, 0x100, ctypes.byref(handle)):
            handles.append((name, handle))
    if not handles:
        raise SystemExit("no donor archives could be opened")

    staged: dict[str, bytes] = {}
    started = time.time()
    try:
        for stem in STEMS:
            found = 0
            for index in range(MAX_INDEX):
                for variation in range(MAX_VARIATION):
                    key = f"{stem}{index:04d}-{variation:02d}.anim"
                    for name, handle in handles:
                        try:
                            payload = storm.read(handle, key)
                        except Exception:
                            continue
                        staged[key] = payload
                        found += 1
                        break
            print(f"{stem}: {found} donor anim files (elapsed {time.time() - started:5.1f}s)")
    finally:
        for _name, handle in handles:
            storm.dll.SFileCloseArchive(handle)

    print(f"staged entries: {len(staged)}  total bytes: {sum(len(v) for v in staged.values()):,}")
    if not staged:
        raise SystemExit("nothing found")
    if args.dry_run:
        print("dry run - Patch-Y untouched")
        return

    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = BACKUP_ROOT / f"patch-y-before-vulpera-anims-{stamp}"
    backup.mkdir(parents=True, exist_ok=True)
    shutil.copy2(PATCH_Y, backup / "Patch-Y.MPQ")
    storm.replace_archive_entries(PATCH_Y, staged)
    print(f"Patch-Y updated ({PATCH_Y.stat().st_size:,} bytes), backup {backup}")


if __name__ == "__main__":
    main()
