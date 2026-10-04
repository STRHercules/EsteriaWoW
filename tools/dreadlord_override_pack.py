"""Build/check the standalone NPC override from the audited, immutable dreadlord source cache."""

import argparse
import hashlib
import json
import math
import struct
from pathlib import Path, PureWindowsPath

from wotlkconv.blp import Blp, convert_blp
from wotlkconv.blp import bcn
from wotlkconv.listfile import Listfile
from wotlkconv.m2 import parse_m2, parse_skin, write_md20
from wotlkconv.m2.convert import _collect_anims
from wotlkconv.m2.downgrade import downgrade_model
from wotlkconv.m2.skin import downgrade_skin, write_skin
from wotlkconv.m2.split import _rebuild_skin
from wotlkconv.m2.texcoords import assign_texture_coord_combos
from wotlkconv.m2.types import value_size
from wotlkconv.options import Options, UnresolvedPolicy
from wotlkconv.report import FileResult
from wotlkconv.resolve import AssetSource

from cars_mount_pack import DLL_DEFAULT, Storm
from highmountain_complete_tracks import embed
from skyborne_visual_pack import compact_bone_palettes

WORK = Path(r"G:\RetroPorterWork\dreadlord")
DONOR = Path(r"G:\Downloads\HDWoWModels\dreadlordfix")
MODEL = r"Creature\Dreadlord\DreadLord.m2"
PREFIX = PureWindowsPath(MODEL).parent
ARCHIVE = WORK / "output/Patch-Dr.MPQ"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def normalize_texture(data):
    result, report = convert_blp(data, "dreadlord texture", Options())
    if not result or not report.ok:
        raise ValueError("Texture conversion failed")
    texture = Blp.parse(result)
    # The supplied body has a missing final mip and garbage in unused header entries.
    while texture.level_size(texture.mip_count - 1) != (1, 1):
        image = texture.decode_level(texture.mip_count - 1).resize(
            *texture.level_size(texture.mip_count))
        if texture.alpha_type != 1 or texture.compression != 2:
            raise ValueError("Unexpected incomplete mip chain")
        texture.mips.append(bcn.encode_bc2(image.data, image.width, image.height))
    return texture.serialize()


def check_entries(entries):
    """One bounded check for mesh, animation, texture, and reference integrity."""
    model_data = entries[MODEL]
    model = parse_m2(model_data)
    skin = parse_skin(entries[str(PREFIX / "DreadLord00.skin")])
    assert model_data[:4] == b"MD20" and model.version == 264
    assert len(model.sequences) == 124 and len(model.bones) == 204
    assert all(s["flags"] & 0x20 for s in model.sequences)
    assert model.vertex_count <= 65535 and len(skin.vertices) <= 65535
    assert max(skin.vertices) < model.vertex_count
    assert max(skin.indices) < len(skin.vertices)
    assert len(skin.bones) == len(skin.vertices) * 4
    for section in skin.submeshes:
        sid, high, first, count, low, indices, bones, palette = struct.unpack_from("<8H", section)
        assert sid == 0 and first + count <= len(skin.vertices)
        start = low | high << 16
        assert start + indices <= len(skin.indices) and indices % 3 == 0
        assert 0 < bones <= 75 and palette + bones <= len(model.bone_combos)
        for vertex in range(first, first + count):
            actual = skin.vertices[vertex]
            for i, local in enumerate(skin.bones[vertex * 4:vertex * 4 + 4]):
                if model.vertices[actual * 48 + 12 + i]:
                    assert local < bones
                    assert model.bone_combos[palette + local] == model.vertices[actual * 48 + 16 + i]
    for batch in skin.batches:
        assert struct.unpack_from("<H", batch, 4)[0] < len(skin.submeshes)
        assert struct.unpack_from("<H", batch, 10)[0] < len(model.materials)
        count, first = struct.unpack_from("<2H", batch, 14)
        assert 1 <= count <= 2 and first + count <= len(model.texture_combos)
        coords = struct.unpack_from("<H", batch, 18)[0]
        assert coords + count <= len(model.texture_coord_combos), "Missing batch UV lookup"
        assert all(c in (0, 1, 65535) for c in model.texture_coord_combos[coords:coords + count])
    paths = {name.casefold() for name in entries}
    for texture in model.textures:
        if texture["type"] == 0:
            assert texture["filename"].casefold() in paths, texture
        else:
            assert texture["type"] in (11, 12), texture
    checked = 0
    for track in model.tracks():
        assert not track.external
        assert -1 <= track.global_sequence < len(model.global_loops)
        for i, (count, offset) in enumerate(track.timestamp_spans):
            assert not count or 0 < offset <= offset + count * 4 <= len(model_data)
            times = track.timestamps[i]
            assert len(times) == count and times == sorted(times)
            if track.global_sequence < 0 and times:
                assert i < len(model.sequences)
                assert max(times) <= model.sequences[i]["duration"] + 1
            if hasattr(track, "values"):
                n, pos = track.value_spans[i]
                assert n == count
                assert not n or 0 < pos <= pos + n * value_size(track.kind) <= len(model_data)
                assert all(math.isfinite(x) for v in track.values[i]
                           for x in (v if isinstance(v, tuple) else (v,)))
            checked += 1
    for name, data in entries.items():
        assert name.casefold().startswith("creature/") or name.casefold().startswith("creature\\")
        if name.casefold().endswith(".blp"):
            texture = Blp.parse(data)
            assert texture.is_wotlk_compatible()[0]
            assert texture.level_size(texture.mip_count - 1) == (1, 1)
            offsets = struct.unpack_from("<16I", data, 20)
            sizes = struct.unpack_from("<16I", data, 84)
            for i, (offset, size) in enumerate(zip(offsets, sizes)):
                if i < texture.mip_count:
                    assert 1172 <= offset < offset + size <= len(data)
                    texture.decode_level(i)
                else:
                    assert offset == size == 0
    return {"animation_track_arrays": checked, "vertices": model.vertex_count,
            "skin_vertices": len(skin.vertices), "triangles": len(skin.indices) // 3,
            "bones": len(model.bones), "sequences": len(model.sequences), "entries": len(entries)}


