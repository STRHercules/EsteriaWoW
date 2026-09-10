# -*- coding: utf-8 -*-
"""Build the move pools the move manager offers.

Three sources, because no single one covers everything we ship:

  * Essentials pokemon.txt      TutorMoves (the TM/tutor pool) for Gen 1-8
  * Essentials pokemon_forms.txt per-form Moves/TutorMoves/FormName overrides
  * cached PokeAPI JSON          real Gen 9 level-up and machine moves, since
                                 Essentials 21.1 predates Gen 9 and our rows
                                 for 899-1025 are identical stubs

Writes species_moves.csv (Gen 9 rows replaced), species_tutor_moves.csv and
form_moves.csv, and fills in real form names so "Raichu (01)" reads
"Alolan Raichu". Any move missing from moves.csv is dropped and counted.

Usage:
    python tools/import_move_pools.py "<...>/AddOns/Battlemon/Data/csv"
"""
from __future__ import annotations

import csv
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

PBS = Path(r"C:\Users\dead\Downloads\pokemon-essentials-21.1\PBS")
CACHE = Path(__file__).resolve().parent / ".cache" / "pokeapi"
GEN9_FIRST = 899
GEN9_LAST = 1025
VERSION_GROUP = "scarlet-violet"
TUTOR_METHODS = {"machine", "tutor"}


