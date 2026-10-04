"""Field-by-field diff of our ChrRaces rows against the donor rows they were ported from."""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[2] / "tools"))

from inspect_client_races import Client  # noqa: E402
from port_race import RACES  # noqa: E402

KEY = "DBFilesClient\\ChrRaces.dbc"


def main() -> None:
    donor = json.loads((HERE / "eunoia-race-rows.json").read_text(encoding="utf-8"))
    client = Client()
    table = client.table(KEY)
    assert table
    fields = table.fields
    for spec in RACES:
        ours = next((r for r in table.rows if r[0] == spec["race_id"]), None)
        theirs = donor.get(str(spec["eunoia_race"]))
        if ours is None or theirs is None:
            print(f"{spec['name']}: missing row (ours={ours is not None}, donor={theirs is not None})")
            continue
        theirs = theirs["chrraces"]
        print(f"== {spec['name']} (ours {spec['race_id']} <- donor {spec['eunoia_race']})")
        for index in range(min(len(ours), len(theirs))):
            if ours[index] == theirs[index]:
                continue
            a, b = ours[index], theirs[index]
            if index in (0, 4, 5, 6, 11, 12, 14, 15, 16):
                continue  # ids, displays, prefix, file string, names
            ours_text = table.text(a) if index in (6, 11, 14, 15, 16) else ""
            print(f"   field {index:>2}: ours={a:<12} donor={b:<12} {ours_text}")
    print(f"\nfield count: ours={fields} donor={len(next(iter(donor.values()))['chrraces'])}")


if __name__ == "__main__":
    main()
