"""Wire garrison NPC + town object looks to retail Casc FileDataIDs.

Creature displays 68100+entry offset, model data 69100+…
GO displays 68600+ for cache/mailbox/crate/lamp/banner/architect table.
Paths are retail\\<FileDataID>.m2 — CascSource pulls them from CDN on first sight.
"""
from __future__ import annotations

import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
MODULE = HERE.parent
sys.path.insert(0, str(MODULE.parents[1] / "tools"))
from cars_mount_pack import Storm  # noqa: E402

CLIENT = Path(r"G:\risServer\Esteria - Client")
STORMLIB = CLIENT / "StormLib.dll"
PATCH_NAME = "Patch-ZZZZZZZZZZZZZZZZZZZZZZZZZZGarrison.MPQ"
MAP_DBC = r"DBFilesClient\Map.dbc"
GO_DISPLAY_DBC = r"DBFilesClient\GameObjectDisplayInfo.dbc"
CREATURE_DISPLAY_DBC = r"DBFilesClient\CreatureDisplayInfo.dbc"
CREATURE_MODEL_DBC = r"DBFilesClient\CreatureModelData.dbc"
# worldserver DataDir="." under RelWithDebInfo; also keep env/dist in sync for packaging.
SERVER_DBC_DIRS = (
    MODULE.parents[1] / "build" / "bin" / "RelWithDebInfo" / "dbc",
    MODULE.parents[1] / "env" / "dist" / "data" / "dbc",
)
DISPLAY_ID_MIN, DISPLAY_ID_MAX = 68100, 68400
MODEL_ID_MIN, MODEL_ID_MAX = 69100, 69400

# esteria creature entry -> (model FileDataID, scale, tex11, tex12, tex13)
# tex slots map to ReplaceMonsterSkin variation 0/1/2 -> model slots 11/12/13.
NPC_MODELS = {
    9601101: (1570137, 1.25, 1570258, 1570255, 0),       # Baros
    9601102: (5764885, 1.0, 0, 0, 0),                    # Gazlowe unique
    9601103: (930099, 1.7, 937286, 0, 0),                # Lieutenant Thorn
    9601104: (918944, 1.5, 962560, 962555, 0),           # Warmaster Zog stand-in (orc officer)
    9601105: (1570137, 1.1, 1570258, 1570255, 0),        # Alliance QM — human kit
    9601106: (918944, 1.2, 962560, 962555, 0),           # Horde QM
    9601107: (1721658, 1.15, 1738965, 1738967, 1738966), # Dungar
    9601108: (1339502, 1.1, 1352638, 0, 1352641),        # Wind rider FM
    9601109: (930099, 1.0, 937291, 937283, 0),           # Alliance guard
    9601110: (918944, 1.0, 962560, 962555, 0),           # Horde guard
    9601111: (930099, 1.05, 937290, 937283, 937293),     # Sergeant Crowley
    9601112: (918944, 1.05, 962560, 962555, 0),          # Horde sergeant
    9601120: (1630744, 1.0, 0, 0, 0),                    # Lunarfall innkeeper
    9601121: (918944, 1.0, 962560, 962555, 0),           # Frostwall innkeeper
    9601122: (2026821, 1.0, 2027016, 0, 0),              # Stable master A
    9601123: (126223, 0.85, 0, 0, 0),                    # Stable master H
    9601124: (1570137, 1.0, 1570258, 1570255, 0),
    9601125: (918944, 1.0, 962560, 962555, 0),
    9601126: (1570137, 1.0, 1570258, 1570255, 0),
    9601127: (918944, 1.0, 962560, 962555, 0),
    9601128: (1630744, 1.0, 0, 0, 0),
    9601129: (918944, 1.0, 962560, 962555, 0),
    9601130: (1570137, 1.0, 1570258, 1570255, 0),
    9601131: (918944, 1.0, 962560, 962555, 0),
    9601132: (1630744, 1.0, 0, 0, 0),
    9601133: (918944, 1.0, 962560, 962555, 0),
    9601134: (1630744, 1.0, 0, 0, 0),
    9601135: (918944, 1.0, 962560, 962555, 0),
    9601136: (1630744, 1.0, 0, 0, 0),
    9601137: (918944, 1.0, 962560, 962555, 0),
    9601138: (1630744, 1.0, 0, 0, 0),
    9601139: (918944, 1.0, 962560, 962555, 0),
    9601140: (1570137, 1.0, 1570258, 1570255, 0),
    9601141: (5764885, 0.9, 0, 0, 0),
    9601142: (1630744, 1.0, 0, 0, 0),
    9601143: (918944, 1.0, 962560, 962555, 0),
    9601144: (1630744, 1.0, 0, 0, 0),
    9601145: (918944, 1.0, 962560, 962555, 0),
    9601146: (1570137, 1.0, 1570258, 1570255, 0),
    9601147: (918944, 1.0, 962560, 962555, 0),
    9601148: (1570137, 1.0, 1570258, 1570255, 0),        # Ken / lumber
    9601149: (918944, 1.0, 962560, 962555, 0),
    9601150: (1570137, 1.0, 1570258, 1570255, 0),
    9601151: (918944, 1.0, 962560, 962555, 0),
    9601152: (1570137, 1.0, 1570258, 1570255, 0),
    9601153: (918944, 1.0, 962560, 962555, 0),
    9601154: (1570137, 1.0, 1570258, 1570255, 0),
    9601155: (918944, 1.0, 962560, 962555, 0),
    9601156: (352936, 1.0, 0, 0, 0),                     # Magus
    9601157: (352936, 1.0, 0, 0, 0),
    9601158: (930099, 1.1, 937291, 937283, 0),
    9601159: (918944, 1.1, 962560, 962555, 0),
    9601160: (5764885, 0.9, 0, 0, 0),
    9601161: (5764885, 0.9, 0, 0, 0),
    9601162: (930099, 1.0, 937290, 937283, 0),
    9601163: (918944, 1.0, 962560, 962555, 0),
    9601164: (930099, 1.0, 937291, 937283, 0),
    9601165: (918944, 1.0, 962560, 962555, 0),
    9601166: (2026821, 1.0, 2027016, 0, 0),              # beast keeper / Ken stand-in
    9601167: (126223, 0.9, 0, 0, 0),
    9601301: (1630744, 1.0, 0, 0, 0),                    # Shelly
    9601302: (1630744, 1.0, 0, 0, 0),                    # Qiana
    9601303: (1722611, 1.0, 1722911, 1722863, 0),        # Rulkan-ish draenei kit (Yrel)
    9601304: (1593262, 1.15, 1593917, 0, 0),             # Delvar
    9601305: (1593262, 1.2, 1593917, 0, 0),              # Admiral Taylor
    9601306: (1722611, 1.0, 1722911, 1722863, 0),        # Fiona
    9601401: (1716306, 1.0, 1716447, 0, 0),              # Olin
    9601402: (918944, 1.1, 962560, 962555, 0),           # Mulverick
    9601403: (1133847, 0.85, 0, 0, 0),                   # Ka'la
    9601404: (1716212, 1.0, 1716222, 0, 0),              # Lantresor stand-in
    9601405: (1716212, 1.0, 1716222, 0, 0),              # Rala
    9601406: (1570137, 1.0, 1570258, 1570255, 0),        # Gibb
}

