"""Stage the donor's *player* Eredar model over the NPC one our race currently uses.

Race 16 points at `Character\Eredar\{Male,Female}\Eredar{Male,Female}.m2`, which the port
staged as a creature-style model: it has no player geoset layout and no helm attachments, so
every helmet - hood geoset or attached model - comes out as the client's error box. Eunoia's
own Eredar race uses `character\eredar\<gender>\race_eredar<gender>.m2`, a regular player model.

This copies that model, its `.mdx` twin, its four `.skin` LODs and its external `.anim` set over
our path (nothing else in the client references `Character\Eredar\` - the NPC eredar live under
`Creature\Eredar\`).
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
DONOR_ARCHIVES = ("Patch-5.mpq", "Patch-4.mpq", "Patch-9.mpq", "Patch-8.mpq", "patch-I.mpq",
                  "Patch-6.mpq", "Patch-7.mpq")
PATCH_D = REPO / "3.3.5a - Dev/Data/Patch-D.MPQ"
BACKUP_ROOT = REPO / "3.3.5a - Dev/Backups"
SOURCE_STEMS = {
    "male": r"character\eredar\male\race_eredarmale",
    "female": r"character\eredar\female\race_eredarfemale",
}
TARGET_STEMS = {
    "male": r"Character\Eredar\Male\EredarMale",
    "female": r"Character\Eredar\Female\EredarFemale",
}
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
        raise SystemExit("no donor archives opened")

    def read(key: str) -> tuple[str, bytes] | None:
        for name, handle in handles:
            try:
                return name, storm.read(handle, key)
            except Exception:
                continue
        return None

    staged: dict[str, bytes] = {}
    try:
        for gender, source in SOURCE_STEMS.items():
            target = TARGET_STEMS[gender]
            for suffix in (".m2", ".mdx", "00.skin", "01.skin", "02.skin", "03.skin"):
                found = read(f"{source}{suffix}")
                if found is None:
                    print(f"  {gender}{suffix}: donor file missing")
                    continue
                staged[f"{target}{suffix}"] = found[1]
            anims = 0
            started = time.time()
            for index in range(MAX_INDEX):
                for variation in range(MAX_VARIATION):
                    key = f"{source}{index:04d}-{variation:02d}.anim"
                    found = read(key)
                    if found is None:
                        continue
                    staged[f"{target}{index:04d}-{variation:02d}.anim"] = found[1]
                    anims += 1
            print(f"  {gender}: {anims} anim files (elapsed {time.time() - started:4.1f}s)")
    finally:
        for _name, handle in handles:
            storm.dll.SFileCloseArchive(handle)

    print(f"staged entries: {len(staged)}  total bytes: {sum(len(v) for v in staged.values()):,}")
    for key in sorted(k for k in staged if k.endswith(".m2")):
        print(f"  {key}: {len(staged[key]):,} bytes sha1={hashlib.sha1(staged[key]).hexdigest()[:12]}")
    if args.dry_run:
        print("dry run - Patch-D untouched")
        return

    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = BACKUP_ROOT / f"patch-d-before-eredar-player-model-{stamp}"
    backup.mkdir(parents=True, exist_ok=True)
    shutil.copy2(PATCH_D, backup / "Patch-D.MPQ")
    storm.replace_archive_entries(PATCH_D, staged)
    print(f"Patch-D updated ({PATCH_D.stat().st_size:,} bytes), backup {backup}")


if __name__ == "__main__":
    main()
