"""Check every texture a custom race M2 references: existence and dimensions."""

from __future__ import annotations

import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "tools"))

from cars_mount_pack import DLL_DEFAULT, Storm  # noqa: E402

CLIENT = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW\3.3.5a - Dev")
ARCHIVES = (
    "Data/PATCH-A.MPQ",
    "Data/Patch-C.MPQ",
    "Data/common.MPQ",
    "Data/patch.MPQ",
    "Data/expansion.MPQ",
    "Data/lichking.MPQ",
)
MODELS = (
    r"character\vulpera\male\vulperamale.m2",
    r"character\vulpera\female\vulperafemale.m2",
    r"character\pandaren\male\pandarenmale.m2",
    r"character\pandaren\female\pandarenfemale.m2",
)


def main() -> None:
    storm = Storm(DLL_DEFAULT)
    pool: dict[str, tuple[str, str]] = {}
    for relative in ARCHIVES:
        path = CLIENT / relative
        if not path.is_file():
            continue
        try:
            handle = storm.open_archive(path)
        except Exception:  # noqa: BLE001
            continue
        try:
            for name, *_ in storm.list_files(handle):
                pool.setdefault(name.casefold().replace("/", "\\"), (relative, name))
        finally:
            storm.dll.SFileCloseArchive(handle)

    for model in MODELS:
        entry = pool.get(model)
        if entry is None:
            print(f"{model}: model not found")
            continue
        handle = storm.open_archive(CLIENT / entry[0])
        try:
            data = storm.read(handle, entry[1])
            count, offset = struct.unpack_from("<II", data, 0x50)
            textures = []
            for index in range(count):
                base = offset + index * 16
                tex_type, flags = struct.unpack_from("<II", data, base)
                length, name_offset = struct.unpack_from("<II", data, base + 8)
                if not length:
                    continue
                name = data[name_offset : name_offset + length].decode("ascii", "replace")
                textures.append((tex_type, flags, name.rstrip("\x00")))
        finally:
            storm.dll.SFileCloseArchive(handle)

        print(f"== {model} ==")
        for tex_type, flags, name in textures:
            target = pool.get(name.casefold().replace("/", "\\"))
            if target is None:
                print(f"   MISSING {name} (type={tex_type} flags={flags:#x})")
                continue
            handle = storm.open_archive(CLIENT / target[0])
            try:
                blob = storm.read(handle, target[1])
            finally:
                storm.dll.SFileCloseArchive(handle)
            magic = blob[:4]
            if magic == b"BLP2":
                width, height = struct.unpack_from("<II", blob, 12)
            else:
                width = height = 0
            print(
                f"   {name} ({target[0]}) type={tex_type} flags={flags:#x} "
                f"magic={magic!r} {width}x{height} bytes={len(blob)}"
            )


if __name__ == "__main__":
    main()