def build():
    manifest = json.loads((WORK / "source-manifest.json").read_text(encoding="utf-8"))
    assets = manifest["assets"]
    listfile = Listfile("verified dreadlord source inventory")
    listfile.update(f"{fid};{asset['name']}" for fid, asset in assets.items())
    for asset in assets.values():
        if sha(Path(asset["path"]).read_bytes()) != asset["sha256"]:
            raise ValueError("Source cache changed: " + asset["path"])
    donor_hashes = {p.name: sha(p.read_bytes()) for p in DONOR.iterdir() if p.is_file()}
    model = parse_m2((DONOR / "dreadlordshadowlands.m2").read_bytes())
    source = AssetSource(listfile=listfile, roots=[WORK / "source"])
    options = Options(strict_limits=True, unresolved=UnresolvedPolicy.FAIL)
    result = FileResult(source=str(DONOR / "dreadlordshadowlands.m2"), kind="m2")
    model = downgrade_model(model, options, listfile, source, result)
    animations = _collect_anims(model, "DreadLord", source, options, result)
    if not result.ok or len(animations) != 8 or any(not a.data or not a.result.ok for a in animations):
        raise ValueError("Incomplete model/animation conversion")
    converted = WORK / "converted"
    converted.mkdir(parents=True, exist_ok=True)
    for animation in animations:
        (converted / animation.filename).write_bytes(animation.data)
    embed(model, converted, "DreadLord")
    raw_skin = parse_skin((DONOR / "dreadlordshadowlands_lod01.skin").read_bytes())
    geosets = json.loads((WORK / "retail-geosets.json").read_text(encoding="utf-8"))["rows"]
    choices = {(r["GeosetIndex"] + 1) * 100 + r["GeosetValue"] for _, r in geosets
               if r["CreatureDisplayInfoID"] == 99098}
    assert choices == {101, 201, 301, 501}
    keep = [i for i, mesh in enumerate(raw_skin.submeshes) if struct.unpack_from("<H", mesh)[0] in choices | {0}]
    skin = _rebuild_skin(raw_skin, keep, {i: i for i in range(model.vertex_count)})
    skin = compact_bone_palettes(model, skin)
    assign_texture_coord_combos(model, {0: skin}, result)
    reflection_passes = 0
    for i, raw in enumerate(skin.batches):
        batch = bytearray(raw)
        count, first = struct.unpack_from("<2H", batch, 14)
        slots = model.texture_combos[first:first + count]
        if len(slots) == 2 and model.textures[slots[0]]["type"] in (11, 12) and slots[1] == 5:
            # Wrath's plain diffuse pass avoids multiplying the body by Retail's reflection texture.
            struct.pack_into("<2H", batch, 2, 0, struct.unpack_from("<H", batch, 4)[0])
            struct.pack_into("<H", batch, 14, 1)
            reflection_passes += 1
        skin.batches[i] = bytes(batch)
    for i, raw in enumerate(skin.submeshes):
        mesh = bytearray(raw)
        struct.pack_into("<H", mesh, 0, 0)
        skin.submeshes[i] = bytes(mesh)
    if not downgrade_skin(skin, options, model.uses_combiner_combos, result):
        raise ValueError("Skin conversion failed")
    # Retail supplies armor first and body second; existing Wrath displays supply body then wing/armor.
    for texture in model.textures:
        if texture["type"] in (11, 12):
            texture["type"] = 23 - texture["type"]
    model.replacable_texture_lookup = [65535] * 16
    for i, texture in enumerate(model.textures):
        if texture["type"]:
            model.replacable_texture_lookup[texture["type"]] = i
    model.num_skin_profiles = 1
    entries = {MODEL: write_md20(model), str(PREFIX / "DreadLord00.skin"): write_skin(skin)}
    for fid in sorted({fid for fid in model.texture_file_ids if fid}):
        asset = assets[str(fid)]
        key = str(PureWindowsPath(asset["name"]))
        entries[key] = normalize_texture(Path(asset["path"]).read_bytes())
    variants = {"DreadLordSkin": DONOR / "dreadlordshadowlands_body_2.blp",
                "DreadLordWingSkin": Path(assets["3743339"]["path"]),
                "DreadLordSkinGreen": Path(assets["3743353"]["path"]),
                "DreadLordWingSkinGreen": Path(assets["3743342"]["path"])}
    for name, path in variants.items():
        entries[str(PREFIX / (name + ".blp"))] = normalize_texture(path.read_bytes())
    checks = check_entries(entries)
    ARCHIVE.parent.mkdir(parents=True, exist_ok=True)
    temporary = ARCHIVE.with_suffix(".partial")
    if temporary.exists():
        raise FileExistsError(temporary)
    storm = Storm(DLL_DEFAULT)
    storm.create_archive(temporary, entries)
    archive = storm.open_archive(temporary)
    try:
        for key, data in entries.items():
            assert storm.read(archive, key) == data, key
    finally:
        storm.dll.SFileCloseArchive(archive)
    temporary.replace(ARCHIVE)
    report = {"retail_pin": manifest["pin"], "donor_hashes": donor_hashes, "checks": checks,
              "selected_retail_display": 99098, "selected_geosets": sorted(choices),
              "green_retail_display": 99101, "embedded_external_animations": 8,
              "diffuse_passes_without_retail_reflection": reflection_passes,
              "conversion_notes": [{"code": n.code, "message": n.message} for n in result.notes],
              "archive": str(ARCHIVE), "archive_sha256": sha(ARCHIVE.read_bytes()),
              "entries": {key: {"bytes": len(data), "sha256": sha(data)} for key, data in entries.items()},
              "installed": False, "live_visual_test": "not run"}
    (WORK / "build-report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    assert donor_hashes == {p.name: sha(p.read_bytes()) for p in DONOR.iterdir() if p.is_file()}
    print(ARCHIVE)
    print(json.dumps(checks))


def check_archive():
    report = json.loads((WORK / "build-report.json").read_text(encoding="utf-8"))
    assert sha(ARCHIVE.read_bytes()) == report["archive_sha256"]
    storm = Storm(DLL_DEFAULT)
    archive = storm.open_archive(ARCHIVE)
    try:
        names = {name for name, *_ in storm.list_files(archive) if not name.startswith("(")}
        assert names == set(report["entries"])
        entries = {name: storm.read(archive, name) for name in names}
        for name, data in entries.items():
            assert sha(data) == report["entries"][name]["sha256"]
        print(json.dumps(check_entries(entries)))
    finally:
        storm.dll.SFileCloseArchive(archive)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("build", "check"))
    action = parser.parse_args().action
    build() if action == "build" else check_archive()
