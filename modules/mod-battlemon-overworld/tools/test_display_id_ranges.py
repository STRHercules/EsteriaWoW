# -*- coding: utf-8 -*-
"""Regression checks for Battlemon display-ID namespaces."""

from pathlib import Path
from tempfile import TemporaryDirectory

from patch_dbc_csv import DISPLAY_NORMAL_BASE, DISPLAY_SHINY_BASE
from patch_dbc_csv import patch_display, read_quoted_csv, write_quoted_csv


def test_shiny_display_range_preserves_broken() -> None:
    assert DISPLAY_SHINY_BASE == 70000

    battlemon_normal = set(range(DISPLAY_NORMAL_BASE + 1, DISPLAY_NORMAL_BASE + 1582))
    battlemon_shiny = set(range(DISPLAY_SHINY_BASE + 1, DISPLAY_SHINY_BASE + 1582))
    broken = {60002, 60003}

    assert battlemon_normal.isdisjoint(broken)
    assert battlemon_shiny.isdisjoint(broken)
    assert battlemon_normal.isdisjoint(battlemon_shiny)


def test_csv_repatch_removes_legacy_battlemon_but_keeps_broken() -> None:
    header = [
        "ID", "ModelID", "SoundID", "ExtendedDisplayInfoID", "CreatureModelScale",
        "CreatureModelAlpha", "TextureVariation_1", "TextureVariation_2", "TextureVariation_3",
        "PortraitTextureName", "BloodLevel", "BloodID", "NPCSoundID", "ParticleColorID",
        "CreatureGeosetData", "ObjectEffectPackageID",
    ]

    def row(display_id: int, model_id: int) -> list[str]:
        return [str(display_id), str(model_id)] + ["0"] * (len(header) - 2)

    with TemporaryDirectory() as temp:
        csv_path = Path(temp) / "CreatureDisplayInfo.csv"
        write_quoted_csv(csv_path, header, [row(60001, 2272001), row(60002, 4898)])
        patch_display(Path(temp), [{"id": "1", "sprite": "001_Test"}])
        _, rows = read_quoted_csv(csv_path)

    values = {(r[0], r[1]) for r in rows}
    assert ("60001", "2272001") not in values
    assert ("60002", "4898") in values
    assert ("50001", "2252001") in values
    assert ("70001", "2272001") in values


if __name__ == "__main__":
    test_shiny_display_range_preserves_broken()
    test_csv_repatch_removes_legacy_battlemon_but_keeps_broken()
    print("display ID range checks passed")
