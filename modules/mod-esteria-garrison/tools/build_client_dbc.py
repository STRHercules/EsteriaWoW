"""Build the garrison client DBC patch on top of whatever Esteria's client already loads, adding rows and changing none.

    python build_client_dbc.py [--client "G:/3.3.5a - Dev"] [--world garrison_verify]

For Map, CreatureDisplayInfo, CreatureModelData and GameObjectDisplayInfo:
  1. Find the copy the client loads (PatchFiles.cpp: patch archives by full path, case-insensitive, highest first).
  2. Take the IDs garrison content uses: the six tier maps, the displays its creature_template_model and
     gameobject_template rows name (read from a world database holding sql/world/garrison_world.sql), and the
     models those displays name.
  3. IDs the client already has are left alone. The rest are copied from data/client_dbc_source (the UWoW port's
     DBCs); an ID found in neither is an error.
  4. Write the winner plus the new rows to Data/<PATCH> (28 Zs: sorts above Patch-...27 Zs...CoAMapsDbc.MPQ) and check
     every original row survives unchanged.
It also writes sql/world/garrison_dbc_world.sql: the same new rows for the server's *_dbc override tables, which the
worldserver needs to accept those displays and maps.
"""
import argparse
import struct
import subprocess
import sys
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1]
SOURCE = MODULE / "data" / "client_dbc_source"
SQL_OUT = MODULE / "sql" / "world" / "garrison_dbc_world.sql"
SEEDS = MODULE / "data" / "client_dbc_seeds.txt"
PATCH = "Patch-ZZZZZZZZZZZZZZZZZZZZZZZZZZZZGarrison.MPQ"
sys.path.insert(0, r"R:\Users\Zach\Documents\GitHub\EsteriaWoW\tools")
sys.path.insert(0, str(MODULE.parent / "mod-esteria-housing" / "tools"))
from cars_mount_pack import Storm  # noqa: E402
from make_slice import STORMLIB  # noqa: E402

MAPS = [1152, 1153, 1158, 1159, 1330, 1331]
# table: (string field indexes, server override table)
TABLES = {
    "Map": (sorted({1} | set(range(5, 21)) | set(range(23, 39)) | set(range(40, 56))), "map_dbc"),
    "CreatureDisplayInfo": ([6, 7, 8, 9], "creaturedisplayinfo_dbc"),
    "CreatureModelData": ([2], "creaturemodeldata_dbc"),
    "GameObjectDisplayInfo": ([1], "gameobjectdisplayinfo_dbc"),
}
DOCKER = ["docker", "exec", "-i", "-e", "MYSQL_PWD=password", "ac-database", "mysql", "-uroot", "-N", "-B"]


