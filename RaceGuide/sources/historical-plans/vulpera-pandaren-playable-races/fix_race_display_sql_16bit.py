"""Second pass: use the 16-bit player display ids (60004-60007)."""

from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parents[3]

REPLACEMENTS = {
    "modules/mod-custom-server/data/sql/db-world/updates/dbc/chrraces_dbc.sql": (
        ("(18, 12, 1, 4140, 141687, 141688, 'Pa'", "(18, 12, 1, 4140, 60004, 60005, 'Pa'"),
        ("(20, 12, 2, 4141, 141254, 141255, 'Vu'", "(20, 12, 2, 4141, 60006, 60007, 'Vu'"),
    ),
    "modules/mod-custom-server/data/sql/db-world/updates/u_custom_server_2026_08_30_race_models.sql": (
        ("WHEN 18 THEN 141687", "WHEN 18 THEN 60004"),
        ("WHEN 18 THEN 141688", "WHEN 18 THEN 60005"),
        ("WHEN 20 THEN 141254", "WHEN 20 THEN 60006"),
        ("WHEN 20 THEN 141255", "WHEN 20 THEN 60007"),
    ),
    "modules/mod-custom-server/data/sql/updates/pending_db_world/rev_1787850000002_race_models.sql": (
        ("WHEN 18 THEN 141687", "WHEN 18 THEN 60004"),
        ("WHEN 18 THEN 141688", "WHEN 18 THEN 60005"),
        ("WHEN 20 THEN 141254", "WHEN 20 THEN 60006"),
        ("WHEN 20 THEN 141255", "WHEN 20 THEN 60007"),
    ),
    "modules/mod-custom-server/data/sql/db-world/updates/u_custom_server_2026_09_02_race_sync.sql": (
        ("WHEN 18 THEN 141687", "WHEN 18 THEN 60004"),
        ("WHEN 18 THEN 141688", "WHEN 18 THEN 60005"),
        ("WHEN 20 THEN 141254", "WHEN 20 THEN 60006"),
        ("WHEN 20 THEN 141255", "WHEN 20 THEN 60007"),
    ),
}


def main() -> None:
    for relative, replacements in REPLACEMENTS.items():
        path = REPO / relative
        text = path.read_text(encoding="utf-8")
        applied = 0
        for old, new in replacements:
            if old in text:
                text = text.replace(old, new)
                applied += 1
        path.write_text(text, encoding="utf-8")
        print(f"{relative}: applied {applied}/{len(replacements)}")


if __name__ == "__main__":
    main()
