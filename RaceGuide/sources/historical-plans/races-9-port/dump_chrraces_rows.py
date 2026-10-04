"""Dump every string-resolving field of selected ChrRaces rows, ours and donor."""
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


def load(root: Path, order, label: str):
    storm = Storm(DLL_DEFAULT)
    payload = None
    source = None
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
                source = name
            except Exception:
                pass
        finally:
            storm.dll.SFileCloseArchive(handle)
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
    print(f"### {label} ({source}) rows={count} fields={fields}")
    return rows, text


def show(rows, text, races):
    for race in races:
        row = rows.get(race)
        if row is None:
            print(f"  race {race}: ABSENT")
            continue
        pairs = [(index, text(value)) for index, value in enumerate(row) if text(value)]
        print(f"  race {race}: id={row[0]} displays={row[4]}/{row[5]} lang={row[7]} "
              f"strings={pairs[:14]}")


def main() -> None:
    ours, ours_text = load(CLIENT, OUR_ORDER, "ours")
    print("stock-ish races:")
    show(ours, ours_text, [1, 2, 3, 4, 5, 6, 7, 8, 10, 11])
    print("custom races:")
    show(ours, ours_text, [14, 16, 18, 20, 22, 29, 30, 31])

    donor, donor_text = load(DONOR, DONOR_LOCALE, "donor")
    print("donor races:")
    show(donor, donor_text, [1, 2, 8, 13, 16, 17, 18, 20, 27, 31])


if __name__ == "__main__":
    main()
