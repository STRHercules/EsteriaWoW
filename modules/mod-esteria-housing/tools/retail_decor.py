"""Retail decor our pinned CASC build lacks, and the WMO decor it has: the catalog rows and the files to ship.

    python retail_decor.py select <community listfile.csv>         # writes data/catalog3.tsv (decor_id, model_fdid,
                                                                    # category, kind, packed); kind m2 or wmo
    python retail_decor.py fetch <cache dir>                        # downloads every packed=1 row's files (wago.tools)
    python retail_decor.py pack <cache dir> <out MPQ>               # EsteriaRetail\\<scope>\\<locale>\\<fdid>.bin
    python retail_decor.py fetch-wmo <cache dir> <root fdid>...     # a building's WMO root, groups, textures, doodads
                                                                    # (house exteriors newer than our build)

data/house_decor.csv is retail HouseDecor (wago.tools, live). A decor our build lacks (not in wowdecomp
docs/housing/existing-assets.tsv, the pinned build's HouseDecor) has packed=1: its model and everything the model
names by FileDataID (skins, textures, skeleton chain, animations, bones, particle and child models) are fetched as retail originals and packed under the key the client's CascSource reads before
the CDN (Engine/Source/Retail/CascSource.cpp Fetch), so they load although the pinned build has never heard of them.
[DNT] and test decor are left out. RetailAssetProbe --batch then says which models load; make_slice.py appends the
rows (block 2) after catalog2.tsv's.
"""
import concurrent.futures
import csv
import os
import struct
import sys
import urllib.request
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1]
INVENTORY = Path(r"R:\Users\Zach\Documents\GitHub\wowdecomp\docs\housing\existing-assets.tsv")
SCOPE, LOCALE = "wow-88d5e8ef05ec5a8446cdec93d142d7c6", 2  # Data/Retail/RetailCasc.ini product-build and locale
CATALOG3 = MODULE / "data/catalog3.tsv"

LIGHT = ["light", "lamp", "lantern", "candle", "torch", "brazier", "fireplace", "sconce", "chandelier"]
NATURE = ["tree", "plant", "flower", "grass", "bush", "foliage", "mushroom", "vine", "boulder", "rock", "shrub", "fern"]
STRUCT = ["wall", "pillar", "column", "door", "window", "fence", "gate", "roof", "beam", "gazebo", "stair", "arch", "floor"]
FURN = ["chair", "table", "desk", "bed", "shelf", "cabinet", "couch", "sofa", "bench", "stool", "rug", "dresser", "wardrobe", "throne"]
ACC = ["book", "banner", "curtain", "painting", "portrait", "statue", "ornament", "vase", "trophy", "food", "crate", "barrel",
       "pot", "basket", "bottle", "candle"]


def category(text, decor_type):
    """As wowdecomp docs/housing/tools/inventory.py names the Phase 0 inventory's categories."""
    text = text.lower()
    for name, tokens in (("Lighting", LIGHT), ("Nature", NATURE), ("Furniture", FURN), ("Structural", STRUCT), ("Accents", ACC)):
        if any(t in text for t in tokens):
            return name
    return "Accents" if decor_type == "4" else "Misc"


def is_dnt(name):
    return "[DNT]" in name or "do not use" in name.lower() or name.lower().startswith("test")


