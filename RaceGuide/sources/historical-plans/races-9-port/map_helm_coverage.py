"""Donor ChrRaces prefixes, plus per-prefix helmet model coverage in both clients."""
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
DONOR_ORDER = ["common.mpq", "common-2.mpq", "expansion.mpq", "lichking.mpq", "patch.mpq",
               "patch-2.mpq", "patch-3.mpq", "Patch-4.mpq", "Patch-5.mpq", "Patch-6.mpq",
               "Patch-7.mpq", "Patch-8.mpq", "Patch-9.mpq", "patch-I.mpq", "patch-m.mpq",
               "patch-x.mpq", "patch-y.mpq", "patch-z.mpq"]
PREFIX = "item\\objectcomponents\\head\\"
SUFFIX = re.compile(r"^(.+)_([a-z]{2})([mf])\.m2$", re.I)


def coverage(storm: Storm, root: Path, order):
    per_prefix: dict[str, set[str]] = {}
    per_stem: dict[str, set[str]] = {}
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
            lower = entry[0].lower()
            if not lower.startswith(PREFIX):
                continue
            match = SUFFIX.match(entry[0][len(PREFIX):])
            if not match:
                continue
            stem, code, _ = match.groups()
            per_prefix.setdefault(code.lower(), set()).add(stem + "_" + match.group(3).lower())
            per_stem.setdefault(stem.lower(), set()).add(code.lower())
    return per_prefix, per_stem


def donor_races(storm: Storm):
    payload = None
    source = None
    for name in DONOR_ORDER:
        path = DONOR / name
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
    if payload is None:
        return None, None
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
    return source, (rows, text)


def main() -> None:
    storm = Storm(DLL_DEFAULT)
    ours_prefixes, ours_stems = coverage(storm, CLIENT, OUR_ORDER)
    donor_prefixes, donor_stems = coverage(storm, DONOR, DONOR_ORDER)

    print("helmet model coverage per race code")
    print(f"  {'code':<6}{'ours':>8}{'donor':>8}", "  (files for fm)")
    for code in sorted(set(ours_prefixes) | set(donor_prefixes)):
        print(f"  {code.upper():<6}{len(ours_prefixes.get(code, ())):>8}"
              f"{len(donor_prefixes.get(code, ())):>8}")

    source, parsed = donor_races(storm)
    print(f"\ndonor ChrRaces from {source}")
    if parsed is None:
        print("  not found")
        return
    rows, text = parsed
    for race in sorted(rows):
        row = rows[race]
        prefix = text(row[6])
        print(f"  race {race:>3} prefix={prefix!r:<14} file={text(row[13])!r:<22} "
              f"helmours={len(ours_prefixes.get(prefix.lower(), ()))} "
              f"helmdonor={len(donor_prefixes.get(prefix.lower(), ()))}")


if __name__ == "__main__":
    main()
