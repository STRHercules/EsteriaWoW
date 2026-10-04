"""Correct ChrRaces prefix dump: field 6 resolved by byte offset into the pool."""
from __future__ import annotations

import ctypes
import struct
import sys
from pathlib import Path

REPO = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW")
sys.path.insert(0, str(REPO / "tools"))

from cars_mount_pack import DLL_DEFAULT, H, Storm

CLIENT = REPO / "3.3.5a - Dev/Data"
DONOR = Path(r"G:\Eunoia\Client\data")
OUR_ORDER = ["common.MPQ", "common-2.MPQ", "expansion.MPQ", "lichking.MPQ", "patch.MPQ",
             "patch-2.MPQ", "patch-3.MPQ", "patch-4.mpq", "PATCH-A.MPQ", "Patch-B.MPQ",
             "Patch-C.MPQ", "Patch-D.MPQ", "Patch-E.MPQ", "Patch-F.MPQ", "Patch-G.MPQ",
             "Patch-O.mpq", "PATCH-X.MPQ", "Patch-Y.MPQ"]
DONOR_LOCALE = ["enUS\\locale-enUS.MPQ", "enUS\\base-enUS.MPQ", "enUS\\patch-enUS.MPQ",
                "enUS\\patch-enUS-2.MPQ", "enUS\\patch-enUS-3.MPQ", "enUS\\patch-enUS-4.MPQ",
                "enUS\\patch-enUS-5.MPQ"]


def dump(root: Path, order, label: str) -> None:
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
                payload = storm.read(handle, "DBFilesClient\\ChrRaces.dbc")
            except Exception:
                payload = None
        finally:
            storm.dll.SFileCloseArchive(handle)
        if payload is None:
            continue
        _, count, fields, record, _ = struct.unpack("<4sIIII", payload[:20])
        pool = payload[20 + count * record :]

        def text(value: int) -> str:
            if not 0 < value < len(pool):
                return ""
            end = pool.find(b"\0", value)
            return pool[value:end].decode("latin1", "replace")

        print(f"[{label}] {name}: rows={count}")
        for index in range(count):
            row = struct.unpack_from(f"<{fields}I", payload, 20 + index * record)
            print(f"    race {row[0]:>3} prefix={text(row[6])!r:<12} "
                  f"displays={row[4]}/{row[5]} file={text(row[13])!r}")


def main() -> None:
    dump(DONOR, DONOR_LOCALE, "donor")
    dump(CLIENT, OUR_ORDER, "ours")


if __name__ == "__main__":
    main()
