"""Dump CreatureModelData rows for the Vulpera models with every string field."""
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
               "enUS\\patch-enUS-5.MPQ"]
WANT = {"ours": (112885, 112886), "donor": (10786, 10787)}


def load(root: Path, order, key: str):
    storm = Storm(DLL_DEFAULT)
    payload = None
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
            except Exception:
                pass
        finally:
            storm.dll.SFileCloseArchive(handle)
    return payload


def main() -> None:
    storm = Storm(DLL_DEFAULT)
    for label, root, order in (("ours", CLIENT, OUR_ORDER), ("donor", DONOR, DONOR_ORDER)):
        payload = load(root, order, "DBFilesClient\\CreatureModelData.dbc")
        _, count, fields, record, pool_size = struct.unpack("<4sIIII", payload[:20])
        pool = payload[20 + count * record:]
        rows = {}
        for index in range(count):
            row = struct.unpack_from(f"<{fields}I", payload, 20 + index * record)
            rows[row[0]] = row

        def text(value: int) -> str:
            if not 0 < value < len(pool):
                return ""
            end = pool.find(b"\0", value)
            return pool[value:end].decode("latin1", "replace")

        print(f"=== {label}: {count} rows, {fields} fields")
        for model_id in WANT[label]:
            row = rows.get(model_id)
            if row is None:
                print(f"  model {model_id}: MISSING")
                continue
            strings = [(index, text(value)) for index, value in enumerate(row) if text(value)]
            print(f"  model {model_id}: {strings}")


if __name__ == "__main__":
    main()
