"""Audit/remap saved stock-race character appearance bytes for the WoD donor contract.

Only stock races are considered. Values already supported by the donor remain
unchanged. Unsupported values are mapped to the numerically nearest valid donor
choice for that race/sex. Apply mode snapshots every changed row and writes a
restore SQL file before updating the live characters database.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

TOOL_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOL_DIR))

from ascension_hd_migration import _table, _u32
from cars_mount_pack import DLL_DEFAULT, Storm
from wod_model_migration import archive_names

STOCK_RACES = frozenset({1, 2, 3, 4, 5, 6, 7, 8, 10, 11})


def nearest(value: int, choices: set[int]) -> int:
    if not choices:
        return 0
    return min(choices, key=lambda candidate: (abs(candidate - value), candidate))


def load_entry(storm: Storm, archive: Path, table: str, layout: str) -> bytes:
    handle = storm.open_archive(archive)
    try:
        names = archive_names(storm, handle)
        return storm.read(handle, names[rf"dbfilesclient\{table.lower()}.dbc"])
    finally:
        storm.dll.SFileCloseArchive(handle)


def donor_contract(donor_root: Path, storm: Storm) -> dict[tuple[int, int], dict[str, object]]:
    x_locale = donor_root / "Data" / "enUS" / "patch-enUS-x.mpq"
    base_locale = donor_root / "Data" / "enUS" / "patch-enUS.MPQ"

    sections = _table(load_entry(storm, x_locale, "CharSections", "CharSections"), "CharSections")
    geosets = _table(load_entry(storm, base_locale, "CharHairGeosets", "CharHairGeosets"), "CharHairGeosets")
    facial = _table(
        load_entry(storm, base_locale, "CharacterFacialHairStyles", "CharacterFacialHairStyles"),
        "CharacterFacialHairStyles",
    )

    contract: dict[tuple[int, int], dict[str, object]] = {}
    for race in STOCK_RACES:
        for gender in (0, 1):
            key = (race, gender)
            skin_colors: set[int] = set()
            faces_by_skin: dict[int, set[int]] = {}
            hair_pairs: set[tuple[int, int]] = set()
            facial_pairs: set[tuple[int, int]] = set()

            for row in sections.records:
                if _u32(row, 1) != race or _u32(row, 2) != gender:
                    continue
                section_type = _u32(row, 3)
                variation = _u32(row, 8)
                color = _u32(row, 9)
                if section_type == 0:
                    skin_colors.add(color)
                elif section_type == 1:
                    faces_by_skin.setdefault(color, set()).add(variation)
                elif section_type == 2:
                    facial_pairs.add((variation, color))
                elif section_type == 3:
                    hair_pairs.add((variation, color))

            hair_styles = {
                _u32(row, 3)
                for row in geosets.records
                if _u32(row, 1) == race and _u32(row, 2) == gender
            }
            facial_styles = {
                _u32(row, 2)
                for row in facial.records
                if _u32(row, 0) == race and _u32(row, 1) == gender
            }

            # Only expose hairstyle/type values that also have a texture pair.
            textured_hair_styles = {style for style, _ in hair_pairs}
            if textured_hair_styles:
                hair_styles &= textured_hair_styles

            contract[key] = {
                "skin_colors": skin_colors,
                "faces_by_skin": faces_by_skin,
                "hair_pairs": hair_pairs,
                "hair_styles": hair_styles,
                "facial_pairs": facial_pairs,
                "facial_styles": facial_styles,
            }
    return contract


def mysql(args: list[str], *, input_text: str | None = None) -> str:
    command = [
        "docker",
        "exec",
        "-i",
        "ac-database",
        "mysql",
        "-uroot",
        "-ppassword",
        "-N",
        "-B",
        *args,
    ]
    result = subprocess.run(
        command,
        input=input_text,
        text=True,
        capture_output=True,
        check=True,
    )
    return result.stdout


def character_rows() -> list[dict[str, int | str]]:
    query = (
        "SELECT guid,name,race,class,gender,skin,face,hairStyle,hairColor,facialStyle,online "
        "FROM acore_characters.characters "
        "WHERE race IN (1,2,3,4,5,6,7,8,10,11) ORDER BY guid;"
    )
    output = mysql(["-e", query])
    rows: list[dict[str, int | str]] = []
    for line in output.splitlines():
        if not line.strip():
            continue
        values = line.split("\t")
        rows.append(
            {
                "guid": int(values[0]),
                "name": values[1],
                "race": int(values[2]),
                "class": int(values[3]),
                "gender": int(values[4]),
                "skin": int(values[5]),
                "face": int(values[6]),
                "hairStyle": int(values[7]),
                "hairColor": int(values[8]),
                "facialStyle": int(values[9]),
                "online": int(values[10]),
            }
        )
    return rows


def repair_row(row: dict[str, int | str], contract: dict[tuple[int, int], dict[str, object]]) -> dict[str, int | str]:
    fixed = dict(row)
    key = (int(row["race"]), int(row["gender"]))
    rules = contract[key]

    skin_colors = set(rules["skin_colors"])
    skin = int(row["skin"])
    if skin not in skin_colors:
        skin = nearest(skin, skin_colors)
    fixed["skin"] = skin

    faces_by_skin = dict(rules["faces_by_skin"])
    face_choices = set(faces_by_skin.get(skin, set()))
    if not face_choices:
        face_choices = {face for choices in faces_by_skin.values() for face in choices}
    face = int(row["face"])
    if face not in face_choices:
        face = nearest(face, face_choices)
    fixed["face"] = face

    hair_styles = set(rules["hair_styles"])
    hair_pairs = set(rules["hair_pairs"])
    hair_style = int(row["hairStyle"])
    hair_color = int(row["hairColor"])
    if hair_style not in hair_styles:
        hair_style = nearest(hair_style, hair_styles)
    colors_for_style = {color for style, color in hair_pairs if style == hair_style}
    if colors_for_style and hair_color not in colors_for_style:
        hair_color = nearest(hair_color, colors_for_style)
    fixed["hairStyle"] = hair_style
    fixed["hairColor"] = hair_color

    facial_styles = set(rules["facial_styles"])
    facial_style = int(row["facialStyle"])
    if facial_styles:
        if facial_style not in facial_styles:
            facial_style = nearest(facial_style, facial_styles)
    else:
        facial_style = 0
    fixed["facialStyle"] = facial_style
    return fixed


def changed_fields(before: dict[str, int | str], after: dict[str, int | str]) -> list[str]:
    fields = ("skin", "face", "hairStyle", "hairColor", "facialStyle")
    return [field for field in fields if before[field] != after[field]]


def main() -> int:
    parser = argparse.ArgumentParser(description="Repair saved stock-race appearances for the WoD model contract")
    parser.add_argument(
        "--donor-root",
        type=Path,
        default=Path(r"F:\Wrath of the Lich King 3.3.5a (wod models)"),
    )
    parser.add_argument("--client-root", type=Path, default=Path(r"G:\3.3.5a - Dev"))
    parser.add_argument("--stormlib", type=Path, default=DLL_DEFAULT)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    storm = Storm(args.stormlib)
    contract = donor_contract(args.donor_root.resolve(), storm)
    before_rows = character_rows()
    changes: list[dict[str, object]] = []
    for before in before_rows:
        after = repair_row(before, contract)
        fields = changed_fields(before, after)
        if fields:
            changes.append({"before": before, "after": after, "fields": fields})

    field_counts: dict[str, int] = {}
    for change in changes:
        for field in change["fields"]:
            field_counts[field] = field_counts.get(field, 0) + 1

    summary = {
        "apply": args.apply,
        "stock_characters": len(before_rows),
        "characters_needing_remap": len(changes),
        "field_changes": field_counts,
        "online_affected": sum(1 for change in changes if int(change["before"]["online"]) != 0),
    }
    print(json.dumps(summary, indent=2))
    for change in changes[:40]:
        before = change["before"]
        after = change["after"]
        print(
            f"{before['guid']} {before['name']} race={before['race']} gender={before['gender']} "
            f"fields={','.join(change['fields'])} "
            f"before=({before['skin']},{before['face']},{before['hairStyle']},{before['hairColor']},{before['facialStyle']}) "
            f"after=({after['skin']},{after['face']},{after['hairStyle']},{after['hairColor']},{after['facialStyle']})"
        )

    if not args.apply or not changes:
        return 0
    if summary["online_affected"]:
        raise RuntimeError("refusing to update appearance rows while an affected character is online")

    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_dir = args.client_root.resolve() / "Backups" / f"wod-character-appearance-{stamp}"
    backup_dir.mkdir(parents=True, exist_ok=False)
    snapshot = backup_dir / "characters-before.json"
    snapshot.write_text(json.dumps(changes, indent=2) + "\n", encoding="utf-8")

    restore_lines = ["START TRANSACTION;"]
    update_lines = ["START TRANSACTION;"]
    for change in changes:
        before = change["before"]
        after = change["after"]
        restore_lines.append(
            "UPDATE acore_characters.characters SET "
            f"skin={before['skin']},face={before['face']},hairStyle={before['hairStyle']},"
            f"hairColor={before['hairColor']},facialStyle={before['facialStyle']} "
            f"WHERE guid={before['guid']};"
        )
        update_lines.append(
            "UPDATE acore_characters.characters SET "
            f"skin={after['skin']},face={after['face']},hairStyle={after['hairStyle']},"
            f"hairColor={after['hairColor']},facialStyle={after['facialStyle']} "
            f"WHERE guid={after['guid']};"
        )
    restore_lines.append("COMMIT;")
    update_lines.append("COMMIT;")
    (backup_dir / "restore.sql").write_text("\n".join(restore_lines) + "\n", encoding="utf-8")

    mysql(["acore_characters"], input_text="\n".join(update_lines) + "\n")

    after_rows = {int(row["guid"]): row for row in character_rows()}
    for change in changes:
        expected = change["after"]
        actual = after_rows[int(expected["guid"])]
        for field in ("skin", "face", "hairStyle", "hairColor", "facialStyle"):
            if actual[field] != expected[field]:
                raise ValueError(
                    f"database verification failed guid={expected['guid']} field={field}: "
                    f"expected={expected[field]} actual={actual[field]}"
                )

    report = dict(summary)
    report["backup_dir"] = str(backup_dir)
    (backup_dir / "repair.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
