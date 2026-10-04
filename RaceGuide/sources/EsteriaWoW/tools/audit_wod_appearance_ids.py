"""Audit stock-race appearance row IDs against the working WoD donor."""

from __future__ import annotations

import sys
from pathlib import Path

TOOL_DIR = Path(__file__).resolve().parent
if str(TOOL_DIR) not in sys.path:
    sys.path.insert(0, str(TOOL_DIR))

from ascension_hd_migration import _read_string, _table, _u32  # noqa: E402
from cars_mount_pack import DLL_DEFAULT, Storm  # noqa: E402

CLIENT = Path(r"G:\3.3.5a - Dev")
DONOR = Path(r"F:\Wrath of the Lich King 3.3.5a (wod models)")
STOCK_RACES = frozenset({1, 2, 3, 4, 5, 6, 7, 8, 10, 11})


def read_entry(storm: Storm, archive_path: Path, entry: str) -> bytes:
    handle = storm.open_archive(archive_path)
    try:
        return storm.read(handle, entry)
    finally:
        storm.dll.SFileCloseArchive(handle)


def char_hair_rows(data: bytes) -> dict[tuple[int, ...], int]:
    table = _table(data, "CharHairGeosets")
    result: dict[tuple[int, ...], int] = {}
    for row in table.records:
        if _u32(row, 1) not in STOCK_RACES:
            continue
        payload = tuple(_u32(row, field) for field in range(1, table.fields))
        result[payload] = _u32(row, 0)
    return result


def barber_rows(data: bytes) -> dict[tuple[object, ...], int]:
    table = _table(data, "BarberShopStyle")
    string_fields = set(tuple(range(2, 18)) + tuple(range(19, 35)))
    result: dict[tuple[object, ...], int] = {}
    for row in table.records:
        if _u32(row, 37) not in STOCK_RACES:
            continue
        payload: list[object] = []
        for field in range(1, table.fields):
            value = _u32(row, field)
            if field in string_fields:
                payload.append(_read_string(table.strings, value))
            else:
                payload.append(value)
        result[tuple(payload)] = _u32(row, 0)
    return result


def report(name: str, live: dict[tuple[object, ...], int], donor: dict[tuple[object, ...], int]) -> None:
    keys = set(live) | set(donor)
    missing = sorted((key for key in keys if key not in live), key=repr)
    extra = sorted((key for key in keys if key not in donor), key=repr)
    drift = sorted(
        ((donor[key], live[key], key) for key in keys if key in live and key in donor and live[key] != donor[key]),
        key=lambda item: (item[0], item[1]),
    )
    print(f"{name}: donor={len(donor)} live={len(live)} missing={len(missing)} extra={len(extra)} id_drift={len(drift)}")
    for donor_id, live_id, key in drift[:40]:
        print(f"  donor_id={donor_id} live_id={live_id} row={key}")


def main() -> int:
    storm = Storm(DLL_DEFAULT)
    live_archive = CLIENT / "Data" / "enUS" / "patch-enUS-Z.MPQ"
    live_hair = read_entry(storm, live_archive, r"DBFilesClient\CharHairGeosets.dbc")
    live_barber = read_entry(storm, live_archive, r"DBFilesClient\BarberShopStyle.dbc")

    donor_hair = read_entry(
        storm,
        DONOR / "Data" / "enUS" / "patch-enUS.MPQ",
        r"DBFilesClient\CharHairGeosets.dbc",
    )
    donor_barber = read_entry(
        storm,
        DONOR / "Data" / "enUS" / "patch-enUS-3.MPQ",
        r"DBFilesClient\BarberShopStyle.dbc",
    )

    report("CharHairGeosets", char_hair_rows(live_hair), char_hair_rows(donor_hair))
    report("BarberShopStyle", barber_rows(live_barber), barber_rows(donor_barber))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
