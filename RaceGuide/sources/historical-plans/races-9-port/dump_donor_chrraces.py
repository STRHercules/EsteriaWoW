"""Dump donor ChrRaces prefixes from its locale archives (last one wins)."""
from __future__ import annotations

import ctypes
import struct
import sys
from pathlib import Path

REPO = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW")
sys.path.insert(0, str(REPO / "tools"))

from cars_mount_pack import DLL_DEFAULT, H, Storm

DONOR = Path(r"G:\Eunoia\Client\data")
ORDER = ["enUS\\locale-enUS.MPQ", "enUS\\base-enUS.MPQ", "enUS\\patch-enUS.MPQ",
         "enUS\\patch-enUS-2.MPQ", "enUS\\patch-enUS-3.MPQ", "enUS\\patch-enUS-4.MPQ",
         "enUS\\patch-enUS-5.MPQ"]


def main() -> None:
    storm = Storm(DLL_DEFAULT)
    for name in ORDER:
        path = DONOR / name
        if not path.is_file():
            print(f"{name}: missing file")
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
            print(f"{name}: no ChrRaces")
            continue
        _, count, fields, record, _ = struct.unpack("<4sIIII", payload[:20])
        pool = payload[20 + count * record:].split(b"\0")

        def text(value: int) -> str:
            if not 0 < value < len(pool):
                return ""
            return pool[value].decode("latin1", "replace")

        rows = {}
        for index in range(count):
            row = struct.unpack_from(f"<{fields}I", payload, 20 + index * record)
            rows[row[0]] = row
        print(f"== {name}: rows={count} ids={sorted(rows)[:40]}")
        for race in sorted(rows):
            row = rows[race]
            print(f"   race {race:>3} prefix={text(row[6])!r:<16} file={text(row[13])!r}")


if __name__ == "__main__":
    main()
