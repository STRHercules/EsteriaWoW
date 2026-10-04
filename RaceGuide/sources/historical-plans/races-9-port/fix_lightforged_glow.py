"""Make the Lightforged skin overlay render like the Eredar one.

The Eredar and Lightforged models we ship are the same file to within 46 bytes.
The only functional difference is `CreatureModelData`-independent: entry 14 of
the model's texture-replace table, `(4, 4)` on the Eredar (whose skin glow
renders in this client) against `(2, 4)` on the Lightforged. Everything else -
textures, texture animations, transforms, geosets - is identical.

This copies the Eredar's replace entry onto the Lightforged model so the
Lightforged skin overlay (the golden rune layer in
`lightforgeddraeneimaleskinEXTRA_*.blp`) is bound the same way.
"""

from __future__ import annotations

import argparse
import struct
import sys
from pathlib import Path

REPO = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW")
sys.path.insert(0, str(REPO / "tools"))
sys.path.insert(0, str(REPO / ".agents/plans/races-9-port"))

from cars_mount_pack import DLL_DEFAULT, H, Storm  # noqa: E402

PATCH_D = REPO / "3.3.5a - Dev/Data/Patch-D.MPQ"
BACKUP = REPO / "3.3.5a - Dev/Backups/patch-d-before-voidelf-ears-20260913-153829/Patch-D.MPQ"
TEXTURE_REPLACE_HEADER = 0x68
ENTRY = 14
# Male and female models differ again on the last replace entry: the males bind
# texture unit 0 to replaceable 4, the females to 52, which this client renders
# without the hand/foot overlay. Both Eredar and Lightforged females share it.
FEMALE_ENTRY = 20
FEMALE_REFERENCE = "Character\\Eredar\\Male\\EredarMale.m2"
FEMALES = (
    "Character\\Eredar\\Female\\EredarFemale",
    "character\\lightforgeddraenei\\female\\lightforgeddraeneifemale",
)
GENDERS = (
    (
        "Character\\Eredar\\Male\\EredarMale",
        "character\\lightforgeddraenei\\male\\lightforgeddraeneimale",
    ),
    (
        "Character\\Eredar\\Female\\EredarFemale",
        "character\\lightforgeddraenei\\female\\lightforgeddraeneifemale",
    ),
)


def entries_of(data: bytes) -> list[tuple[int, int]]:
    count, offset = struct.unpack_from("<II", data, TEXTURE_REPLACE_HEADER)
    return [struct.unpack_from("<HH", data, offset + index * 4) for index in range(count)]


def replace_offset(data: bytes, entry: int = ENTRY) -> int:
    _count, offset = struct.unpack_from("<II", data, TEXTURE_REPLACE_HEADER)
    return offset + entry * 4


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    storm = Storm(DLL_DEFAULT)
    handle = storm.open_archive(PATCH_D)
    try:
        live = {name.casefold(): name for name, *_ in storm.list_files(handle)}
        updates: dict[str, bytes] = {}
        for donor_stem, stem in GENDERS:
            donor_name = live.get((donor_stem + ".m2").casefold())
            if donor_name is None:
                raise SystemExit(f"donor model missing from Patch-D: {donor_stem}")
            donor = storm.read(handle, donor_name)
            want = entries_of(donor)[ENTRY]
            for suffix in (".m2", ".mdx"):
                key = (stem + suffix).casefold()
                name = live.get(key)
                if name is None:
                    print(f"{stem}{suffix}: not in Patch-D")
                    continue
                payload = storm.read(handle, name)
                have = entries_of(payload)[ENTRY]
                print(f"{name}: entry {ENTRY} {have} -> {want}")
                if have == want:
                    continue
                updated = bytearray(payload)
                struct.pack_into("<HH", updated, replace_offset(payload), *want)
                updates[name] = bytes(updated)
        reference_name = live.get(FEMALE_REFERENCE.casefold())
        if reference_name is None:
            raise SystemExit(f"reference model missing from Patch-D: {FEMALE_REFERENCE}")
        reference = storm.read(handle, reference_name)
        want = entries_of(reference)[FEMALE_ENTRY]
        for stem in FEMALES:
            for suffix in (".m2", ".mdx"):
                name = live.get((stem + suffix).casefold())
                if name is None:
                    print(f"{stem}{suffix}: not in Patch-D")
                    continue
                payload = storm.read(handle, name)
                have = entries_of(payload)[FEMALE_ENTRY]
                print(f"{name}: entry {FEMALE_ENTRY} {have} -> {want}")
                if have == want:
                    continue
                updated = bytearray(payload)
                struct.pack_into("<HH", updated, replace_offset(payload, FEMALE_ENTRY), *want)
                updates[name] = bytes(updated)
    finally:
        storm.dll.SFileCloseArchive(handle)
    if not updates:
        raise SystemExit("nothing to change")
    if args.dry_run:
        print("dry run - Patch-D untouched")
        return
    storm.replace_archive_entries(PATCH_D, updates)
    print(f"Patch-D updated ({len(updates)} entries); rollback archive: {BACKUP}")


if __name__ == "__main__":
    main()
