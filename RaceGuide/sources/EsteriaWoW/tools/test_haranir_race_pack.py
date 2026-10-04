"""Verify every Haranir control, transport byte, source material and staged archive before installation."""

import ctypes
import hashlib
import random
import struct
from pathlib import Path

from luaparser import ast
from PIL import Image

import haranir_race_pack as h


def encode(profile, choices):
    fields = [0] * 13
    for value, (field, count, factor) in zip(choices, profile["descriptors"], strict=True):
        assert 0 <= value < count
        fields[field] += value * factor
    return fields


def selected_records(records, gender, choices):
    return [r for r in records if struct.unpack_from("<I", r)[0] == gender and all(
        selector == 0xffffffff or choices[selector & 65535] == selector >> 16
        for selector in struct.unpack_from("<3I", r, 16))]


def main():
    profiles = h.audit()["sexes"]
    catalog = (h.STAGE / "EsteriaHaranir.bin").read_bytes()
    magic, version, count = struct.unpack_from("<3I", catalog)
    assert (magic, version) == (0x314D4845, 1) and len(catalog) == 12 + count * 156
    records = [catalog[12 + i * 156:12 + (i + 1) * 156] for i in range(count)]
    payload = (h.STAGE / "EsteriaHaranirTextures.bin").read_bytes()
    magic, version, payload_count, signature = struct.unpack_from("<4I", payload)
    assert (magic, version) == (0x31544845, 1)
    assert signature == int.from_bytes(hashlib.sha256(payload[16:]).digest()[:4], "little")
    bitmap_cache = {}
    offsets = {struct.unpack_from("<I", r, 12)[0] for r in records if struct.unpack_from("<I", r, 4)[0] == 3}
    assert len(offsets) == payload_count
    native = ctypes.WinDLL("ntdll")
    for offset in sorted(offsets):
        width, height, size = struct.unpack_from("<3I", payload, offset)
        assert 0 < width <= 512 and 0 < height <= 512 and offset + 12 + size <= len(payload)
        output, restored = ctypes.create_string_buffer(width * height * 4), ctypes.c_ulong()
        assert native.RtlDecompressBuffer(2, output, len(output), payload[offset + 12:offset + 12 + size],
                                          size, ctypes.byref(restored)) == 0
        assert restored.value == len(output)
        bitmap_cache[offset] = (width, height, output.raw)
    for gender, sex in enumerate(("male", "female")):
        profile = profiles[sex]
        assert len(profile["options"]) == (29 if gender == 0 else 28)
        for field, capacity in enumerate(profile["capacities"]):
            descriptors = [(count, factor) for f, count, factor in profile["descriptors"] if f == field]
            for encoded in range(capacity):
                assert encoded == sum((encoded // factor % count) * factor for count, factor in descriptors)
        randomizer = random.Random(12340 + gender)
        for _ in range(1000):
            choices = [randomizer.randrange(len(o["choices"])) for o in profile["options"]]
            fields = encode(profile, choices)
            assert all(value < capacity for value, capacity in zip(fields, profile["capacities"], strict=True))
            assert choices == [fields[field] // factor % count for field, count, factor in profile["descriptors"]]
            extra = int.from_bytes(bytes(fields[5:]), "little")
            assert fields == list(bytes(fields[:5]) + struct.pack("<Q", extra))
            assert extra == (extra & 0xffffffff) | ((extra >> 32) << 32)
        default = [0] * len(profile["options"])
        visible = [min(1, len(o["choices"]) - 1) for o in profile["options"]]
        for index, option in enumerate(profile["options"]):
            fingerprints = set()
            for value in range(len(option["choices"])):
                choices = list(visible)
                choices[index] = value
                active = selected_records(records, gender, choices)
                fingerprints.add(tuple(sorted((struct.unpack_from("<3I", r, 4), r[28:]) for r in active)))
                fields = encode(profile, choices)
                assert all(fields[f] // factor % count == choices[j]
                           for j, (f, count, factor) in enumerate(profile["descriptors"]))
            assert len(fingerprints) == len(option["choices"]), (sex, option["label"], len(fingerprints))
        key = f"{h.PREFIX}\\{sex}\\harronir{sex}.m2"
        model = h.parse_m2(h.path(h.ART, key).read_bytes())
        skin = h.parse_skin(h.path(h.ART, key[:-3] + "00.skin").read_bytes())
        raw = h.parse_m2((h.CACHE / f"{h.MODELS[sex]}.m2").read_bytes())
        source = h.parse_m2(h.path(h.SOURCE,
            f"custom\\haranir\\character\\harronir\\harronir{sex}.m2").read_bytes())
        raw_vertices = {raw.vertices[i * 48:(i + 1) * 48] for i in range(raw.vertex_count)}
        assert all(source.vertices[i * 48:(i + 1) * 48] in raw_vertices for i in range(source.vertex_count))
        assert [(s["id"], s["variation_index"]) for s in source.sequences] == [
            (s["id"], s["variation_index"]) for s in raw.sequences]
        assert model.vertex_count <= 65535 and len(skin.vertices) <= 65535
        assert [b["bone_name_crc"] for b in model.bones] == [b["bone_name_crc"] for b in raw.bones]
        for animation in (4, 5, 13, 16, 26, 38, 69, 96, 97):
            index = model.sequence_lookups[animation]
            assert index != 65535 and model.sequences[index]["id"] == animation
        assert all(not track.external and all(times == sorted(times) for times in track.timestamps)
                   for track in model.tracks())
        assert len(model.events) == len(raw.events)
        assert all(0 <= t <= model.sequences[i]["duration"] for event in model.events
                   for i, times in enumerate(event["enabled"].timestamps) for t in times)
        geosets = {h.e.v.u16(mesh, 0) for mesh in skin.submeshes}
        for mesh in skin.submeshes:
            first = h.e.v.u16(mesh, 8) | h.e.v.u16(mesh, 2) << 16
            assert first + h.e.v.u16(mesh, 10) <= len(skin.indices) and h.e.v.u16(mesh, 12) <= 75
        for r in records:
            g, kind, target, value = struct.unpack_from("<4I", r)
            if g == gender and kind == 0:
                selector = struct.unpack_from("<I", r, 16)[0]
                authored_none = selector != 0xffffffff and profile["options"][selector & 65535]["choices"][
                    selector >> 16]["Name_lang"] == "None"
                assert value % 100 == 0 or value in geosets or authored_none, (sex, target, value)
        # Independent source layers compose in authored order; each default yields body and face materials.
        for group in range(9):
            art, seen = None, set()
            for r in selected_records(records, gender, default):
                g, kind, target, offset = struct.unpack_from("<4I", r)
                if kind != 3 or target != group:
                    continue
                material = int(r[28:].split(b"\0")[0].split(b":")[0])
                if material in seen:
                    continue
                seen.add(material)
                width, height, rgba = bitmap_cache[offset]
                layer = Image.frombytes("RGBA", (width, height), rgba)
                art = layer if art is None else Image.alpha_composite(art, layer)
            assert art is not None, (sex, group)
            art.save(h.STAGE / f"preview-{sex}-{group}.png")
    report = h.p.load_json(h.STAGE / "build-report.json")
    receipt_file = h.STAGE / "last-install.json"
    receipt = h.p.load_json(receipt_file) if receipt_file.exists() else None
    baseline = Path(receipt["backup"]) if receipt else h.p.CLIENT_DEFAULT
    storm = h.p.Storm(h.p.DLL_DEFAULT)
    for name in report["tables"]:
        key = h.p.DBC_ROOT + name + ".dbc"
        old = h.p.RawWdbc(h.p._read_archive_entry(storm, baseline / h.p.GLOBAL_ARCHIVE_REL, key))
        data = h.p._read_archive_entry(storm, h.STAGE / "pack" / h.p.GLOBAL_ARCHIVE_REL, key)
        new = h.p.RawWdbc(data)
        assert new.records[:len(old.records)] == old.records, name
        assert data == h.p._read_archive_entry(storm, h.STAGE / "pack" / h.p.LOCALE_ARCHIVE_REL, key)
        if name in h.p.SERVER_DBC_TABLES:
            assert data == (h.STAGE / "server-dbc" / (name + ".dbc")).read_bytes()
    for relative in (h.p.GLOBAL_ARCHIVE_REL, h.p.LOCALE_ARCHIVE_REL, h.p.ASSET_ARCHIVE_REL):
        assert h.p.sha256(baseline / relative) == report["source_hashes"][str(relative)]
        if receipt:
            assert h.p.sha256(h.p.CLIENT_DEFAULT / relative) == receipt["installed_hashes"][str(relative)]
        archive = h.STAGE / "pack" / relative
        assert h.p.sha256(archive) == report["stage_hashes"][str(relative)]
        for name in ("CharacterCreate.lua", "CharacterInfo.lua", "GlueStrings.lua", "GlueParent.lua",
                     "ECS_Schema.lua", "ECS_Integrate.lua"):
            ast.parse(h.p._read_archive_entry(storm, archive, h.p.GLUE_ROOT + name).decode())
        for key in h.p.load_json(h.ROOT / "integration/portraits.json"):
            h.p.validate_portrait(h.p._read_archive_entry(storm, archive, key), Path(key))
    for name in ("EsteriaAppearance.bin", "EsteriaAppearanceMaterials.bin",
                 "EsteriaHighmountain.bin", "EsteriaEarthen.bin"):
        assert (h.STAGE / name).read_bytes() == (baseline / name).read_bytes()
    prior = (baseline / "EsteriaAppearanceGeometry.bin").read_bytes()
    assert (h.STAGE / "EsteriaAppearanceGeometry.bin").read_bytes()[12:len(prior)] == prior[12:]
    print("Haranir PASS: every ordinary control, 13-byte persistence, materials, animations/events, mesh budgets,")
    print("both factions, portraits, archive/server DBC agreement; prior race data and live files preserved")


if __name__ == "__main__":
    main()
