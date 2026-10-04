"""Read-only dump of one or more ChrRaces rows plus the display/model/extra chain."""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from inspect_client_races import Client  # noqa: E402

RACES = (14, 15, 18, 20)
RACES_KEY = "DBFilesClient\\ChrRaces.dbc"
DISPLAY_KEY = "DBFilesClient\\CreatureDisplayInfo.dbc"
MODEL_KEY = "DBFilesClient\\CreatureModelData.dbc"
EXTRA_KEY = "DBFilesClient\\CreatureDisplayInfoExtra.dbc"


def main() -> None:
    client = Client()
    races = client.table(RACES_KEY)
    displays = client.table(DISPLAY_KEY)
    models = client.table(MODEL_KEY)
    extras = client.table(EXTRA_KEY)
    assert races and displays and models
    wanted = tuple(int(a) for a in sys.argv[1:]) or RACES
    for race in wanted:
        row = next((r for r in races.rows if r[0] == race), None)
        if row is None:
            print(f"race {race}: no row")
            continue
        print(
            f"=== race {race} flags={row[1]} faction={row[2]} expl={row[3]} "
            f"displays={row[4]}/{row[5]} prefix={races.text(row[6])!r} lang={row[7]} "
            f"ctype={row[8]} resSick={row[9]} splash={row[10]} file={races.text(row[11])!r} "
            f"cinematic={row[12]} alliance={row[13]} name={races.text(row[14])!r}"
        )
        for gender, display_id in (("M", row[4]), ("F", row[5])):
            display = next((r for r in displays.rows if r[0] == display_id), None)
            if display is None:
                print(f"    {gender} display {display_id}: MISSING")
                continue
            model = next((r for r in models.rows if r[0] == display[1]), None)
            path = models.text(model[2]) if model else "<no model row>"
            extra = next((r for r in extras.rows if r[0] == display[3]), None) if extras else None
            print(f"    {gender} display {display_id}: model {display[1]} {path} extra {display[3]}"
                  + (f" {extra}" if extra else " (no extra row)"))
            print(f"       display {display}")
            if model:
                print(f"       modeldata {model}")


if __name__ == "__main__":
    main()