def read_csv(path: Path) -> tuple[list[str], list[dict]]:
    with path.open(encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        return list(reader.fieldnames or []), list(reader)


def write_csv(path: Path, header: list[str], rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=header, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def parse_pbs(path: Path) -> list[tuple[str, str]]:
    """Split a PBS file into (header, body) pairs."""
    text = path.read_text(encoding="utf-8", errors="replace")
    parts = re.split(r"^\[([^\]]+)\]$", text, flags=re.M)[1:]
    return list(zip(parts[0::2], parts[1::2]))


def field(body: str, key: str) -> str:
    m = re.search(rf"^{key}\s*=\s*(.+)$", body, re.M)
    return m.group(1).strip() if m else ""


def internal(name: str) -> str:
    return "".join(ch for ch in name.upper() if ch.isalnum())


class Dropped:
    """Counts moves referenced by a source but absent from moves.csv."""

    def __init__(self, known: set[str]):
        self.known = known
        self.missing: dict[str, int] = defaultdict(int)

    def keep(self, move: str) -> bool:
        if move in self.known:
            return True
        self.missing[move] += 1
        return False

    def report(self, label: str) -> None:
        if not self.missing:
            print(f"{label}: every move resolved")
            return
        total = sum(self.missing.values())
        worst = sorted(self.missing.items(), key=lambda kv: -kv[1])[:8]
        print(f"{label}: dropped {total} rows across {len(self.missing)} unknown moves")
        for name, count in worst:
            print(f"    {name} x{count}")


def gen9_moves(sid: int, drop: Dropped) -> tuple[list[tuple[int, str]], list[str]]:
    """Real level-up and TM/tutor moves for one Gen 9 species."""
    path = CACHE / f"pokemon_{sid}.json"
    if not path.exists():
        return [], []
    data = json.loads(path.read_text(encoding="utf-8"))
    level_up: list[tuple[int, str]] = []
    tutor: list[str] = []
    for entry in data.get("moves", []):
        name = internal(entry["move"]["name"])
        for detail in entry["version_group_details"]:
            if detail["version_group"]["name"] != VERSION_GROUP:
                continue
            method = detail["move_learn_method"]["name"]
            if method == "level-up":
                if drop.keep(name):
                    level_up.append((max(1, detail["level_learned_at"]), name))
            elif method in TUTOR_METHODS:
                if drop.keep(name):
                    tutor.append(name)
    level_up.sort()
    return level_up, sorted(set(tutor))


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    csv_dir = Path(sys.argv[1])
    if not PBS.is_dir():
        raise SystemExit(f"Essentials PBS not found: {PBS}")

    known = {r["internal_name"] for r in read_csv(csv_dir / "moves.csv")[1]}
    species_header, species = read_csv(csv_dir / "species.csv")
    forms_header, forms = read_csv(csv_dir / "forms.csv")
    by_internal = {r["internal_name"]: int(r["id"]) for r in species}

    # --- level-up moves: keep Gen 1-8 as curated, rebuild the Gen 9 stubs -----
    sm_header, species_moves = read_csv(csv_dir / "species_moves.csv")
    kept = [r for r in species_moves if int(r["species_id"]) < GEN9_FIRST]
    drop_g9 = Dropped(known)
    gen9_level: list[dict] = []
    gen9_tutor: dict[int, list[str]] = {}
    for sid in range(GEN9_FIRST, GEN9_LAST + 1):
        level_up, tutor = gen9_moves(sid, drop_g9)
        gen9_tutor[sid] = tutor
        for level, move in level_up:
            gen9_level.append({"species_id": str(sid), "level": str(level),
                               "move_internal_name": move})
    rebuilt = kept + gen9_level
    for i, row in enumerate(rebuilt, 1):
        row["id"] = str(i)
    write_csv(csv_dir / "species_moves.csv", sm_header, rebuilt)
    print(f"species_moves.csv: {len(kept)} kept + {len(gen9_level)} real Gen 9 rows")
    drop_g9.report("gen 9 level-up")

    # --- tutor pool ----------------------------------------------------------
    drop_tutor = Dropped(known)
    tutor_rows: list[dict] = []
    unmatched = 0
    for header, body in parse_pbs(PBS / "pokemon.txt"):
        sid = by_internal.get(header)
        if not sid:
            unmatched += 1
            continue
        raw = field(body, "TutorMoves")
        if not raw:
            continue
        for move in dict.fromkeys(m.strip() for m in raw.split(",")):
            if move and drop_tutor.keep(move):
                tutor_rows.append({"species_id": str(sid), "move_internal_name": move})
    for sid, moves in gen9_tutor.items():
        for move in moves:
            tutor_rows.append({"species_id": str(sid), "move_internal_name": move})
    for i, row in enumerate(tutor_rows, 1):
        row["id"] = str(i)
    write_csv(csv_dir / "species_tutor_moves.csv",
              ["id", "species_id", "move_internal_name"], tutor_rows)
    print(f"species_tutor_moves.csv: {len(tutor_rows)} rows"
          + (f" ({unmatched} Essentials entries had no species id)" if unmatched else ""))
    drop_tutor.report("tutor")

    # --- per-form overrides --------------------------------------------------
    # Our variants come from sprite filenames ("01"), Essentials keys forms as
    # [SPECIES,1]; the numbering lines up where both define the same form.
    form_by_key: dict[tuple[int, str], dict] = {}
    for row in forms:
        form_by_key[(int(row["species_id"]), row["variant"])] = row

    drop_form = Dropped(known)
    form_rows: list[dict] = []
    renamed = 0
    matched = 0
    skipped = 0
    for header, body in parse_pbs(PBS / "pokemon_forms.txt"):
        name, _, number = header.partition(",")
        sid = by_internal.get(name)
        if not sid or not number.isdigit():
            skipped += 1
            continue
        form = form_by_key.get((sid, f"{int(number):02d}"))
        if not form:
            skipped += 1
            continue
        matched += 1
        form_id = form["id"]

        level_raw = field(body, "Moves")
        if level_raw:
            bits = [b.strip() for b in level_raw.split(",")]
            for level, move in zip(bits[0::2], bits[1::2]):
                if drop_form.keep(move):
                    form_rows.append({"form_id": form_id, "method": "level",
                                      "level": level, "move_internal_name": move})
        tutor_raw = field(body, "TutorMoves")
        if tutor_raw:
            for move in dict.fromkeys(m.strip() for m in tutor_raw.split(",")):
                if move and drop_form.keep(move):
                    form_rows.append({"form_id": form_id, "method": "tutor",
                                      "level": "0", "move_internal_name": move})

        pretty = field(body, "FormName")
        if pretty:
            species_name = next((s["name"] for s in species if int(s["id"]) == sid), name.title())
            # Some form names already carry the species ("Heat Rotom"), most do
            # not ("Alolan"), and a few are standalone ("Ash-Greninja").
            if species_name.lower() in pretty.lower():
                label = pretty
            else:
                label = f"{pretty} {species_name}"
            if form["name"] != label:
                form["name"] = label
                renamed += 1

    for i, row in enumerate(form_rows, 1):
        row["id"] = str(i)
    write_csv(csv_dir / "form_moves.csv",
              ["id", "form_id", "method", "level", "move_internal_name"], form_rows)
    print(f"form_moves.csv: {len(form_rows)} rows for {matched} matched forms"
          f" ({skipped} Essentials forms had no counterpart here)")
    drop_form.report("form")

    if renamed:
        write_csv(csv_dir / "forms.csv", forms_header, forms)
    print(f"forms.csv: renamed {renamed} forms")


if __name__ == "__main__":
    main()
