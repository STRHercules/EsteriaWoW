from __future__ import annotations

import hashlib
from collections import Counter
from pathlib import Path

from cars_mount_pack import DLL_DEFAULT, Storm

CLIENT = Path(r"G:\3.3.5a - Dev\Data")
OG = CLIENT / "OG"

IMPORTANT = {
    r"DBFilesClient\AreaTable.dbc",
    r"DBFilesClient\ChrRaces.dbc",
    r"DBFilesClient\CharSections.dbc",
    r"DBFilesClient\CharHairGeosets.dbc",
    r"DBFilesClient\CharHairTextures.dbc",
    r"DBFilesClient\CharacterFacialHairStyles.dbc",
    r"DBFilesClient\BarberShopStyle.dbc",
    r"DBFilesClient\CreatureDisplayInfo.dbc",
    r"DBFilesClient\CreatureDisplayInfoExtra.dbc",
    r"DBFilesClient\CreatureModelData.dbc",
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def names(storm: Storm, archive: Path) -> dict[str, str]:
    handle = storm.open_archive(archive)
    try:
        return {name.casefold(): name for name, *_ in storm.list_files(handle)}
    finally:
        storm.dll.SFileCloseArchive(handle)


def read(storm: Storm, archive: Path, path: str) -> bytes | None:
    handle = storm.open_archive(archive)
    try:
        try:
            return storm.read(handle, path)
        except OSError:
            return None
    finally:
        storm.dll.SFileCloseArchive(handle)


def root_name(path: str) -> str:
    normalized = path.replace("/", "\\")
    return normalized.split("\\", 1)[0]


def main() -> int:
    storm = Storm(DLL_DEFAULT)
    old_archives = sorted(OG.glob("*.mpq"), key=lambda p: p.name.casefold())
    current = {p.name.casefold(): p for p in CLIENT.glob("*.mpq")}

    for old in old_archives:
        new = current.get(old.name.casefold())
        old_names = names(storm, old)
        new_names = names(storm, new) if new else {}
        overlap = set(old_names) & set(new_names)
        only_old = set(old_names) - set(new_names)
        different = []
        same = 0
        for key in sorted(overlap):
            a = read(storm, old, old_names[key])
            b = read(storm, new, new_names[key]) if new else None
            if a == b:
                same += 1
            else:
                different.append(key)

        roots = Counter(root_name(name) for name in old_names.values())
        print(f"\n=== {old.name} ===")
        print(f"old_files={len(old_names)} new_files={len(new_names)} overlap={len(overlap)} same={same} different={len(different)} old_only={len(only_old)}")
        print("old top roots:", roots.most_common(15))
        print("old-only samples:")
        for key in sorted(only_old)[:80]:
            print("  ", old_names[key])
        print("different-overlap samples:")
        for key in different[:80]:
            print("  ", old_names[key])
        print("important rows:")
        for wanted in sorted(IMPORTANT):
            key = wanted.casefold()
            in_old = key in old_names
            in_new = key in new_names
            if not in_old and not in_new:
                continue
            status = ""
            if in_old and in_new:
                status = "same" if read(storm, old, old_names[key]) == read(storm, new, new_names[key]) else "DIFFERENT"
            elif in_old:
                status = "old-only"
            else:
                status = "new-only"
            print(f"  {wanted}: {status}")

    print("\n=== Current AreaTable providers ===")
    for archive in sorted(CLIENT.glob("*.mpq"), key=lambda p: p.name.casefold()):
        n = names(storm, archive)
        key = r"DBFilesClient\AreaTable.dbc".casefold()
        if key in n:
            payload = read(storm, archive, n[key])
            print(f"{archive.name}\t{len(payload or b'')}\t{sha256_bytes(payload or b'')}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
