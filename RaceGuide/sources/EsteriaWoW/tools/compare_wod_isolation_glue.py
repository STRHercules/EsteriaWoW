"""Compare effective GlueXML payloads between the WoD donor and isolation client."""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

TOOL_DIR = Path(__file__).resolve().parent
if str(TOOL_DIR) not in sys.path:
    sys.path.insert(0, str(TOOL_DIR))

from cars_mount_pack import DLL_DEFAULT, FindData, Storm  # noqa: E402
from mount_pack_batch2 import client_archive_chain  # noqa: E402

DONOR = Path(r"F:\Wrath of the Lich King 3.3.5a (wod models)\Data")
ISOLATION = Path(r"G:\3.3.5a - Dev\_WOD_RUNTIME_ISOLATION\Data")


def archive_names_tolerant(storm: Storm, archive) -> list[str]:
    data = FindData()
    finder = storm.dll.SFileFindFirstFile(archive, b"*", __import__("ctypes").byref(data), None)
    if not finder:
        return []
    names: list[str] = []
    try:
        while True:
            raw = data.cFileName.split(b"\0", 1)[0]
            names.append(raw.decode("ascii", errors="replace"))
            if not storm.dll.SFileFindNextFile(finder, __import__("ctypes").byref(data)):
                break
    finally:
        storm.dll.SFileFindClose(finder)
    return names


def effective_glue(root: Path, storm: Storm) -> tuple[dict[str, str], dict[str, str]]:
    hashes: dict[str, str] = {}
    sources: dict[str, str] = {}
    for archive_path in client_archive_chain(root, "enUS"):
        try:
            archive = storm.open_archive(archive_path)
        except Exception:
            continue
        try:
            for name in archive_names_tolerant(storm, archive):
                key = name.casefold()
                if not key.startswith("interface\\gluexml\\") or key in hashes:
                    continue
                try:
                    payload = storm.read(archive, name)
                except Exception:
                    continue
                hashes[key] = hashlib.sha256(payload).hexdigest()
                sources[key] = str(archive_path)
        finally:
            storm.dll.SFileCloseArchive(archive)
    return hashes, sources


def glue_inventory(root: Path, storm: Storm) -> list[tuple[Path, int]]:
    inventory: list[tuple[Path, int]] = []
    for archive_path in client_archive_chain(root, "enUS"):
        try:
            archive = storm.open_archive(archive_path)
        except Exception:
            continue
        try:
            count = sum(
                1
                for name in archive_names_tolerant(storm, archive)
                if name.casefold().startswith("interface\\gluexml\\")
            )
            if count:
                inventory.append((archive_path, count))
        finally:
            storm.dll.SFileCloseArchive(archive)
    return inventory


def main() -> int:
    storm = Storm(DLL_DEFAULT)
    donor_hashes, donor_sources = effective_glue(DONOR, storm)
    iso_hashes, iso_sources = effective_glue(ISOLATION, storm)
    keys = sorted(set(donor_hashes) | set(iso_hashes))
    differences = [key for key in keys if donor_hashes.get(key) != iso_hashes.get(key)]

    print(f"donor effective GlueXML files: {len(donor_hashes)}")
    print(f"isolation effective GlueXML files: {len(iso_hashes)}")
    print(f"different/missing files: {len(differences)}")
    print("isolation archives containing GlueXML:")
    for archive_path, count in glue_inventory(ISOLATION, storm):
        print(f"  {count:3d}  {archive_path}")
    for key in differences:
        print(key)
        print(f"  donor: {donor_sources.get(key, '<missing>')}")
        print(f"  iso:   {iso_sources.get(key, '<missing>')}")
    return 1 if differences else 0


if __name__ == "__main__":
    raise SystemExit(main())
