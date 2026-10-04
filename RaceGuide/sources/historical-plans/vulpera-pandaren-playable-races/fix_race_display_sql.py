"""Point every server-side race display mapping at the ids the client actually ships."""

from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parents[3]

REPLACEMENTS = {
    "modules/mod-custom-server/data/sql/db-world/updates/dbc/chrraces_dbc.sql": (
        ("(18, 12, 1, 4140, 49, 50, 'Pa'", "(18, 12, 1, 4140, 141687, 141688, 'Pa'"),
        ("(20, 12, 2, 4141, 6894, 6895, 'Vu'", "(20, 12, 2, 4141, 141254, 141255, 'Vu'"),
    ),
    "modules/mod-custom-server/data/sql/db-world/updates/u_custom_server_2026_08_30_race_models.sql": (
        ("WHEN 18 THEN 90006", "WHEN 18 THEN 141687"),
        ("WHEN 18 THEN 90007", "WHEN 18 THEN 141688"),
        ("WHEN 20 THEN 90010", "WHEN 20 THEN 141254"),
        ("WHEN 20 THEN 90011", "WHEN 20 THEN 141255"),
    ),
    "modules/mod-custom-server/data/sql/updates/pending_db_world/rev_1787850000002_race_models.sql": (
        ("WHEN 18 THEN 90006", "WHEN 18 THEN 141687"),
        ("WHEN 18 THEN 90007", "WHEN 18 THEN 141688"),
        ("WHEN 20 THEN 90010", "WHEN 20 THEN 141254"),
        ("WHEN 20 THEN 90011", "WHEN 20 THEN 141255"),
    ),
    "modules/mod-custom-server/data/sql/db-world/updates/u_custom_server_2026_09_02_race_sync.sql": (
        ("WHEN 18 THEN 3000006", "WHEN 18 THEN 141687"),
        ("WHEN 18 THEN 3000007", "WHEN 18 THEN 141688"),
        ("WHEN 20 THEN 3000010", "WHEN 20 THEN 141254"),
        ("WHEN 20 THEN 3000011", "WHEN 20 THEN 141255"),
    ),
}


def main() -> None:
    for relative, replacements in REPLACEMENTS.items():
        path = REPO / relative
        text = path.read_text(encoding="utf-8")
        changed = []
        for old, new in replacements:
            if old in text:
                text = text.replace(old, new)
                changed.append(old)
        path.write_text(text, encoding="utf-8")
        print(f"{relative}: {len(changed)}/{len(replacements)} replacements")
        for old in replacements:
            if old not in changed:
                print(f"    (already updated or absent: {old})")


if __name__ == "__main__":
    main()
