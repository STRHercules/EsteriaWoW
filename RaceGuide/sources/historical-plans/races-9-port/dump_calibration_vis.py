"""HelmetGeosetVis ids for the calibration items plus the original test helm."""
from __future__ import annotations

import ctypes
import struct
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
WANT = {
    64503: "A item 50679", 64429: "B item 50713", 65195: "C item 51494",
    65160: "D item 51825", 64427: "E item 50073", 61210: "F item 47688",
    62159: "G item 47690", 43230: "orig item 30935", 15304: "plate 1024",
}


def load(storm: Storm, key: str):
    for name in reversed(ORDER):
        path = CLIENT / name
        if not path.is_file():
            continue
        handle = H()
        if not storm.dll.SFileOpenArchive(str(path), 0, 0x100, ctypes.byref(handle)):
            continue
        try:
            try:
                return name, storm.read(handle, key)
            except Exception:
                pass
        finally:
            storm.dll.SFileCloseArchive(handle)
    return None, None


def main() -> None:
    storm = Storm(DLL_DEFAULT)
    source, payload = load(storm, "DBFilesClient\\ItemDisplayInfo.dbc")
    table = Wdbc(payload)
    vis_source, vis_payload = load(storm, "DBFilesClient\\HelmetGeosetVisData.dbc")
    _, vis_count, vis_fields, vis_record, _ = struct.unpack("<4sIIII", vis_payload[:20])
    vis_rows = {}
    for index in range(vis_count):
        row = struct.unpack_from(f"<{vis_fields}I", vis_payload, 20 + index * vis_record)
        vis_rows[row[0]] = row
    print(f"ItemDisplayInfo <- {source} ({table.fields} fields); "
          f"HelmetGeosetVisData <- {vis_source} ({vis_fields} fields)")
    for row in table.rows:
        if row[0] not in WANT:
            continue
        name = table.text(row[1])
        vis = [value for value in row[10:16] if value]
        print(f"   {WANT[row[0]]:<16} display {row[0]:<6} model={name:<40} fields10-15={vis}")
        for vis_id in vis:
            entry = vis_rows.get(vis_id)
            if entry:
                print(f"       vis {vis_id}: " + " ".join(f"{value:#x}" for value in entry))


if __name__ == "__main__":
    main()
