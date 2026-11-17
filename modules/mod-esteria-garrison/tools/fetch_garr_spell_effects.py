"""Retail SpellEffect rows for the garrison effects UWoW's Spell.cpp handles, saved where import_garr_db2.py picks
them up (db2_spell_effect). 3.3.5 Spell.dbc has none of these spells, so the module applies the effects itself."""
import csv
import io
import urllib.request
from pathlib import Path

OUT = Path(r"G:\risServer\_ref\garr_csv\SpellEffect.csv")
EFFECTS = {
    210: "LEARN_GARRISON_BUILDING",
    214: "CREATE_GARRISON",
    216: "CREATE_SHIPMENT",
    217: "UPGRADE_GARRISON",
    220: "ADD_GARRISON_FOLLOWER",
    221: "ADD_GARRISON_MISSION",
    224: "ACTIVATE_GARRISON_BUILDING",
    230: "INCREASE_FOLLOWER_ITEM_LEVEL",
    233: "RETRAIN_FOLLOWER",
}


def fetch(effect: int) -> list[dict]:
    url = f"https://wago.tools/db2/SpellEffect/csv?filter[Effect]=exact:{effect}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=120) as r:
        text = r.read().decode("utf-8")
    return list(csv.DictReader(io.StringIO(text)))


def main():
    rows, fields = [], None
    for effect, name in EFFECTS.items():
        part = fetch(effect)
        part = [r for r in part if r.get("Effect") == str(effect)]
        print(f"{effect} {name}: {len(part)}")
        if part and fields is None:
            fields = list(part[0].keys())
        rows += part
    with OUT.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} rows -> {OUT}")


if __name__ == "__main__":
    main()
