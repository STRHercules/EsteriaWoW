"""Extract every Interface\\AddOns\\<prefix> file from an MPQ into a staging tree."""

from __future__ import annotations

import ctypes as c
import sys
from pathlib import Path

sys.path.insert(0, str(Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW\tools")))

from cars_mount_pack import Storm, FindData, DLL_DEFAULT  # noqa: E402


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
    out_root = Path(sys.argv[3])
    suffix = sys.argv[4] if len(sys.argv) > 4 else ""

    storm = Storm(DLL_DEFAULT)
    handle = storm.open_archive(archive_path)
    written = 0
    try:
        hits = [n for n, _ in list_files_safe(storm, handle) if needle in n.casefold()]
        for name in hits:
            if suffix and not name.casefold().endswith(suffix):
                continue
            rel = name.replace("\\", "/")
            # strip the leading Interface/AddOns/<prefix>/ to keep paths short
            parts = rel.split("/")
            target = out_root / Path(*parts[3:]) if len(parts) > 3 else out_root / parts[-1]
            try:
                payload = storm.read(handle, name.replace("/", "\\"))
            except OSError as exc:
                print(f"  skip {name}: {exc}")
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(payload)
            written += 1
    finally:
        storm.dll.SFileCloseArchive(handle)
    print(f"wrote {written} files to {out_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
