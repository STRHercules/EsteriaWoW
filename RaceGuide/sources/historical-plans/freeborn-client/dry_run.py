"""Dry-run the Freeborn GlueXML transforms against the real client archives.

Reads only the two GlueXML entries, applies both transforms, proves the anchor matched and
the XML stays well-formed, and writes the results for diff inspection. Changes nothing.
"""

from __future__ import annotations

import difflib
import sys
import xml.etree.ElementTree as ElementTree
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))

import freeborn_team_pack as pack  # noqa: E402
from cars_mount_pack import DLL_DEFAULT, Storm  # noqa: E402

CLIENT = Path(r"G:\3.3.5a - Dev")
OUT = Path(__file__).resolve().parent / "dryrun"

ARCHIVES = (
    CLIENT / "Data" / pack.ARCHIVE_NAME,
    CLIENT / "Data" / "enUS" / pack.LOCALE_ARCHIVE_NAME,
)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    storm = Storm(DLL_DEFAULT)
    for archive in ARCHIVES:
        print(f"=== {archive.name} ===")
        handle = storm.open_archive(archive)
        try:
            originals = {e: storm.read(handle, e) for e in pack.GLUE_FILES}
        finally:
            storm.dll.SFileCloseArchive(handle)

        for entry, original in originals.items():
            patched = pack.TRANSFORMS[entry](original)
            name = Path(entry).name
            assert patched != original, f"{archive.name}: {name} was not changed"
            (OUT / f"{archive.parent.name}.{name}.patched").write_bytes(patched)

            before = original.decode("utf-8").splitlines(keepends=True)
            after = patched.decode("utf-8").splitlines(keepends=True)
            added = sum(1 for line in difflib.ndiff(before, after) if line.startswith("+ "))
            removed = sum(1 for line in difflib.ndiff(before, after) if line.startswith("- "))
            print(f"  {name}: +{added} -{removed} lines")

            if name.endswith(".xml"):
                ElementTree.fromstring(patched.decode("utf-8"))
                print(f"  {name}: well-formed XML")

            assert pack.TRANSFORMS[entry](patched) == patched, "not idempotent"
            marker = pack.FREEBORN_BUTTON_NAME if name.endswith(".xml") else pack.LUA_MARKER
            assert marker in patched.decode("utf-8")

    print("\nwrote patched copies under", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
