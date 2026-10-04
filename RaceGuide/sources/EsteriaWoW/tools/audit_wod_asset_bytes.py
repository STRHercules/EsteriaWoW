"""Exhaustively compare donor WoD character assets with Esteria's resolved live bytes."""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

TOOL_DIR = Path(__file__).resolve().parent
if str(TOOL_DIR) not in sys.path:
    sys.path.insert(0, str(TOOL_DIR))

from cars_mount_pack import DLL_DEFAULT, Storm  # noqa: E402
from mount_pack_batch2 import client_archive_chain  # noqa: E402

CLIENT = Path(r"G:\3.3.5a - Dev")
DONOR = Path(r"F:\Wrath of the Lich King 3.3.5a (wod models)")
DONOR_X = DONOR / "Data" / "patch-x.mpq"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    storm = Storm(DLL_DEFAULT)
    donor = storm.open_archive(DONOR_X)
    live_handles: list[tuple[Path, object]] = []
    try:
        names = [
            name
            for name, *_ in storm.list_files(donor)
            if name.casefold().startswith("character\\") or name.casefold().startswith("textures\\")
        ]
        for archive_path in client_archive_chain(CLIENT / "Data", "enUS"):
            try:
                live_handles.append((archive_path, storm.open_archive(archive_path)))
            except Exception:
                continue

        missing: list[str] = []
        different: list[tuple[str, str, int, int, str, str]] = []
        matched = 0
        by_ext: dict[str, list[int]] = {}

        for index, name in enumerate(names, 1):
            expected = storm.read(donor, name)
            actual = None
            source = None
            for archive_path, handle in live_handles:
                try:
                    actual = storm.read(handle, name)
                    source = str(archive_path)
                    break
                except OSError:
                    continue
            ext = Path(name).suffix.casefold() or "<none>"
            counts = by_ext.setdefault(ext, [0, 0, 0])
            if actual is None:
                missing.append(name)
                counts[1] += 1
            elif actual != expected:
                different.append((name, source or "", len(expected), len(actual), digest(expected), digest(actual)))
                counts[2] += 1
            else:
                matched += 1
                counts[0] += 1
            if index % 1000 == 0:
                print(f"audited {index}/{len(names)}")

        print(f"donor assets audited: {len(names)}")
        print(f"matched: {matched}")
        print(f"missing: {len(missing)}")
        print(f"different: {len(different)}")
        print("by extension (matched/missing/different):")
        for ext, counts in sorted(by_ext.items()):
            print(f"  {ext}: {counts[0]}/{counts[1]}/{counts[2]}")
        if missing:
            print("missing examples:")
            for name in missing[:100]:
                print(f"  {name}")
        if different:
            print("different examples:")
            for name, source, expected_size, actual_size, expected_hash, actual_hash in different[:100]:
                print(f"  {name}")
                print(f"    source={source}")
                print(f"    donor={expected_size} {expected_hash}")
                print(f"    live ={actual_size} {actual_hash}")
        return 1 if missing or different else 0
    finally:
        for _, handle in live_handles:
            storm.dll.SFileCloseArchive(handle)
        storm.dll.SFileCloseArchive(donor)


if __name__ == "__main__":
    raise SystemExit(main())
