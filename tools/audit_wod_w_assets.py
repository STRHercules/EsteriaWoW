"""Audit visible and directly-addressable WoD patch-w character assets against live Esteria."""

from __future__ import annotations

import hashlib
import sys
from collections import Counter
from pathlib import Path

TOOL_DIR = Path(__file__).resolve().parent
if str(TOOL_DIR) not in sys.path:
    sys.path.insert(0, str(TOOL_DIR))

from cars_mount_pack import DLL_DEFAULT, Storm  # noqa: E402
from mount_pack_batch2 import client_archive_chain  # noqa: E402

CLIENT = Path(r"G:\3.3.5a - Dev")
DONOR = Path(r"F:\Wrath of the Lich King 3.3.5a (wod models)")
DONOR_W = DONOR / "Data" / "patch-w.mpq"
DONOR_X = DONOR / "Data" / "patch-x.mpq"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    storm = Storm(DLL_DEFAULT)
    w = storm.open_archive(DONOR_W)
    x = storm.open_archive(DONOR_X)
    live_handles: list[tuple[Path, object]] = []
    try:
        visible = [
            name
            for name, *_ in storm.list_files(w)
            if name.casefold().startswith("character\\") or name.casefold().startswith("textures\\")
        ]
        print(f"visible W Character/Textures entries: {len(visible)}")
        print("visible W by extension:", Counter(Path(name).suffix.casefold() for name in visible))

        # Only W-only visible assets matter; X wins for duplicate names under the
        # normal W->X patch order.
        w_only: list[str] = []
        duplicates_in_x = 0
        for name in visible:
            try:
                storm.read(x, name)
                duplicates_in_x += 1
            except OSError:
                w_only.append(name)
        print(f"visible W entries also in X: {duplicates_in_x}")
        print(f"visible W-only entries: {len(w_only)}")

        for archive_path in client_archive_chain(CLIENT / "Data", "enUS"):
            try:
                live_handles.append((archive_path, storm.open_archive(archive_path)))
            except Exception:
                continue

        missing: list[str] = []
        different: list[tuple[str, str, str, str]] = []
        matched = 0
        for name in w_only:
            expected = storm.read(w, name)
            actual = None
            source = None
            for archive_path, handle in live_handles:
                try:
                    actual = storm.read(handle, name)
                    source = str(archive_path)
                    break
                except OSError:
                    continue
            if actual is None:
                missing.append(name)
            elif actual != expected:
                different.append((name, source or "", digest(expected), digest(actual)))
            else:
                matched += 1

        print(f"visible W-only matched: {matched}")
        print(f"visible W-only missing: {len(missing)}")
        print(f"visible W-only different: {len(different)}")
        if missing:
            print("missing examples:")
            for name in missing[:100]:
                print(f"  {name}")
        if different:
            print("different examples:")
            for name, source, expected_hash, actual_hash in different[:100]:
                print(f"  {name}")
                print(f"    source={source}")
                print(f"    donor={expected_hash}")
                print(f"    live ={actual_hash}")
        return 1 if missing or different else 0
    finally:
        for _, handle in live_handles:
            storm.dll.SFileCloseArchive(handle)
        storm.dll.SFileCloseArchive(x)
        storm.dll.SFileCloseArchive(w)


if __name__ == "__main__":
    raise SystemExit(main())
