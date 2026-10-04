"""ChrRaces rows keyed by their real id field, all string-looking fields shown."""
from __future__ import annotations

import ctypes
import struct
import sys
from pathlib import Path

REPO = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW")
sys.path.insert(0, str(REPO / "tools"))

from cars_mount_pack import DLL_DEFAULT, H, Storm

CLIENT = REPO / "3.3.5a - Dev/Data"
ORDER = ["common.MPQ", "common-2.MPQ", "expansion.MPQ", "lichking.MPQ", "patch.MPQ",
         "patch-2.MPQ", "patch-3.MPQ", "patch-4.mpq", "PATCH-A.MPQ", "Patch-B.MPQ",
         "Patch-C.MPQ", "Patch-D.MPQ", "Patch-E.MPQ", "Patch-F.MPQ", "Patch-G.MPQ",
         "Patch-O.mpq", "PATCH-X.MPQ", "Patch-Y.MPQ"]


def rows_of(payload: bytes):
    _, count, fields, record, _ = struct.unpack("<4sIIII", payload[:20])
    pool = payload[20 + count * record:].split(b"\0")

    def text(value: int) -> str:
        if not 0 < value < len(pool):
            return ""
        return pool[value].decode("latin1", "replace")

    out = {}
    for index in range(count):
        row = struct.unpack_from(f"<{fields}I", payload, 20 + index * record)
        out[row[0]] = (row, text)
    return out


def main() -> None:
    storm = Storm(DLL_DEFAULT)
    payload = None
    source = None
    for name in ORDER:
        path = CLIENT / name
        if not path.is_file():
            continue
        handle = H()
        if not storm.dll.SFileOpenArchive(str(path), 0, 0x100, ctypes.byref(handle)):
            continue
        try:
            try:
                payload = storm.read(handle, "DBFilesClient\\ChrRaces.dbc")
                source = name
            except Exception:
                pass
        finally:
            storm.dll.SFileCloseArchive(handle)
    print("source:", source)
    table = rows_of(payload)
    for race in sorted(table):
        row, text = table[race]
        strings = [(index, text(value)) for index, value in enumerate(row) if text(value)]
        short = [(index, value) for index, value in strings if len(value) <= 8]
        print(f"race {race:>2}: " + " ".join(f"[{index}]={value!r}" for index, value in short[:8]))


if __name__ == "__main__":
    main()
