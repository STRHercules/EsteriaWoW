"""Every retail file the garrison needs, taken from the local retail client first and the CDN second, packed for the
client as originals.

    python retail_assets.py collect <cache dir> [--seeds file...]   # closure from the six garrison WDTs (+ seeds)
    python retail_assets.py pack <cache dir> <out MPQ>              # EsteriaRetail\\<scope>\\<locale>\\<fdid>.bin

collect starts at the tier WDTs (retail Map.db2 WdtFileDataID) and follows what each file names by FileDataID: WDT
MPHD/MAID (ADT root, obj0, obj1, tex0, lod, map and minimap textures, WDL, lights, fog, occlusion), obj MDDF/MODF
placements, tex0 MDID/MHID, WMO groups/materials/doodads, and M2 skins/textures/skeletons/animations/particles.
--seeds adds every `retail\\<id>.m2|.wmo|.blp` named in the given files (the garrison client DBCs, the addon).

Files come out of RetailAssetProbe --extract-batch: once with a local-mode config on the installed client
(T:\\World of Warcraft), then with the client's online config for whatever the install lacks. pack writes them
under the key Engine/Source/Retail/CascSource.cpp Fetch reads before the CDN, like mod-esteria-housing's
retail_decor.py pack.
"""
import argparse
import re
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "mod-esteria-housing" / "tools"))
from retail_decor import chunks, references, wmo_references, words  # noqa: E402

PROBE = Path(r"R:\Users\Zach\Documents\GitHub\wowdecomp\build\retail-satchel\Release\RetailAssetProbe.exe")
INSTALL = Path(r"T:\World of Warcraft")
ONLINE_DIR = Path(r"G:\3.3.5a - Dev\Data\Retail")  # RetailCasc.ini there streams the pinned build from the CDN
SCOPE, LOCALE = "wow-88d5e8ef05ec5a8446cdec93d142d7c6", 2  # must match Data/Retail/RetailCasc.ini build and locale
# map id: retail WdtFileDataID (Map.db2 field 21, read from the installed client 2026-11-16)
WDTS = {1152: 876612, 1153: 876623, 1158: 879512, 1159: 879360, 1330: 1001652, 1331: 1001653}


def wdt_refs(c):
    found = []
    for blob in c.get(b"DHPM", []):  # MPHD: flags, lgt, occ, fogs, mpv, tex, wdl, pd4
        found += words(blob[4:32])
    for blob in c.get(b"DIAM", []):  # MAID: 4096 x (root, obj0, obj1, tex0, lod, map, mapN, minimap)
        found += words(blob)
    for blob in c.get(b"FDOM", []):  # MODF (global WMO), FileDataID when flag 0x8
        for k in range(0, len(blob) - 63, 64):
            if struct.unpack_from("<H", blob, k + 56)[0] & 0x8:
                found.append(struct.unpack_from("<I", blob, k)[0])
    return found


def adt_refs(c, names):
    found = []
    for blob in c.get(b"DIDM", []) + c.get(b"DIHM", []):  # tex0 MDID diffuse / MHID height
        found += words(blob)
    for blob in c.get(b"FDDM", []):  # MDDF 36-byte placements, FileDataID when flag 0x40
        for k in range(0, len(blob) - 35, 36):
            if struct.unpack_from("<H", blob, k + 34)[0] & 0x40:
                found.append(struct.unpack_from("<I", blob, k)[0])
            else:
                names.add(("mmdx", struct.unpack_from("<I", blob, k)[0]))
    for blob in c.get(b"FDOM", []):  # MODF 64-byte placements, FileDataID when flag 0x8
        for k in range(0, len(blob) - 63, 64):
            if struct.unpack_from("<H", blob, k + 56)[0] & 0x8:
                found.append(struct.unpack_from("<I", blob, k)[0])
            else:
                names.add(("mwmo", struct.unpack_from("<I", blob, k)[0]))
    # shortcut: lod ADTs (MLDD/MLMD placements) are fetched but not followed; they place the obj ADTs' models
    return found


