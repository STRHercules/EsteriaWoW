"""Exact field indices of the helmet geoset-vis ids in ItemDisplayInfo rows."""
from __future__ import annotations

import ctypes
import sys
from pathlib import Path

REPO = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW")
sys.path.insert(0, str(REPO / "tools"))
from cars_mount_pack import DLL_DEFAULT, H, Storm, Wdbc  # noqa: E402

CLIENT = REPO / "3.3.5a - Dev/Data"
ORDER = ["common.MPQ", "common-2.MPQ", "expansion.MPQ", "lichking.MPQ", "patch.MPQ",
         "patch-2.MPQ", "patch-3.MPQ", "patch-4.mpq", "PATCH-A.MPQ", "Patch-B.MPQ",
         "Patch-C.MPQ", "Patch-D.MPQ", "Patch-E.MPQ", "Patch-F.MPQ", "Patch-G.MPQ",
         "Patch-O.mpq", "PATCH-X.MPQ", "Patch-Y.MPQ"]
WANT = (64503, 64429, 65195, 65160, 64427, 61210, 62159, 43230)


def main() -> None:
    storm = Storm(DLL_DEFAULT)
    payload = None
    for name in reversed(ORDER):
        path = CLIENT / name
        if not path.is_file():
            continue
        handle = H()
        if not storm.dll.SFileOpenArchive(str(path), 0, 0x100, ctypes.byref(handle)):
            continue
        try:
            try:
                payload = storm.read(handle, "DBFilesClient\\ItemDisplayInfo.dbc")
            except Exception:
                pass
        finally:
            storm.dll.SFileCloseArchive(handle)
    table = Wdbc(payload)
    for row in table.rows:
        if row[0] not in WANT:
            continue
        print(f"display {row[0]}: " + ", ".join(
            f"[{index}]={value}" for index, value in enumerate(row) if value))


if __name__ == "__main__":
    main()
