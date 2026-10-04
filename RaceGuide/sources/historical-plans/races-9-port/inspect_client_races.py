"""Read-only dump of the live client's race tables (ChrRaces, display/model, customisation).

Run with no arguments for the full report, or `--model <path>` to list the
geosets a model's level-0 .skin actually contains.
"""

from __future__ import annotations

import argparse
import ctypes
import struct
import sys
from pathlib import Path

REPO = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW")
sys.path.insert(0, str(REPO / "tools"))

from cars_mount_pack import DLL_DEFAULT, H, Storm, Wdbc  # noqa: E402

DATA = REPO / "3.3.5a - Dev/Data"
ORDER = [
    "common.MPQ",
    "common-2.MPQ",
    "expansion.MPQ",
    "lichking.MPQ",
    "patch.MPQ",
    "patch-2.MPQ",
    "patch-3.MPQ",
    "patch-4.mpq",
    "PATCH-A.MPQ",
    "Patch-B.MPQ",
    "Patch-C.MPQ",
    "Patch-D.MPQ",
    "Patch-E.MPQ",
    "Patch-F.MPQ",
    "Patch-G.MPQ",
    "Patch-O.mpq",
    "PATCH-X.MPQ",
    "Patch-Y.MPQ",
]
TABLES = [
    "DBFilesClient\\ChrRaces.dbc",
    "DBFilesClient\\CreatureDisplayInfo.dbc",
    "DBFilesClient\\CreatureDisplayInfoExtra.dbc",
    "DBFilesClient\\CreatureModelData.dbc",
    "DBFilesClient\\CharSections.dbc",
    "DBFilesClient\\CharHairGeosets.dbc",
    "DBFilesClient\\CharacterFacialHairStyles.dbc",
    "DBFilesClient\\CharStartOutfit.dbc",
    "DBFilesClient\\CharBaseInfo.dbc",
    "DBFilesClient\\CharVariations.dbc",
]
RACES = [1, 2, 4, 11, 15, 16, 17, 19, 20, 21, 22, 23, 28, 29, 30]
CHRRACES_FIELDS = {
    0: "ID",
    1: "Flags",
    2: "FactionID",
    4: "MaleDisplayId",
    5: "FemaleDisplayId",
    6: "ClientPrefix",
    7: "BaseLanguage",
    8: "CreatureType",
    9: "ResSicknessSpellID",
    10: "SplashSoundID",
    11: "ClientFilestring",
    12: "CinematicSequenceID",
    13: "Alliance",
}


class Client:
    READ_ONLY = 0x00000100

    def __init__(self) -> None:
        self.storm = Storm(DLL_DEFAULT)
        self.payloads: dict[str, bytes] = {}
        self.source: dict[str, str] = {}
        self.archives: dict[str, list[str]] = {}
        for name in ORDER:
            path = DATA / name
            if not path.exists():
                continue
            try:
                handle = self.open(name)
            except Exception:  # noqa: BLE001
                continue
            listing = [entry for entry, *_ in self.storm.list_files(handle)]
            lowered = {entry.casefold(): entry for entry in listing}
            self.archives[name] = listing
            for table in TABLES:
                entry = lowered.get(table.casefold())
                if entry is None:
                    continue
                try:
                    self.payloads[table] = self.storm.read(handle, entry)
                    self.source[table] = name
                except Exception:  # noqa: BLE001
                    continue
            self.storm.dll.SFileCloseArchive(handle)
        self.tables: dict[str, Wdbc] = {}
        self.raw: dict[str, "RawTable"] = {}
        self.listing = {entry.casefold(): entry for name in ORDER for entry in self.archives.get(name, [])}

    def table(self, name: str) -> Wdbc | None:
        if name not in self.tables and name in self.payloads:
            self.tables[name] = Wdbc(self.payloads[name])
        return self.tables.get(name)

    def raw_table(self, name: str) -> "RawTable | None":
        if name not in self.raw and name in self.payloads:
            self.raw[name] = RawTable(self.payloads[name])
        return self.raw.get(name)

    def open(self, name: str):
        """Read-only handle; the game locks its archives while it is running."""
        handle = H()
        if not self.storm.dll.SFileOpenArchive(str(DATA / name), 0, self.READ_ONLY, ctypes.byref(handle)):
            raise OSError(f"open {name} failed ({ctypes.get_last_error()})")
        return handle

    def find(self, path: str) -> bytes | None:
        entry = self.listing.get(path.casefold())
        if entry is None:
            return None
        for name in reversed(ORDER):
            if name not in self.archives:
                continue
            if any(item.casefold() == entry.casefold() for item in self.archives[name]):
                try:
                    handle = self.open(name)
                except Exception:  # noqa: BLE001
                    continue
                try:
                    return self.storm.read(handle, entry)
                finally:
                    self.storm.dll.SFileCloseArchive(handle)
        return None


def rows_for(table: Wdbc | None, index: int, value: int) -> list[list[int]]:
    if table is None:
        return []
    return [row for row in table.rows if row[index] == value]


class RawTable:
    """Tables with byte fields (CharStartOutfit, CharBaseInfo) keep raw records."""

    def __init__(self, data: bytes) -> None:
        magic, count, fields, record_size, string_size = struct.unpack_from("<4s4I", data)
        if magic != b"WDBC":
            raise ValueError("not a WDBC file")
        self.count = count
        self.fields = fields
        self.record_size = record_size
        start = 20 + count * record_size
        self.strings = data[start : start + string_size]
        self.records = [data[20 + i * record_size : 20 + (i + 1) * record_size] for i in range(count)]


