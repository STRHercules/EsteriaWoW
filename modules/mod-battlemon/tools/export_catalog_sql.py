# -*- coding: utf-8 -*-
"""Generate AzerothCore world SQL INSERTs from Battlemon addon CSVs."""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

ADDON_CSV = Path(
    r"D:\new-client\vanilla test\3.3.5a - Chromie (Reforged)\Interface\AddOns\Battlemon\Data\csv")
OUT = Path(__file__).resolve().parents[1] / "data" / "sql" / "db-world" / "base"
CHUNK = 80

TABLES = [
    (
        "types.csv",
        "battlemon_types",
        [
            "id",
            "internal_name",
            "name",
            "icon_position",
            "is_pseudo",
            "is_special",
            "weaknesses",
            "resistances",
            "immunities",
        ],
        {"icon_position", "weaknesses", "resistances", "immunities"},
    ),
    (
        "type_chart.csv",
        "battlemon_type_chart",
        ["id", "attacker", "defender", "multiplier"],
        set(),
    ),
    (
        "abilities.csv",
        "battlemon_abilities",
        ["id", "internal_name", "name", "description"],
        {"description"},
    ),
    (
        "moves.csv",
        "battlemon_moves",
        [
            "id",
            "internal_name",
            "name",
            "type",
            "move_category",
            "power",
            "accuracy",
            "pp",
            "target",
            "function_code",
            "flags",
            "priority",
            "effect_chance",
            "description",
        ],
        {"power", "accuracy", "pp", "target", "function_code", "flags", "description"},
    ),
    (
        "items.csv",
        "battlemon_items",
        [
            "id",
            "internal_name",
            "name",
            "name_plural",
            "pocket",
            "price",
            "field_use",
            "battle_use",
            "flags",
            "heal_amount",
            "description",
        ],
        {
            "name_plural",
            "pocket",
            "price",
            "field_use",
            "battle_use",
            "flags",
            "heal_amount",
            "description",
        },
    ),
    (
        "species.csv",
        "battlemon_species",
        [
            "id",
            "internal_name",
            "name",
            "type1",
            "type2",
            "hp",
            "atk",
            "def",
            "spa",
            "spd",
            "spe",
            "gender_ratio",
            "growth_rate",
            "base_exp",
            "catch_rate",
            "happiness",
            "ability1",
            "ability2",
            "hidden_ability",
            "egg_groups",
            "hatch_steps",
            "height",
            "weight",
            "color",
            "shape",
            "habitat",
            "category",
            "pokedex",
            "generation",
            "evolutions",
            "sprite",
        ],
        {
            "type2",
            "gender_ratio",
            "growth_rate",
            "catch_rate",
            "happiness",
            "ability1",
            "ability2",
            "hidden_ability",
            "egg_groups",
            "hatch_steps",
            "height",
            "weight",
            "color",
            "shape",
            "habitat",
            "category",
            "pokedex",
            "generation",
            "evolutions",
            "sprite",
        },
    ),
    (
        "forms.csv",
        "battlemon_forms",
        ["id", "species_id", "sprite", "variant", "name", "back_sprite"],
        {"variant", "back_sprite"},
    ),
    (
        "species_moves.csv",
        "battlemon_species_moves",
        ["id", "species_id", "level", "move_internal_name"],
        set(),
    ),
    (
        "species_tutor_moves.csv",
        "battlemon_species_tutor_moves",
        ["id", "species_id", "move_internal_name"],
        set(),
    ),
    (
        "form_moves.csv",
        "battlemon_form_moves",
        ["id", "form_id", "method", "level", "move_internal_name"],
        set(),
    ),
]

NUMERIC = {
    "id",
    "species_id",
    "form_id",
    "icon_position",
    "is_pseudo",
    "is_special",
    "multiplier",
    "power",
    "accuracy",
    "pp",
    "priority",
    "effect_chance",
    "pocket",
    "price",
    "hp",
    "atk",
    "def",
    "spa",
    "spd",
    "spe",
    "base_exp",
    "catch_rate",
    "happiness",
    "hatch_steps",
    "height",
    "weight",
    "level",
}