# esteria GO entry -> (model FileDataID, is_wmo)
GO_MODELS = {
    9602001: (971921, False),   # garrison_ui_chest_goldalliance — cache look
    9602002: (950137, False),   # 6hu_garrison_crate_empty
    9602003: (944905, False),   # 6hu_garrison_mailbox
    9602004: (960215, False),   # 6hu_garrison_lamppost
    9602005: (1021317, False),  # 6hu_garrison_banner01
    9602006: (969977, False),   # architect drafting table
    9602007: (969971, False),   # architect drafting set lvl1
    9602008: (948449, False),   # farm crate
    9602009: (950119, False),   # empty barrel
    9602010: (971926, False),   # garrison_ui_chest_goldhorde
}


def creature_display_id(entry: int) -> int:
    return 68100 + (entry - 9601100)


def creature_model_id(entry: int) -> int:
    return 69100 + (entry - 9601100)


def go_display_id(entry: int) -> int:
    return 68600 + (entry - 9602000)


def f32(value: float) -> int:
    return struct.unpack("<I", struct.pack("<f", value))[0]


def q(text: str) -> str:
    return "'" + str(text).replace("\\", "\\\\").replace("'", "''") + "'"


def read_wdbc(data: bytes):
    assert data[:4] == b"WDBC"
    count, fields, size, strings = struct.unpack_from("<4I", data, 4)
    rows = [data[20 + i * size : 20 + (i + 1) * size] for i in range(count)]
    blob = bytearray(data[20 + count * size : 20 + count * size + strings])
    return fields, size, rows, blob


