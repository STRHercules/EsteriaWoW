"""Check complete opaque sequences, inherited hand transforms and accepted geometry/material preservation."""

import struct

from wotlkconv.m2 import parse_m2
import highmountain_animation_repair as repair


def main():
    report = repair.h.p.load_json(repair.STAGE / "build-report.json")
    installed = repair.STAGE / "last-install.json"
    before = repair.h.p.Path(repair.h.p.load_json(installed)["backup"]) if installed.exists() else repair.h.STAGE / "pack"
    storm = repair.h.p.Storm(repair.h.p.DLL_DEFAULT)
    for sex, row in report["models"].items():
        key = row["model_path"]
        model_path = repair.STAGE.joinpath(*repair.h.p.PureWindowsPath(key).parts)
        model = parse_m2(model_path.read_bytes())
        old = parse_m2(repair.h.p._read_archive_entry(storm, before / repair.h.p.GLOBAL_ARCHIVE_REL, key))
        assert model.vertices == old.vertices and model.textures == old.textures
        assert model.materials == old.materials and model.texture_combos == old.texture_combos
        assert len(model.sequences) == (349 if sex == "male" else 341)
        weight = model.texture_weights[0]["weight"]
        assert len(weight.values) == len(model.sequences)
        assert all(v == [32767] for v in weight.values) and all(t == [0] for t in weight.timestamps)
        reread = repair.h.v.read_player_model(model_path)
        assert reread.texture_weights[0]["weight"].values == weight.values
        for aid in (0, 4, 5, 13, 16, 26, 60, 69, 96, 97):
            index = model.sequence_lookups[aid]
            assert index != 65535 and model.sequences[index]["id"] == aid
            assert weight.values[index] == [32767]
        for bone in model.bones:
            for name in ("translation", "rotation", "scale"):
                track = bone[name]
                assert track.global_sequence >= 0 or len(track.timestamps) <= len(model.sequences)
        for aid in (1, 2):
            attachment = next(a for a in model.attachments if a["id"] == aid)
            helper = reread.bones[model.bones[attachment["bone"]]["parent_bone"]]
            translation = helper["translation"]
            for animation in (0, 13, 16, 60, 69):
                i = model.sequence_lookups[animation]
                if i in translation.external:
                    sequence = model.sequences[i]
                    path = model_path.with_name(
                        f"{model_path.stem}{sequence['id']:04d}-{sequence['variation_index']:02d}.anim")
                    count, offset = translation.value_spans[i]
                    assert count > 0
                    point = struct.unpack_from("<3f", path.read_bytes(), offset)
                else:
                    assert translation.values[i]
                    point = translation.values[i][0]
                assert sum(v * v for v in point) > .1
                if animation in (0, 13):
                    assert point[2] > 1.0
            for kind in ("translation", "rotation", "scale"):
                socket = model.bones[attachment["bone"]][kind]
                assert socket.global_sequence >= 0 or not any(socket.timestamps)
        for index, sequence in enumerate(model.sequences):
            if sequence["flags"] & (0x20 | 0x40):
                continue
            path = model_path.with_name(f"{model_path.stem}{sequence['id']:04d}-{sequence['variation_index']:02d}.anim")
            for bone in model.bones:
                for kind in ("translation", "rotation", "scale"):
                    track = bone[kind]
                    if track.global_sequence >= 0:
                        continue
                    for spans, stride in ((track.timestamp_spans, 4),
                                          (track.value_spans, 8 if kind == "rotation" else 12)):
                        if index < len(spans):
                            count, offset = spans[index]
                            assert not count or offset + count * stride <= path.stat().st_size
        for relative in repair.installer.RELATIVES:
            assert repair.h.p._read_archive_entry(storm, repair.STAGE / "pack" / relative, key) == model_path.read_bytes()
    print("Highmountain animation repair: PASS (all opacity keys, talk/dance, hand binds, ANIM ranges, preserved geometry)")


if __name__ == "__main__":
    main()