def select(listfile):
    paths = {}
    for line in open(listfile, encoding="utf-8", errors="replace"):
        i, _, p = line.rstrip().partition(";")
        paths[i] = p
    ours = {r["decor_id"]: r for r in csv.DictReader(INVENTORY.open(encoding="utf-8"), delimiter="\t")}
    rows = []
    for r in csv.DictReader((MODULE / "data/house_decor.csv").open(encoding="utf-8")):
        fdid, name = r["ModelFileDataID"], r["Name_lang"].strip()
        if is_dnt(name) or not name or fdid in ("", "0") or r["ModelType"] not in ("1", "2"):
            continue
        kind = "wmo" if r["ModelType"] == "2" else "m2"
        if r["ID"] in ours and kind == "m2":
            continue  # in our build: catalog() or catalog2.tsv has it, or the probe refused it
        rows.append((r["ID"], fdid, category(name + " " + paths.get(fdid, ""), r["Type"]), kind, int(r["ID"] not in ours)))
    with CATALOG3.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter="\t", lineterminator="\n")
        w.writerow(["decor_id", "model_fdid", "category", "kind", "packed"])
        w.writerows(rows)
    print(f"{len(rows)} decor -> {CATALOG3}: {sum(r[4] for r in rows)} to fetch, {sum(r[3] == 'wmo' for r in rows)} WMO")


# ------------------------------------------------------------------------------------------------ fetching


def chunks(data):
    out, i = {}, 0
    while i + 8 <= len(data):
        tag, size = data[i:i + 4], struct.unpack_from("<I", data, i + 4)[0]
        out.setdefault(tag, []).append(data[i + 8:i + 8 + size])
        i += 8 + size
    return out


def words(data, stride=4, at=0):
    return [struct.unpack_from("<I", data, k + at)[0] for k in range(0, len(data) - stride + 1, stride)]


def references(data):
    """Every FileDataID an M2 or .skel names, with the kind each is (m2, skel or other). shortcut: no WMO roots; every
    WMO decor is in our build (select), so none is fetched."""
    found = []
    if data[:4] == b"MD21":  # chunked M2
        c = chunks(data)
        for tag in (b"SFID", b"TXID", b"BFID"):
            found += [(v, "other") for blob in c.get(tag, []) for v in words(blob)]
        found += [(v, "other") for blob in c.get(b"AFID", []) for v in words(blob, 8, 4)]  # anim id, sub id, fdid
        found += [(v, "skel") for blob in c.get(b"SKID", []) for v in words(blob)]
        found += [(v, "other") for blob in c.get(b"PFID", []) for v in words(blob)]
        found += [(v, "m2") for tag in (b"RPID", b"GPID") for blob in c.get(tag, []) for v in words(blob)]
    elif data[:4] in (b"SKB1", b"SKS1", b"SKA1", b"SKPD", b"SKL1", b"SKID"):  # .skel
        c = chunks(data)
        found += [(v, "skel") for blob in c.get(b"SKPD", []) for v in words(blob[8:12])]
        found += [(v, "other") for blob in c.get(b"AFID", []) for v in words(blob, 8, 4)]
        found += [(v, "other") for blob in c.get(b"BFID", []) for v in words(blob)]
    return [(v, kind) for v, kind in found if v]


def download(fdid, cache):
    path = cache / f"{fdid}.bin"
    if path.exists():
        return path.read_bytes()
    request = urllib.request.Request(f"https://wago.tools/api/casc/{fdid}?download", headers={"User-Agent": "Mozilla/5.0"})
    try:
        data = urllib.request.urlopen(request, timeout=120).read()
    except Exception as e:  # noqa: BLE001 (a missing or encrypted file stays missing; the probe says which model fails)
        print(f"  {fdid}: {e}", file=sys.stderr)
        return None
    path.write_bytes(data)
    return data


