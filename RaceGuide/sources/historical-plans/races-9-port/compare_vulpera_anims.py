"""Compare our Vulpera external .anim set with the donor client's, file by file."""

from __future__ import annotations

import ctypes
import hashlib
import sys
from pathlib import Path

REPO = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW")
sys.path.insert(0, str(REPO / "tools"))

from cars_mount_pack import DLL_DEFAULT, H, Storm  # noqa: E402

OURS = REPO / "3.3.5a - Dev/Data"
# Highest priority first: the client reads Patch-Y before PATCH-X before Patch-C.
OUR_ARCHIVES = ("Patch-Y.MPQ", "PATCH-X.MPQ", "Patch-C.MPQ", "Patch-G.MPQ", "Patch-E.MPQ", "Patch-D.MPQ", "PATCH-A.MPQ")
DONOR = Path(r"G:\Eunoia\Client\data")
DONOR_ARCHIVES = ("Patch-5.mpq", "Patch-4.mpq", "Patch-9.mpq", "Patch-8.mpq", "patch-I.mpq", "Patch-6.mpq", "Patch-7.mpq")
MAX_INDEX = 1500
MAX_VARIATION = 4


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
        for gender in ("male", "female"):
            stem = f"character\\vulpera\\{gender}\\vulpera{gender}"
            missing: list[str] = []
            differing: list[str] = []
            ours_only: list[str] = []
            donor_count = 0
            for index in range(MAX_INDEX):
                for variation in range(MAX_VARIATION):
                    key = f"{stem}{index:04d}-{variation:02d}.anim"
                    a = read(storm, ours, key)
                    b = read(storm, donor, key)
                    if b is not None:
                        donor_count += 1
                    if a is None and b is not None:
                        missing.append(f"{index:04d}-{variation:02d}")
                    elif a is not None and b is None:
                        ours_only.append(f"{index:04d}-{variation:02d}")
                    elif a is not None and b is not None:
                        if hashlib.sha1(a[1]).digest() != hashlib.sha1(b[1]).digest():
                            differing.append(f"{index:04d}-{variation:02d} ({len(a[1])} vs {len(b[1])})")
            print(f"== {gender}: donor anims={donor_count} ours_missing={len(missing)} "
                  f"ours_only={len(ours_only)} differing={len(differing)}")
            if missing:
                print(f"   MISSING (donor has, we do not): {missing[:40]}")
            if ours_only:
                print(f"   ours-only: {ours_only[:20]}")
            if differing:
                print(f"   differing bytes: {differing[:20]}")
    finally:
        for _name, handle in ours + donor:
            storm.dll.SFileCloseArchive(handle)


if __name__ == "__main__":
    main()
