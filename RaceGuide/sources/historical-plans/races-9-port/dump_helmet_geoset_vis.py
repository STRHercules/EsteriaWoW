"""Dump HelmetGeosetVisData rows used by helm 30935, plus the header shape."""
from __future__ import annotations

import ctypes
import struct
import sys
from pathlib import Path

REPO = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW")
sys.path.insert(0, str(REPO / "tools"))
from cars_mount_pack import DLL_DEFAULT, H, Storm  # noqa: E402

CLIENT = REPO / "3.3.5a - Dev/Data"
ORDER = ["common.MPQ", "common-2.MPQ", "expansion.MPQ", "lichking.MPQ", "patch.MPQ",
         "patch-2.MPQ", "patch-3.MPQ", "patch-4.mpq", "PATCH-A.MPQ", "Patch-B.MPQ",
         "Patch-C.MPQ", "Patch-D.MPQ", "Patch-E.MPQ", "Patch-F.MPQ", "Patch-G.MPQ",
         "Patch-O.mpq", "PATCH-X.MPQ", "Patch-Y.MPQ"]
KEY = "DBFilesClient\\HelmetGeosetVisData.dbc"
WANT = (7, 366, 367)


def main() -> None:
    storm = Storm(DLL_DEFAULT)
    for name in ORDER:
        path = CLIENT / name
        if not path.is_file():
            continue
        handle = H()
        if not storm.dll.SFileOpenArchive(str(path), 0, 0x100, ctypes.byref(handle)):
            continue
        try:
            try:
                payload = storm.read(handle, KEY)
            except Exception:
                payload = None
        finally:
            storm.dll.SFileCloseArchive(handle)
        if payload is None:
            continue
        _, count, fields, record, pool = struct.unpack("<4sIIII", payload[:20])
        print(f"{name}: rows={count} fields={fields} record={record} pool={pool}")
        for index in range(count):
            row = struct.unpack_from(f"<{fields}I", payload, 20 + index * record)
            if row[0] in WANT:
                print(f"    id {row[0]:>3}: " + " ".join(f"[{i}]={v:#x}" for i, v in enumerate(row)))


if __name__ == "__main__":
    main()
