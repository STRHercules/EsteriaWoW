"""Dump ChrRaces records honestly: header, record size, and every field of a few races."""
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
WANT = [1, 2, 8, 14, 16, 18, 20, 30, 31]


def load(key: str):
    storm = Storm(DLL_DEFAULT)
    hits = []
    for name in ORDER:
        path = CLIENT / name
        if not path.is_file():
            continue
        handle = H()
        if not storm.dll.SFileOpenArchive(str(path), 0, 0x100, ctypes.byref(handle)):
            continue
        try:
            try:
                hits.append((name, storm.read(handle, key)))
            except Exception:
                pass
        finally:
            storm.dll.SFileCloseArchive(handle)
    return storm, hits


def main() -> None:
    storm, hits = load("DBFilesClient\\ChrRaces.dbc")
    for name, payload in hits:
        sig, rows, fields, record, poolsize = struct.unpack("<4sIIII", payload[:20])
        print(f"{name}: sig={sig} rows={rows} fields={fields} record={record} "
              f"pool={poolsize} file={len(payload)}")
    name, payload = hits[-1]
    sig, rows, fields, record, poolsize = struct.unpack("<4sIIII", payload[:20])
    pool = payload[20 + rows * record:].split(b"\0")

    def text(value: int) -> str:
        if not 0 < value < len(pool):
            return ""
        return pool[value].decode("latin1", "replace")

    for race in WANT:
        row = struct.unpack_from(f"<{record // 4}I", payload, 20 + race * record)
        strings = {index: text(value) for index, value in enumerate(row) if text(value)}
        print(f"--- race {race} (id field {row[0]})")
        for index, value in list(strings.items())[:10]:
            print(f"      [{index:>2}] {value!r}")


if __name__ == "__main__":
    main()