def winning(storm: Storm, name: str, skip: str = PATCH_NAME):
    data_dir = CLIENT / "Data"
    found = [(f"data\\{p.name.lower()}", p) for p in data_dir.glob("patch-*") if p.suffix.lower() == ".mpq"]
    found += [
        (f"data\\enus\\{p.name.lower()}", p)
        for p in (data_dir / "enUS").glob("patch-enus-*")
        if p.suffix.lower() == ".mpq"
    ]
    for _, archive in sorted(found, reverse=True):
        if archive.name.lower() == skip.lower():
            continue
        handle = storm.open_archive(archive)
        try:
            return archive, storm.read(handle, name)
        except OSError:
            continue
        finally:
            storm.dll.SFileCloseArchive(handle)
    raise SystemExit("no patch MPQ holds " + name)


def append_string(blob: bytearray, text: str) -> int:
    offset = len(blob)
    blob += text.encode("ascii") + b"\0"
    return offset


def write_wdbc(fields: int, size: int, rows: list[bytes | bytearray], blob: bytearray | bytes) -> bytes:
    return (
        b"WDBC"
        + struct.pack("<4I", len(rows), fields, size, len(blob))
        + b"".join(bytes(r) for r in rows)
        + bytes(blob)
    )


def merge_garrison_rows(
    base: bytes,
    patch: bytes,
    id_min: int,
    id_max: int,
    string_offs: list[int],
) -> tuple[bytes, int]:
    """Append patch rows in [id_min, id_max] into base WDBC, remapping string offsets."""
    fields, size, rows, blob = read_wdbc(base)
    pf, ps, prows, pblob = read_wdbc(patch)
    assert (fields, size) == (pf, ps)
    blob = bytearray(blob)
    taken = {struct.unpack_from("<I", r)[0] for r in rows}
    added = 0
    for r in prows:
        rid = struct.unpack_from("<I", r)[0]
        if rid < id_min or rid > id_max or rid in taken:
            continue
        nr = bytearray(r)
        for off in string_offs:
            so = struct.unpack_from("<I", nr, off)[0]
            if not so:
                continue
            end = pblob.find(b"\0", so)
            text = bytes(pblob[so : end + 1]) if end >= 0 else b"\0"
            new_off = len(blob)
            blob += text
            struct.pack_into("<I", nr, off, new_off)
        rows.append(nr)
        taken.add(rid)
        added += 1
    return write_wdbc(fields, size, rows, blob), added


def sync_server_creature_dbc(model_patch: bytes, display_patch: bytes) -> None:
    """Server ObjectMgr strips models whose CreatureDisplayInfo is missing — keep DBC in sync."""
    for d in SERVER_DBC_DIRS:
        if not d.exists():
            print("skip missing server dbc dir", d)
            continue
        for name in ("CreatureDisplayInfo.dbc", "CreatureModelData.dbc"):
            src = d / name
            bak = d / f"{name}.pre_garrison"
            if src.exists() and not bak.exists():
                bak.write_bytes(src.read_bytes())
        model_path = d / "CreatureModelData.dbc"
        display_path = d / "CreatureDisplayInfo.dbc"
        model_out, m_added = merge_garrison_rows(
            model_path.read_bytes(), model_patch, MODEL_ID_MIN, MODEL_ID_MAX, [8]
        )
        display_out, d_added = merge_garrison_rows(
            display_path.read_bytes(), display_patch, DISPLAY_ID_MIN, DISPLAY_ID_MAX, [24, 28, 32, 36]
        )
        model_path.write_bytes(model_out)
        display_path.write_bytes(display_out)
        print(f"synced server dbc {d}: +{m_added} models, +{d_added} displays")


