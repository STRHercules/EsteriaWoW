"""Offline checks of the staged output. Staged evidence only; says nothing about in-game behaviour."""
import sys, struct
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import lib, closure, dbcdelta, ctx as C

S = C.STAGE
bad = 0
def fail(m):
    global bad; bad += 1; print("FAIL", m)
def ok(m): print("ok  ", m)

delta = dbcdelta.Delta.load(S / "reports" / "dbc-delta.json")
cl = {p.stem: lib.Dbc(p.read_bytes()) for p in (S / "client-dbc" / "DBFilesClient").glob("*.dbc")}
sv = {p.stem: lib.Dbc(p.read_bytes()) for p in (S / "server" / "dbc").glob("*.dbc")}
for side, d in (("client", cl), ("server", sv)):
    for t, db in d.items():
        ids = [r[0] for r in db.rows]
        (fail if len(ids) != len(set(ids)) else ok)(f"{side} {t}: {len(ids)} rows, unique ids")
        try:
            lib.Dbc(db.to_bytes())
        except Exception as e:
            fail(f"{side} {t} reserialise: {e}")
# no Russian left in new rows
for t, specs in delta.rows.items():
    for sp in specs:
        for v in sp:
            if isinstance(v, str) and lib.has_cyrillic(v):
                fail(f"cyrillic in new {t} row {sp[0]}: {v!r}")
ok("no Cyrillic strings in new rows") if not bad else None
# server/client agreement on shared tables
for t in sv:
    new = set(delta.ids(t))
    if new != {r[0] for r in sv[t].rows} & new or not new <= {r[0] for r in cl[t].rows}:
        fail(f"{t}: new ids differ between client and server")
ok("server and client share the new AreaTable/Map/WorldSafeLocs/AreaTrigger ids")
# referential checks
maps = {r[0] for r in cl["Map"].rows}
newmaps = set(delta.ids("Map"))
at = cl["AreaTable"]; at_ids = {r[0] for r in at.rows}
for sp in delta.rows["AreaTable"]:
    if sp[1] not in maps: fail(f"area {sp[0]} continent {sp[1]} missing")
    if sp[2] and sp[2] not in at_ids: fail(f"area {sp[0]} parent {sp[2]} missing")
    if sp[8] and sp[8] not in {r[0] for r in cl["ZoneMusic"].rows}: fail(f"area {sp[0]} ZoneMusic {sp[8]} missing")
    if sp[9] and sp[9] not in {r[0] for r in cl["ZoneIntroMusicTable"].rows}: fail(f"area {sp[0]} intro {sp[9]} missing")
    if sp[7] and sp[7] not in {r[0] for r in cl["SoundAmbience"].rows}: fail(f"area {sp[0]} ambience {sp[7]} missing")
    if sp[35] and sp[35] not in {r[0] for r in cl["Light"].rows}: fail(f"area {sp[0]} light {sp[35]} missing")
ok("AreaTable references (continent/parent/music/ambience/light)")
bits = [r[3] for r in at.rows if r[3]]
newbits = [sp[3] for sp in delta.rows["AreaTable"] if sp[3]]
clash = [b for b in set(newbits) if bits.count(b) > newbits.count(b)]
(fail if clash else ok)(f"AreaBit collisions with pre-existing areas: {clash}")
lp = {r[0] for r in cl["LightParams"].rows}
for sp in delta.rows.get("Light", []):
    for p in sp[7:15]:
        if p and p not in lp: fail(f"light {sp[0]} params {p} missing")
sky = {r[0] for r in cl["LightSkybox"].rows}
ib = {r[0] for r in cl["LightIntBand"].rows}; fb = {r[0] for r in cl["LightFloatBand"].rows}
for sp in delta.rows.get("LightParams", []):
    if sp[2] and sp[2] not in sky: fail(f"params {sp[0]} sky {sp[2]} missing")
    if not all(sp[0]*18-17+k in ib for k in range(18)): fail(f"params {sp[0]} int bands incomplete")
    if not all(sp[0]*6-5+k in fb for k in range(6)): fail(f"params {sp[0]} float bands incomplete")
ok("Light / LightParams / LightSkybox / bands")
wma = {r[0] for r in cl["WorldMapArea"].rows}
for sp in delta.rows.get("WorldMapOverlay", []):
    if sp[1] not in wma: fail(f"overlay {sp[0]} wma {sp[1]}")
    for a in sp[2:6]:
        if a and a not in at_ids: fail(f"overlay {sp[0]} area {a}")
for sp in delta.rows.get("AreaPOI", []):
    if sp[17] and sp[17] not in at_ids: fail(f"poi {sp[0]} area {sp[17]}")
ok("WorldMapOverlay / AreaPOI references")
# archives: every new map has WDT + ADT area ids inside the new area set
arch = {}
for p in (S / "client").glob("*.MPQ"):
    h = lib.open_ro(p); arch[p.name] = {lib.norm(n): n for n, _ in lib.list_archive(h) if not n.startswith("(")}; arch[p.name]["_h"] = h
allfiles = {}
for k, v in arch.items():
    for n, orig in v.items():
        if n != "_h": allfiles[n] = (k, orig)
newareas = set(delta.ids("AreaTable"))
for sp in delta.rows["Map"]:
    d = sp[1]; wdt = f"world/maps/{d.lower()}/{d.lower()}.wdt"
    (ok if wdt in allfiles else fail)(f"map {sp[0]} '{d}' WDT in staged archives" if wdt in allfiles else f"map {sp[0]} '{d}' missing {wdt}")
    tiles = [n for n in allfiles if n.startswith(f"world/maps/{d.lower()}/") and n.endswith(".adt")]
    for n in tiles:
        k, orig = allfiles[n]
        data = lib.read_member(arch[k]["_h"], orig)
        ids = closure.adt_area_ids(data) - {0}
        stray = ids - newareas - set(range(1, 4000))  # stock ids (<4000) are fine
        if stray: fail(f"{n} area ids not imported: {sorted(stray)[:6]}")
    print(f"     map {sp[0]} '{d}': {len(tiles)} tiles")
# stock-path rule: no staged path is under a stock map dir or already exists in the client
cf = lib.ClientFiles(C.CLIENT_DATA, Path(sys.argv[1])).open()
stock_dirs = ("world/maps/azeroth/", "world/maps/kalimdor/", "world/maps/expansion01/", "world/maps/northrend/", "world/maps/outland/")
viol = [n for n in allfiles if n.startswith(stock_dirs)]
(fail if viol else ok)(f"no staged file under stock continent map dirs ({len(viol)})")
dup = [n for n in allfiles if cf.has(n) and not n.startswith("dbfilesclient/") and not n.endswith(".trs")]
(fail if dup else ok)(f"no staged path already exists in the current client ({len(dup)} found)")
for n in dup[:10]: print("      ", n)
names = sorted([p.name.lower() for p in C.CLIENT_DATA.glob("*.[mM][pP][qQ]")] + [p.name.lower() for p in (C.CLIENT_DATA / "enUS").glob("*.[mM][pP][qQ]")])
mine = {p.name.lower() for p in (S / "client").glob("*.MPQ")}
others = [n for n in names if n not in mine and n.startswith("patch-")]  # base archives (patch.mpq, speech-*) always load first
dbc_name = "patch-zzzzzzzzzzzzzzzzzzzzzzzzzzmapsimportdbc.mpq"
late = [n for n in others if n > dbc_name]
(fail if late else ok)(f"DBC archive name sorts after every existing archive (later: {late})")
print("RESULT:", "FAIL" if bad else "PASS", f"({bad} failures)")
