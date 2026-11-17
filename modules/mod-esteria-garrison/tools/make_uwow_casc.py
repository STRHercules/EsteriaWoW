"""Patch client+server CreatureDisplayInfo for real UWoW garrison creature entries.

Uses Casc retail/<FileDataID>.m2 paths. Display IDs are 700000+entry (see import_uwow_spawns.py).
"""
from __future__ import annotations

import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
MODULE = HERE.parent
sys.path.insert(0, str(MODULE.parents[1] / "tools"))
from cars_mount_pack import Storm  # noqa: E402

from make_residents import (  # noqa: E402
    CLIENT,
    CREATURE_DISPLAY_DBC,
    CREATURE_MODEL_DBC,
    PATCH_NAME,
    STORMLIB,
    append_string,
    f32,
    merge_garrison_rows,
    read_wdbc,
    sync_server_creature_dbc,
    write_wdbc,
    winning,
)
from uwow_npc_casc_models import DISPLAY_FOR, NPC_MODELS  # noqa: E402

DISPLAY_MIN, DISPLAY_MAX = 700000, 800000
MODEL_MIN, MODEL_MAX = 710000, 810000


def model_id_for(entry: int) -> int:
    return 710000 + entry


def patch(model_dbc: bytes, display_dbc: bytes):
    m_fields, m_size, m_rows, m_blob = read_wdbc(model_dbc)
    d_fields, d_size, d_rows, d_blob = read_wdbc(display_dbc)
    m_blob = bytearray(m_blob)
    d_blob = bytearray(d_blob)
    m_taken = {struct.unpack_from("<I", r)[0] for r in m_rows}
    d_taken = {struct.unpack_from("<I", r)[0] for r in d_rows}
    donor = m_rows[0]
    added = 0
    for entry, (fdid, scale, t11, t12, t13) in sorted(NPC_MODELS.items()):
        mid = model_id_for(entry)
        did = DISPLAY_FOR[entry]
        if mid in m_taken or did in d_taken:
            continue
        path_off = append_string(m_blob, f"retail\\{fdid}.m2")
        row = bytearray(donor)
        struct.pack_into("<I", row, 0, mid)
        struct.pack_into("<I", row, 8, path_off)
        m_rows.append(bytes(row))
        m_taken.add(mid)
        tex = []
        for t in (t11, t12, t13):
            tex.append(append_string(d_blob, f"{t}.blp") if t else 0)
        display = bytearray(d_size)
        struct.pack_into("<4I", display, 0, did, mid, 0, 0)
        struct.pack_into("<I", display, 16, f32(float(scale)))
        struct.pack_into("<I", display, 20, 255)
        struct.pack_into("<3I", display, 24, tex[0], tex[1], tex[2])
        d_rows.append(bytes(display))
        d_taken.add(did)
        added += 1
    model_out = write_wdbc(m_fields, m_size, m_rows, m_blob)
    display_out = write_wdbc(d_fields, d_size, d_rows, d_blob)
    return model_out, display_out, added


def main():
    storm = Storm(STORMLIB)
    own = CLIENT / "Data" / PATCH_NAME
    src = HERE / "_mpq_src" / PATCH_NAME
    if not src.exists():
        bak = Path(str(own) + ".bak_residents")
        source = bak if bak.exists() else own
    else:
        source = src
    files: dict[str, bytes] = {}
    if source.exists():
        h = storm.open_archive(source)
        try:
            for name in (CREATURE_DISPLAY_DBC, CREATURE_MODEL_DBC):
                try:
                    files[name] = storm.read(h, name)
                except OSError:
                    pass
        finally:
            storm.dll.SFileCloseArchive(h)
    for name in (CREATURE_DISPLAY_DBC, CREATURE_MODEL_DBC):
        if name not in files:
            _, files[name] = winning(storm, name)
    model_out, display_out, added = patch(files[CREATURE_MODEL_DBC], files[CREATURE_DISPLAY_DBC])
    files[CREATURE_MODEL_DBC] = model_out
    files[CREATURE_DISPLAY_DBC] = display_out
    # merge only our band into server DBC
    for d in (
        MODULE.parents[1] / "build" / "bin" / "RelWithDebInfo" / "dbc",
        MODULE.parents[1] / "env" / "dist" / "data" / "dbc",
    ):
        if not d.exists():
            continue
        for name, patch_bytes, lo, hi, offs in (
            ("CreatureModelData.dbc", model_out, MODEL_MIN, MODEL_MAX, [8]),
            ("CreatureDisplayInfo.dbc", display_out, DISPLAY_MIN, DISPLAY_MAX, [24, 28, 32, 36]),
        ):
            path = d / name
            bak = d / f"{name}.pre_uwow"
            if path.exists() and not bak.exists():
                bak.write_bytes(path.read_bytes())
            out, n = merge_garrison_rows(path.read_bytes(), patch_bytes, lo, hi, offs)
            path.write_bytes(out)
            print(f"server {d.name}/{name} +{n}")
    out = Path(str(own) + ".new")
    if out.exists():
        out.unlink()
    storm.create_archive(out, files)
    try:
        if own.exists():
            own.unlink()
        out.replace(own)
        print(f"wrote {own} (+{added} uwow npc models)")
    except OSError as err:
        print(f"wrote {out} (replace later — locked: {err})")


if __name__ == "__main__":
    main()
