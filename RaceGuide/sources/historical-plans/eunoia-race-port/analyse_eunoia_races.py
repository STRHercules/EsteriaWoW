"""Read-only inventory of the races shipped in G:\\Eunoia\\Client.

For every ChrRaces row: resolve the model paths, then check which of those
models, skins and CharSections textures actually exist in their archives.
"""

from __future__ import annotations

import collections
import json
import pathlib
import sys
from pathlib import Path

REPO = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW")
sys.path.insert(0, str(REPO / "tools"))
sys.path.insert(0, str(REPO / ".agents/plans/vulpera-pandaren-playable-races"))

from cars_mount_pack import Wdbc  # noqa: E402
from mpq_hash_probe import lookup, read_hash_map  # noqa: E402

EUNOIA_DBC = REPO / ".agents/plans/vulpera-pandaren-playable-races/eunoia-dbc"
EUNOIA_DATA = Path(r"G:\Eunoia\Client\data")
OUT = REPO / ".agents/plans/eunoia-race-port"

REQUESTED = [
    "Kul Tiran", "Eredar", "Lightforged Draenei", "Nightborne", "Void Elf",
    "Dark Iron Dwarf", "Zandalari Troll", "Dracthyr", "Illidari",
]

UPRIGHT_PROBES = [
    "character\\orc\\male\\orcmale.m2",
    "character\\orc\\male\\orcmaleupright.m2",
    "character\\orc\\male\\orcupright.m2",
    "character\\orcmale\\orcmale.m2",
    "character\\orcupright\\orcmale.m2",
    "character\\orcupright\\orcfemale.m2",
    "character\\uprightorc\\orcmale.m2",
    "character\\orc\\male\\orcmale_hd.m2",
    "character\\orc\\male\\orcmalehd.m2",
    "character\\orc\\female\\orcfemale.m2",
]


def dbc(name: str) -> Wdbc:
    return Wdbc((EUNOIA_DBC / f"{name}.dbc").read_bytes())


class SimpleDbc:
    """Reader for tables whose fields are smaller than four bytes (CharBaseInfo uses bytes)."""

    def __init__(self, data: bytes) -> None:
        magic, count, fields, record_size, string_size = __import__("struct").unpack_from("<4s4I", data, 0)
        if magic != b"WDBC":
            raise ValueError("not a WDBC")
        width = record_size // fields
        code = {1: "B", 2: "H", 4: "I"}[width]
        self.rows = [
            __import__("struct").unpack_from(f"<{fields}{code}", data, 20 + index * record_size)
            for index in range(count)
        ]


