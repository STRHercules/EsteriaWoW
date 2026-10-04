"""Compare start-outfit ItemDisplayInfo rows between Patch-C and the donor."""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "tools"))

from cars_mount_pack import DLL_DEFAULT, Storm  # noqa: E402
from playable_race_pack import RawWdbc  # noqa: E402

HERE = Path(__file__).resolve().parent
CLIENT = REPO / "3.3.5a - Dev"
DONOR_DBC = Path(
    r"G:\Ascension\Ascension\resources\ascension-live\Data\Extracted\DBFilesClient"
)
DONOR_ASSETS = Path(r"G:\Ascension\Ascension\resources\ascension-live\Data\Extracted\patch-CHA.mpq")
TARGET_RACES = {18, 20}


def cstring(pool: bytes, offset: int) -> str:
    if not offset:
        return ""
    end = pool.find(b"\x00", offset)
    return pool[offset:end].decode("ascii", "replace")


def archive_names(path: Path) -> set[str]:
    storm = Storm(DLL_DEFAULT)
    handle = storm.open_archive(path)
    try:
        return {name.casefold().replace("/", "\\") for name, *_ in storm.list_files(handle)}
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

    present = archive_names(CLIENT / "Data" / "Patch-C.MPQ")
    legacy = archive_names(CLIENT / "Data" / "PATCH-A.MPQ")
    donor_root = DONOR_ASSETS

    paths: dict[str, set[int]] = {}
    for display_id in sorted(display_ids):
        row = rows.get(display_id)
        if row is None:
            print(f"display {display_id}: no donor row")
            continue
        for field in (1, 2, *range(15, 23)):
            path = cstring(donor.strings, int.from_bytes(row[field * 4 : field * 4 + 4], "little"))
            if path:
                paths.setdefault(path.casefold().replace("/", "\\"), set()).add(display_id)

    print(f"donor display rows: {len(display_ids)}  distinct asset paths: {len(paths)}")
    in_patch_c = [p for p in paths if p in present]
    in_patch_a = [p for p in paths if p not in present and p in legacy]
    missing = [p for p in paths if p not in present and p not in legacy]
    local = [p for p in missing if (donor_root / p).is_file()]
    print(f"  in Patch-C: {len(in_patch_c)}")
    print(f"  only in PATCH-A: {len(in_patch_a)}")
    print(f"  missing from both archives: {len(missing)} (of which {len(local)} exist in donor extraction)")
    for path in sorted(missing)[:12]:
        print(f"    {path}  donor_extract={'yes' if (donor_root / path).is_file() else 'no'}")


if __name__ == "__main__":
    main()