def patch_creature_models(model_dbc: bytes, display_dbc: bytes):
    m_fields, m_size, m_rows, m_blob = read_wdbc(model_dbc)
    d_fields, d_size, d_rows, d_blob = read_wdbc(display_dbc)
    assert (m_fields, m_size) == (28, 112), f"CreatureModelData layout {m_fields}x{m_size}"
    assert (d_fields, d_size) == (16, 64), f"CreatureDisplayInfo layout {d_fields}x{d_size}"
    m_taken = {struct.unpack_from("<I", r)[0] for r in m_rows}
    d_taken = {struct.unpack_from("<I", r)[0] for r in d_rows}
    # donor model row for flags/bounds — first existing
    donor = m_rows[0]

    for entry, (fdid, scale, t11, t12, t13) in sorted(NPC_MODELS.items()):
        mid = creature_model_id(entry)
        did = creature_display_id(entry)
        assert mid not in m_taken and did not in d_taken, (mid, did)
        path = f"retail\\{fdid}.m2"
        path_off = append_string(m_blob, path)
        row = bytearray(donor)
        struct.pack_into("<I", row, 0, mid)
        struct.pack_into("<I", row, 8, path_off)  # ModelName string offset (field 2)
        m_rows.append(bytes(row))
        m_taken.add(mid)

        tex_offs = []
        for tex in (t11, t12, t13):
            tex_offs.append(append_string(d_blob, f"{tex}.blp") if tex else 0)
        # 3.3.5 CreatureDisplayInfo (16 x uint32 / 64 bytes). Scale is a float bit-pattern in field 4.
        display = bytearray(d_size)
        struct.pack_into("<4I", display, 0, did, mid, 0, 0)
        struct.pack_into("<I", display, 16, f32(float(scale)))
        struct.pack_into("<I", display, 20, 255)
        struct.pack_into("<3I", display, 24, tex_offs[0], tex_offs[1], tex_offs[2])
        d_rows.append(bytes(display))
        d_taken.add(did)

    model_out = b"WDBC" + struct.pack("<4I", len(m_rows), m_fields, m_size, len(m_blob)) + b"".join(m_rows) + bytes(m_blob)
    display_out = b"WDBC" + struct.pack("<4I", len(d_rows), d_fields, d_size, len(d_blob)) + b"".join(d_rows) + bytes(d_blob)
    return model_out, display_out


def patch_go_displays(go_dbc: bytes, existing_added: bytes | None = None):
    # Prefer already-patched garrison GO displays (buildings) as base when present in own archive.
    base = existing_added if existing_added else go_dbc
    fields, size, rows, blob = read_wdbc(base)
    assert (fields, size) == (19, 76), f"GO display layout {fields}x{size}"
    taken = {struct.unpack_from("<I", r)[0] for r in rows}
    added = []
    for entry, (fdid, is_wmo) in sorted(GO_MODELS.items()):
        did = go_display_id(entry)
        if did in taken:
            continue
        ext = ".wmo" if is_wmo else ".m2"
        model = f"retail\\{fdid}{ext}"
        offset = append_string(blob, model)
        added.append(struct.pack("<2I10I6fI", did, offset, *([0] * 10), -2, -2, 0, 2, 2, 3, 0))
        taken.add(did)
    rows += added
    return b"WDBC" + struct.pack("<4I", len(rows), fields, size, len(blob)) + b"".join(rows) + bytes(blob)


def world_sql() -> str:
    lines = [
        "-- Generated by modules/mod-esteria-garrison/tools/make_residents.py",
        "-- Retail Casc models (retail/<FileDataID>.m2) for garrison NPCs and town objects.",
        "",
        "DELETE FROM `creature_template_model` WHERE `CreatureID` BETWEEN 9601101 AND 9601499;",
        "DELETE FROM `gameobject_template` WHERE `entry` BETWEEN 9602001 AND 9602010;",
        "DELETE FROM `gameobjectdisplayinfo_dbc` WHERE `ID` BETWEEN 68601 AND 68610;",
    ]
    for entry in sorted(NPC_MODELS):
        did = creature_display_id(entry)
        scale = NPC_MODELS[entry][1]
        lines.append(
            f"INSERT INTO `creature_template_model` (`CreatureID`, `Idx`, `CreatureDisplayID`, `DisplayScale`, `Probability`) "
            f"VALUES ({entry}, 0, {did}, {scale}, 1);"
        )
    lines.append("DELETE FROM `creature_model_info` WHERE `DisplayID` BETWEEN 68100 AND 68400;")
    for entry in sorted(NPC_MODELS):
        did = creature_display_id(entry)
        lines.append(
            "INSERT INTO `creature_model_info` "
            "(`DisplayID`, `BoundingRadius`, `CombatReach`, `Gender`, `DisplayID_Other_Gender`, `VerifiedBuild`) "
            f"VALUES ({did}, 0.5, 1.5, 2, 0, 0);"
        )
    # Keep creature_template rows from garrison_residents_world.sql — only models + GO templates here.
    go_names = {
        9602001: "Garrison Cache",
        9602002: "Supply Crate",
        9602003: "Mailbox",
        9602004: "Lamppost",
        9602005: "Garrison Banner",
        9602006: "Architect Table",
        9602007: "Drafting Set",
        9602008: "Crate",
        9602009: "Barrel",
        9602010: "Garrison Cache",
    }
    for entry, (fdid, is_wmo) in sorted(GO_MODELS.items()):
        did = go_display_id(entry)
        ext = ".wmo" if is_wmo else ".m2"
        model = f"retail\\{fdid}{ext}"
        name = go_names[entry]
        go_type = 3 if entry in (9602001, 9602010) else (19 if entry == 9602003 else 5)
        script = "garrison_cache" if entry in (9602001, 9602010) else ("garrison_architect_table" if entry == 9602006 else "")
        lines.append(
            f"INSERT INTO `gameobjectdisplayinfo_dbc` (`ID`, `ModelName`, `GeoBoxMinX`, `GeoBoxMinY`, `GeoBoxMinZ`, "
            f"`GeoBoxMaxX`, `GeoBoxMaxY`, `GeoBoxMaxZ`) VALUES ({did}, {q(model)}, -2, -2, 0, 2, 2, 3);"
        )
        lines.append(
            f"INSERT INTO `gameobject_template` (`entry`, `type`, `displayId`, `name`, `size`, `Data0`, `ScriptName`) "
            f"VALUES ({entry}, {go_type}, {did}, {q(name)}, 1, 0, {q(script)});"
        )
    return "\n".join(lines) + "\n"


