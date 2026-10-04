"""Read effective client files, mounted server DBCs and optional database state for the handoff."""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import ntpath
from pathlib import Path
import re
import struct
import subprocess
import sys


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--client", type=Path, default=Path(r"G:\3.3.5a - Dev"))
    parser.add_argument("--work", type=Path, default=Path(r"G:\RetroPorterWork"))
    parser.add_argument("--database", action="store_true", help="Issue SELECT/SHOW queries in ac-database")
    args = parser.parse_args()
    sys.path.insert(0, str(args.server / "tools"))
    import retroported_race_pack as pack

    out = Path(__file__).resolve().parents[1]
    evidence = out / "evidence"
    report = {"client": str(args.client), "server": str(args.server), "dbc": [], "glue": [], "codecs": {}}
    race_table = None
    with pack.ClientFiles(str(args.client / "Data"), "enUS") as client:
        for name in (*pack.SERVER_DBC_TABLES, "CharHairGeosets", "CharacterFacialHairStyles", "CharBaseInfo",
                     "SkillRaceClassInfo", "SkillLineAbility", "SkillLine", "ItemDisplayInfo"):
            data, archive = client.find(f"DBFilesClient\\{name}.dbc")
            table = pack.RawWdbc(data)
            row = {"name": name, "archive": archive, "sha256": digest(data), "records": table.count,
                   "record_size": table.record_size, "bytes": len(data)}
            mounted = args.server / "modules/mod-custom-server/data/dbc/retroported-races" / f"{name}.dbc"
            if name == "SkillRaceClassInfo":
                mounted = args.server / "modules/mod-custom-server/data/dbc/SkillRaceClassInfo.dbc"
            if mounted.is_file():
                server_data = mounted.read_bytes()
                row.update(server_file=str(mounted), server_sha256=digest(server_data),
                           byte_equal_to_server=data == server_data)
                if data != server_data:
                    server_table = pack.RawWdbc(server_data)
                    row.update(server_records=server_table.count,
                               same_record_multiset=Counter(table.records) == Counter(server_table.records),
                               string_pools_equal=table.strings == server_table.strings)
                    if name in {"ChrRaces", "SkillRaceClassInfo"}:
                        string_fields = set(pack.STRING_FIELDS.get(name, ()))

                        def normalized(record, strings):
                            values = struct.unpack(f"<{len(record)//4}I", record)
                            return tuple(strings[v:].split(b"\0", 1)[0].decode("utf-8", errors="replace")
                                         if i in string_fields else v for i, v in enumerate(values))

                        before = {int.from_bytes(r[:4], "little"): normalized(r, server_table.strings)
                                  for r in server_table.records}
                        after = {int.from_bytes(r[:4], "little"): normalized(r, table.strings)
                                 for r in table.records}
                        row["semantic_changes"] = [{"id": key, "server": before.get(key), "client": after.get(key)}
                            for key in sorted(before.keys() | after.keys()) if before.get(key) != after.get(key)]
            if name == "ChrRaces":
                race_table = table
            if name == "CharSections":
                keys = [tuple(int.from_bytes(r[n:n+4], "little") for n in (4, 8, 12, 32, 36))
                        for r in table.records]
                row["native_cache_order_sorted"] = keys == sorted(keys)
                row["race_gender_counts"] = {f"{race}/{gender}": count
                    for (race, gender), count in sorted(Counter(k[:2] for k in keys).items())}
            report["dbc"].append(row)

        key = "Interface\\GlueXML\\GlueXML.toc"
        toc, archive = client.find(key)
        names = {"GlueXML.toc", "CharacterInfo.lua", "CharacterCreate.lua", "CharacterCreate.xml",
                 "CharacterSelect.lua", "CharacterSelect.xml", "GlueParent.lua", "GlueParent.xml",
                 "GlueStrings.lua", "AccountLogin.lua", "AccountLogin.xml"}
        names.update(line.strip() for line in toc.decode("utf-8-sig").splitlines()
                     if not line.strip().startswith("#") and line.strip().endswith((".lua", ".xml")))
        pending = sorted(names)
        done = set()
        while pending:
            name = pending.pop(0)
            if name in done:
                continue
            done.add(name)
            key = ntpath.normpath("Interface\\GlueXML\\" + name)
            try:
                data, archive = client.find(key)
            except FileNotFoundError:
                report["glue"].append({"entry": key, "missing": True})
                continue
            path = out / "sources/client-active" / key.replace("\\", "/")
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
            if name.endswith(".xml"):
                pending.extend(re.findall(r'<(?:Script|Include)\s+file="([^"]+)"', data.decode("utf-8-sig")))
            report["glue"].append({"entry": key, "archive": archive, "bytes": len(data),
                                   "sha256": digest(data), "snapshot": path.relative_to(out).as_posix()})

    def value(record, field):
        return int.from_bytes(record[field*4:field*4+4], "little")

    def text(record, field):
        offset = value(record, field)
        return race_table.strings[offset:].split(b"\0", 1)[0].decode("utf-8", errors="replace")

    report["race_rows"] = [{"id": value(r, 0), "name": text(r, 14), "prefix": text(r, 6),
        "file_string": text(r, 11), "male_display": value(r, 4), "female_display": value(r, 5),
        "team_id": value(r, 7), "faction_id": value(r, 2)} for r in race_table.records]
    for race in sorted(p for p in args.work.iterdir() if p.is_dir()):
        path = race / "integration/codec.json"
        if not path.is_file():
            continue
        codec = json.loads(path.read_text(encoding="utf-8"))
        report["codecs"][race.name] = {
            sex: {"controls": [{"label": o["label"], "choices": len(o["choices"])} for o in p["options"]],
                  "capacities": p.get("capacities"), "descriptors": p.get("descriptors")}
            for sex, p in codec.items() if isinstance(p, dict) and "options" in p}
    report["extension_manifests"] = {}
    for path in sorted((args.client / "Extensions").glob("*/wxl.json")):
        report["extension_manifests"][path.parent.name] = json.loads(path.read_text(encoding="utf-8"))

    if args.database:
        queries = {
            "creation_rows": "SELECT race,COUNT(*) AS starts,GROUP_CONCAT(DISTINCT class ORDER BY class) AS classes "
                             "FROM acore_world.playercreateinfo GROUP BY race ORDER BY race;",
            "appearance_schema": "SHOW COLUMNS FROM acore_characters.characters LIKE 'extraAppearance';",
            "race_overlay_schema": "SHOW COLUMNS FROM acore_world.chrraces_dbc;",
            "recent_world_migrations": "SELECT name,hash,state FROM acore_world.updates "
                "WHERE name REGEXP '20260930|20261001|20261002|20261003|darkfallen' ORDER BY name;",
            "recent_character_migrations": "SELECT name,hash,state FROM acore_characters.updates "
                "WHERE name REGEXP '20260930|20261001|20261002|20261003' ORDER BY name;",
        }
        results = {}
        for name, sql in queries.items():
            command = ["rtk", "proxy", "docker", "exec", "-i", "ac-database", "sh", "-c",
                       'MYSQL_PWD="$MYSQL_ROOT_PASSWORD" mysql -uroot --batch --raw']
            result = subprocess.run(command, input=sql, text=True, capture_output=True)
            results[name] = {"exit_code": result.returncode, "stdout": result.stdout, "stderr": result.stderr}
        columns = {line.split('\t')[0] for line in results['race_overlay_schema']['stdout'].splitlines()[1:]}
        selected = [name for name in ("ID", "Flags", "FactionID", "MaleDisplayID", "FemaleDisplayID",
                    "ClientPrefix", "TeamID", "ClientFileString", "CinematicSequenceID", "Alliance",
                    "Name_Lang_enUS", "ExpansionID") if name in columns]
        if "ID" in selected:
            sql = f"SELECT {','.join('`' + n + '`' for n in selected)} FROM acore_world.chrraces_dbc ORDER BY ID;"
            result = subprocess.run(command, input=sql, text=True, capture_output=True)
            results["race_sql_overlays"] = {"exit_code": result.returncode,
                                          "stdout": result.stdout, "stderr": result.stderr}
        result = subprocess.run(["rtk", "proxy", "docker", "inspect", "ac-worldserver", "--format",
            '{{json .State.Status}} {{json .Image}} {{json .Mounts}}'], text=True, capture_output=True)
        results["worldserver"] = {"exit_code": result.returncode, "stdout": result.stdout, "stderr": result.stderr}
        report["database_readback"] = results
    target = evidence / "current-state.json"
    target.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"dbc": [{"name": d["name"], "records": d["records"],
                              "server_equal": d.get("byte_equal_to_server")} for d in report["dbc"]],
                      "race_rows": len(report["race_rows"]), "glue_snapshots": len(report["glue"]),
                      "codec_controls": {r: {s: len(p["controls"]) for s, p in c.items()}
                                         for r, c in report["codecs"].items()}}, indent=2))


if __name__ == "__main__":
    main()
