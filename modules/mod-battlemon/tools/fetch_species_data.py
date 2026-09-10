# -*- coding: utf-8 -*-
"""Replace placeholder species rows in species.csv with real PokeAPI data.

The Gen 9 rows (IDs 899-1025) were generated from sprite filenames alone: every
stat 80, type NORMAL, no ability, no dex text. This pulls the real values and
rewrites just those rows, leaving the hand-curated Gen 1-8 rows untouched.

Abilities the catalog has never seen (Protosynthesis, Quark Drive, ...) are
appended to abilities.csv so the new species rows do not point at nothing.

Usage:
    python tools/fetch_species_data.py "<...>/AddOns/Battlemon/Data/csv"
"""
from __future__ import annotations

import csv
import json
import sys
import time
import urllib.request
from pathlib import Path

API = "https://pokeapi.co/api/v2"
CACHE = Path(__file__).resolve().parent / ".cache" / "pokeapi"
STUB_MARKER = "Data stub generated from sprite"

GENDER_RATIO = {
    -1: "Genderless",
    0: "AlwaysMale",
    1: "FemaleOneEighth",
    2: "Female25Percent",
    4: "Female50Percent",
    6: "Female75Percent",
    7: "FemaleSevenEighths",
    8: "AlwaysFemale",
}

GROWTH_RATE = {
    "slow": "Slow",
    "medium": "Medium",
    "fast": "Fast",
    "medium-slow": "Parabolic",
    "slow-then-very-fast": "Erratic",
    "fast-then-very-slow": "Fluctuating",
}

EGG_GROUP = {
    "monster": "Monster",
    "water1": "Water1",
    "water2": "Water2",
    "water3": "Water3",
    "bug": "Bug",
    "flying": "Flying",
    "ground": "Field",
    "fairy": "Fairy",
    "plant": "Grass",
    "humanshape": "Humanlike",
    "mineral": "Mineral",
    "indeterminate": "Amorphous",
    "ditto": "Ditto",
    "dragon": "Dragon",
    "no-eggs": "Undiscovered",
}

# PokeAPI body shapes in the same order Essentials lists its own.
SHAPE = {
    "ball": "Head",
    "squiggle": "Serpentine",
    "fish": "Finned",
    "arms": "HeadArms",
    "blob": "HeadBase",
    "upright": "BipedalTail",
    "legs": "HeadLegs",
    "quadruped": "Quadruped",
    "wings": "Winged",
    "tentacles": "Multiped",
    "heads": "MultiBody",
    "humanoid": "Bipedal",
    "bug-wings": "MultiWinged",
    "armor": "Insectoid",
}

HABITAT = {
    "cave": "Cave",
    "forest": "Forest",
    "grassland": "Grassland",
    "mountain": "Mountain",
    "rare": "Rare",
    "rough-terrain": "RoughTerrain",
    "sea": "Sea",
    "urban": "Urban",
    "waters-edge": "WatersEdge",
}


def get(path: str) -> dict:
    safe = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in path)
    cache_file = CACHE / (safe + ".json")
    if cache_file.exists():
        return json.loads(cache_file.read_text(encoding="utf-8"))
    # PokeAPI rejects the default urllib user agent with a 403.
    req = urllib.request.Request(
        API + "/" + path, headers={"User-Agent": "mod-battlemon/1.0 (catalog import)"})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            break
        except Exception as exc:
            if attempt == 3:
                raise
            print(f"  retry {path}: {exc}")
            time.sleep(2 * (attempt + 1))
    cache_file.parent.mkdir(parents=True, exist_ok=True)
    cache_file.write_text(json.dumps(data), encoding="utf-8")
    return data


# PokeAPI uses typographic punctuation; the rest of the corpus is straight ASCII.
PUNCTUATION = {
    "\u2018": "'", "\u2019": "'", "\u201c": '"', "\u201d": '"',
    "\u2013": "-", "\u2014": "-", "\u2026": "...",
}


def plain_punctuation(text: str) -> str:
    for bad, good in PUNCTUATION.items():
        text = text.replace(bad, good)
    return text


def internal(name: str) -> str:
    return "".join(ch for ch in name.upper() if ch.isalnum())


def english(entries: list, key: str) -> str:
    for e in entries:
        if e["language"]["name"] == "en":
            return " ".join(e[key].split())
    return ""


def flavor_text(species: dict) -> str:
    best = ""
    for e in species.get("flavor_text_entries", []):
        if e["language"]["name"] != "en":
            continue
        text = " ".join(e["flavor_text"].replace("\u00ad", "").split())
        # Later games phrase entries more completely; keep taking the newest.
        best = plain_punctuation(text)
    return best


