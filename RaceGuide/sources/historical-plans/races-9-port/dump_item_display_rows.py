"""Dump raw ItemDisplayInfo rows for the item ids we are tracing."""
from __future__ import annotations

import ctypes
import struct
import subprocess
import sys
from pathlib import Path

REPO = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW")
sys.path.insert(0, str(REPO / "tools"))

from cars_mount_pack import DLL_DEFAULT, H, Storm, Wdbc

CLIENT = REPO / "3.3.5a - Dev/Data"
ORDER = ["common.MPQ", "common-2.MPQ", "expansion.MPQ", "lichking.MPQ", "patch.MPQ",
         "patch-2.MPQ", "patch-3.MPQ", "patch-4.mpq", "PATCH-A.MPQ", "Patch-B.MPQ",
         "Patch-C.MPQ", "Patch-D.MPQ", "Patch-E.MPQ", "Patch-F.MPQ", "Patch-G.MPQ",
         "Patch-O.mpq", "PATCH-X.MPQ", "Patch-Y.MPQ"]
ITEMS = [30935, 1280, 3732, 4323, 1024]


def main() -> None:
    storm = Storm(DLL_DEFAULT)
    payload = None
    src = None
    for name in ORDER:
        path = CLIENT / name
        if not path.is_file():
            continue
        handle = H()
        if not storm.dll.SFileOpenArchive(str(path), 0, 0x100, ctypes.byref(handle)):
            continue
        try:
            try:
                payload = storm.read(handle, "DBFilesClient\\ItemDisplayInfo.dbc")
                src = name
            except Exception:
                pass
        finally:
            storm.dll.SFileCloseArchive(handle)
        if payload:
            break
    print("source:", src, "size", len(payload))
    _, rows, fields, record, pool = struct.unpack("<4sIIII", payload[:20])
    print("rows", rows, "fields", fields, "record", record, "pool", pool)
    table = Wdbc(payload)

    ids = ids_for(ITEMS)
    for item, display_id in ids:
        row = next((candidate for candidate in table.rows if candidate[0] == display_id), None)
        print(f"--- item {item} -> display {display_id}")
        if row is None:
            print("    MISSING ROW")
            continue
        for index, value in enumerate(row):
            text = table.text(value) if 0 < value < len(table.strings) else ""
            print(f"   [{index:>2}] {value:<10} {text}")


def ids_for(items: list[int]) -> list[tuple[int, int]]:
    out = []
    for item in items:
        result = subprocess.run(
            ["docker", "exec", "ac-database", "mysql", "-uroot", "-ppassword", "-N", "-e",
             f"SELECT entry, displayid FROM acore_world.item_template WHERE entry = {item};"],
            capture_output=True, text=True, check=True).stdout.strip()
        if not result:
            out.append((item, -1))
            continue
        entry, display = result.split("\t")[:2]
        out.append((int(entry), int(display)))
    return out


if __name__ == "__main__":
    main()
