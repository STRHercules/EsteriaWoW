"""Compare CreatureDisplayInfo/CreatureModelData rows and head pivots across races."""
from __future__ import annotations

import ctypes
import struct
import sys
from pathlib import Path

REPO = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW")
sys.path.insert(0, str(REPO / "tools"))
from cars_mount_pack import DLL_DEFAULT, H, Storm  # noqa: E402

CLIENT = REPO / "3.3.5a - Dev/Data"
DONOR = Path(r"G:\Eunoia\Client\data")
OUR_ORDER = ["common.MPQ", "common-2.MPQ", "expansion.MPQ", "lichking.MPQ", "patch.MPQ",
             "patch-2.MPQ", "patch-3.MPQ", "patch-4.mpq", "PATCH-A.MPQ", "Patch-B.MPQ",
             "Patch-C.MPQ", "Patch-D.MPQ", "Patch-E.MPQ", "Patch-F.MPQ", "Patch-G.MPQ",
             "Patch-O.mpq", "PATCH-X.MPQ", "Patch-Y.MPQ"]
DONOR_ORDER = ["common.mpq", "common-2.mpq", "expansion.mpq", "lichking.mpq", "patch.mpq",
               "patch-2.mpq", "patch-3.mpq", "Patch-4.mpq", "Patch-5.mpq", "Patch-6.mpq",
               "Patch-7.mpq", "Patch-8.mpq", "Patch-9.mpq", "patch-I.mpq", "patch-m.mpq",
               "patch-x.mpq", "patch-y.mpq", "patch-z.mpq"]
MODELS = {
    "human": "character\\human\\male\\humanmale.m2",
    "gnome": "character\\gnome\\male\\gnomemale.m2",
    "dwarf": "character\\dwarf\\male\\dwarfmale.m2",
    "bloodelf": "character\\bloodelf\\male\\bloodelfmale.m2",
    "scourge": "character\\scourge\\male\\scourgemalem2",
    "tauren": "character\\tauren\\male\\taurenmale.m2",
    "vulpera": "character\\vulpera\\male\\vulperamale.m2",
    "pandaren": "character\\pandaren\\male\\pandarenmale.m2",
}
STRIDE = 0x28


def open_all(storm: Storm, root: Path, order):
    handles = []
    for name in order:
        path = root / name
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


def find_table(payload: bytes, minimum: int = 10):
    for offset in range(0, len(payload) - STRIDE * minimum, 4):
        if struct.unpack_from("<I", payload, offset)[0] != 0:
            continue
        for index in range(1, minimum):
            if struct.unpack_from("<I", payload, offset + index * STRIDE)[0] != index:
                break
        else:
            return offset
    return None


def main() -> None:
    storm = Storm(DLL_DEFAULT)
    ours = open_all(storm, CLIENT, OUR_ORDER)
    donor = open_all(storm, DONOR, DONOR_ORDER)
    try:
        for label, key in MODELS.items():
            source, payload = read(storm, ours, key)
            if payload is None:
                print(f"{label}: model missing")
                continue
            offset = find_table(payload)
            if offset is None:
                print(f"{label} [{source}]: no ordered attachment table")
                continue
            pivots = {}
            for index in range(12):
                record = offset + index * STRIDE
                identifier, bone = struct.unpack_from("<IH", payload, record)
                pivots[identifier] = struct.unpack_from("<3f", payload, record + 8)
            head = pivots.get(11, (0, 0, 0))
            print(f"{label:<9} [{source:<12}] head id11 pivot=({head[0]:+.3f}, {head[1]:+.3f}, "
                  f"{head[2]:+.3f})  id5=({pivots.get(5, (0,0,0))[2]:+.3f}) "
                  f"id6=({pivots.get(6, (0,0,0))[2]:+.3f})")
    finally:
        for _name, handle in ours + donor:
            storm.dll.SFileCloseArchive(handle)


if __name__ == "__main__":
    main()
