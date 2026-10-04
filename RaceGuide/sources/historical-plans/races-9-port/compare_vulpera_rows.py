"""Numeric comparison of the Vulpera display/model rows, ours vs donor."""
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
               "enUS\locale-enUS.MPQ", "enUS\patch-enUS.MPQ",
               "enUS\patch-enUS-2.MPQ", "enUS\patch-enUS-3.MPQ",
               "enUS\patch-enUS-4.MPQ", "enUS\patch-enUS-5.MPQ"]


def load(root: Path, order, key: str):
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
                payload = storm.read(handle, key)
                source = name
            except Exception:
                pass
        finally:
            storm.dll.SFileCloseArchive(handle)
    return source, payload


def rows(payload: bytes):
    _, count, fields, record, _ = struct.unpack("<4sIIII", payload[:20])
    out = {}
    for index in range(count):
        row = struct.unpack_from(f"<{fields}I", payload, 20 + index * record)
        out[row[0]] = row
    return out, fields


def show(label: str, row, other, other_label: str) -> None:
    print(f"== {label}")
    for index, value in enumerate(row):
        as_float = struct.unpack("<f", struct.pack("<I", value))[0]
        reference = other[index] if other and index < len(other) else None
        marker = ""
        if reference is not None and reference != value:
            ref_float = struct.unpack("<f", struct.pack("<I", reference))[0]
            marker = f"   (donor {reference} / {ref_float:.4f})"
        print(f"   [{index:>2}] {value:>12}  float {as_float:>12.4f}{marker}")


def main() -> None:
    for key, want in (("DBFilesClient\\CreatureDisplayInfo.dbc", (141254, 32767)),
                      ("DBFilesClient\\CreatureModelData.dbc", (112885, 10786))):
        ours_source, ours_payload = load(CLIENT, OUR_ORDER, key)
        donor_source, donor_payload = load(DONOR, DONOR_ORDER, key)
        ours_rows, _ = rows(ours_payload)
        donor_rows, _ = rows(donor_payload)
        print(f"\n### {key} ours <- {ours_source}, donor <- {donor_source}")
        show(f"ours {want[0]}", ours_rows[want[0]], donor_rows.get(want[1]), f"donor {want[1]}")


if __name__ == "__main__":
    main()
