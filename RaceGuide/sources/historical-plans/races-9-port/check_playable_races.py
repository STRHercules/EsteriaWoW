"""Is the Sethrak row (15) playable, and what are the faction/flag fields for our races?"""
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


def load(storm: Storm, key: str):
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
                payload = storm.read(handle, key)
                source = name
            except Exception:
                pass
        finally:
            storm.dll.SFileCloseArchive(handle)
    return source, payload


def main() -> None:
    storm = Storm(DLL_DEFAULT)
    source, payload = load(storm, "DBFilesClient\\CharBaseInfo.dbc")
    _, count, fields, record, _ = struct.unpack("<4sIIII", payload[:20])
    print(f"CharBaseInfo header: fields={fields} record={record}")
    pairs = set()
    for index in range(count):
        start = 20 + index * record
        row = struct.unpack_from(f"<{record}B", payload, start)
        pairs.add((row[0], row[1]))
    print(f"CharBaseInfo <- {source}: {len(pairs)} race/class pairs")
    races = sorted({race for race, _cls in pairs})
    print(f"races with classes: {races}")
    for race in (14, 15, 16, 18, 20, 24):
        classes = sorted(cls for r, cls in pairs if r == race)
        print(f"  race {race}: {len(classes)} classes {classes}")

    source, payload = load(storm, "DBFilesClient\\ChrRaces.dbc")
    _, count, fields, record, poolsize = struct.unpack("<4sIIII", payload[:20])
    pool = payload[20 + count * record :]

    def text(value: int) -> str:
        if not 0 < value < len(pool):
            return ""
        end = pool.find(b"\0", value)
        return pool[value:end].decode("latin1", "replace")

    print(f"ChrRaces <- {source}")
    for index in range(count):
        row = struct.unpack_from(f"<{fields}I", payload, 20 + index * record)
        if row[0] not in (14, 15, 16, 18, 20, 24, 25, 26, 28, 29, 30, 31):
            continue
        print(f"  race {row[0]:>2} flags={row[1]} faction={row[2]} alliance={row[3]} "
              f"display={row[4]}/{row[5]} prefix={text(row[6])!r}")


if __name__ == "__main__":
    main()

