"""Dump CreatureDisplayInfoExtra rows: python inspect_extras.py <first> <last>."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from inspect_client_races import Client  # noqa: E402

KEY = "DBFilesClient\\CreatureDisplayInfoExtra.dbc"


def main() -> None:
    low, high = (int(a) for a in sys.argv[1:3])
    client = Client()
    extras = client.table(KEY)
    displays = client.table("DBFilesClient\\CreatureDisplayInfo.dbc")
    assert extras and displays
    print(f"extra fields={extras.fields} record={extras.record_size}")
    for row in sorted(extras.rows, key=lambda r: r[0]):
        if not low <= row[0] <= high:
            continue
        name = extras.text(row[-1]) if row[-1] < len(extras.strings) else "?"
        linked = [d[0] for d in displays.rows if d[3] == row[0]]
        print(f"extra {row[0]}: {row} bake={name!r} linked_displays={linked}")


if __name__ == "__main__":
    main()
