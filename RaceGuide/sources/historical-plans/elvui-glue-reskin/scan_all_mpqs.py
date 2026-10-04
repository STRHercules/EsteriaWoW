"""Scan every MPQ in a client Data tree for GlueXML / login-related entries."""

from __future__ import annotations

import ctypes as c
import sys
from pathlib import Path

sys.path.insert(0, str(Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW\tools")))

from cars_mount_pack import Storm, FindData, DLL_DEFAULT  # noqa: E402


def list_safe(storm: Storm, archive) -> list[str]:
    data = FindData()
    finder = storm.dll.SFileFindFirstFile(archive, b"*", c.byref(data), None)
    if not finder:
        return []
    out: list[str] = []
    try:
        while True:
            out.append(data.cFileName.split(b"\0", 1)[0].decode("latin-1"))
            if not storm.dll.SFileFindNextFile(finder, c.byref(data)):
                break
    finally:
        storm.dll.SFileFindClose(finder)
    return out


WANT = ("gluexml", "accountlogin", "charactercreate", "characterselect", "glueparent",
        "gluestrings", "loginscreen", "models")


def main() -> int:
    data_root = Path(sys.argv[1])
    needle = sys.argv[2].casefold() if len(sys.argv) > 2 else None
    storm = Storm(DLL_DEFAULT)
    archives = sorted(
        [p for p in data_root.rglob("*") if p.is_file() and p.suffix.casefold() == ".mpq"],
        key=lambda p: str(p).casefold(),
    )
    for archive_path in archives:
        try:
            handle = storm.open_archive(archive_path)
        except OSError as exc:
            print(f"{archive_path.name}: OPEN FAILED {exc}")
            continue
        try:
            names = list_safe(storm, handle)
        finally:
            storm.dll.SFileCloseArchive(handle)
        if needle:
            hits = [n for n in names if needle in n.casefold()]
        else:
            hits = [n for n in names if any(w in n.casefold() for w in WANT)]
        if hits:
            rel = archive_path.relative_to(data_root)
            print(f"\n=== {rel}  (total={len(names)}, hits={len(hits)}) ===")
            for name in sorted(hits, key=str.casefold):
                print(f"    {name}")
        else:
            print(f"{archive_path.relative_to(data_root)}: no hits (total={len(names)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
