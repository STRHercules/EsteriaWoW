"""Compare the shipped Vulpera model/skins/textures with the donor archive."""

from __future__ import annotations

import ctypes
import hashlib
import sys
from pathlib import Path

REPO = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW")
sys.path.insert(0, str(REPO / "tools"))

from cars_mount_pack import DLL_DEFAULT, H, Storm  # noqa: E402

OURS = REPO / "3.3.5a - Dev/Data"
OUR_ARCHIVES = ("Patch-C.MPQ", "PATCH-X.MPQ", "Patch-Y.MPQ", "Patch-D.MPQ", "Patch-E.MPQ", "Patch-G.MPQ", "PATCH-A.MPQ")
DONOR = Path(r"G:\Eunoia\Client\data")
DONOR_ARCHIVES = ("Patch-5.mpq", "Patch-4.mpq", "Patch-9.mpq", "Patch-8.mpq", "patch-I.mpq", "Patch-6.mpq", "Patch-7.mpq")
KEYS = (
    r"character\vulpera\male\vulperamale.m2",
    r"character\vulpera\male\vulperamale00.skin",
    r"character\vulpera\male\vulperamale01.skin",
    r"character\vulpera\male\vulperamale02.skin",
    r"character\vulpera\male\vulperamale03.skin",
    r"character\vulpera\female\vulperafemale.m2",
    r"character\vulpera\male\vulperamaleskin00_00.blp",
)


def open_all(storm: Storm, root: Path, names: tuple[str, ...]) -> list:
    handles = []
    for name in names:
        path = root / name
        if not path.is_file():
            continue
        handle = H()
        if storm.dll.SFileOpenArchive(str(path), 0, 0x100, ctypes.byref(handle)):
            handles.append((name, handle))
    return handles


def read(storm: Storm, handles: list, key: str) -> tuple[str, bytes] | None:
    for name, handle in handles:
        try:
            return name, storm.read(handle, key)
        except Exception:
            continue
    return None


def main() -> None:
    storm = Storm(DLL_DEFAULT)
    ours = open_all(storm, OURS, OUR_ARCHIVES)
    donor = open_all(storm, DONOR, DONOR_ARCHIVES)
    try:
        for key in KEYS:
            a = read(storm, ours, key)
            b = read(storm, donor, key)
            left = f"{len(a[1]):,} sha1={hashlib.sha1(a[1]).hexdigest()[:12]} <- {a[0]}" if a else "missing"
            right = f"{len(b[1]):,} sha1={hashlib.sha1(b[1]).hexdigest()[:12]} <- {b[0]}" if b else "missing"
            same = "SAME" if a and b and hashlib.sha1(a[1]).digest() == hashlib.sha1(b[1]).digest() else "DIFFERENT"
            print(f"{key}\n   ours : {left}\n   donor: {right}\n   -> {same}")
    finally:
        for _name, handle in ours + donor:
            storm.dll.SFileCloseArchive(handle)


if __name__ == "__main__":
    main()