def refs(data, unresolved):
    """FileDataIDs a retail file names."""
    if data[:4] in (b"MD21", b"SKB1", b"SKS1", b"SKA1", b"SKPD", b"SKL1", b"SKID"):
        return [v for v, _ in references(data)]
    if data[:4] != b"REVM":
        return []  # BLP, skins, anims and the rest name nothing further
    c = chunks(data)
    if b"DHPM" in c:
        return wdt_refs(c)
    if b"DHOM" in c:
        return [v for v, _ in wmo_references(data)]
    return adt_refs(c, unresolved)


def extract(config_dir, ini, names, out):
    """RetailAssetProbe --extract-batch; returns the names that failed."""
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
        f.write("\n".join(names) + "\n")
        listing = f.name
    r = subprocess.run([str(PROBE), ini, "--extract-batch", listing, str(out)], cwd=config_dir, capture_output=True, text=True)
    Path(listing).unlink()
    failed = [line.split()[1].rstrip(":") for line in r.stdout.splitlines() if line.startswith("fail ")]
    if r.returncode and not failed:
        raise SystemExit(f"probe failed: {r.stderr.strip() or r.stdout[-500:]}")
    return failed


def collect(cache, seed_files):
    cache = Path(cache)
    cache.mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix="garrison_local_"))  # no Data\ above it, so the probe opens no client MPQs
    (work / "Local.ini").write_text(f"mode=local\npath={INSTALL.as_posix()}\nproduct=wow\nlocale={LOCALE}\n")
    todo = set(WDTS.values())
    for seed in seed_files or []:
        text = Path(seed).read_bytes().decode("latin1")
        todo |= {int(m) for m in re.findall(r"(?:retail[\\/])?(\d{4,})\.(?:m2|wmo|blp)", text, re.I)}
    seen, missing, unresolved = set(), set(), set()
    while todo:
        batch = sorted(f for f in todo if f not in seen)
        seen.update(batch)
        todo = set()
        names = [f"retail/{f}.bin" for f in batch if not (cache / f"{f}.bin").exists()]
        if names:
            failed = extract(work, "Local.ini", names, cache)
            if failed:
                print(f"  {len(failed)} not in the local install, trying the CDN")
                failed = extract(ONLINE_DIR, "RetailCasc.ini", failed, cache)
            missing |= {int(re.search(r"(\d+)", n).group(1)) for n in failed}
        for f in batch:
            path = cache / f"{f}.bin"
            if path.exists():
                todo |= {v for v in refs(path.read_bytes(), unresolved) if v > 0 and v not in seen}
        print(f"level done: {len(seen)} named, {len(seen) - len(missing)} on disk, {len(missing)} missing")
    have = sorted(f for f in seen if (cache / f"{f}.bin").exists())
    (cache / "manifest.txt").write_text("\n".join(map(str, have)) + "\n", encoding="utf-8")
    (cache / "missing.txt").write_text("\n".join(map(str, sorted(missing))) + "\n", encoding="utf-8")
    size = sum((cache / f"{f}.bin").stat().st_size for f in have)
    print(f"{len(have)} files, {size >> 20} MiB in {cache}; {len(missing)} missing; "
          f"{len(unresolved)} placements by name (not FileDataID) left unresolved")


def pack(cache, out):
    sys.path.insert(0, r"R:\Users\Zach\Documents\GitHub\EsteriaWoW\tools")
    from cars_mount_pack import Storm  # noqa: E402
    from make_slice import STORMLIB  # noqa: E402
    cache, out = Path(cache), Path(out)
    mipped = cache.parent / "retail-mipped"  # ui_mips.py: the same UI textures with a mip chain, preferred
    files = {f"EsteriaRetail\\{SCOPE}\\{LOCALE}\\{f}.bin": ((mipped if (mipped / f"{f}.bin").exists() else cache) / f"{f}.bin").read_bytes()
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


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("collect")
    c.add_argument("cache")
    c.add_argument("--seeds", nargs="*")
    p = sub.add_parser("pack")
    p.add_argument("cache")
    p.add_argument("out")
    a = ap.parse_args()
    collect(a.cache, a.seeds) if a.cmd == "collect" else pack(a.cache, a.out)


if __name__ == "__main__":
    main()