def sql_str(value: str) -> str:
    return "'" + value.replace("\\", "\\\\").replace("'", "''") + "'"


def sql_val(col: str, raw: str | None, nullable: set[str]) -> str:
    value = "" if raw is None else str(raw).strip()
    if value == "":
        if col in nullable:
            return "NULL"
        return "0" if col in NUMERIC else "''"
    if col in NUMERIC:
        return value
    return sql_str(value)


def load_rows(csv_name: str, columns: list[str]) -> list[dict[str, str]]:
    path = ADDON_CSV / csv_name
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = []
        for row in reader:
            rows.append({c: row.get(c, "") or "" for c in columns})
        return rows


def write_inserts(table: str, columns: list[str], nullable: set[str], rows: list[dict[str, str]], fh) -> None:
    col_sql = ", ".join(f"`{c}`" for c in columns)
    for i in range(0, len(rows), CHUNK):
        chunk = rows[i : i + CHUNK]
        fh.write(f"REPLACE INTO `{table}` ({col_sql}) VALUES\n")
        lines = []
        for row in chunk:
            vals = ", ".join(sql_val(c, row.get(c), nullable) for c in columns)
            lines.append(f"({vals})")
        fh.write(",\n".join(lines))
        fh.write(";\n\n")


def write_file(name: str, title: str, specs: list) -> None:
    path = OUT / name
    with path.open("w", encoding="utf-8", newline="\n") as fh:
        fh.write(f"-- {title}\n")
        fh.write("-- Generated by tools/export_catalog_sql.py from addon Data/csv.\n")
        fh.write("-- REPLACE INTO so this file can be re-applied by hand.\n\n")
        for csv_name, table, columns, nullable in specs:
            rows = load_rows(csv_name, columns)
            fh.write(f"-- {csv_name} -> {table} ({len(rows)} rows)\n")
            write_inserts(table, columns, nullable, rows, fh)
            print(f"  {table}: {len(rows)}")
    print(f"wrote {path.name}")


FILES = {
    "types": ("01_battlemon_catalog_types", "Battlemon catalog: types, type chart, abilities",
              ["types.csv", "type_chart.csv", "abilities.csv"]),
    "moves": ("02_battlemon_catalog_moves", "Battlemon catalog: moves", ["moves.csv"]),
    "items": ("03_battlemon_catalog_items", "Battlemon catalog: items", ["items.csv"]),
    "species": ("04_battlemon_catalog_species", "Battlemon catalog: species", ["species.csv"]),
    "forms": ("05_battlemon_catalog_forms", "Battlemon catalog: forms", ["forms.csv"]),
    "learnsets": ("06_battlemon_catalog_species_moves", "Battlemon catalog: species learnsets",
                  ["species_moves.csv"]),
    "tutor": ("07_battlemon_catalog_tutor_moves", "Battlemon catalog: TM/tutor move pools",
              ["species_tutor_moves.csv"]),
    "formmoves": ("08_battlemon_catalog_form_moves", "Battlemon catalog: per-form move overrides",
                  ["form_moves.csv"]),
}


def main() -> None:
    global ADDON_CSV
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--csv", default=str(ADDON_CSV), help="addon Data/csv directory")
    ap.add_argument("--date", default="2026_08_13",
                    help="filename date prefix; use a new date when the old file is already applied")
    ap.add_argument("--only", nargs="*", choices=sorted(FILES), default=sorted(FILES),
                    help="which catalog files to emit")
    args = ap.parse_args()

    ADDON_CSV = Path(args.csv)
    if not ADDON_CSV.is_dir():
        raise SystemExit(f"CSV dir missing: {ADDON_CSV}")
    OUT.mkdir(parents=True, exist_ok=True)

    by_csv = {spec[0]: spec for spec in TABLES}
    for key in args.only:
        stem, title, sources = FILES[key]
        write_file(f"{args.date}_{stem}.sql", title, [by_csv[s] for s in sources])


if __name__ == "__main__":
    main()
