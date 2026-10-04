"""Locate and dump a model's attachment table.

Attachment records start with their id (0, 1, 2, ...), so the table can be found without
knowing the exact header layout: scan for an array whose first dword of each record counts up.
"""

from __future__ import annotations

import ctypes
import struct
import sys
from pathlib import Path

REPO = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW")
sys.path.insert(0, str(REPO / "tools"))

from cars_mount_pack import DLL_DEFAULT, H, Storm  # noqa: E402

OURS = REPO / "3.3.5a - Dev/Data"
OUR_ARCHIVES = ("Patch-Y.MPQ", "PATCH-X.MPQ", "Patch-G.MPQ", "Patch-E.MPQ", "Patch-D.MPQ",
                "Patch-C.MPQ", "PATCH-A.MPQ", "lichking.MPQ", "patch.MPQ")
MODELS = {
    "broken_male": r"character\esteriabroken\male\brokenmale.m2",
    "eredar_male": r"character\eredar\male\eredarmale.m2",
    "vulpera_male": r"character\vulpera\male\vulperamale.m2",
    "dracthyr_male": r"character\dracthyr\male\dracthyrmale.m2",
    "dracthyr_female": r"character\dracthyr\female\dracthyrfemale.m2",
}


def read_model(storm: Storm, key: str) -> bytes | None:
    for name in OUR_ARCHIVES:
        path = OURS / name
        if not path.is_file():
            continue
        handle = H()
        if not storm.dll.SFileOpenArchive(str(path), 0, 0x100, ctypes.byref(handle)):
            continue
        try:
            try:
                return storm.read(handle, key)
            except Exception:
                continue
        finally:
            storm.dll.SFileCloseArchive(handle)
    return None


def find_attachments(data: bytes) -> tuple[int, int, int] | None:
    """Walk the header's (count, offset) array descriptors and keep the one that looks like
    an attachment table: records whose first dword counts 0, 1, 2, ... in order."""
    for header_offset in range(0x30, 0x150, 4):
        count, offset = struct.unpack_from("<II", data, header_offset)
        if not (4 <= count <= 64) or offset == 0 or offset + 4 > len(data):
            continue
        for stride in (0x1C, 0x20, 0x24, 0x28, 0x2C, 0x30):
            if offset + count * stride > len(data):
                continue
            if all(struct.unpack_from("<I", data, offset + index * stride)[0] == index
                   for index in range(count)):
                return count, offset, stride
    return None


def main() -> None:
    storm = Storm(DLL_DEFAULT)
    for label, key in MODELS.items():
        data = read_model(storm, key)
        if data is None:
            print(f"{label}: model not found")
            continue
        found = find_attachments(data)
        if not found:
            print(f"{label}: no attachment table found")
            continue
        count, offset, stride = found
        print(f"== {label} ({len(data):,} bytes): {count} attachments at {offset:#x}, stride {stride:#x}")
        for index in range(count):
            base = offset + index * stride
            entry_id, bone = struct.unpack_from("<II", data, base)
            position = struct.unpack_from("<3f", data, base + 8)
            print(f"   id {entry_id:>2} bone {bone:>4} pos ({position[0]:+.4f}, {position[1]:+.4f}, {position[2]:+.4f})")


if __name__ == "__main__":
    main()
