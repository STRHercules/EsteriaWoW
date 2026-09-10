# -*- coding: utf-8 -*-
"""Patch Chromie CreatureDisplayInfo / CreatureModelData CSVs with Battlemon rows.

Does not touch MPQs or DBC binaries. Re-runnable: strips previous Battlemon
rows (exact form display IDs / model ID blocks / Battlemon paths), then
appends a fresh copy. Other rows in the 50k-70k display range are left
alone so a customized client CSV is not wiped.

    python tools/patch_dbc_csv.py

IDs (keep in sync with src/BattlemonOverworld.h):
    CreatureModelData  2252000 + formId       (normal m2)
    CreatureModelData  2272000 + formId       (shiny m2)
    CreatureDisplayInfo 50000 + formId        (normal)
    CreatureDisplayInfo 70000 + formId        (shiny; 60000 is reserved by Broken/Sethrak)
    One .mdx per sprite; TextureVariation empty (hardcoded type 0 in the M2).

Import the two CSVs back into the DBCs yourself (WDBX etc.) and drop the
.dbc files in patch-z.mpq/DBFilesClient/.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

MODEL_NORMAL_BASE = 2252000
MODEL_SHINY_BASE = 2272000
DISPLAY_NORMAL_BASE = 50000
DISPLAY_SHINY_BASE = 70000
LEGACY_DISPLAY_SHINY_BASE = 60000
MODEL_DIR = r"Creature\Battlemon"

DEFAULT_FORMS = Path(
    r"D:\new-client\vanilla test\3.3.5a - Chromie (Reforged)"
    r"\Interface\AddOns\Battlemon\Data\csv\forms.csv"
)
DEFAULT_CSV_DIR = Path(
    r"D:\new-client\vanilla test\3.3.5a - Chromie (Reforged)"
    r"\Data\patch-z.mpq\DBFilesClient\CSV"
)


def quote_row(fields: list[str]) -> str:
    return ",".join('"' + f.replace('"', '""') + '"' for f in fields)


def read_quoted_csv(path: Path) -> tuple[list[str], list[list[str]]]:
    with path.open(encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.reader(fh))
    if not rows:
        raise SystemExit(f"empty csv: {path}")
    return rows[0], rows[1:]


def write_quoted_csv(path: Path, header: list[str], rows: list[list[str]]) -> None:
    lines = [quote_row(header)]
    lines.extend(quote_row(r) for r in rows)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def load_forms(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def model_template(model_id: int, model_name: str) -> dict[str, str]:
    return {
        "ID": str(model_id),
        "Flags": "0",
        "ModelName": model_name,
        "SizeClass": "0",
        "ModelScale": "1",
        "BloodID": "1",
        "FootprintTextureID": "1",
        "FootprintTextureLength": "18",
        "FootprintTextureWidth": "12",
        "FootprintParticleScale": "1",
        "FoleyMaterialID": "0",
        "FootstepShakeSize": "0",
        "DeathThudShakeSize": "0",
        "SoundID": "16",
        "CollisionWidth": "0.5",
        "CollisionHeight": "0.95",
        "MountHeight": "0",
        "GeoBoxMinX": "-0.4",
        "GeoBoxMinY": "-0.15",
        "GeoBoxMinZ": "0",
        "GeoBoxMaxX": "0.4",
        "GeoBoxMaxY": "0.15",
        "GeoBoxMaxZ": "1.05",
        "WorldEffectScale": "1",
        "AttachedEffectScale": "1",
        "MissileCollisionRadius": "0",
        "MissileCollisionPush": "0",
        "MissileCollisionRaise": "0",
    }


def is_battlemon_model_id(n: int) -> bool:
    if MODEL_NORMAL_BASE <= n < MODEL_NORMAL_BASE + 10000:
        return True
    if MODEL_SHINY_BASE <= n < MODEL_SHINY_BASE + 10000:
        return True
    return False


def patch_model(csv_dir: Path, forms: list[dict[str, str]]) -> None:
    path = csv_dir / "CreatureModelData.csv"
    header, rows = read_quoted_csv(path)
    id_idx = header.index("ID")
    name_idx = header.index("ModelName")
    kept = []
    for r in rows:
        try:
            n = int(r[id_idx])
        except ValueError:
            n = -1
        name = r[name_idx]
        if is_battlemon_model_id(n) or "Battlemon" in name:
            continue
        kept.append(r)

    added = 0
    for form in forms:
        form_id = int(form["id"])
        sprite = (form.get("sprite") or "").strip()
        if not sprite:
            continue
        kept.append(
            [model_template(MODEL_NORMAL_BASE + form_id, f"{MODEL_DIR}\\{sprite}.mdx")[col] for col in header]
        )
        kept.append(
            [model_template(MODEL_SHINY_BASE + form_id, f"{MODEL_DIR}\\{sprite}_s.mdx")[col] for col in header]
        )
        added += 2

    write_quoted_csv(path, header, kept)
    print(f"{path.name}: {len(kept)} rows ({added} Battlemon models)")


def battlemon_display_ids(forms: list[dict[str, str]]) -> set[int]:
    ids: set[int] = set()
    for form in forms:
        if not (form.get("sprite") or "").strip():
            continue
        form_id = int(form["id"])
        ids.add(DISPLAY_NORMAL_BASE + form_id)
        ids.add(DISPLAY_SHINY_BASE + form_id)
    return ids


def patch_display(csv_dir: Path, forms: list[dict[str, str]]) -> None:
    path = csv_dir / "CreatureDisplayInfo.csv"
    header, rows = read_quoted_csv(path)
    id_idx = header.index("ID")
    model_idx = header.index("ModelID")
    ours = battlemon_display_ids(forms)
    legacy_ids = {
        LEGACY_DISPLAY_SHINY_BASE + int(form["id"])
        for form in forms
        if (form.get("sprite") or "").strip()
    }
    legacy_model_ids = {
        MODEL_SHINY_BASE + int(form["id"])
        for form in forms
        if (form.get("sprite") or "").strip()
    }

    def keep(r: list[str]) -> bool:
        try:
            n = int(r[id_idx])
        except ValueError:
            return True
        if n in ours:
            return False
        if n not in legacy_ids:
            return True
        try:
            return int(r[model_idx]) not in legacy_model_ids
        except ValueError:
            return True

    kept = [r for r in rows if keep(r)]

    def display_row(display_id: int, model_id: int) -> list[str]:
        fields = {
            "ID": str(display_id),
            "ModelID": str(model_id),
            "SoundID": "0",
            "ExtendedDisplayInfoID": "0",
            "CreatureModelScale": "1",
            "CreatureModelAlpha": "255",
            "TextureVariation_1": "",
            "TextureVariation_2": "",
            "TextureVariation_3": "",
            "PortraitTextureName": "",
            "BloodLevel": "0",
            "BloodID": "0",
            "NPCSoundID": "0",
            "ParticleColorID": "0",
            "CreatureGeosetData": "0",
            "ObjectEffectPackageID": "0",
        }
        return [fields[col] for col in header]

    added = 0
    for form in forms:
        form_id = int(form["id"])
        sprite = (form.get("sprite") or "").strip()
        if not sprite:
            continue
        kept.append(display_row(DISPLAY_NORMAL_BASE + form_id, MODEL_NORMAL_BASE + form_id))
        kept.append(display_row(DISPLAY_SHINY_BASE + form_id, MODEL_SHINY_BASE + form_id))
        added += 2

    write_quoted_csv(path, header, kept)
    print(f"{path.name}: {len(kept)} rows ({added} Battlemon displays, {len(forms)} forms)")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--forms", type=Path, default=DEFAULT_FORMS)
    ap.add_argument("--csv-dir", type=Path, default=DEFAULT_CSV_DIR)
    args = ap.parse_args()
    if not args.forms.is_file():
        raise SystemExit(f"forms.csv not found: {args.forms}")
    if not (args.csv_dir / "CreatureDisplayInfo.csv").is_file():
        raise SystemExit(f"CreatureDisplayInfo.csv not found in {args.csv_dir}")
    forms = load_forms(args.forms)
    patch_model(args.csv_dir, forms)
    patch_display(args.csv_dir, forms)


if __name__ == "__main__":
    main()