def main() -> None:
    races = dbc("ChrRaces")
    display = dbc("CreatureDisplayInfo")
    models = dbc("CreatureModelData")
    sections = dbc("CharSections")
    hair_geosets = dbc("CharHairGeosets")
    hair_tex = dbc("CharHairTextures")
    facial = dbc("CharacterFacialHairStyles")
    base_info = SimpleDbc((EUNOIA_DBC / "CharBaseInfo.dbc").read_bytes())

    model_by_display = {row[0]: row[1] for row in display.rows}
    path_by_model = {row[0]: models.text(row[2]) for row in models.rows}

    race_rows = []
    for row in races.rows:
        race_id = row[0]
        if race_id == 0 or race_id > 60:
            continue
        race_rows.append(
            {
                "id": race_id,
                "flags": row[1],
                "faction": row[2],
                "male_display": row[4],
                "female_display": row[5],
                "prefix": races.text(row[6]),
                "client_file": races.text(row[13]),
                "name": races.text(row[16]),
                "male_model": path_by_model.get(model_by_display.get(row[4], -1), ""),
                "female_model": path_by_model.get(model_by_display.get(row[5], -1), ""),
            }
        )

    section_textures: dict[int, set[str]] = collections.defaultdict(set)
    section_rows = collections.Counter()
    section_shapes = collections.defaultdict(set)
    for row in sections.rows:
        race_id = row[1]
        section_rows[race_id] += 1
        section_shapes[race_id].add((row[2], row[3]))
        for field in (4, 5, 6):
            text = sections.text(row[field])
            if text:
                section_textures[race_id].add(text)

    geoset_rows = collections.Counter(row[1] for row in hair_geosets.rows)
    hair_texture_rows = collections.Counter(row[1] for row in hair_tex.rows)
    facial_rows = collections.Counter(row[1] for row in facial.rows)
    class_rows: dict[int, set[int]] = collections.defaultdict(set)
    for row in base_info.rows:
        class_rows[row[0]].add(row[1])

    probes: set[str] = set(UPRIGHT_PROBES)
    for info in race_rows:
        for path in (info["male_model"], info["female_model"]):
            if not path:
                continue
            stem = path.lower().replace(".mdx", ".m2")
            probes.add(stem)
            for index in range(4):
                probes.add(f"{stem[:-3]}0{index}.skin")
        probes |= section_textures[info["id"]]

    # resolve the extension-less names as well
    probes = {name.lower().replace("/", "\\") for name in probes}

    present: dict[str, list[str]] = {}
    archives = sorted(EUNOIA_DATA.glob("*.mpq"), key=lambda p: p.name.casefold())
    for archive in archives:
        try:
            table, _info = read_hash_map(archive)
        except Exception as error:  # noqa: BLE001
            print(f"skip {archive.name}: {error}")
            continue
        for name in probes:
            if lookup(table, name) is not None:
                present.setdefault(name, []).append(archive.name)
        print(f"scanned {archive.name}: {len(present)} names resolved so far", flush=True)

    report = []
    for info in race_rows:
        race_id = info["id"]
        models_found = {}
        skins_found = 0
        skins_expected = 0
        for gender, path in (("male", info["male_model"]), ("female", info["female_model"])):
            if not path:
                models_found[gender] = None
                continue
            stem = path.lower().replace(".mdx", ".m2")
            models_found[gender] = bool(present.get(stem))
            for index in range(4):
                skins_expected += 1
                if present.get(f"{stem[:-3]}0{index}.skin"):
                    skins_found += 1
        textures = section_textures[race_id]
        textures_found = sum(1 for name in textures if present.get(name.lower().replace("/", "\\")))
        report.append(
            {
                **info,
                "models_present": models_found,
                "skins": f"{skins_found}/{skins_expected}",
                "textures": f"{textures_found}/{len(textures)}",
                "sections_rows": section_rows[race_id],
                "sections_shapes": sorted(section_shapes[race_id]),
                "hair_geosets": geoset_rows.get(race_id, 0),
                "hair_textures": hair_texture_rows.get(race_id, 0),
                "facial_styles": facial_rows.get(race_id, 0),
                "classes": sorted(class_rows.get(race_id, [])),
                "archive_male": present.get(info["male_model"].lower().replace(".mdx", ".m2"), []),
            }
        )

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "eunoia-race-inventory.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    print("\n=== requested races ===")
    for entry in report:
        if entry["name"] not in REQUESTED and entry["name"] != "Illidari Blood Elf":
            continue
        print(
            f"{entry['id']:>3} {entry['name']:<20} model m/f={entry['models_present']['male']}/"
            f"{entry['models_present']['female']} skins={entry['skins']} textures={entry['textures']} "
            f"sections={entry['sections_rows']} hair={entry['hair_geosets']} classes={len(entry['classes'])}"
        )
        print(f"      male   {entry['male_model']}")
        print(f"      female {entry['female_model']}")

    print("\n=== every race with model+skin+texture coverage ===")
    for entry in sorted(report, key=lambda item: item["id"]):
        if not entry["male_model"] and not entry["female_model"]:
            continue
        print(
            f"{entry['id']:>3} {entry['name'][:22]:<22} m/f={int(bool(entry['models_present']['male']))}/"
            f"{int(bool(entry['models_present']['female']))} skins={entry['skins']:<3} "
            f"tex={entry['textures']:<12} cls={len(entry['classes'])}"
        )

    print("\n=== upright orc probes ===")
    for name in UPRIGHT_PROBES:
        print(f"   {'HIT ' if present.get(name) else 'miss'} {name} {present.get(name, '')}")


if __name__ == "__main__":
    main()
