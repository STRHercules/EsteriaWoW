"""Find which ChrRaces row/field references the strings we care about."""
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
WANTED = ["Er", "Nb", "Ve", "Lf", "Za", "Di", "Dr", "Kt", "Il", "Bk", "Hu", "Sc", "Tr"]


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
    _, count, fields, record, poolsize = struct.unpack("<4sIIII", payload[:20])
    print(f"source={source} rows={count} fields={fields} record={record} pool={poolsize} "
          f"file={len(payload)}")
    pool = payload[20 + count * record:]

    offsets: dict[str, list[int]] = {}
    for wanted in WANTED:
        needle = wanted.encode() + b"\0"
        found = []
        start = 0
        while True:
            index = pool.find(needle, start)
            if index < 0:
                break
            if index == 0 or pool[index - 1] == 0:
                found.append(index)
            start = index + 1
        offsets[wanted] = found
        print(f"{wanted!r}: offsets {found}")

    print("\nrows referencing those offsets (any field):")
    for index in range(count):
        row = struct.unpack_from(f"<{fields}I", payload, 20 + index * record)
        hits = []
        for field_index, value in enumerate(row):
            for wanted, found in offsets.items():
                if value in found:
                    hits.append(f"[{field_index}]={wanted}")
        if hits:
            print(f"  row {index}: id={row[0]} " + " ".join(hits))


if __name__ == "__main__":
    main()
