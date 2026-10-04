"""Find where start-outfit item models/textures live for races 18/20."""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "tools"))

from cars_mount_pack import DLL_DEFAULT, Storm  # noqa: E402
from playable_race_pack import RawWdbc  # noqa: E402

HERE = Path(__file__).resolve().parent
CLIENT = REPO / "3.3.5a - Dev"
DONOR_DBC = Path(r"G:\Ascension\Ascension\resources\ascension-live\Data\Extracted\DBFilesClient")
DONOR_ASSETS = Path(r"G:\Ascension\Ascension\resources\ascension-live\Data\Extracted\patch-CHA.mpq")
TARGET_RACES = {18, 20}


def cstring(pool: bytes, offset: int) -> str:
    if not offset:
        return ""
    end = pool.find(b"\x00", offset)
    return pool[offset:end].decode("ascii", "replace")


def archive_entries(path: Path) -> list[str]:
    storm = Storm(DLL_DEFAULT)
    handle = storm.open_archive(path)
    try:
        return [name.casefold().replace("/", "\\") for name, *_ in storm.list_files(handle)]
    finally:
        storm.dll.SFileCloseArchive(handle)


def main() -> None:
    outfits = RawWdbc((HERE / "client-dbc-fixed" / "CharStartOutfit.dbc").read_bytes())
    donor = RawWdbc((DONOR_DBC / "ItemDisplayInfo.dbc").read_bytes())
    rows = {int.from_bytes(r[:4], "little"): r for r in donor.records}

    display_ids: set[int] = set()
    for record in outfits.records:
        if record[4] not in TARGET_RACES:
            continue
        display_ids.update(
            int.from_bytes(record[o : o + 4], "little") for o in range(104, 200, 4)
        )
    display_ids.discard(0)
    display_ids.discard(0xFFFFFFFF)

    wanted: dict[str, set[str]] = {"model": set(), "texture": set()}
    for display_id in sorted(display_ids):
        row = rows.get(display_id)
        if row is None:
            continue
        for field in (1, 2):
            name = cstring(donor.strings, int.from_bytes(row[field * 4 : field * 4 + 4], "little"))
            if name:
                wanted["model"].add(name.casefold().removesuffix(".mdx").removesuffix(".m2"))
        for field in range(15, 23):
            name = cstring(donor.strings, int.from_bytes(row[field * 4 : field * 4 + 4], "little"))
            if name:
                wanted["texture"].add(name.casefold().removesuffix(".blp"))

    sources = {
        "Patch-C": archive_entries(CLIENT / "Data" / "Patch-C.MPQ"),
        "PATCH-A": archive_entries(CLIENT / "Data" / "PATCH-A.MPQ"),
        "PATCH-X": archive_entries(CLIENT / "Data" / "PATCH-X.MPQ"),
    }

    def has(entries: list[str], name: str, kind: str) -> bool:
        suffixes = (".m2", ".mdx") if kind == "model" else (".blp",)
        return any(e.rsplit("\\", 1)[-1].startswith(name) and e.endswith(suffixes) for e in entries)

    for kind, names in wanted.items():
        print(f"distinct {kind} names: {len(names)}")
        for label, entries in sources.items():
            missing = [n for n in names if not has(entries, n, kind)]
            print(f"  {label}: missing {len(missing)}/{len(names)}")
        if kind == "model":
            local = [
                n
                for n in names
                if not any(DONOR_ASSETS.rglob(f"{n}*"))
            ]
            print(f"  donor extraction: missing {len(local)}/{len(names)}")
            for name in sorted(local)[:10]:
                print(f"    {name}")


if __name__ == "__main__":
    main()