def mysql(sql):
    r = subprocess.run(DOCKER, input=sql, capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(r.stderr)
    return [line.split("\t") for line in r.stdout.splitlines() if line]


class Dbc:
    def __init__(self, data, strings):
        assert data[:4] == b"WDBC", "not a WDBC file"
        count, self.fields, self.size, slen = struct.unpack_from("<4I", data, 4)
        self.rows = {}
        self.order = []
        for i in range(count):
            row = data[20 + i * self.size:20 + (i + 1) * self.size]
            rid = struct.unpack_from("<I", row)[0]
            self.rows[rid] = row
            self.order.append(rid)
        self.blob = bytearray(data[20 + count * self.size:20 + count * self.size + slen])
        self.strings = strings

    def text(self, row, field):
        off = struct.unpack_from("<I", row, field * 4)[0]
        return bytes(self.blob[off:self.blob.index(b"\0", off)])

    def values(self, rid):
        """The row with its strings resolved, for comparing rows across files."""
        row = self.rows[rid]
        return tuple(self.text(row, f) if f in self.strings else row[f * 4:f * 4 + 4] for f in range(self.fields))

    def add(self, other, rid):
        row = bytearray(other.rows[rid])
        for f in self.strings:
            text = other.text(row, f)
            if text:
                struct.pack_into("<I", row, f * 4, len(self.blob))
                self.blob += text + b"\0"
            else:
                struct.pack_into("<I", row, f * 4, 0)
        self.rows[rid] = bytes(row)
        self.order.append(rid)

    def bytes(self):
        body = b"".join(self.rows[r] for r in self.order)
        return b"WDBC" + struct.pack("<4I", len(self.order), self.fields, self.size, len(self.blob)) + body + bytes(self.blob)


def winners(storm, client):
    data = Path(client) / "Data"
    found = [(f"data\\{p.name.lower()}", p) for p in data.glob("*") if p.name.lower().startswith("patch-") and p.suffix.lower() == ".mpq"]
    found += [(f"data\\enus\\{p.name.lower()}", p) for p in (data / "enUS").glob("*")
              if p.name.lower().startswith("patch-enus-") and p.suffix.lower() == ".mpq"]
    out = {}
    for _, archive in sorted(found, reverse=True):
        if archive.name.lower() == PATCH.lower():
            continue
        handle = storm.open_archive(archive)
        try:
            for name in TABLES:
                if name not in out:
                    try:
                        out[name] = (archive.name, storm.read(handle, f"DBFilesClient\\{name}.dbc"))
                    except OSError:
                        pass
        finally:
            storm.dll.SFileCloseArchive(handle)
        if len(out) == len(TABLES):
            return out
    raise SystemExit(f"no patch archive holds {sorted(set(TABLES) - set(out))}")


def wanted(world, source_display):
    creature = {int(r[0]) for r in mysql(f"SELECT DISTINCT CreatureDisplayID FROM {world}.creature_template_model WHERE CreatureDisplayID > 0")}
    gameobject = {int(r[0]) for r in mysql(f"SELECT DISTINCT displayId FROM {world}.gameobject_template WHERE displayId > 0")}
    return {"Map": set(MAPS), "CreatureDisplayInfo": creature, "GameObjectDisplayInfo": gameobject}


def sql_rows(table, columns, dbc, added):
    out = []
    for rid in added:
        row = dbc.rows[rid]
        vals = []
        for f, (name, ctype) in enumerate(columns):
            if f in dbc.strings:
                vals.append("'" + dbc.text(row, f).decode("utf-8", "replace").replace("\\", "\\\\").replace("'", "''") + "'")
            elif ctype.startswith(("float", "double")):
                vals.append(repr(round(struct.unpack_from("<f", row, f * 4)[0], 6)))
            elif "unsigned" in ctype:
                vals.append(str(struct.unpack_from("<I", row, f * 4)[0]))
            else:
                vals.append(str(struct.unpack_from("<i", row, f * 4)[0]))
        out.append("(" + ",".join(vals) + ")")
    cols = ",".join(f"`{c}`" for c, _ in columns)
    return f"REPLACE INTO `{table}` ({cols}) VALUES\n" + ",\n".join(out) + ";"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--client", default=r"G:\3.3.5a - Dev")
    ap.add_argument("--world", default="garrison_verify", help="a database holding garrison_world.sql's rows")
    ap.add_argument("--live", default="acore_world", help="the server world database (its *_dbc tables)")
    a = ap.parse_args()
    storm = Storm(STORMLIB)
    win = winners(storm, a.client)
    source = {n: Dbc((SOURCE / f"{n}.dbc").read_bytes(), TABLES[n][0]) for n in TABLES}
    base = {n: Dbc(win[n][1], TABLES[n][0]) for n in TABLES}
    want = wanted(a.world, source["CreatureDisplayInfo"])
    # models the needed displays name (field 1 ModelID), whichever file supplies the display
    want["CreatureModelData"] = set()
    for d in want["CreatureDisplayInfo"]:
        holder = base["CreatureDisplayInfo"] if d in base["CreatureDisplayInfo"].rows else source["CreatureDisplayInfo"]
        if d in holder.rows:
            want["CreatureModelData"].add(struct.unpack_from("<I", holder.rows[d], 4)[0])
    added, problems = {}, []
    for n in TABLES:
        b, s = base[n], source[n]
        assert (b.fields, b.size) == (s.fields, s.size), f"{n}: layout differs"
        new, differ = [], []
        for rid in sorted(want[n]):
            if rid in b.rows:
                if rid in s.rows and b.values(rid) != s.values(rid):
                    differ.append(rid)
            elif rid in s.rows:
                new.append(rid)
            else:
                problems.append(f"{n} {rid}: in neither the client nor the UWoW source")
        before = {rid: b.values(rid) for rid in b.order}
        for rid in new:
            b.add(s, rid)
        assert all(b.values(rid) == v for rid, v in before.items()), f"{n}: an existing row changed"
        added[n] = new
        print(f"{n}: winner {win[n][0]} ({len(before)} rows); garrison uses {len(want[n])}; "
              f"{len(want[n]) - len(new)} already in Esteria (kept as is, {len(differ)} differ from UWoW); +{len(new)} added")
        if differ:
            print(f"   kept Esteria's rows for {differ[:15]}{' ...' if len(differ) > 15 else ''}")
    if problems:
        print("\n".join(problems[:30]))
        raise SystemExit(f"{len(problems)} ids have no row")
    out = Path(a.client) / "Data" / PATCH
    files = {f"DBFilesClient\\{n}.dbc": base[n].bytes() for n in TABLES}
    if out.exists():
        out.unlink()
    storm.create_archive(out, files)
    handle = storm.open_archive(out)
    try:
        for name, data in files.items():
            assert storm.read(handle, name) == data, f"read-back mismatch {name}"
    finally:
        storm.dll.SFileCloseArchive(handle)
    print(f"wrote {out}")
    # the model and texture names of the added rows: retail_assets.py collect --seeds follows them
    seeds = sorted({base[n].text(base[n].rows[rid], f).decode("latin1") for n in TABLES if n != "Map"
                    for rid in added[n] for f in TABLES[n][0]} - {""})
    SEEDS.write_text("\n".join(seeds) + "\n", encoding="utf-8")
    print(f"wrote {SEEDS} ({len(seeds)} names)")
    # server override rows for the same new IDs; skip any the server already has in its table
    parts = ["-- Generated by modules/mod-esteria-garrison/tools/build_client_dbc.py: the rows the garrison client patch adds,",
             "-- for the worldserver's *_dbc override tables. Every ID was absent from the client DBCs and these tables.", ""]
    for n, (strings, table) in TABLES.items():
        ids = added[n]
        if not ids:
            continue
        taken = {int(r[0]) for r in mysql(f"SELECT ID FROM {a.live}.{table} WHERE ID IN ({','.join(map(str, ids))})")}
        ids = [i for i in ids if i not in taken]
        if taken:
            print(f"{table}: {len(taken)} ids already in the server table, left alone")
        cols = [(c, t) for c, t in mysql(f"SELECT column_name, column_type FROM information_schema.columns WHERE table_schema='{a.live}' "
                                          f"AND table_name='{table}' ORDER BY ordinal_position")]
        assert len(cols) == base[n].fields, f"{table} has {len(cols)} columns, {n}.dbc {base[n].fields} fields"
        if ids:
            parts += [sql_rows(table, cols, base[n], ids), ""]
    SQL_OUT.write_text("\n".join(parts) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {SQL_OUT}")


if __name__ == "__main__":
    main()
