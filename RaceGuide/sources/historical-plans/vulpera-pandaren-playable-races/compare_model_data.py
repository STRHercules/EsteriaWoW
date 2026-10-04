"""Compare CreatureModelData rows: custom donor vs packaged vs working races."""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "tools"))

from cars_mount_pack import DLL_DEFAULT, Storm  # noqa: E402
from playable_race_pack import RawWdbc  # noqa: E402

DONOR_DBC = Path(r"G:\Ascension\Ascension\resources\ascension-live\Data\Extracted\DBFilesClient")
LIVE = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW\3.3.5a - Dev\Data\Patch-C.MPQ")
IDS = (49, 4896, 4898, 112885, 112929)


def load(path: Path) -> RawWdbc:
    return RawWdbc(path.read_bytes())


def main() -> None:
    donor = load(DONOR_DBC / "CreatureModelData.dbc")
    storm = Storm(DLL_DEFAULT)
    handle = storm.open_archive(LIVE)
    try:
        names = {name.casefold(): name for name, *_ in storm.list_files(handle)}
        packed = RawWdbc(storm.read(handle, names["dbfilesclient\\creaturemodeldata.dbc"]))
    finally:
        storm.dll.SFileCloseArchive(handle)
    donor_rows = {int.from_bytes(r[:4], "little"): r for r in donor.records}
    packed_rows = {int.from_bytes(r[:4], "little"): r for r in packed.records}

    for model_id in IDS:
        for label, rows, table in (
            ("donor", donor_rows, donor),
            ("Patch-C", packed_rows, packed),
        ):
            row = rows.get(model_id)
            if row is None:
                print(f"{model_id} {label}: absent")
                continue
            fields = [int.from_bytes(row[i * 4 : i * 4 + 4], "little") for i in range(28)]
            offset = fields[2]
            end = table.strings.find(b"\x00", offset) if offset else 0
            path = table.strings[offset:end].decode("ascii", "replace") if offset else ""
            print(f"{model_id} {label}: flags={fields[1]} path={path!r}")
            print(f"      fields={fields}")


if __name__ == "__main__":
    main()
