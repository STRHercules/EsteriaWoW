"""Brute-force locate the attachment array: ordered small ids at a fixed stride."""
from __future__ import annotations

import ctypes
import struct
import sys
from pathlib import Path

REPO = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW")
sys.path.insert(0, str(REPO / "tools"))
from cars_mount_pack import DLL_DEFAULT, H, Storm  # noqa: E402

CLIENT = REPO / "3.3.5a - Dev/Data"
ORDER = ["common.MPQ", "common-2.MPQ", "expansion.MPQ", "lichking.MPQ", "patch.MPQ",
         "patch-2.MPQ", "patch-3.MPQ", "patch-4.mpq", "PATCH-A.MPQ", "Patch-B.MPQ",
         "Patch-C.MPQ", "Patch-D.MPQ", "Patch-E.MPQ", "Patch-F.MPQ", "Patch-G.MPQ",
         "Patch-O.mpq", "PATCH-X.MPQ", "Patch-Y.MPQ"]
KEYS = {
    "human": "character\\human\\male\\humanmale.m2",
    "vulpera": "character\\vulpera\\male\\vulperamale.m2",
    "eredar": "character\\eredar\\male\\eredarmale.m2",
}


def load(storm: Storm, key: str):
    for name in ORDER:
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
    return None, None


def scan(payload: bytes):
    size = len(payload)
    for stride in (0x20, 0x24, 0x28, 0x2C, 0x30, 0x34, 0x38, 0x3C):
        for offset in range(0x40, min(size - stride * 12, 0x400000)):
            values = []
            for index in range(12):
                here = offset + index * stride
                value = struct.unpack_from("<I", payload, here)[0]
                if value != index:
                    break
                values.append(value)
            else:
                yield stride, offset, 12
                continue


def main() -> None:
    storm = Storm(DLL_DEFAULT)
    for label, key in KEYS.items():
        source, payload = load(storm, key)
        if payload is None:
            print(f"{label}: missing")
            continue
        hits = list(scan(payload))
        print(f"== {label} [{source}] size={len(payload):,}: {len(hits)} candidate tables")
        for stride, offset, count in hits[:5]:
            print(f"   stride {stride:#x} offset {offset:#x} (first {count} ids 0..11)")
            for index in range(min(count, 12)):
                record = offset + index * stride
                identifier, bone = struct.unpack_from("<IH", payload, record)
                rest = struct.unpack_from("<4I", payload, record + 8)
                values = struct.unpack_from("<II", payload, record + 0x14) if stride >= 0x20 else (0, 0)
                pivot = ""
                if 1 <= values[0] <= 4 and values[1] + 12 <= len(payload):
                    point = struct.unpack_from("<3f", payload, values[1])
                    pivot = f"pivot=({point[0]:+.3f}, {point[1]:+.3f}, {point[2]:+.3f})"
                print(f"      id {identifier:>2} bone {bone:>3} words={rest} {pivot}")


if __name__ == "__main__":
    main()
