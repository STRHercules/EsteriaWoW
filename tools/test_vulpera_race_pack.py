"""Check source controls, atlas projection, animation closure and the exact staged Vulpera merge."""

import ctypes
import hashlib
import random
import struct
from pathlib import Path

from PIL import Image
from luaparser import ast
from wotlkconv.m2 import parse_m2, parse_skin

import vulpera_race_pack as v


def main():
    profiles = v.audit()
    catalog = (v.STAGE / "EsteriaVulpera.bin").read_bytes()
    magic, version, count = struct.unpack_from("<3I", catalog)
    assert (magic, version) == (0x314D4845, 1) and len(catalog) == 12 + count * 156
    records = [catalog[12 + i * 156:12 + (i + 1) * 156] for i in range(count)]
    bank = (v.STAGE / "EsteriaVulperaTextures.bin").read_bytes()
    magic, version, payload_count, signature = struct.unpack_from("<4I", bank)
    assert (magic, version) == (0x31544845, 1)
    assert signature == int.from_bytes(hashlib.sha256(bank[16:]).digest()[:4], "little")
    offsets = {struct.unpack_from("<I", r, 12)[0] for r in records if struct.unpack_from("<I", r, 4)[0] == 3}
    assert len(offsets) == payload_count
    images = {}
    native = ctypes.WinDLL("ntdll")
    for offset in offsets:
        width, height, length = struct.unpack_from("<3I", bank, offset)
        assert 0 < width <= 512 and 0 < height <= 512 and offset + 12 + length <= len(bank)
        output, restored = ctypes.create_string_buffer(width * height * 4), ctypes.c_ulong()
        assert native.RtlDecompressBuffer(2, output, len(output), bank[offset + 12:offset + 12 + length],
                                          length, ctypes.byref(restored)) == 0
        assert restored.value == len(output)
        images[offset] = Image.frombytes("RGBA", (width, height), output.raw)
    def selected(gender, choices):
        return [r for r in records if struct.unpack_from("<I", r)[0] == gender and all(
            selector == 0xffffffff or choices[selector & 65535] == selector >> 16
            for selector in struct.unpack_from("<3I", r, 16))]
    render = v.p.load_json(v.ROOT / "integration/rendering.json")
    for gender, sex in enumerate(("male", "female")):
        profile = profiles[sex]
        assert len(profile["options"]) == 10
        rng = random.Random(335 + gender)
        for _ in range(1000):
            choices = [rng.randrange(len(o["choices"])) for o in profile["options"]]
            assert v.decode(profile, v.encode(profile, choices)) == choices
        default = [0] * 10
        for index, option in enumerate(profile["options"]):
            fingerprints = set()
            for choice in range(len(option["choices"])):
                values = list(default)
                if option["label"] == "Eye Style":
                    values[5 if gender == 0 else 6] = 15
                values[index] = choice
                active = [r for r in selected(gender, values) if struct.unpack_from("<I", r, 4)[0] < 4]
                fingerprints.add(tuple(active))
            assert len(fingerprints) == len(option["choices"]), (sex, option["label"])
        model_path = v.path(v.ART, render[sex]["model_path"])
        model = parse_m2(model_path.read_bytes())
        skin = parse_skin(model_path.with_name(model_path.stem + "00.skin").read_bytes())
        raw = parse_m2((v.ROOT / "raw" / f"{v.MODELS[sex]}.m2").read_bytes())
        assert len(model.sequences) == len(raw.sequences) == 336
        assert len(model.events) == len(raw.events) == (24 if gender == 0 else 25)
        assert not any(t.external for t in model.tracks())
        assert model.vertex_count <= 65535 and len(skin.vertices) <= 65535
        assert max(skin.vertices) < model.vertex_count and max(skin.indices) < len(skin.vertices)
        assert [s["id"] for s in model.sequences] == [s["id"] for s in raw.sequences]
        assert next(a["position"] for a in model.attachments if a["id"] == 11) == next(
            a["position"] for a in raw.attachments if a["id"] == 11)
        for mesh in skin.submeshes:
            start = v.e.v.u16(mesh, 8) | v.e.v.u16(mesh, 2) << 16
            assert start + v.e.v.u16(mesh, 10) <= len(skin.indices)
            assert v.e.v.u16(mesh, 12) <= 75
        assert render[sex]["atlas"]["source_triangles"] == render[sex]["atlas"]["target_triangles"]
        source_skin = parse_skin((v.ROOT / "raw" / f"{raw.skin_file_ids[0]}.skin").read_bytes())
        assert len(skin.vertices) == len(source_skin.vertices)
        assert {v.e.v.u16(m, 0) for m in skin.submeshes} == {v.e.v.u16(m, 0) for m in source_skin.submeshes}
        authored_positions = {raw.vertices[i * 48:i * 48 + 12] for i in source_skin.vertices}
        for i in range(model.vertex_count):
            assert model.vertices[i * 48:i * 48 + 12] in authored_positions
        for group in (0, 1, 3, 4):
            composed, seen = None, set()
            for record in selected(gender, default):
                _, kind, target, offset = struct.unpack_from("<4I", record)
                if kind != 3 or target != group:
                    continue
                source_target = record[28:].split(b"\0")[0].split(b":")[0]
                if source_target in seen:
                    continue
                seen.add(source_target)
                layer = images[offset]
                composed = layer if composed is None else Image.alpha_composite(composed, layer)
            assert composed is not None and composed.getbbox() is not None, (sex, group)
            composed.save(v.STAGE / f"preview-{sex}-{group}.png")
    report = v.p.load_json(v.STAGE / "build-report.json")
    receipt_path = v.STAGE / "last-install.json"
    receipt = v.p.load_json(receipt_path) if receipt_path.exists() else None
    baseline = Path(receipt["backup"]) if receipt else v.p.CLIENT_DEFAULT
    checkpoint_path = v.STAGE / "repair-checkpoint.json"
    if checkpoint_path.exists():
        checkpoint = v.p.load_json(checkpoint_path)
        if all(report["source_hashes"][str(rel)] == checkpoint["client_before"][str(rel)]
               for rel in (v.p.GLOBAL_ARCHIVE_REL, v.p.LOCALE_ARCHIVE_REL)):
            baseline = Path(checkpoint["backup"]) / "client"
    storm = v.p.Storm(v.p.DLL_DEFAULT)
    for name in report["tables"]:
        key = v.p.DBC_ROOT + name + ".dbc"
        old = v.p.RawWdbc(v.p._read_archive_entry(storm, baseline / v.p.GLOBAL_ARCHIVE_REL, key))
        data = v.p._read_archive_entry(storm, v.STAGE / "pack" / v.p.GLOBAL_ARCHIVE_REL, key)
        new = v.p.RawWdbc(data)
        if name in v.p.WDBC_LAYOUTS and name in ("CharSections", "CharHairGeosets", "CharHairTextures",
                                               "CharacterFacialHairStyles", "BarberShopStyle"):
            layout = v.p.WDBC_LAYOUTS[name]
            keep = lambda t: [r for r in t.records if v.p._value(r, layout.race_offset, layout.race_width) != 20]
            assert keep(new) == keep(old), name
        elif name == "CreatureModelData":
            keep = lambda t: [r for r in t.records if v.p._value(r, 0) not in (112885, 112886)]
            assert keep(old) == keep(new)
        else:
            assert new.records == old.records and new.strings == old.strings, name
        assert data == v.p._read_archive_entry(storm, v.STAGE / "pack" / v.p.LOCALE_ARCHIVE_REL, key)
        if name in v.p.SERVER_DBC_TABLES:
            assert data == (v.STAGE / "server-dbc" / (name + ".dbc")).read_bytes()
    for rel in (v.p.GLOBAL_ARCHIVE_REL, v.p.LOCALE_ARCHIVE_REL):
        archive = v.STAGE / "pack" / rel
        assert archive.stat().st_size < 0x80000000
        assert v.p.sha256(archive) == report["stage_hashes"][str(rel)]
        assert v.p.sha256(baseline / rel) == report["source_hashes"][str(rel)]
        if receipt:
            assert v.p.sha256(v.p.CLIENT_DEFAULT / rel) == receipt["installed_hashes"][str(rel)]
        ast.parse(v.p._read_archive_entry(storm, archive, v.p.GLUE_ROOT + "CharacterCreate.lua").decode())
        for file in v.ART.rglob("*"):
            if file.is_file():
                key = str(file.relative_to(v.ART)).replace("/", "\\")
                assert v.p._read_archive_entry(storm, archive, key) == file.read_bytes(), key
    assert v.p.sha256(v.p.CLIENT_DEFAULT / "Wow.exe") == report["preserved_exe_sha256"]
    for name, digest in report["companion_hashes"].items():
        assert v.p.sha256(v.STAGE / name) == digest, name
    print("Vulpera PASS: all controls, source face/snout meshes, body/extra atlas, animation/event closure,")
    print("skin limits, staged assets/helmets, root/locale/server DBC agreement,")
    print("unrelated rows and executable preserved")


if __name__ == "__main__":
    main()
