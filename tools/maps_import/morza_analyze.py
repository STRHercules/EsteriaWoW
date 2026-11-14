"""Parse the Morza SQL, compare with live acore_world (read-only SELECTs) and print what is importable."""

import collections
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sqlrows  # noqa: E402
from morza_load import FOLDERS, ROOT, clean, mysql  # noqa: E402


def load_all():
    merged: dict[str, sqlrows.Table] = {}
    problems = []
    for d in FOLDERS:
        for p in sorted(d.rglob("*.sql")):
            try:
                tabs, unh = sqlrows.parse(clean(p.read_text(encoding="utf-8", errors="replace")))
            except Exception as e:  # noqa: BLE001
                problems.append((str(p.relative_to(ROOT)), repr(e)))
                continue
            for n, t in tabs.items():
                merged.setdefault(n, sqlrows.Table(n)).rows.extend(t.rows)
            for u in unh:
                problems.append((str(p.relative_to(ROOT)), "unhandled: " + u))
    return merged, problems


def live_cols(table: str) -> list[str]:
    out = mysql(f"SHOW COLUMNS FROM acore_world.`{table}`;")
    return [l.split("\t")[0] for l in out.splitlines() if l and not l.startswith("ERROR")]


def live_keys(sql: str) -> set:
    out = mysql(sql)
    return {tuple(l.split("\t")) if "\t" in l else l for l in out.splitlines() if l and not l.startswith("ERROR")}


if __name__ == "__main__":
    tabs, problems = load_all()
    print("PROBLEMS", len(problems))
    for p in problems[:15]:
        print("  ", p)
    for n, t in sorted(tabs.items()):
        cols = list(t.rows[0].keys()) if t.rows else []
        lc = live_cols(n)
        print(f"{n:28} rows={len(t.rows):5} missing-in-live={[c for c in cols if c not in lc]} live-only={[c for c in lc if c not in cols][:8]}")
    ct = tabs["creature_template"].rows
    ents = [r["entry"] for r in ct]
    print("creature_template entries", len(ents), min(ents), max(ents))
    live = live_keys(f"SELECT entry FROM acore_world.creature_template WHERE entry IN ({','.join(map(str, ents))});")
    print("  already in live:", sorted(int(x) for x in live))
    spawns = tabs["creature"].rows
    print("creature spawns", len(spawns), collections.Counter(r["map"] for r in spawns).most_common(6))
    m5000 = [r for r in spawns if r["map"] == 5000]
    print("  map 5000 spawns", len(m5000), "ids", len({r["id1"] for r in m5000}))
    go = tabs.get("gameobject")
    if go:
        print("gameobject spawns", len(go.rows), collections.Counter(r["map"] for r in go.rows).most_common(6))
    gt = tabs.get("gameobject_template")
    if gt:
        ge = [r["entry"] for r in gt.rows]
        lv = live_keys(f"SELECT entry FROM acore_world.gameobject_template WHERE entry IN ({','.join(map(str, ge))});")
        print("gameobject_template", len(ge), min(ge), max(ge), "in live:", sorted(int(x) for x in lv))
    it = tabs.get("item_template")
    if it:
        ie = [r["entry"] for r in it.rows]
        lv = live_keys(f"SELECT entry FROM acore_world.item_template WHERE entry IN ({','.join(map(str, ie))});")
        print("item_template", ie, "in live:", lv)
    q = tabs.get("quest_template")
    if q:
        qe = [r["ID"] for r in q.rows]
        lv = live_keys(f"SELECT ID FROM acore_world.quest_template WHERE ID IN ({','.join(map(str, qe))});")
        print("quest_template", qe, "in live:", lv)
    # which creature spawn ids are not Morza templates
    stock = sorted({r["id1"] for r in m5000} - set(ents))
    print("map-5000 spawns using templates not defined by Morza SQL:", stock)
    print("lua scripts:", [p.name for p in (ROOT / "Lua Scripts").glob("*.lua")])
