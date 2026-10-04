"""Confirm Pandaren/Vulpera glue portrait assets resolve in the dev client."""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "tools"))

from cars_mount_pack import DLL_DEFAULT, Storm  # noqa: E402

CLIENT = REPO / "3.3.5a - Dev"
NEEDLES = ("pandaren", "vulpera")
ROOTS = (
    CLIENT / "Data" / "Patch-C.MPQ",
    CLIENT / "Data" / "PATCH-A.MPQ",
    CLIENT / "Data" / "PATCH-X.MPQ",
)


def main() -> None:
    storm = Storm(DLL_DEFAULT)
    for archive_path in ROOTS:
        handle = storm.open_archive(archive_path)
        try:
            hits = [
                name
                for name, *_ in storm.list_files(handle)
                if any(needle in name.casefold() for needle in NEEDLES)
            ]
        finally:
            storm.dll.SFileCloseArchive(handle)
        glue = [name for name in hits if name.casefold().startswith("interface\\glues")]
        print(f"{archive_path.name}: total={len(hits)} glue={len(glue)}")
        for name in sorted(glue)[:12]:
            print(f"    {name}")

    loose = CLIENT / "Data" / "patch-z.mpq"
    loose_hits = [
        path
        for path in loose.rglob("*")
        if path.is_file() and any(n in path.name.casefold() for n in NEEDLES)
    ]
    print(f"patch-z folder loose matches: {len(loose_hits)}")
    for path in loose_hits[:8]:
        print(f"    {path.relative_to(loose)}")


if __name__ == "__main__":
    main()
