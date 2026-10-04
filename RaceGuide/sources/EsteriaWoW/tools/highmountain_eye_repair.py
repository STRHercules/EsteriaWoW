"""Bind Highmountain iris meshes through the proven Wrath opaque UV0 material path."""

import argparse
import json
import shutil
import struct

from wotlkconv.m2 import parse_skin, write_md20
from wotlkconv.m2.skin import write_skin

import highmountain_head_repair as installer
import highmountain_race_pack as h
import retroported_race_pack as p

STAGE = h.STAGE / "eye-repair"


def prepare():
    STAGE.mkdir(parents=True, exist_ok=True)
    updates = {}
    report = {"source_hashes": {}, "stage_hashes": {}, "companion_hashes": {}, "models": {}}
    for sex in ("male", "female"):
        key = f"{h.PREFIX}\\{sex}\\highmountaintauren{sex}.m2"
        model = h.v.read_player_model(h.art_path(key))
        skin_key = key[:-3] + "00.skin"
        skin = parse_skin(h.art_path(skin_key).read_bytes())
        eye_slot = next(i for i, texture in enumerate(model.textures) if texture["type"] == 5)
        material = len(model.materials)
        model.materials.append({"flags": 4, "blending_mode": 0})
        count = 0
        for i, raw in enumerate(skin.batches):
            slots = model.texture_combos[h.v.u16(raw, 16):h.v.u16(raw, 16) + h.v.u16(raw, 14)]
            if not any(model.textures[j]["type"] == 5 for j in slots):
                continue
            batch = bytearray(raw)
            for offset, value in ((0, 0), (10, material), (14, 1), (16, len(model.texture_combos)), (18, 0)):
                h.v.patch16(batch, offset, value)
            model.texture_combos.append(eye_slot)
            skin.batches[i] = bytes(batch)
            count += 1
        if count != 1:
            raise ValueError("Expected one actual eye batch per gender")
        model.texture_coord_combos[0] = 0
        updates[key] = write_md20(model)
        updates[skin_key] = write_skin(skin)
        report["models"][sex] = {"model_path": key, "eye_batches": count,
                                "binding": "slot5, opaque, unlit, shader0, one UV0 texture"}
    geometry = bytearray((p.CLIENT_DEFAULT / "EsteriaAppearanceGeometry.bin").read_bytes())
    offset = 12
    while offset < len(geometry):
        key = bytes(geometry[offset:offset + 128]).split(b"\0")[0].decode()
        length = struct.unpack_from("<I", geometry, offset + 128)[0]
        skin_key = key[:-3] + "00.skin"
        if skin_key in updates:
            if length != len(updates[skin_key]):
                raise ValueError("Eye material repair changed geometry layout")
            geometry[offset + 132:offset + 132 + length] = updates[skin_key]
        offset += 132 + length
    if offset != len(geometry):
        raise ValueError("Unexpected geometry catalog")
    (STAGE / "EsteriaAppearanceGeometry.bin").write_bytes(geometry)
    report["companion_hashes"]["EsteriaAppearanceGeometry.bin"] = p.sha256(STAGE / "EsteriaAppearanceGeometry.bin")
    storm = p.Storm(p.DLL_DEFAULT)
    for relative in installer.RELATIVES:
        live = p.CLIENT_DEFAULT / relative
        stage = STAGE / "pack" / relative
        stage.parent.mkdir(parents=True, exist_ok=True)
        report["source_hashes"][str(relative)] = p.sha256(live)
        shutil.copy2(live, stage)
        storm.replace_archive_entries(stage, updates)
        for key, data in updates.items():
            if p._read_archive_entry(storm, stage, key) != data:
                raise ValueError("Eye repair archive readback mismatch")
        if stage.stat().st_size >= 0x80000000:
            raise ValueError("Eye repair exceeds classic reader boundary")
        report["stage_hashes"][str(relative)] = p.sha256(stage)
    for key, data in updates.items():
        path = STAGE.joinpath(*p.PureWindowsPath(key).parts)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    h.save(STAGE / "build-report.json", report)
    return report


def install():
    installer.STAGE = STAGE
    report = installer.install("eyes")
    for record in report["models"].values():
        key = record["model_path"]
        for entry in (key, key[:-3] + "00.skin"):
            shutil.copy2(STAGE.joinpath(*p.PureWindowsPath(entry).parts), h.art_path(entry))
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("prepare", "install"))
    args = parser.parse_args()
    print(json.dumps(prepare() if args.command == "prepare" else install(), indent=2))
