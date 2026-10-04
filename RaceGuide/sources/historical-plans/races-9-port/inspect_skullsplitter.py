"""Skullsplitter Helm: what model and geoset-vis does it use, and does a Vu copy exist?"""
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
HEAD = "Item\\ObjectComponents\\Head\\"
DISPLAY_ID = 15340


def open_archives(storm: Storm):
    handles = []
    for name in ORDER:
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


def main() -> None:
    storm = Storm(DLL_DEFAULT)
    handles = open_archives(storm)
    try:
        source, payload = read(storm, handles, "DBFilesClient\\ItemDisplayInfo.dbc")
        table = Wdbc(payload)
        row = next(candidate for candidate in table.rows if candidate[0] == DISPLAY_ID)
        print(f"display {DISPLAY_ID} [{source}]: " +
              ", ".join(f"[{index}]={value}" for index, value in enumerate(row) if value))
        stem = table.text(row[1])
        print(f"   ModelName[0] = {stem!r}, vis ids = {row[13]}/{row[14]}")
        base = stem[:-4] if stem.lower().endswith(".mdx") else stem
        for sex in ("M", "F"):
            for suffix in (".m2", "00.skin"):
                key = f"{HEAD}{base}_Vu{sex}{suffix}"
                found, blob = read(storm, handles, key)
                print(f"   {key.split(chr(92))[-1]}: "
                      f"{found + f' ({len(blob):,} bytes)' if blob else 'MISSING'}")
        vis_source, vis_payload = read(storm, handles, "DBFilesClient\\HelmetGeosetVisData.dbc")
        _, count, fields, record, _ = struct.unpack("<4sIIII", vis_payload[:20])
        for index in range(count):
            entry = struct.unpack_from(f"<{fields}I", vis_payload, 20 + index * record)
            if entry[0] in (row[13], row[14], 285):
                print(f"   vis {entry[0]}: " + " ".join(f"{value:#x}" for value in entry))
    finally:
        for _name, handle in handles:
            storm.dll.SFileCloseArchive(handle)


if __name__ == "__main__":
    main()
