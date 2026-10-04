"""Header + bounding box of head component models, ours vs donor."""
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
KEYS = [
    "Item\\ObjectComponents\\Head\\Helm_Leather_B_06_HuM.m2",
    "Item\\ObjectComponents\\Head\\Helm_Leather_B_06_BeM.m2",
    "Item\\ObjectComponents\\Head\\Helm_Leather_B_06_VuM.m2",
    "Item\\ObjectComponents\\Head\\Helm_Leather_B_06_PaM.m2",
    "character\\vulpera\\male\\vulperamale.m2",
    "character\\human\\male\\humanmale.m2",
]


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


def describe(label: str, payload: bytes) -> None:
    magic = payload[:4]
    version = struct.unpack_from("<I", payload, 4)[0]
    print(f"{label}: magic={magic!r} version={version} size={len(payload):,}")
    # M2Array descriptors: {count, offset} relative to file start, first 24 of them
    for index in range(24):
        count, offset = struct.unpack_from("<II", payload, 8 + index * 8)
        if count and offset and offset < len(payload):
            pass
    # look for a bounding box: 6 floats that look like coordinates plus a radius
    best = None
    for offset in range(0x30, min(len(payload), 0x400), 4):
        try:
            values = struct.unpack_from("<6f", payload, offset)
        except struct.error:
            break
        if all(-100 < v < 100 for v in values) and any(abs(v) > 0.001 for v in values):
            spread = max(values[:3]) - min(values[:3])
            span = max(values[3:]) - min(values[3:])
            if 0.001 < span < 5 and spread < 5:
                best = (offset, values)
                break
    if best:
        offset, values = best
        print(f"     bbox candidate @{offset:#x}: min=({values[0]:.3f}, {values[1]:.3f}, "
              f"{values[2]:.3f}) max=({values[3]:.3f}, {values[4]:.3f}, {values[5]:.3f})")


def main() -> None:
    storm = Storm(DLL_DEFAULT)
    ours = open_all(storm, CLIENT, OUR_ORDER)
    donor = open_all(storm, DONOR, DONOR_ORDER)
    try:
        for key in KEYS:
            for label, handles in (("ours", ours), ("donor", donor)):
                source, payload = read(storm, handles, key)
                if payload is None:
                    print(f"{key} [{label}]: MISSING")
                    continue
                describe(f"{key.split(chr(92))[-1]} [{label} <- {source}]", payload)
            print()
    finally:
        for _name, handle in ours + donor:
            storm.dll.SFileCloseArchive(handle)


if __name__ == "__main__":
    main()
