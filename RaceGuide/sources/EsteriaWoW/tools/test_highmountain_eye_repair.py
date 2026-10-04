"""Check the iris binding, authored UVs and preservation of the accepted face geometry."""

import struct

from wotlkconv.m2 import parse_m2, parse_skin
import highmountain_eye_repair as repair


def main():
    report = repair.p.load_json(repair.STAGE / "build-report.json")
    installed = repair.STAGE / "last-install.json"
    before = repair.p.Path(repair.p.load_json(installed)["backup"]) if installed.exists() else repair.h.STAGE / "pack"
    storm = repair.p.Storm(repair.p.DLL_DEFAULT)
    for sex, record in report["models"].items():
        key = record["model_path"]
        old_data = repair.p._read_archive_entry(storm, before / repair.p.GLOBAL_ARCHIVE_REL, key)
        model = parse_m2(repair.STAGE.joinpath(*repair.p.PureWindowsPath(key).parts).read_bytes())
        old = parse_m2(old_data)
        assert model.vertices == old.vertices and model.vertex_count == old.vertex_count
        assert model.sequences == old.sequences and model.sequence_lookups == old.sequence_lookups
        assert model.textures == old.textures and model.materials[:-1] == old.materials
        skin_key = key[:-3] + "00.skin"
        old_skin = parse_skin(repair.p._read_archive_entry(storm, before / repair.p.GLOBAL_ARCHIVE_REL, skin_key))
        skin = parse_skin(repair.STAGE.joinpath(*repair.p.PureWindowsPath(skin_key).parts).read_bytes())
        assert skin.submeshes == old_skin.submeshes and skin.vertices == old_skin.vertices
        assert skin.indices == old_skin.indices and skin.bones == old_skin.bones
        changed = 0
        for previous, current in zip(old_skin.batches, skin.batches, strict=True):
            old_slots = old.texture_combos[repair.h.v.u16(previous, 16):
                                           repair.h.v.u16(previous, 16) + repair.h.v.u16(previous, 14)]
            if not any(old.textures[i]["type"] == 5 for i in old_slots):
                assert current == previous
                continue
            changed += 1
            assert repair.h.v.u16(current, 0) == 0 and repair.h.v.u16(current, 14) == 1
            assert model.materials[repair.h.v.u16(current, 10)] == {"flags": 4, "blending_mode": 0}
            assert model.texture_coord_combos[repair.h.v.u16(current, 18)] == 0
            slot = model.texture_combos[repair.h.v.u16(current, 16)]
            assert model.textures[slot]["type"] == 5
        assert changed == 1
        for relative in repair.installer.RELATIVES:
            stage = repair.STAGE / "pack" / relative
            assert repair.p._read_archive_entry(storm, stage, key) == repair.STAGE.joinpath(
                *repair.p.PureWindowsPath(key).parts).read_bytes()
            assert repair.p._read_archive_entry(storm, stage, skin_key) == repair.STAGE.joinpath(
                *repair.p.PureWindowsPath(skin_key).parts).read_bytes()
    print("Highmountain eyes: PASS (opaque UV0 iris; accepted face geometry and unrelated materials unchanged)")


if __name__ == "__main__":
    main()
