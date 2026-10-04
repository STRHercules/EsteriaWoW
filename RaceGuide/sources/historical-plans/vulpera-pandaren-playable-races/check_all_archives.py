"""Resolve every start-outfit item asset for races 18/20 across all archives."""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "tools"))

from cars_mount_pack import DLL_DEFAULT, Storm  # noqa: E402
from playable_race_pack import RawWdbc, _start_outfit_display_ids  # noqa: E402

HERE = Path(__file__).resolve().parent
CLIENT = REPO / "3.3.5a - Dev"
ARCHIVES = (
    "Data/common.MPQ",
    "Data/common-2.MPQ",
    "Data/expansion.MPQ",
    "Data/lichking.MPQ",
    "Data/patch.MPQ",
    "Data/patch-2.MPQ",
    "Data/patch-3.MPQ",
    "Data/patch-4.mpq",
    "Data/PATCH-A.MPQ",
    "Data/PATCH-X.MPQ",
    "Data/Patch-C.MPQ",
    "Data/Patch-F.MPQ",
    "Data/Patch-O.mpq",
    "Data/enUS/locale-enUS.MPQ",
    "Data/enUS/patch-enUS-2.MPQ",
    "Data/enUS/patch-enUS-3.MPQ",
)


def cstring(pool: bytes, offset: int) -> str:
    if not offset:
        return ""
    end = pool.find(b"\x00", offset)
    return pool[offset:end].decode("ascii", "replace")


def main() -> None:
    outfits = RawWdbc((HERE / "client-dbc-final" / "CharStartOutfit.dbc").read_bytes())
    items = RawWdbc((HERE / "client-dbc-final" / "ItemDisplayInfo.dbc").read_bytes())
    rows = {int.from_bytes(r[:4], "little"): r for r in items.records}

    entries: dict[str, set[str]] = {}
    storm = Storm(DLL_DEFAULT)
    for relative in ARCHIVES:
        path = CLIENT / relative
        if not path.is_file():
            continue
        try:
            handle = storm.open_archive(path)
        except Exception as error:  # noqa: BLE001
            print(f"{relative}: unreadable ({error})")
            continue
        try:
            names = {
                name.casefold().replace("/", "\\") for name, *_ in storm.list_files(handle)
            }
        finally:
            storm.dll.SFileCloseArchive(handle)
        entries[relative] = names
        print(f"{relative}: {len(names)} entries")

    loose_roots = [CLIENT / "Data" / "patch-z.mpq", CLIENT / "Data" / "Patch-Housing.MPQ"]
    loose: set[str] = set()
    for root in loose_roots:
        if root.is_dir():
            for path in root.rglob("*"):
                if path.is_file():
                    loose.add(str(path.relative_to(root)).casefold().replace("/", "\\"))
    existing = loose | set().union(*entries.values())

    models: dict[str, set[int]] = {}
    textures: dict[str, set[int]] = {}
    for display_id in sorted(_start_outfit_display_ids(outfits.records)):
        row = rows.get(display_id)
        if row is None:
            continue
        for field in (1, 2):
            name = cstring(items.strings, int.from_bytes(row[field * 4 : field * 4 + 4], "little"))
            if name:
                models.setdefault(name.casefold(), set()).add(display_id)
        for field in range(15, 23):
            name = cstring(items.strings, int.from_bytes(row[field * 4 : field * 4 + 4], "little"))
            if name:
                textures.setdefault(name.casefold(), set()).add(display_id)

    def missing(names: dict[str, set[int]], suffixes: tuple[str, ...]) -> dict[str, set[int]]:
        result = {}
        for name, ids in names.items():
            stem = name.removesuffix(".mdx").removesuffix(".m2").removesuffix(".blp")
            if not any(
                entry.endswith(suffix) and stem in entry for entry in existing for suffix in suffixes
            ):
                result[name] = ids
        return result

    for label, names, suffixes in (
        ("models", models, (".m2", ".mdx")),
        ("textures", textures, (".blp",)),
    ):
        gaps = missing(names, suffixes)
        print(f"{label}: {len(names)} distinct, unresolved {len(gaps)}")
        for name, ids in sorted(gaps.items())[:15]:
            print(f"    {name}  (displays {sorted(ids)[:4]})")


if __name__ == "__main__":
    main()
