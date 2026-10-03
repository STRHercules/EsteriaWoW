"""Run after earthen_race_pack.py prepare/stage; checks source selections and archive preservation."""

import struct
from pathlib import Path

from luaparser import ast
from wotlkconv.m2 import parse_m2, parse_skin

import earthen_race_pack as e


def main():
    profiles = e.audit()["sexes"]
    catalog = (e.STAGE / "EsteriaEarthen.bin").read_bytes()
    magic, version, count = struct.unpack_from("<3I", catalog)
    assert magic == 0x314D4845 and version == 1 and len(catalog) == 12 + count * 156
    records = [catalog[12 + i * 156:12 + (i + 1) * 156] for i in range(count)]
    for gender, sex in enumerate(("male", "female")):
        prof = profiles[sex]
        assert len(prof["options"]) == 16
        for field, cap in enumerate(prof["capacities"]):
            descriptors = [(n, factor) for f, n, factor in prof["descriptors"] if f == field]
            assert cap <= 256
            for encoded in range(cap):
                decoded = [(encoded // factor) % n for n, factor in descriptors]
                assert encoded == sum(v * factor for v, (_, factor) in zip(decoded, descriptors))
                for i, (n, factor) in enumerate(descriptors):
                    changed = encoded - decoded[i] * factor + (decoded[i] + 1) % n * factor
                    assert all(j == i or decoded[j] == changed // other_factor % other_n
                               for j, (other_n, other_factor) in enumerate(descriptors))
        key = f"{e.PREFIX}\\{sex}\\earthendwarf{sex}.m2"
        model = parse_m2(e.path(e.ART, key).read_bytes())
        skin = parse_skin(e.path(e.ART, key[:-3] + "00.skin").read_bytes())
        raw = parse_m2((e.CACHE / f"{e.MODELS[sex]}.m2").read_bytes())
        original = parse_m2(e.path(e.SOURCE, f"custom\\earthen\\character\\earthendwarf\\earthendwarf{sex}.m2").read_bytes())
        # The recorded conversion removes unused LOD vertices; verify every retained vertex against Retail.
        raw_vertices = {raw.vertices[i * 48:(i + 1) * 48] for i in range(raw.vertex_count)}
        assert all(original.vertices[i * 48:(i + 1) * 48] in raw_vertices for i in range(original.vertex_count))
        assert [b["bone_name_crc"] for b in raw.bones] == [b["bone_name_crc"] for b in model.bones]
        assert [(s["id"], s["variation_index"]) for s in model.sequences] == [
            (s["id"], s["variation_index"]) for s in original.sequences]
        assert model.vertex_count <= 65535 and len(skin.vertices) <= 65535
        for animation in (4, 5, 13, 16, 26, 38, 69, 96, 97):
            index = model.sequence_lookups[animation]
            assert index != 65535 and model.sequences[index]["id"] == animation
        assert all(model.sequence_lookups[s["id"]] == i for i, s in enumerate(model.sequences)
                   if s["variation_index"] == 0)
        for track in model.tracks():
            assert not track.external
            assert all(times == sorted(times) for times in track.timestamps)
        assert all(s["flags"] & 0x20 for s in model.sequences)
        assert all(w["weight"].global_sequence >= 0 and w["weight"].values == [[32767]]
                   for w in model.texture_weights)
        assert len(model.events) == len(raw.events)
        for event in model.events:
            for i, timestamps in enumerate(event["enabled"].timestamps):
                assert all(0 <= t <= model.sequences[i]["duration"] for t in timestamps)
        geosets = {e.v.u16(mesh, 0) for mesh in skin.submeshes}
        for mesh in skin.submeshes:
            start = e.v.u16(mesh, 8) | e.v.u16(mesh, 2) << 16
            assert start + e.v.u16(mesh, 10) <= len(skin.indices)
            assert e.v.u16(mesh, 12) <= 75
        for record in records:
            g, kind, target, value, *selectors = struct.unpack_from("<7I", record)
            if g != gender:
                continue
            for selected in selectors:
                if selected != 0xffffffff:
                    option, choice = selected & 65535, selected >> 16
                    assert option < 16 and choice < len(prof["options"][option]["choices"])
            if kind == 0:
                assert value % 100 == 0 or value in geosets, (sex, target, value)
            elif kind == 1:
                key = record[28:].split(b"\0")[0].decode()
                asset = e.path(e.ART, key) if e.path(e.ART, key).exists() else e.path(e.SOURCE, key)
                e.p.Blp.parse(asset.read_bytes())
        for texture in model.textures:
            assert texture["type"] < 11
            if texture["type"] == 0 and texture["filename"]:
                key = texture["filename"]
                asset = e.path(e.ART, key) if e.path(e.ART, key).exists() else e.path(e.SOURCE, key)
                e.p.Blp.parse(asset.read_bytes())
    report = e.p.load_json(e.STAGE / "build-report.json")
    storm = e.p.Storm(e.p.DLL_DEFAULT)
    for name in report["tables"]:
        key = e.p.DBC_ROOT + name + ".dbc"
        old = e.p.RawWdbc(e.p._read_archive_entry(storm, e.p.CLIENT_DEFAULT / e.p.GLOBAL_ARCHIVE_REL, key))
        data = e.p._read_archive_entry(storm, e.STAGE / "pack" / e.p.GLOBAL_ARCHIVE_REL, key)
        new = e.p.RawWdbc(data)
        assert data == e.p._read_archive_entry(storm, e.STAGE / "pack" / e.p.LOCALE_ARCHIVE_REL, key)
        if name in e.p.SERVER_DBC_TABLES:
            assert data == (e.STAGE / "server-dbc" / (name + ".dbc")).read_bytes()
        assert new.records[:len(old.records)] == old.records, name
        if name not in ("CharBaseInfo", "CharacterFacialHairStyles"):
            ids = [e.p._value(r, 0) for r in new.records]
            assert len(ids) == len(set(ids)), name
    for rel in (e.p.GLOBAL_ARCHIVE_REL, e.p.LOCALE_ARCHIVE_REL, e.p.ASSET_ARCHIVE_REL):
        assert e.p.sha256(e.p.CLIENT_DEFAULT / rel) == report["source_hashes"][str(rel)]
        archive = e.STAGE / "pack" / rel
        assert e.p.sha256(archive) == report["stage_hashes"][str(rel)]
        for name in ("CharacterCreate.lua", "CharacterInfo.lua", "GlueStrings.lua", "GlueParent.lua",
                     "ECS_Schema.lua", "ECS_Integrate.lua"):
            ast.parse(e.p._read_archive_entry(storm, archive, e.p.GLUE_ROOT + name).decode())
        handle = storm.open_archive(archive)
        try:
            for sex in ("male", "female"):
                key = f"{e.PREFIX}\\{sex}\\earthendwarf{sex}.m2"
                assert storm.read(handle, key) == e.path(e.ART, key).read_bytes()
            for key in e.p.load_json(e.ROOT / "integration/portraits.json"):
                e.p.validate_portrait(storm.read(handle, key), Path(key))
        finally:
            storm.dll.SFileCloseArchive(handle)
    for name in ("EsteriaAppearance.bin", "EsteriaAppearanceMaterials.bin", "EsteriaHighmountain.bin"):
        assert (e.STAGE / name).read_bytes() == (e.p.CLIENT_DEFAULT / name).read_bytes()
    prior = (e.p.CLIENT_DEFAULT / "EsteriaAppearanceGeometry.bin").read_bytes()
    assert (e.STAGE / "EsteriaAppearanceGeometry.bin").read_bytes()[12:len(prior)] == prior[12:]
    print("Earthen PASS: independent controls, complete animations/events, materials, mesh budgets, both factions,")
    print("root/locale/server DBC agreement, supplied portraits, preserved existing rows/catalogs and live archives")


if __name__ == "__main__":
    main()
