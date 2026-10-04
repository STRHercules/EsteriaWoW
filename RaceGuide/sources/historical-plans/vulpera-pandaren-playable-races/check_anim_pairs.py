"""Compare a model's declared animation entries with the .anim files the client can load.

The WotLK client loads external animation data as `<stem><animID:04d>-<subAnimID:02d>.anim`;
an entry with no file leaves the client without the track data it is about to evaluate.

Usage: python check_anim_pairs.py <stem> [<stem> ...]  (default: the custom race models)
"""

from __future__ import annotations

import struct
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "tools"))

from cars_mount_pack import DLL_DEFAULT, H, Storm  # noqa: E402

READ_ONLY = 0x00000100


def open_ro(storm: Storm, path: Path) -> H | None:
    handle = H()
    if not storm.dll.SFileOpenArchive(str(path), 0, READ_ONLY, __import__("ctypes").byref(handle)):
        return None
    return handle

CLIENT = REPO / "3.3.5a - Dev/Data"
ARCHIVES = (
    "Patch-Y.MPQ",
    "PATCH-X.MPQ",
    "Patch-G.MPQ",
    "Patch-E.MPQ",
    "Patch-D.MPQ",
    "Patch-C.MPQ",
    "Patch-B.MPQ",
    "PATCH-A.MPQ",
)
DEFAULT_STEMS = (
    r"character\vulpera\male\vulperamale",
    r"character\vulpera\female\vulperafemale",
    r"character\pandaren\male\pandarenmale",
    r"character\pandaren\female\pandarenfemale",
    r"character\esteriabroken\male\brokenmale",
)


def load(storm: Storm, name: str) -> bytes | None:
    for archive in ARCHIVES:
        path = CLIENT / archive
        if not path.is_file():
            continue
        handle = open_ro(storm, path)
        if handle is None:
            continue
        try:
            try:
                return storm.read(handle, name)
            except Exception:  # noqa: BLE001
                continue
        finally:
            storm.dll.SFileCloseArchive(handle)
    return None


def listing(storm: Storm) -> set[str]:
    names: set[str] = set()
    for archive in ARCHIVES:
        path = CLIENT / archive
        if not path.is_file():
            continue
        handle = open_ro(storm, path)
        if handle is None:
            continue
        try:
            names |= {entry.casefold() for entry, *_ in storm.list_files(handle)}
        finally:
            storm.dll.SFileCloseArchive(handle)
    return names


def animation_pairs(data: bytes) -> list[tuple[int, int, int]]:
    if data[:4] not in (b"MD20", b"MD21"):
        raise ValueError("not an M2 file")
    base = 0
    if data[:4] == b"MD21":
        base = struct.unpack_from("<I", data, 4)[0]
    count, offset = struct.unpack_from("<II", data, base + 0x54)
    pairs = []
    for index in range(count):
        record = base + offset + index * 0x28
        anim_id, sub_anim, length = struct.unpack_from("<III", data, record)
        pairs.append((anim_id, sub_anim, length))
    return pairs


def main() -> None:
    stems = tuple(sys.argv[1:]) or DEFAULT_STEMS
    storm = Storm(DLL_DEFAULT)
    names = listing(storm)
    for stem in stems:
        payload = load(storm, f"{stem}.m2")
        if payload is None:
            print(f"{stem}: model not found")
            continue
        pairs = animation_pairs(payload)
        missing = []
        for anim_id, sub_anim, length in pairs:
            name = f"{stem}{anim_id:04d}-{sub_anim:02d}.anim".casefold()
            if name not in names:
                missing.append((anim_id, sub_anim, length))
        print(f"{stem}: model {len(payload):,} bytes, animations={len(pairs)}, "
              f"external files missing={len(missing)}")
        for anim_id, sub_anim, length in missing[:12]:
            print(f"    missing {anim_id:04d}-{sub_anim:02d} (declared length {length})")


if __name__ == "__main__":
    main()
