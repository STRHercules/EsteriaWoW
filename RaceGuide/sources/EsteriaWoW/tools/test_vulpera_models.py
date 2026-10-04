"""Regress the source head selection and the UV/material path used by the tail."""

import ctypes
import struct

from PIL import Image

from wotlkconv.m2 import parse_m2, parse_skin

import vulpera_models as models
import vulpera_race_pack as v


def main():
    catalog = (v.STAGE / "EsteriaVulpera.bin").read_bytes()
    count = struct.unpack_from("<I", catalog, 8)[0]
    records = [struct.unpack_from("<7I", catalog, 12 + i * 156) for i in range(count)]
    paths = [catalog[12 + i * 156 + 28:12 + (i + 1) * 156].split(b"\0")[0] for i in range(count)]
    bank = (v.STAGE / "EsteriaVulperaTextures.bin").read_bytes()
    native = ctypes.WinDLL("ntdll")
    images = {}

    def layer(offset):
        if offset not in images:
            width, height, length = struct.unpack_from("<3I", bank, offset)
            output = ctypes.create_string_buffer(width * height * 4)
            restored = ctypes.c_ulong()
            assert native.RtlDecompressBuffer(2, output, len(output), bank[offset + 12:offset + 12 + length],
                                              length, ctypes.byref(restored)) == 0
            assert restored.value == len(output)
            images[offset] = Image.frombytes("RGBA", (width, height), output.raw)
        return images[offset]

    def composed(gender, choices, group):
        result, seen = None, set()
        for record, path in zip(records, paths, strict=True):
            sex, kind, target, offset, *selectors = record
            source_target = path.split(b":")[0]
            if sex != gender or kind != 3 or target != group or source_target in seen:
                continue
            if not all(selector == 0xffffffff or choices[selector & 65535] == selector >> 16
                       for selector in selectors):
                continue
            seen.add(source_target)
            art = layer(offset)
            result = art if result is None else Image.alpha_composite(result, art)
        assert result is not None, (gender, group)
        return result

    for gender, sex in enumerate(("male", "female")):
        source = v.path(v.SOURCE, f"custom\\vulpera\\character\\vulpera\\{sex}\\vulpera{sex}.m2")
        model = parse_m2(source.read_bytes())
        skin = parse_skin(source.with_name(source.stem + "00.skin").read_bytes())
        head = next(mesh for mesh in skin.submeshes if v.e.v.u16(mesh, 0) == 3202)
        start = v.e.v.u16(head, 8) | v.e.v.u16(head, 2) << 16
        indices = skin.indices[start:start + v.e.v.u16(head, 10)]
        # The neck ring 3201 cannot substitute for the complete face/head mesh 3202.
        assert max(struct.unpack_from("<f", model.vertices, skin.vertices[i] * 48 + 8)[0]
                   for i in indices) > 1.25
        assert any(record[:4] == (gender, 0, 32, 3202) and record[4:] == (0xffffffff,) * 3
                   for record in records), sex
        positions = model.vertices
        atlas = models.split_atlas(model, skin)
        assert atlas["source_triangles"] == atlas["target_triangles"]
        tail = {i for i in range(model.vertex_count)
                if struct.unpack_from("<f", positions, i * 48)[0] < -.8}
        assert len(tail) > 20
        bound_tail = set()
        for batch in skin.batches:
            mesh = skin.submeshes[v.e.v.u16(batch, 4)]
            start = v.e.v.u16(mesh, 8) | v.e.v.u16(mesh, 2) << 16
            vertices = {skin.vertices[i] for i in skin.indices[start:start + v.e.v.u16(mesh, 10)]}
            if vertices & tail:
                texture = model.textures[model.texture_combos[v.e.v.u16(batch, 16)]]
                assert texture["type"] == 1, (sex, v.e.v.u16(mesh, 0), texture)
                for i in vertices & tail:
                    old_u, old_y = struct.unpack_from("<2f", positions, i * 48 + 32)
                    new_u, new_y = struct.unpack_from("<2f", model.vertices, i * 48 + 32)
                    assert abs(new_u - old_u * 2) < .00001 and new_y == old_y
                bound_tail |= vertices & tail
        assert bound_tail == tail, (sex, len(tail - bound_tail))
        # Native body composition fills regions 0..7; regions 8/9 are the two face layers.
        # Compare their actual pixels at the tail UVs for every fur/pattern, rather than only decoding files.
        profile = v.audit()[sex]
        fur = next(i for i, option in enumerate(profile["options"]) if option["label"] == "Fur Color")
        pattern = next(i for i, option in enumerate(profile["options"]) if option["label"] == "Pattern")
        for fur_choice in range(len(profile["options"][fur]["choices"])):
            for pattern_choice in range(len(profile["options"][pattern]["choices"])):
                choices = [0] * len(profile["options"])
                choices[fur], choices[pattern] = fur_choice, pattern_choice
                body, face = composed(gender, choices, 0), composed(gender, choices, 1)
                assert face.size == (256, 192)
                assert face.tobytes() == body.crop((0, 320, 256, 512)).tobytes()
                for vertex in tail:
                    u, y = struct.unpack_from("<2f", model.vertices, vertex * 48 + 32)
                    x, row = min(int(u * 512), 511), min(int(y * 512), 511)
                    assert x < 256 and row >= 320, (sex, vertex, x, row)
                    pixel = face.getpixel((x, row - 320))
                    assert pixel == body.getpixel((x, row)) and pixel[3] and max(pixel[:3]) > 0
        eye = next(i for i, option in enumerate(profile["options"]) if option["label"] == "Eye Color")
        style = next(i for i, option in enumerate(profile["options"]) if option["label"] == "Eye Style")
        eyesight = next(i for i, option in enumerate(profile["options"]) if option["label"] == "Eyesight")
        # Only source-authored DK/Primalist choices enable additive eye sprites. Ordinary iris/vision
        # selections must not fall back to the DK sprite and obscure their composed eye material.
        glow_by_eye = {14: 1701, 29: 1702, 30: 1703, 31: 1704, 32: 1705}
        for eye_choice in range(len(profile["options"][eye]["choices"])):
            for vision in range(len(profile["options"][eyesight]["choices"])):
                choices = [0] * len(profile["options"])
                choices[eye], choices[eyesight] = eye_choice, vision
                glow = next(record[3] for record in records
                            if record[:3] == (gender, 0, 17) and all(
                                selector == 0xffffffff or choices[selector & 65535] == selector >> 16
                                for selector in record[4:]))
                assert glow == glow_by_eye.get(eye_choice, 1700), (sex, eye_choice, vision, glow)
        for eye_choice in range(15, 29):
            authored_styles = set()
            for style_choice in range(3):
                choices = [0] * len(profile["options"])
                choices[eye], choices[style] = eye_choice, style_choice
                authored_styles.add(composed(gender, choices, 3).tobytes())
            assert len(authored_styles) == 3, (sex, eye_choice)
    print("Vulpera model head visibility and source tail UV/material binding: PASS")


if __name__ == "__main__":
    main()