def report(client: Client) -> None:
    for table, name in client.source.items():
        print(f"{table:<48} <- {name}")
    chrraces = client.table("DBFilesClient\\ChrRaces.dbc")
    displays = client.table("DBFilesClient\\CreatureDisplayInfo.dbc")
    models = client.table("DBFilesClient\\CreatureModelData.dbc")
    extras = client.table("DBFilesClient\\CreatureDisplayInfoExtra.dbc")
    geosets = client.table("DBFilesClient\\CharHairGeosets.dbc")
    sections = client.table("DBFilesClient\\CharSections.dbc")
    facial = client.table("DBFilesClient\\CharFacialHairStyles.dbc")
    outfits = client.raw_table("DBFilesClient\\CharStartOutfit.dbc")
    variations = client.table("DBFilesClient\\CharVariations.dbc")
    if chrraces is None or displays is None or models is None:
        raise SystemExit("client tables missing")
    print(f"fields: chrraces={chrraces.fields} display={displays.fields} model={models.fields}")
    if geosets:
        print(f"hair geoset fields={geosets.fields} sections fields={sections.fields if sections else '-'} "
              f"facial fields={facial.fields if facial else '-'} outfit record={outfits.record_size if outfits else '-'}")
    for race in RACES:
        row = next((r for r in chrraces.rows if r[0] == race), None)
        print()
        if row is None:
            print(f"race {race}: no ChrRaces row")
            continue
        info = {name: row[field] for field, name in CHRRACES_FIELDS.items() if field < len(row)}
        print(f"race {race}: {info}")
        for gender, display_id in (("male", row[4]), ("female", row[5])):
            display = next((r for r in displays.rows if r[0] == display_id), None)
            if display is None:
                print(f"   {gender} display {display_id}: MISSING")
                continue
            model = next((r for r in models.rows if r[0] == display[1]), None)
            path = models.text(model[2]) if model else "<no model row>"
            extra = ""
            if extras is not None and len(display) > 3 and display[3]:
                extra_row = next((r for r in extras.rows if r[0] == display[3]), None)
                extra = f" extra={display[3]}{'-ok' if extra_row else '-MISSING'}"
            print(f"   {gender} display {display_id}: model {display[1]} {path}{extra}")
            print(f"      display row {display}")
        for sex in (0, 1):
            race_geosets = sorted(
                (r[3], r[4], r[5]) for r in (geosets.rows if geosets else []) if r[1] == race and r[2] == sex
            )
            print(f"   hairGeosets sex={sex}: {len(race_geosets)} {race_geosets[:8]}")
        race_sections = sections.rows if sections else []
        mine = [r for r in race_sections if r[1] == race]
        kinds: dict[int, int] = {}
        for row in mine:
            kinds[row[3]] = kinds.get(row[3], 0) + 1
        print(f"   sections: {len(mine)} rows, by field3 {kinds}")
        if variations is not None:
            print(f"   variations: {len(rows_for(variations, 1, race))} rows")
        race_facial = rows_for(facial, 1, race) if facial else []
        print(f"   facialHairStyles: {len(race_facial)} rows {race_facial[:4]}")
        race_outfits = [row for row in (outfits.records if outfits else []) if row[4] == race]
        classes = sorted({row[5] for row in race_outfits})
        print(f"   outfits: record={outfits.record_size if outfits else '-'} rows={len(race_outfits)} classes={classes}")
        for row in race_outfits[:3]:
            print(f"      outfit id={int.from_bytes(row[0:4], 'little')} race={row[4]} class={row[5]} "
                  f"sex={row[6]} gear={row[8:20].hex()}")


def dump_model(client: Client, path: str) -> None:
    stem = path[:-4] if path.lower().endswith((".m2", ".mdx")) else path
    for suffix in (".m2", ".mdx"):
        payload = client.find(stem + suffix)
        if payload:
            print(f"{stem + suffix}: {len(payload)} bytes")
            break
    else:
        raise SystemExit(f"{path}: model not found in client archives")
    for index in range(4):
        skin = client.find(f"{stem}0{index}.skin")
        if not skin:
            continue
        vals = struct.unpack_from("<10I", skin, 4)
        n_sub, ofs_sub = vals[6], vals[7]
        entries = []
        for sub in range(n_sub):
            o = ofs_sub + sub * 48
            gid, level, v_start, v_count, i_start, i_count = struct.unpack_from("<6H", skin, o)
            entries.append((gid, i_count // 3))
        print(f"  {Path(stem).name}0{index}.skin: {n_sub} submeshes")
        print(f"    geosets: {entries}")
    for kind in (".anim", ".m2", ".mdx", ".skin"):
        found = [entry for entry in client.listing.values() if entry.casefold().startswith(stem.casefold())]
        if kind == ".anim" and found:
            print(f"  external anims: {len(found)}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", action="append", default=[])
    parser.add_argument("--race", type=int, action="append", default=[])
    args = parser.parse_args()
    if args.race:
        RACES[:] = args.race
    client = Client()
    if args.model:
        for path in args.model:
            dump_model(client, path)
        return
    report(client)


if __name__ == "__main__":
    main()
