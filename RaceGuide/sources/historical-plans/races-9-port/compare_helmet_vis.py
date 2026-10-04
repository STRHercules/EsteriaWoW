"""Compare HelmetGeosetVisData across our client and the donor."""
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
               "patch-x.mpq", "patch-y.mpq", "patch-z.mpq",
               "enUS\\locale-enUS.MPQ", "enUS\\base-enUS.MPQ", "enUS\\patch-enUS.MPQ",
               "enUS\\patch-enUS-2.MPQ", "enUS\\patch-enUS-3.MPQ",
               "enUS\\patch-enUS-4.MPQ", "enUS\\patch-enUS-5.MPQ"]
KEY = "DBFilesClient\\HelmetGeosetVisData.dbc"


def scan(root: Path, order, label: str) -> None:
    storm = Storm(DLL_DEFAULT)
    for name in order:
        path = root / name
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
        ids = []
        for index in range(count):
            ids.append(struct.unpack_from("<I", payload, 20 + index * record)[0])
        print(f"[{label}] {name}: rows={count} fields={fields} record={record} "
              f"pool={pool} ids={ids[:8]}...")


def main() -> None:
    scan(CLIENT, OUR_ORDER, "ours")
    scan(DONOR, DONOR_ORDER, "donor")


if __name__ == "__main__":
    main()
