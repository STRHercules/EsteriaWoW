"""Compare M2 texture type slots between the Vulpera and Pandaren character models."""

from __future__ import annotations

import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "tools"))

from cars_mount_pack import DLL_DEFAULT, Storm  # noqa: E402

LIVE = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW\3.3.5a - Dev\Data\Patch-C.MPQ")
MODELS = (
    r"character\vulpera\male\vulperamale.m2",
    r"character\pandaren\male\pandarenmale.m2",
    r"character\vulpera\female\vulperafemale.m2",
    r"character\pandaren\female\pandarenfemale.m2",
)


def describe(data: bytes) -> None:
    magic, version = struct.unpack_from("<4sI", data, 0)
    if magic != b"MD20":
        print(f"    not an MD20 model ({magic!r})")
        return
    texture_count, texture_offset = struct.unpack_from("<II", data, 0x50)
    print(f"    version={version} textures={texture_count}")
    for index in range(texture_count):
        entry = texture_offset + index * 16
        tex_type, flags = struct.unpack_from("<II", data, entry)
        name_length, name_offset = struct.unpack_from("<II", data, entry + 8)
        name = data[name_offset : name_offset + name_length].decode("ascii", "replace")
        print(f"      [{index}] type={tex_type} flags=0x{flags:02x} name={name}")


def main() -> None:
    storm = Storm(DLL_DEFAULT)
    handle = storm.open_archive(LIVE)
    try:
        names = {name.casefold(): name for name, *_ in storm.list_files(handle)}
        for wanted in MODELS:
            actual = names.get(wanted)
            print(f"== {wanted} ==")
            if actual is None:
                print("    missing from archive")
                continue
            describe(storm.read(handle, actual))
    finally:
        storm.dll.SFileCloseArchive(handle)


if __name__ == "__main__":
    main()
