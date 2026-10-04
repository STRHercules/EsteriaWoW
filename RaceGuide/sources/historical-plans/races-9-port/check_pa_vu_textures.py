"""Do the donor's Pa/Vu head models reference textures, and can we supply them?"""
from __future__ import annotations

import ctypes
import re
import sys
from pathlib import Path

REPO = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW")
sys.path.insert(0, str(REPO / "tools"))
from cars_mount_pack import DLL_DEFAULT, H, Storm  # noqa: E402

DONOR = Path(r"G:\Eunoia\Client\data")
CLIENT = REPO / "3.3.5a - Dev/Data"
DONOR_ORDER = ["common.mpq", "common-2.mpq", "expansion.mpq", "lichking.mpq", "patch.mpq",
               "patch-2.mpq", "patch-3.mpq", "Patch-4.mpq", "Patch-5.mpq", "Patch-6.mpq",
               "Patch-7.mpq", "Patch-8.mpq", "Patch-9.mpq", "patch-I.mpq", "patch-m.mpq",
               "patch-x.mpq", "patch-y.mpq", "patch-z.mpq"]
OUR_ORDER = ["common.MPQ", "common-2.MPQ", "expansion.MPQ", "lichking.MPQ", "patch.MPQ",
             "patch-2.MPQ", "patch-3.MPQ", "patch-4.mpq", "PATCH-A.MPQ", "Patch-B.MPQ",
             "Patch-C.MPQ", "Patch-D.MPQ", "Patch-E.MPQ", "Patch-F.MPQ", "Patch-G.MPQ",
             "Patch-O.mpq", "PATCH-X.MPQ", "Patch-Y.MPQ"]
STEM = "item\\objectcomponents\\head\\"
PATTERN = re.compile(rb"[ -~]{5,}?\.(blp|tga)", re.IGNORECASE)


def open_all(storm: Storm, root: Path, order):
    out = []
    for name in order:
        path = root / name
        if not path.is_file():
            continue
        handle = H()
        if storm.dll.SFileOpenArchive(str(path), 0, 0x100, ctypes.byref(handle)):
            out.append((name, handle))
    return out


def read(storm: Storm, handles, key: str):
    for name, handle in reversed(handles):
        try:
            return name, storm.read(handle, key)
        except Exception:
            continue
    return None, None


def main() -> None:
    storm = Storm(DLL_DEFAULT)
    donor = open_all(storm, DONOR, DONOR_ORDER)
    ours = open_all(storm, CLIENT, OUR_ORDER)
    try:
        names = []
        for name, handle in donor:
            if name.lower() != "patch-i.mpq":
                continue
            try:
                listing = storm.list_files(handle)
            except Exception:
                listing = []
            for entry in listing:
                lower = entry[0].lower()
                if not lower.startswith(STEM) or not lower.endswith(".m2"):
                    continue
                tail = entry[0][len(STEM):]
                if re.search(r"_(Pa|Vu)[MF]\.m2$", tail, re.I):
                    names.append(entry[0])
        print(f"{len(names)} donor Pa/Vu .m2 files")
        textures = set()
        sampled = 0
        for key in names:
            _src, payload = read(storm, donor, key)
            if payload is None:
                continue
            sampled += 1
            for match in PATTERN.finditer(payload):
                textures.add(match.group().decode("latin1"))
            if sampled >= 40:
                break
        print(f"sampled {sampled} models, {len(textures)} distinct texture paths")
        missing = []
        for key in sorted(textures):
            ours_src, _ = read(storm, ours, key)
            donor_src, _ = read(storm, donor, key)
            if ours_src is None:
                missing.append((key, donor_src))
        print(f"textures missing from our client: {len(missing)}")
        for key, src in missing[:25]:
            print(f"   {key}  (donor: {src})")
    finally:
        for _name, handle in donor + ours:
            storm.dll.SFileCloseArchive(handle)


if __name__ == "__main__":
    main()
