"""Retail ItemEffect rows that cast a garrison spell (blueprints, follower contracts, shipment items), saved for
import_garr_db2.py as db2_item_effect."""
import csv
import io
import time
import urllib.request
from pathlib import Path

SRC = Path(r"G:\risServer\_ref\garr_csv\SpellEffect.csv")
OUT = Path(r"G:\risServer\_ref\garr_csv\ItemEffect.csv")


def fetch(spell: str) -> list[dict]:
    url = f"https://wago.tools/db2/ItemEffect/csv?filter[SpellID]=exact:{spell}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return list(csv.DictReader(io.StringIO(r.read().decode("utf-8"))))
        except Exception:
            time.sleep(2 + attempt * 3)
    print(f"failed {spell}")
    return []


def main():
    with SRC.open(encoding="utf-8") as f:
        spells = sorted({r["SpellID"] for r in csv.DictReader(f) if r["Effect"] in ("210", "220", "221")}, key=int)
    rows, fields = [], None
    for i, spell in enumerate(spells):
        part = [r for r in fetch(spell) if r.get("SpellID") == spell]
        if part and fields is None:
            fields = list(part[0].keys())
        rows += part
        if i % 50 == 0:
            print(f"{i}/{len(spells)} spells, {len(rows)} item effects", flush=True)
    with OUT.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} rows -> {OUT}")


def link_items():
    """Retail moved the item reference out of ItemEffect into ItemXItemEffect; write one row per (item, effect)."""
    with OUT.open(encoding="utf-8") as f:
        effects = list(csv.DictReader(f))
    if effects and "ParentItemID" in effects[0]:
        return
    by_id = {r["ID"]: r for r in effects}
    req = urllib.request.Request("https://wago.tools/db2/ItemXItemEffect/csv", headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=300) as r:
        links = list(csv.DictReader(io.StringIO(r.read().decode("utf-8"))))
    rows = [dict(by_id[l["ItemEffectID"]], ParentItemID=l["ItemID"]) for l in links if l["ItemEffectID"] in by_id]
    with OUT.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(effects[0].keys()) + ["ParentItemID"])
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} item links -> {OUT}")


if __name__ == "__main__":
    import sys
    if "--link" not in sys.argv:
        main()
    link_items()
