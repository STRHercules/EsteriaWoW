"""Make the Void Elf ear geometry render in this client.

Bounds analysis (`inspect_geoset_bounds.py`) puts the Void Elf ears on geoset
`702` in every LOD - the only head mesh that protrudes sideways (y +-0.178 male,
+-0.174 female). The client renders the race's base geoset and the geosets its
customisation tables name, and nothing ever names group 7, so the ears stay
hidden; the working custom races instead carry their ears on a geoset the client
reaches. Re-tagging the ear submeshes to geoset `7` folds them into the base
variant the client already draws, leaving every other submesh untouched.
"""

from __future__ import annotations

import argparse
import datetime
import shutil
import struct
import sys
from pathlib import Path

REPO = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW")
sys.path.insert(0, str(REPO / "tools"))

from cars_mount_pack import DLL_DEFAULT, H, Storm  # noqa: E402

PATCH_D = REPO / "3.3.5a - Dev/Data/Patch-D.MPQ"
BACKUP_ROOT = REPO / "3.3.5a - Dev/Backups"
STEMS = [
    "Character\\Voidelf\\Male\\VoidelfMale",
    "Character\\Voidelf\\Female\\VoidelfFemale",
]
FROM_GEOSET = 702
TO_GEOSET = 7


def retag(skin: bytes) -> list[tuple[int, int]]:
    vals = struct.unpack_from("<10I", skin, 4)
    n_sub, ofs_sub = vals[6], vals[7]
    out = bytearray(skin)
    moved = []
    for index in range(n_sub):
        offset = ofs_sub + index * 48
        gid, level, v_start, v_count, i_start, i_count = struct.unpack_from("<6H", skin, offset)
        if gid != FROM_GEOSET:
            continue
        struct.pack_into("<H", out, offset, TO_GEOSET)
        moved.append((level, i_count // 3))
    return moved, bytes(out)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    storm = Storm(DLL_DEFAULT)
    handle = storm.open_archive(PATCH_D)
    entries: dict[str, bytes] = {}
    try:
        for name, *_ in storm.list_files(handle):
            if name.startswith("("):
                continue
            key = name.casefold()
            if any(key.endswith(f"{stem.casefold()}0{lod}.skin") for stem in STEMS for lod in range(4)):
                entries[name] = storm.read(handle, name)
    finally:
        storm.dll.SFileCloseArchive(handle)
    if not entries:
        raise SystemExit("no Void Elf skins found in Patch-D")

    updated: dict[str, bytes] = {}
    for name, payload in sorted(entries.items()):
        moved, out = retag(payload)
        print(f"{name}: moved {len(moved)} submeshes {FROM_GEOSET}->{TO_GEOSET} {moved}")
        if len(moved):
            updated[name] = out
    if not updated:
        raise SystemExit("nothing to retag")
    if args.dry_run:
        print("dry run - Patch-D untouched")
        return
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = BACKUP_ROOT / f"patch-d-before-voidelf-ears-{stamp}"
    backup.mkdir(parents=True, exist_ok=True)
    shutil.copy2(PATCH_D, backup / "Patch-D.MPQ")
    storm.replace_archive_entries(PATCH_D, updated)
    print(f"Patch-D updated ({PATCH_D.stat().st_size:,} bytes), backup {backup}")


if __name__ == "__main__":
    main()