def build_row(template: list, header: list, sid: int) -> list:
    poke = get(f"pokemon/{sid}")
    spec = get(f"pokemon-species/{sid}")
    row = dict(zip(header, template))

    stats = {s["stat"]["name"]: s["base_stat"] for s in poke["stats"]}
    row["hp"] = stats.get("hp", 80)
    row["atk"] = stats.get("attack", 80)
    row["def"] = stats.get("defense", 80)
    row["spa"] = stats.get("special-attack", 80)
    row["spd"] = stats.get("special-defense", 80)
    row["spe"] = stats.get("speed", 80)

    types = sorted(poke["types"], key=lambda t: t["slot"])
    row["type1"] = types[0]["type"]["name"].upper()
    row["type2"] = types[1]["type"]["name"].upper() if len(types) > 1 else ""

    normal, hidden = [], ""
    for a in sorted(poke["abilities"], key=lambda a: a["slot"]):
        name = internal(a["ability"]["name"])
        if a["is_hidden"]:
            hidden = name
        else:
            normal.append(name)
    row["ability1"] = normal[0] if normal else ""
    row["ability2"] = normal[1] if len(normal) > 1 else ""
    row["hidden_ability"] = hidden

    row["gender_ratio"] = GENDER_RATIO.get(spec["gender_rate"], "Female50Percent")
    row["growth_rate"] = GROWTH_RATE.get(spec["growth_rate"]["name"], "Medium")
    row["base_exp"] = poke.get("base_experience") or 100
    row["catch_rate"] = spec["capture_rate"]
    row["happiness"] = spec["base_happiness"]
    row["hatch_steps"] = spec["hatch_counter"] * 256
    row["egg_groups"] = ",".join(
        EGG_GROUP.get(g["name"], g["name"].capitalize()) for g in spec["egg_groups"]
    )

    row["height"] = round(poke["height"] / 10, 1)
    row["weight"] = round(poke["weight"] / 10, 1)
    row["color"] = spec["color"]["name"].capitalize() if spec.get("color") else ""
    row["shape"] = SHAPE.get(spec["shape"]["name"], "") if spec.get("shape") else ""
    row["habitat"] = HABITAT.get(spec["habitat"]["name"], "") if spec.get("habitat") else ""
    row["category"] = english(spec.get("genera", []), "genus").replace(" Pokémon", "")
    row["pokedex"] = flavor_text(spec) or row["pokedex"]
    row["generation"] = "9"

    return [row[h] for h in header]


def sync_abilities(csv_dir: Path) -> None:
    """Add any ability species.csv references but abilities.csv has never heard of."""
    with (csv_dir / "species.csv").open(encoding="utf-8", newline="") as fh:
        wanted = set()
        for row in csv.DictReader(fh):
            for key in ("ability1", "ability2", "hidden_ability"):
                wanted.add(row[key])

    path = csv_dir / "abilities.csv"
    with path.open(encoding="utf-8", newline="") as fh:
        reader = csv.reader(fh)
        header = next(reader)
        rows = list(reader)
    known = {r[1] for r in rows}
    missing = sorted(w for w in wanted if w and w not in known)
    if not missing:
        print("abilities: nothing to add")
        return

    # Internal names drop the hyphens the API slugs need, so map back via the index.
    slugs = {internal(a["name"]): a["name"] for a in get("ability?limit=1000")["results"]}
    next_id = max(int(r[0]) for r in rows) + 1
    for name in missing:
        slug = slugs.get(name)
        if not slug:
            print("ability ? unknown to PokeAPI:", name)
            continue
        data = get("ability/" + slug)
        pretty = english(data.get("names", []), "name") or name.title()
        desc = english(data.get("flavor_text_entries", []), "flavor_text")
        if not desc:
            desc = english(data.get("effect_entries", []), "short_effect")
        rows.append([str(next_id), name, pretty, desc])
        print("ability +", name)
        next_id += 1
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh, lineterminator="\n")
        writer.writerow(header)
        writer.writerows(rows)
    print(f"abilities: added {len(missing)}")


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    csv_dir = Path(sys.argv[1])
    path = csv_dir / "species.csv"
    with path.open(encoding="utf-8", newline="") as fh:
        reader = csv.reader(fh)
        header = next(reader)
        rows = list(reader)

    dex_col = header.index("pokedex")
    changed = 0
    for i, row in enumerate(rows):
        if STUB_MARKER not in row[dex_col]:
            folded = plain_punctuation(row[dex_col])
            if folded != row[dex_col]:
                row[dex_col] = folded
                changed += 1
            continue
        rows[i] = build_row(row, header, int(row[0]))
        changed += 1
        if changed % 20 == 0:
            print(f"  {changed} species")

    if changed:
        with path.open("w", encoding="utf-8", newline="") as fh:
            writer = csv.writer(fh, lineterminator="\n")
            writer.writerow(header)
            writer.writerows(rows)
        print(f"species: rewrote {changed} rows")
    else:
        print("species: no stub rows left")

    sync_abilities(csv_dir)


if __name__ == "__main__":
    main()
