"""Stage the Shadowlands-to-WOTLK Vulpera port into PATCH-X."""
from __future__ import annotations
import datetime, gc, os, shutil, struct, sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "tools"))
from cars_mount_pack import DLL_DEFAULT, Storm

B = chr(92)
PORT = Path(r"G:\\Downloads\\Shadowland-to-WOTLK-port-main\\Character\\Vulpera")
DATA = REPO / "3.3.5a - Dev" / "Data"
LIVE = DATA / "PATCH-X.MPQ"
STAGE = REPO / "var" / "slport-x"
DBC_ENTRY = B.join(["DBFilesClient", "CreatureModelData.dbc"])
MODEL_PATHS = {
    112885: B.join(["character", "vulpera", "male", "vulperamale.m2"]),
    112886: B.join(["character", "vulpera", "female", "vulperafemale.m2"]),
}


def repath_dbc(data, replacements):
    magic, count, fields, rec_size, str_size = struct.unpack_from("<4sIIII", data, 0)
    records_end = 20 + count * rec_size
    rows = {}
    for i in range(count):
        rec = 20 + i * rec_size
        rows[struct.unpack_from("<I", data, rec)[0]] = rec
    missing = sorted(set(replacements) - set(rows))
    if missing:
        raise ValueError("model rows absent: %s" % missing)
    added = bytearray()
    offsets = {}
    for path in replacements.values():
        if path in offsets:
            continue
        offsets[path] = str_size + len(added)
        added.extend(path.encode("ascii"))
        added.append(0)
    out = bytearray(data)
    for rid, path in replacements.items():
        struct.pack_into("<I", out, rows[rid] + 8, offsets[path])
    header = struct.pack("<4sIIII", magic, count, fields, rec_size, str_size + len(added))
    return bytes(header + bytes(out[20:records_end]) + bytes(data[records_end:]) + bytes(added))


def main():
    entries = {}
    for g in ("Male", "Female"):
        for f in sorted((PORT / g).iterdir()):
            if f.is_file():
                entries[B.join(["character", "vulpera", g.lower(), f.name])] = f.read_bytes()
    print("port files: %d (%.1f MB)" % (len(entries), sum(len(v) for v in entries.values()) / 1e6))
    if STAGE.exists():
        shutil.rmtree(STAGE, ignore_errors=True)
    STAGE.mkdir(parents=True)
    staged = STAGE / LIVE.name
    print("copying PATCH-X (%.0f MB)" % (LIVE.stat().st_size / 1e6))
    shutil.copy2(LIVE, staged)
    storm = Storm(DLL_DEFAULT)
    handle = storm.open_archive(staged)
    try:
        table = storm.read(handle, DBC_ENTRY)
    finally:
        storm.dll.SFileCloseArchive(handle)
    payload = dict(entries)
    payload[DBC_ENTRY] = repath_dbc(table, MODEL_PATHS)
    print("writing entries...")
    storm.replace_archive_entries(staged, payload)
    del storm
    gc.collect()
    chk = Storm(DLL_DEFAULT)
    h2 = chk.open_archive(staged)
    try:
        names = {n.casefold(): n for n, *_ in chk.list_files(h2)}
        raw = chk.read(h2, DBC_ENTRY)
    finally:
        chk.dll.SFileCloseArchive(h2)
    del chk
    gc.collect()
    for k in MODEL_PATHS.values():
        if k.casefold() not in names:
            raise SystemExit("VERIFY FAIL missing %s" % k)
    magic, count, fields, rec_size, str_size = struct.unpack_from("<4sIIII", raw, 0)
    base = 20 + count * rec_size
    for i in range(count):
        rec = 20 + i * rec_size
        rid = struct.unpack_from("<I", raw, rec)[0]
        if rid in MODEL_PATHS:
            off = struct.unpack_from("<I", raw, rec + 8)[0]
            got = raw[base + off:raw.find(bytes([0]), base + off)].decode("ascii")
            if got != MODEL_PATHS[rid]:
                raise SystemExit("VERIFY FAIL row %d -> %s" % (rid, got))
    print("verify: port models present, rows repointed")
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    bk = REPO / "3.3.5a - Dev" / "Backups" / ("patch-x-before-slport-" + stamp)
    bk.mkdir(parents=True, exist_ok=True)
    backup = bk / LIVE.name
    shutil.copy2(LIVE, backup)
    os.replace(staged, LIVE)
    shutil.rmtree(STAGE, ignore_errors=True)
    print("installed PATCH-X (%.0f MB); rollback %s" % (LIVE.stat().st_size / 1e6, backup))


if __name__ == "__main__":
    main()
