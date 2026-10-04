"""Find fields where the two failing races differ from every working race.

Working set (reported in game): 16,17,18,19,21,22,23,28,30 (Pandaren talks).
Failing: 20 (Vulpera), 29 (Kul Tiran).
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from inspect_client_races import Client  # noqa: E402

RACES_KEY = "DBFilesClient\\ChrRaces.dbc"
DISPLAY_KEY = "DBFilesClient\\CreatureDisplayInfo.dbc"
MODEL_KEY = "DBFilesClient\\CreatureModelData.dbc"
WORKING = (16, 17, 18, 19, 21, 22, 23, 28, 30)
FAILING = (20, 29)
FIELDS = {
    1: "Flags", 2: "FactionID", 3: "ExplorationSoundID", 7: "BaseLanguage", 8: "CreatureType",
    9: "ResSicknessSpellID", 10: "SplashSoundID", 12: "CinematicSequenceID", 13: "Alliance",
    65: "FacialHairCustomization_1", 66: "FacialHairCustomization_2", 67: "HairCustomization",
    68: "Required_Expansion",
}


def main() -> None:
    client = Client()
    races = client.table(RACES_KEY)
    displays = client.table(DISPLAY_KEY)
    models = client.table(MODEL_KEY)
    assert races and displays and models
    rows = {row[0]: row for row in races.rows}
    print("== ChrRaces fields")
    for index, name in FIELDS.items():
        working_values = {rows[race][index] for race in WORKING}
        for race in FAILING:
            value = rows[race][index]
            flag = "  <-- unique to failing" if value not in working_values else ""
            print(f"  {name:<26} race {race}: {value:<12} working set: {sorted(working_values)}{flag}")
    print("\n== race -> display -> model chain")
    for race in WORKING + FAILING:
        row = rows[race]
        for gender, display_id in (("M", row[4]), ("F", row[5])):
            display = next((r for r in displays.rows if r[0] == display_id), None)
            model = next((r for r in models.rows if display and r[0] == display[1]), None)
            path = models.text(model[2]) if model else "<none>"
            print(f"  race {race:>3} {gender}: display {display_id} model {display[1] if display else '?'} {path}")


if __name__ == "__main__":
    main()
