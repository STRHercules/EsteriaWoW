"""Stage seven Vulpera helmet variants so the anchor can be picked in one game session.

Each variant is the donor's Vulpera leather helm model with its vertices shifted by a
different (back/forward, up/down) offset, published under its own model stem, and seven
leather helm items are re-pointed at those stems through `ItemDisplayInfo`.  Equipping the
items in game shows every candidate at once instead of one client restart per guess.

Usage:
    python build_vulpera_helm_calibration.py --dry-run
    python build_vulpera_helm_calibration.py
"""

from __future__ import annotations

import argparse
import ctypes
import datetime
import shutil
import struct
import sys
from pathlib import Path

REPO = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW")
sys.path.insert(0, str(REPO / "tools"))

from cars_mount_pack import DLL_DEFAULT, H, Storm, Wdbc  # noqa: E402

CLIENT = REPO / "3.3.5a - Dev/Data"
PATCH_Y = CLIENT / "Patch-Y.MPQ"
BACKUP_ROOT = REPO / "3.3.5a - Backups"
ORDER = ["common.MPQ", "common-2.MPQ", "expansion.MPQ", "lichking.MPQ", "patch.MPQ",
         "patch-2.MPQ", "patch-3.MPQ", "patch-4.mpq", "PATCH-A.MPQ", "Patch-B.MPQ",
         "Patch-C.MPQ", "Patch-D.MPQ", "Patch-E.MPQ", "Patch-F.MPQ", "Patch-G.MPQ",
         "Patch-O.mpq", "PATCH-X.MPQ", "Patch-Y.MPQ"]
HEAD = "Item\\ObjectComponents\\Head\\"
VULPERA_PREFIX = "Vu"
CHRRACES = "DBFilesClient\\ChrRaces.dbc"
ITEM_DISPLAY_INFO = "DBFilesClient\\ItemDisplayInfo.dbc"
STRIDE = 48
BASE_STEM = "Helm_Leather_B_06"

# item id -> (display id, dx = backwards, dz = up)
VARIANTS = {
    "A": (50679, 64503, 0.00, -0.10),
    "B": (50713, 64429, 0.08, -0.10),
    "C": (51494, 65195, 0.16, -0.10),
    "D": (51825, 65160, 0.00, -0.25),
    "E": (50073, 64427, 0.08, -0.25),
    "F": (47688, 61210, 0.16, -0.25),
    "G": (47690, 62159, 0.00, 0.05),
}


def open_archives(storm: Storm, names):
    handles = []
    for name in names:
        path = CLIENT / name
        if not path.is_file():
            continue
        handle = H()
        if storm.dll.SFileOpenArchive(str(path), 0, 0x100, ctypes.byref(handle)):
            handles.append((name, handle))
    return handles


def read(storm: Storm, handles, key: str):
    for name, handle in reversed(handles):
        try:
            return name, storm.read(handle, key)
        except Exception:
            continue
    return None, None


def shifted(payload: bytes, dx: float, dz: float) -> bytes:
    patched = bytearray(payload)
    count, offset = struct.unpack_from("<II", patched, 0x3C)
    for index in range(count):
        record = offset + index * STRIDE
        x, y, z = struct.unpack_from("<3f", patched, record)
        struct.pack_into("<3f", patched, record, x + dx, y, z + dz)
    return bytes(patched)


def intern(pool: bytearray, text: str) -> int:
    encoded = text.encode("ascii")
    needle = b"\0" + encoded + b"\0"
    index = pool.find(needle)
    while index > 0:
        if pool.rfind(b"\0", 0, index + 1) == index:
            return index + 1
        index = pool.find(needle, index + 1)
    offset = len(pool)
    pool.extend(encoded + b"\0")
    return offset


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    storm = Storm(DLL_DEFAULT)
    handles = open_archives(storm, ORDER)
    entries: dict[str, bytes] = {}
    try:
        race_source, races_payload = read(storm, handles, CHRRACES)
        races = Wdbc(races_payload)
        pool = bytearray(races.strings)
        for row in races.rows:
            if row[0] == 20:
                row[6] = intern(pool, VULPERA_PREFIX)
        entries[CHRRACES] = (struct.pack("<4s4I", b"WDBC", len(races.rows), races.fields,
                                         races.record_size, len(pool))
                             + b"".join(struct.pack(f"<{races.fields}I",
                                                    *(value & 0xFFFFFFFF for value in row))
                                        for row in races.rows)
                             + bytes(pool))
        print(f"{CHRRACES} <- {race_source}: race 20 prefix -> {VULPERA_PREFIX!r}")

        display_source, display_payload = read(storm, handles, ITEM_DISPLAY_INFO)
        display = Wdbc(display_payload)
        display_pool = bytearray(display.strings)
        by_id = {row[0]: row for row in display.rows}
        for label, (item, display_id, dx, dz) in VARIANTS.items():
            row = by_id.get(display_id)
            if row is None:
                raise SystemExit(f"display {display_id} (item {item}) missing from ItemDisplayInfo")
            stem = f"HelmCal{label}"
            print(f"   item {item} display {display_id}: {display.text(row[1])!r} -> {stem} "
                  f"(dx {dx:+.2f}, dz {dz:+.2f})")
            row[1] = intern(display_pool, stem + ".mdx")
        entries[ITEM_DISPLAY_INFO] = (
            struct.pack("<4s4I", b"WDBC", len(display.rows), display.fields,
                        display.record_size, len(display_pool))
            + b"".join(struct.pack(f"<{display.fields}I", *(value & 0xFFFFFFFF for value in row))
                       for row in display.rows)
            + bytes(display_pool))
        print(f"{ITEM_DISPLAY_INFO} <- {display_source}: {len(VARIANTS)} rows re-pointed")

        for label, (item, display_id, dx, dz) in VARIANTS.items():
            stem = f"HelmCal{label}"
            for sex in ("M", "F"):
                for suffix in (".m2", "00.skin"):
                    key = f"{HEAD}{BASE_STEM}_{VULPERA_PREFIX}{sex}{suffix}"
                    source, payload = read(storm, handles, key)
                    if payload is None:
                        raise SystemExit(f"{key}: not found")
                    if suffix == ".m2":
                        blob = shifted(payload, dx, dz)
                    else:
                        blob = payload
                    entries[f"{HEAD}{stem}_{VULPERA_PREFIX}{sex}{suffix}"] = blob
            print(f"   staged {stem}_{VULPERA_PREFIX}[MF] from {source}")
    finally:
        for _name, handle in handles:
            storm.dll.SFileCloseArchive(handle)

    if args.dry_run:
        print("dry run - Patch-Y untouched")
        return

    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = BACKUP_ROOT / f"patch-y-before-vulpera-calibration-{stamp}"
    backup.mkdir(parents=True, exist_ok=True)
    shutil.copy2(PATCH_Y, backup / "Patch-Y.MPQ")
    storm.replace_archive_entries(PATCH_Y, entries)
    print(f"Patch-Y updated ({PATCH_Y.stat().st_size:,} bytes), {len(entries)} entries, "
          f"backup {backup}")


if __name__ == "__main__":
    main()
