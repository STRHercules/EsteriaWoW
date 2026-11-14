"""Row-delta model: new DBC rows kept as plain Python values (strings stay strings), applied onto any baseline.

The delta is the unit that survives other threads changing the winning DBCs: install-time rebase re-applies it
onto whatever the current winners are, rejecting any ID that has since been taken.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

import lib

STR_COLS = {
    "Map": [1], "WorldMapArea": [3], "WorldMapOverlay": [8], "LoadingScreens": [1, 2], "LightSkybox": [1],
    "ZoneMusic": [1], "ZoneIntroMusicTable": [1], "SoundEntries": [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 23],
}
LOC_COLS = {"Map": [5, 23, 40], "AreaTable": [11], "AreaPOI": [18, 35], "WorldSafeLocs": [5]}


@dataclass
class Delta:
    rows: dict[str, list[list]] = field(default_factory=dict)  # table -> list of rowspecs (ints and str)

    def add(self, table: str, spec: list) -> None:
        self.rows.setdefault(table, []).append(spec)

    def ids(self, table: str) -> list[int]:
        return [r[0] for r in self.rows.get(table, [])]

    def dump(self, path: Path) -> None:
        path.write_text(json.dumps(self.rows, indent=0), encoding="utf-8")

    @staticmethod
    def load(path: Path) -> "Delta":
        return Delta(json.loads(path.read_text(encoding="utf-8")))


def spec_from_src(table: str, src: lib.Dbc, row: list[int]) -> list:
    """Copy a source row, resolving string offsets to text (loc fields collapse to the best available text)."""
    spec: list = list(row)
    for c in STR_COLS.get(table, []):
        spec[c] = src.text(row[c])
    for s in LOC_COLS.get(table, []):
        spec[s] = lib.best_loc(src, row, s)
        for i in range(1, 17):
            spec[s + i] = 0
    return spec


def apply_spec(table: str, base: lib.Dbc, spec: list, reject_dupes: bool = True) -> None:
    if reject_dupes and base.get(spec[0]) is not None:
        raise ValueError(f"{table}: ID {spec[0]} already exists in baseline")
    out = list(spec)
    locs = LOC_COLS.get(table, [])
    flag_src = base.rows[0] if base.rows else None
    for c in STR_COLS.get(table, []):
        out[c] = base.add_str(spec[c]) if isinstance(spec[c], str) else spec[c]
    for s in locs:
        txt = spec[s] if isinstance(spec[s], str) else ""
        out[s] = base.add_str(txt)
        for i in range(1, 16):
            out[s + i] = 0
        out[s + 16] = flag_src[s + 16] if flag_src else 0xFFFFFFFF
    base.rows.append([v & 0xFFFFFFFF if isinstance(v, int) else v for v in out])


def apply_delta(delta: Delta, bases: dict[str, lib.Dbc], only: set[str] | None = None) -> dict[str, int]:
    done = {}
    for table, specs in delta.rows.items():
        if table not in bases or (only is not None and table not in only):
            continue
        for sp in specs:
            apply_spec(table, bases[table], sp)
        done[table] = len(specs)
    return done


def next_free(used: set[int], start: int, count: int = 1) -> list[int]:
    out = []
    n = start
    while len(out) < count:
        if n not in used:
            out.append(n)
            used.add(n)
        n += 1
    return out
