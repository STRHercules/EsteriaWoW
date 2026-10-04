"""Compare donor CreatureDisplayInfo rows with the rows our client ships for the same models."""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[2] / "tools"))

from cars_mount_pack import Wdbc  # noqa: E402
from inspect_client_races import Client  # noqa: E402
from port_race import RACES  # noqa: E402

DONOR = HERE.parent / "vulpera-pandaren-playable-races/eunoia-dbc/CreatureDisplayInfo.dbc"
KEY = "DBFilesClient\\CreatureDisplayInfo.dbc"


def main() -> None:
    donor = Wdbc(DONOR.read_bytes())
    client = Client()
    ours = client.table(KEY)
    assert ours
    print(f"donor fields={donor.fields} record={donor.record_size} rows={len(donor.rows)}")
    for spec in RACES:
        male, female = spec["display_pair"]
        our_ids = (spec["race_id"], spec["race_id"])
        target_rows = {
            spec["race_id"]: None,
        }
        print(f"== {spec['name']} (donor displays {male}/{female})")
        for label, donor_id in (("male", male), ("female", female)):
            donor_row = next((r for r in donor.rows if r[0] == donor_id), None)
            our_row = next((r for r in ours.rows if r[1] == (donor_row[1] if donor_row else -1)), None)
            print(f"   donor {label} display {donor_id}: {donor_row}")
            print(f"   ours  {label} row (model {donor_row[1] if donor_row else '?'}): {our_row}")


if __name__ == "__main__":
    main()
