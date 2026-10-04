"""Case-insensitive substring search over MPQ entry names, tolerant of non-ASCII names."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW\tools")))

import ctypes as c  # noqa: E402
from cars_mount_pack import Storm, FindData, DLL_DEFAULT, H, U  # noqa: E402


def list_files_safe(storm: Storm, archive) -> list[tuple[str, int]]:
    data = FindData()
    finder = storm.dll.SFileFindFirstFile(archive, b"*", c.byref(data), None)
    if not finder:
        raise OSError(f"SFileFindFirstFile failed ({c.get_last_error()})")
    out: list[tuple[str, int]] = []
    try:
        while True:
            raw = data.cFileName.split(b"\0", 1)[0]
            out.append((raw.decode("latin-1"), data.dwFileSize))
            if not storm.dll.SFileFindNextFile(finder, c.byref(data)):
                break
    finally:
        storm.dll.SFileFindClose(finder)
    return out


def main() -> int:
    archive_path = Path(sys.argv[1])
    needle = sys.argv[2].casefold()
    storm = Storm(DLL_DEFAULT)
    handle = storm.open_archive(archive_path)
    try:
        entries = list_files_safe(storm, handle)
        hits = [e for e in entries if needle in e[0].casefold()]
        print(f"{archive_path.name}: total={len(entries)} hits={len(hits)}")
        tops: dict[str, int] = {}
        for name, size in hits:
            parts = name.replace("/", "\\").split("\\")
            key = "\\".join(parts[:3])
            tops[key] = tops.get(key, 0) + 1
        for key in sorted(tops, key=str.casefold):
            print(f"  {key}  ({tops[key]} files)")
        print("  --- first 25 names ---")
        for name, size in sorted(hits, key=lambda e: e[0].casefold())[:25]:
            print(f"    {name}  ({size})")
    finally:
        storm.dll.SFileCloseArchive(handle)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
