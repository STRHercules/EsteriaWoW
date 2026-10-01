"""Run after highmountain_race_pack.py prepare; exercises source and staged asset contracts."""

from luaparser import ast
from wotlkconv.m2 import parse_m2, parse_skin

import highmountain_race_pack as h
import highmountain_appearance as codec
import highmountain_faces as faces


def main():
    audit = h.audit()
    assert audit["target_race_id"] == 46 and audit["retail_race_id"] == 28
    assert audit["sexes"]["male"]["control_count"] == 20
    assert audit["sexes"]["female"]["control_count"] == 22
    assert [audit["sexes"][s]["valid_horn_states"] for s in ("male", "female")] == [97, 65]
    discovery = h.p.load_json(h.ROOT / "reports/discovery.json")
    selected = {c["ID"] for sex in audit["sexes"].values() for option in sex["options"]
                for c in option["choices"]}
    expected = {c["ID"] for c in discovery["choices"] if c["ChrCustomizationReqID"] != 10}
    assert selected == expected, "A source customization choice was dropped"
    for sex, profile in codec.codec(audit).items():
        zeros = [0] * len(profile["options"])
        for option, entry in enumerate(profile["options"]):
            for value in range(len(entry["choices"])):
                choices = zeros.copy()
                choices[option] = value
                try:
                    encoded = codec.encode(profile, choices)
                except ValueError:
                    continue  # Accessory needs its authored prerequisite before it is available.
                assert codec.decode(profile, encoded) == choices, (sex, option, value)
        assert not codec.valid(profile, [255] * 6)
    identity = {0: tuple(1.0 if i in (0, 5, 10, 15) else 0.0 for i in range(16))}
    import struct
    vertex = bytearray(48)
    struct.pack_into("<3f", vertex, 0, 1.0, 2.0, 3.0)
    vertex[12] = 255
    struct.pack_into("<3f", vertex, 20, 0.0, 0.0, 1.0)
    assert faces.deform(vertex, identity) == bytes(vertex)
    translated = dict(identity)
    matrix = list(identity[0])
    matrix[12] = 0.5
    translated[0] = matrix
    assert struct.unpack_from("<3f", faces.deform(vertex, translated)) == (1.5, 2.0, 3.0)
    for sex in ("Male", "Female"):
        for root, prefix in (("CharacterCreate", "UI-CharacterCreate"), ("CharacterSelect", "ECS-Portrait")):
            path = h.art_path(f"Interface\\Glues\\{root}\\{prefix}-HighmountainTauren{sex}.blp")
            h.p.validate_portrait(path.read_bytes(), path)
    for name in ("CharacterCreate.lua", "CharacterInfo.lua", "GlueStrings.lua", "GlueParent.lua",
                 "ECS_Schema.lua", "ECS_Integrate.lua"):
        text = h.art_path(h.p.GLUE_ROOT + name).read_text(encoding="utf-8")
        ast.parse(text)
        assert "Highmountain" in text or "HIGHMOUNTAINTAUREN" in text or "race == 46" in text, name
    prepared = h.p.load_json(h.ROOT / "integration/preparation.json")
    for sex, entry in prepared["models"].items():
        path = h.art_path(entry["model_path"])
        model = parse_m2(path.read_bytes())
        skin = parse_skin(path.with_name(path.stem + "00.skin").read_bytes())
        assert len(model.sequences) >= 340, sex
        for animation in (0, 4, 5, 13, 16, 26, 38, 60, 69, 96, 97):
            index = model.sequence_lookups[animation]
            assert index != 65535 and model.sequences[index]["id"] == animation, (sex, animation)
        for mesh in skin.submeshes:
            start = h.v.u16(mesh, 8) | h.v.u16(mesh, 2) << 16
            assert start + h.v.u16(mesh, 10) <= len(skin.indices)
            assert h.v.u16(mesh, 12) <= 75
        # Every external bone track must resolve within its actual companion, including talk.
        for index, sequence in enumerate(model.sequences):
            if sequence["flags"] & (0x20 | 0x40):
                continue
            tracks = [(bone[kind], 8 if kind == "rotation" else 12)
                      for bone in model.bones for kind in ("translation", "rotation", "scale")]
            if not any(index < len(t.timestamp_spans) and t.timestamp_spans[index][0] for t, _ in tracks):
                continue
            animation = path.with_name(f"{path.stem}{sequence['id']:04d}-{sequence['variation_index']:02d}.anim")
            size = animation.stat().st_size
            for track, value_stride in tracks:
                for spans, stride in ((track.timestamp_spans, 4),
                                      (track.value_spans, value_stride)):
                    if index < len(spans):
                        count, offset = spans[index]
                        assert not count or offset + count * stride <= size, (sex, sequence["id"], offset, count)
    material_count = 0
    for asset in discovery["file_assets"]:
        if asset["path"].lower().endswith(".blp"):
            key = "custom\\highmountain\\" + asset["path"]
            h.p.Blp.parse(h.art_path(key).read_bytes(), key)
            material_count += 1
    assert len(audit["bone_sets"]) == 9
    print(f"Highmountain staging check passed: all choices, {material_count} materials, "
          "both animation sets, portraits and Lua")


if __name__ == "__main__":
    main()
