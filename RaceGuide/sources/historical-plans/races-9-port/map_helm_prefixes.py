"""Which race/sex suffixes exist for helmet object models, ours vs donor.

Also prints the ChrRaces ClientPrefix for every race so the two can be compared.
"""
from __future__ import annotations

import ctypes
import re
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
STEM = r"item\objectcomponents\head\helm_cloth_a_01_"
SUFFIX = re.compile(re.escape(STEM) + r"([a-z]{2})([mf])\.m2$")


def suffixes(storm: Storm, root: Path, order) -> dict[str, set[str]]:
    found: dict[str, set[str]] = {}
    for name in order:
        path = root / name
        if not path.is_file():
            continue
        handle = H()
        if not storm.dll.SFileOpenArchive(str(path), 0, 0x100, ctypes.byref(handle)):
            continue
        try:
            try:
                listing = storm.list_files(handle)
            except Exception:
                listing = []
        finally:
            storm.dll.SFileCloseArchive(handle)
        for entry in listing:
            match = SUFFIX.match(entry[0].lower())
            if match:
                found.setdefault(match.group(1), set()).add(match.group(2))
    return found


def read_dbc(storm: Storm, key: str) -> tuple[str, bytes] | None:
    for name in reversed(OUR_ORDER):
        path = CLIENT / name
        if not path.is_file():
            continue
        handle = H()
        if not storm.dll.SFileOpenArchive(str(path), 0, 0x100, ctypes.byref(handle)):
            continue
        try:
            try:
                return name, storm.read(handle, key)
            except Exception:
                pass
        finally:
            storm.dll.SFileCloseArchive(handle)
    return None


def main() -> None:
    storm = Storm(DLL_DEFAULT)
    ours = suffixes(storm, CLIENT, OUR_ORDER)
    donor = suffixes(storm, DONOR, sorted(p.name for p in DONOR.glob("*.mpq")))
    keys = sorted(set(ours) | set(donor))
    print("prefix  ours donor")
    for key in keys:
        print(f"  {key.upper():<4}  {''.join(sorted(ours.get(key, ()))):>4} "
              f"{''.join(sorted(donor.get(key, ()))):>5}")

    hit = read_dbc(storm, "DBFilesClient\\ChrRaces.dbc")
    if hit is None:
        raise SystemExit("ChrRaces.dbc not found")
    name, payload = hit
    _, rows, fields, record, _ = struct.unpack("<4sIIII", payload[:20])
    offset = 20 + rows * record
    pool = payload[offset:].split(b"\0")

    def text(value: int) -> str:
        return pool[value].decode("latin1") if 0 < value < len(pool) else ""

    print(f"\nChrRaces ({name}), {rows} rows, {fields} fields")
    for index in range(rows):
        row = struct.unpack_from(f"<{fields}I", payload, 20 + index * record)
        if row[0] > 40:
            continue
        prefix = text(row[6])
        sex = "".join(sorted(ours.get(prefix.lower(), ())))
        print(f"  race {row[0]:>2} prefix={prefix!r:<6} alliance={row[3]}/{row[2]:<3} "
              f"helmsex={sex or 'NONE'}")


if __name__ == "__main__":
    main()
