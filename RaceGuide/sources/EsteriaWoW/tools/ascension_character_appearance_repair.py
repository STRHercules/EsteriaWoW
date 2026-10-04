"""Audit/remap saved stock-race character appearance bytes for the live Ascension HD contract."""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

from ascension_hd_migration import _table, _u32
from cars_mount_pack import DLL_DEFAULT, Storm
from wod_character_appearance_repair import character_rows, changed_fields, mysql, repair_row
from wod_model_migration import archive_names

STOCK_RACES = frozenset({1, 2, 3, 4, 5, 6, 7, 8, 10, 11})


def load_table(storm: Storm, archive: Path, table: str) -> bytes:
    handle = storm.open_archive(archive)
    try:
        names = archive_names(storm, handle)
        return storm.read(handle, names[rf"dbfilesclient\{table.lower()}.dbc"])
    finally:
        storm.dll.SFileCloseArchive(handle)


def live_contract(client_root: Path, storm: Storm) -> dict[tuple[int, int], dict[str, object]]:
    archive = client_root / "Data" / "enUS" / "patch-enUS-Z.MPQ"
    sections = _table(load_table(storm, archive, "CharSections"), "CharSections")
    geosets = _table(load_table(storm, archive, "CharHairGeosets"), "CharHairGeosets")
    facial = _table(
        load_table(storm, archive, "CharacterFacialHairStyles"),
        "CharacterFacialHairStyles",
    )

    contract: dict[tuple[int, int], dict[str, object]] = {}
    for race in STOCK_RACES:
        for gender in (0, 1):
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
            textured_hair_styles = {style for style, _ in hair_pairs}
            if textured_hair_styles:
                hair_styles &= textured_hair_styles

            contract[(race, gender)] = {
                "skin_colors": skin_colors,
                "faces_by_skin": faces_by_skin,
                "hair_pairs": hair_pairs,
                "hair_styles": hair_styles,
                "facial_pairs": facial_pairs,
                "facial_styles": facial_styles,
            }
    return contract


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--client-root", type=Path, default=Path(r"G:\3.3.5a - Dev"))
    parser.add_argument("--stormlib", type=Path, default=DLL_DEFAULT)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    client = args.client_root.resolve()
    storm = Storm(args.stormlib)
    contract = live_contract(client, storm)
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
    backup_dir = client / "Backups" / f"ascension-character-appearance-{stamp}"
    backup_dir.mkdir(parents=True, exist_ok=False)
    (backup_dir / "characters-before.json").write_text(json.dumps(changes, indent=2) + "\n", encoding="utf-8")

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

    # Re-audit rather than trusting the UPDATE result alone.
    remaining = []
    for row in character_rows():
        fixed = repair_row(row, contract)
        if changed_fields(row, fixed):
            remaining.append(row)
    if remaining:
        raise ValueError(f"appearance remap verification failed for {len(remaining)} character(s)")

    report = dict(summary)
    report["backup_dir"] = str(backup_dir)
    (backup_dir / "repair.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