def fetch(cache):
    cache = Path(cache)
    cache.mkdir(parents=True, exist_ok=True)
    rows = [r for r in csv.DictReader(CATALOG3.open(encoding="utf-8"), delimiter="\t") if r["packed"] == "1"]
    house = {r["ID"]: r for r in csv.DictReader((MODULE / "data/house_decor.csv").open(encoding="utf-8"))}
    todo = [int(r["model_fdid"]) for r in rows]
    todo += [int(house[r["decor_id"]]["ThumbnailFileDataID"]) for r in rows if house[r["decor_id"]]["ThumbnailFileDataID"] not in ("", "0")]
    seen, failed = set(), set()
    with concurrent.futures.ThreadPoolExecutor(8) as pool:
        while todo:
            batch = [f for f in dict.fromkeys(todo) if f not in seen]
            seen.update(batch)
            todo = []
            for fdid, data in zip(batch, pool.map(lambda f: download(f, cache), batch)):
                if data is None:
                    failed.add(fdid)
                    continue
                todo += [v for v, _kind in references(data)]
            print(f"  fetched {len(seen) - len(failed)} files so far")
    (cache / "manifest.txt").write_text("\n".join(str(f) for f in sorted(seen - failed)) + "\n", encoding="utf-8")
    print(f"{len(seen) - len(failed)} files in {cache} ({len(failed)} unavailable)")


def wmo_references(data):
    """The FileDataIDs a WMO root names: its groups (GFID), material textures (MOMT texture_1..3 and the runtime
    texture slots shaders use) and doodads (MODI). Chunk tags are stored reversed."""
    c = chunks(data)
    found = [(v, "other") for blob in c.get(b"DIFG", []) for v in words(blob)]
    for blob in c.get(b"TMOM", []):
        for k in range(0, len(blob) - 63, 64):
            found += [(struct.unpack_from("<I", blob, k + at)[0], "other") for at in (12, 24, 36, 48, 52, 56, 60)]
    found += [(v, "m2") for blob in c.get(b"IDOM", []) for v in words(blob)]
    return [(v, kind) for v, kind in found if v > 1000]  # small values in the runtime slots are not files


def fetch_wmo(cache, roots):
    """Like fetch, for building models (house exteriors): each root, its groups, textures and doodads (and theirs)."""
    cache = Path(cache)
    cache.mkdir(parents=True, exist_ok=True)
    todo, seen, failed = [(int(r), "wmo") for r in roots], set(), set()
    while todo:
        batch = [(f, k) for f, k in dict.fromkeys(todo) if f not in seen]
        seen.update(f for f, _ in batch)
        todo = []
        for (fdid, kind), data in zip(batch, map(lambda b: download(b[0], cache), batch)):
            if data is None:
                failed.add(fdid)
                continue
            todo += wmo_references(data) if kind == "wmo" else references(data)
        print(f"  fetched {len(seen) - len(failed)} files so far")
    (cache / "manifest.txt").write_text("\n".join(str(f) for f in sorted(seen - failed)) + "\n", encoding="utf-8")
    print(f"{len(seen) - len(failed)} files in {cache} ({len(failed)} unavailable: {sorted(failed)[:20]})")


def pack(cache, out):
    sys.path.insert(0, r"R:\Users\Zach\Documents\GitHub\EsteriaWoW\tools")
    from cars_mount_pack import Storm  # noqa: E402
    sys.path.insert(0, str(Path(__file__).parent))
    from make_slice import STORMLIB  # noqa: E402
    cache, out = Path(cache), Path(out)
    files = {f"EsteriaRetail\\{SCOPE}\\{LOCALE}\\{f}.bin": (cache / f"{f}.bin").read_bytes()
             for f in (cache / "manifest.txt").read_text(encoding="utf-8").split()}
    storm = Storm(STORMLIB)
    if out.exists():
        out.unlink()
    storm.create_archive(out, files)
    handle = storm.open_archive(out)
    try:
        for name, data in files.items():
            assert storm.read(handle, name) == data, f"read-back mismatch: {name}"
    finally:
        storm.dll.SFileCloseArchive(handle)
    print(f"wrote {out}: {len(files)} files, {sum(map(len, files.values())) >> 20} MiB")


if __name__ == "__main__":
    {"select": lambda: select(sys.argv[2]), "fetch": lambda: fetch(sys.argv[2]),
     "fetch-wmo": lambda: fetch_wmo(sys.argv[2], sys.argv[3:]),
     "pack": lambda: pack(sys.argv[2], sys.argv[3])}[sys.argv[1]]()
