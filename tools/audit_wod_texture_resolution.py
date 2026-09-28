"""Read-only audit that every donor stock-race CharSections texture resolves in Esteria."""

from __future__ import annotations

import sys
from pathlib import Path

TOOL_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOL_DIR))

from ascension_hd_migration import _read_string, _table, _u32
from cars_mount_pack import DLL_DEFAULT, Storm
from mount_pack_batch2 import client_archive_chain
from wod_model_migration import archive_names

STOCK_RACES = frozenset({1, 2, 3, 4, 5, 6, 7, 8, 10, 11})
CLIENT = Path(r"G:\3.3.5a - Dev")
DONOR = Path(r"F:\Wrath of the Lich King 3.3.5a (wod models)")


def try_read(storm: Storm, handle, path: str) -> bool:
    try:
        storm.read(handle, path)
        return True
    except OSError:
        return False


def main() -> int:
    storm = Storm(DLL_DEFAULT)
    x_locale = DONOR / "Data" / "enUS" / "patch-enUS-x.mpq"
    h = storm.open_archive(x_locale)
    try:
        names = archive_names(storm, h)
        sections = _table(storm.read(h, names[r"dbfilesclient\charsections.dbc"]), "CharSections")
    finally:
        storm.dll.SFileCloseArchive(h)

    referenced: set[str] = set()
    for row in sections.records:
        if _u32(row, 1) not in STOCK_RACES:
            continue
        for field in (4, 5, 6):
            offset = _u32(row, field)
            if offset:
                value = _read_string(sections.strings, offset).decode("utf-8")
                if value:
                    referenced.add(value.replace("/", "\\"))

    client_archives = client_archive_chain(CLIENT / "Data", "enUS")
    donor_archives = client_archive_chain(DONOR / "Data", "enUS")
    client_handles = [(path, storm.open_archive(path)) for path in client_archives]
    donor_handles = [(path, storm.open_archive(path)) for path in donor_archives]
    try:
        client_missing: list[str] = []
        donor_missing: list[str] = []
        donor_resolved_client_missing: list[tuple[str, str]] = []
        client_resolved = 0
        donor_resolved = 0
        for texture in sorted(referenced, key=str.casefold):
            client_source = next(
                (str(path) for path, handle in client_handles if try_read(storm, handle, texture)),
                None,
            )
            donor_source = next(
                (str(path) for path, handle in donor_handles if try_read(storm, handle, texture)),
                None,
            )
            if client_source is None:
                client_missing.append(texture)
            else:
                client_resolved += 1
            if donor_source is None:
                donor_missing.append(texture)
            else:
                donor_resolved += 1
            if client_source is None and donor_source is not None:
                donor_resolved_client_missing.append((texture, donor_source))
    finally:
        for _, handle in donor_handles:
            storm.dll.SFileCloseArchive(handle)
        for _, handle in client_handles:
            storm.dll.SFileCloseArchive(handle)

    print(
        f"referenced={len(referenced)} "
        f"client_resolved={client_resolved} client_missing={len(client_missing)} "
        f"donor_resolved={donor_resolved} donor_missing={len(donor_missing)} "
        f"must_import={len(donor_resolved_client_missing)}"
    )
    print("--- donor-resolved but missing in Esteria ---")
    for texture, source in donor_resolved_client_missing[:200]:
        print(f"{texture}\t{source}")
    print("--- missing even in donor ---")
    for texture in donor_missing[:100]:
        print(texture)
    return 1 if donor_resolved_client_missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