def load_loose(name: str) -> bytes | None:
    loose = HERE / "_mpq_src" / Path(name).name
    return loose.read_bytes() if loose.exists() else None


def main():
    storm = Storm(STORMLIB)
    own = CLIENT / "Data" / PATCH_NAME
    src_dir = HERE / "_mpq_src"
    source = src_dir / PATCH_NAME
    if not source.exists():
        source = Path(str(own) + ".bak_residents") if Path(str(own) + ".bak_residents").exists() else own
    out = Path(str(own) + ".new")

    # Start from current garrison patch if present (keeps Map + building GO displays).
    files: dict[str, bytes] = {}
    if source.exists():
        handle = storm.open_archive(source)
        try:
            for name in (MAP_DBC, GO_DISPLAY_DBC, CREATURE_DISPLAY_DBC, CREATURE_MODEL_DBC):
                try:
                    files[name] = storm.read(handle, name)
                except OSError:
                    pass
        finally:
            storm.dll.SFileCloseArchive(handle)

    # Creature tables are not in the garrison patch yet — pull from env DBC copies or other MPQs.
    housing = src_dir / "Patch-ZZZZZZZZZZZZZZZZZZZZZZZZZHousingDev.MPQ"
    if housing.exists() and (CREATURE_DISPLAY_DBC not in files or CREATURE_MODEL_DBC not in files):
        handle = storm.open_archive(housing)
        try:
            for name in (CREATURE_DISPLAY_DBC, CREATURE_MODEL_DBC, GO_DISPLAY_DBC, MAP_DBC):
                if name in files:
                    continue
                try:
                    files[name] = storm.read(handle, name)
                except OSError:
                    pass
        finally:
            storm.dll.SFileCloseArchive(handle)

    for name, key in (
        (MAP_DBC, "Map.dbc"),
        (GO_DISPLAY_DBC, "GameObjectDisplayInfo.dbc"),
        (CREATURE_DISPLAY_DBC, "CreatureDisplayInfo.dbc"),
        (CREATURE_MODEL_DBC, "CreatureModelData.dbc"),
    ):
        if name not in files:
            loose = load_loose(key)
            if loose:
                files[name] = loose
            else:
                _, files[name] = winning(storm, name)

    # If GO display already has building rows from make_buildings, append resident GOs onto that.
    files[GO_DISPLAY_DBC] = patch_go_displays(files[GO_DISPLAY_DBC])
    model_out, display_out = patch_creature_models(files[CREATURE_MODEL_DBC], files[CREATURE_DISPLAY_DBC])
    files[CREATURE_MODEL_DBC] = model_out
    files[CREATURE_DISPLAY_DBC] = display_out
    sync_server_creature_dbc(model_out, display_out)

    sql_path = MODULE / "sql" / "world" / "garrison_residents_models.sql"
    sql_path.write_text(world_sql(), encoding="utf-8", newline="\n")
    print("wrote", sql_path)

    if out.exists():
        out.unlink()
    storm.create_archive(out, files)
    try:
        if own.exists():
            own.unlink()
        out.replace(own)
        print(f"wrote {own}")
    except OSError as err:
        print(f"wrote {out} (replace later — {own.name} locked: {err})")
    print(f"{len(NPC_MODELS)} creature displays, {len(GO_MODELS)} town object displays (CDN retail/<fdid>)")


if __name__ == "__main__":
    main()
