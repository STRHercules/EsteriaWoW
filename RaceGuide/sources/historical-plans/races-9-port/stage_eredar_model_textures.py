"""Stage every texture the donor's Eredar player models reference.

The player models carry their own texture list (paths embedded in the M2 string block), and the
files behind those paths only exist in the donor client, so the race rendered untextured after
the swap. This reads the `.blp` paths out of the two staged models, checks which are missing
from our client, and copies them from Eunoia into Patch-D.
"""

from __future__ import annotations

import argparse
import ctypes
import datetime
import re
import shutil
import sys
from pathlib import Path

REPO = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW")
sys.path.insert(0, str(REPO / "tools"))

from cars_mount_pack import DLL_DEFAULT, H, Storm  # noqa: E402

DONOR = Path(r"G:\Eunoia\Client\data")
DONOR_ARCHIVES = ("Patch-5.mpq", "Patch-4.mpq", "Patch-9.mpq", "Patch-8.mpq", "patch-I.mpq",
                  "Patch-6.mpq", "Patch-7.mpq")
CLIENT = REPO / "3.3.5a - Dev/Data"
OUR_ARCHIVES = ("Patch-D.MPQ", "Patch-E.MPQ", "Patch-G.MPQ", "Patch-C.MPQ", "PATCH-A.MPQ",
                "PATCH-X.MPQ", "Patch-Y.MPQ")
PATCH_D = CLIENT / "Patch-D.MPQ"
BACKUP_ROOT = REPO / "3.3.5a - Dev/Backups"
MODELS = (
    r"Character\Eredar\Male\EredarMale.m2",
    r"Character\Eredar\Female\EredarFemale.m2",
)
PATTERN = re.compile(rb"[ -~]{5,}?\.blp", re.IGNORECASE)


def open_archives(storm: Storm, root: Path, names: tuple[str, ...]) -> list:
    handles = []
    for name in names:
        path = root / name
        if not path.is_file():
            continue
        handle = H()
        if storm.dll.SFileOpenArchive(str(path), 0, 0x100, ctypes.byref(handle)):
            handles.append(handle)
    return handles


def read(storm: Storm, handles: list, key: str) -> bytes | None:
    for handle in handles:
        try:
            return storm.read(handle, key)
        except Exception:
            continue
    return None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    storm = Storm(DLL_DEFAULT)
    ours = open_archives(storm, CLIENT, OUR_ARCHIVES)
    donor = open_archives(storm, DONOR, DONOR_ARCHIVES)
    try:
        wanted: set[str] = set()
        for model in MODELS:
            data = read(storm, ours, model)
            if data is None:
                print(f"{model}: not readable")
                continue
            for match in PATTERN.finditer(data):
                wanted.add(match.group().decode("latin1"))
        print(f"{len(wanted)} texture paths referenced by the Eredar player models")
        missing: list[str] = []
        staged: dict[str, bytes] = {}
        for key in sorted(wanted):
            if read(storm, ours, key) is not None:
                continue
            payload = read(storm, donor, key)
            if payload is None:
                missing.append(key)
                continue
            staged[key] = payload
            print(f"  + {key} ({len(payload):,} bytes)")
        print(f"missing from our client: {len(staged)}, not found in donor: {len(missing)}")
        for key in missing[:20]:
            print(f"  ! {key}")
        if not staged:
            print("nothing to stage")
            return
        if args.dry_run:
            print("dry run - Patch-D untouched")
            return
        stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        backup = BACKUP_ROOT / f"patch-d-before-eredar-textures-{stamp}"
        backup.mkdir(parents=True, exist_ok=True)
        shutil.copy2(PATCH_D, backup / "Patch-D.MPQ")
        storm.replace_archive_entries(PATCH_D, staged)
        print(f"Patch-D updated ({PATCH_D.stat().st_size:,} bytes), backup {backup}")
    finally:
        for handle in ours + donor:
            storm.dll.SFileCloseArchive(handle)


if __name__ == "__main__":
    main()
