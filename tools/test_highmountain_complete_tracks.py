"""Check inline animation ranges, source events, opacity, hands and preserved art."""

import math
import struct

from wotlkconv.m2 import parse_m2
from wotlkconv.m2.skel import parse_skel
from wotlkconv.m2.types import value_size

import highmountain_complete_tracks as repair


def check_model(data, old, sex):
    model = parse_m2(data)
    assert len(model.sequences) == (349 if sex == "male" else 341)
    assert all(s["flags"] & 0x20 for s in model.sequences)
    for name in ("vertices", "textures", "materials", "bone_combos", "texture_combos",
                 "texture_coord_combos", "texture_weight_combos", "texture_transform_combos",
                 "attachment_lookup", "key_bone_lookup"):
        assert getattr(model, name) == getattr(old, name), name
    for track in model.tracks():
        assert not track.external
        assert -1 <= track.global_sequence < len(model.global_loops)
        assert track.global_sequence >= 0 or len(track.timestamps) <= len(model.sequences)
        for i, (count, offset) in enumerate(track.timestamp_spans):
            assert not count or 0 < offset <= offset + count * 4 <= len(data)
            times = track.timestamps[i]
            assert len(times) == count and times == sorted(times), (sex, getattr(track, "kind", "event"), i)
            if hasattr(track, "values"):
                n, pos = track.value_spans[i]
                assert count == n, (sex, track.kind, i, count, n)
                assert not n or 0 < pos <= pos + n * value_size(track.kind) <= len(data)
                assert len(track.values[i]) == n
                for value in track.values[i]:
                    assert all(math.isfinite(v) for v in (value if isinstance(value, tuple) else (value,))), (
                        sex, track.kind, i, value)
    for i, sequence in enumerate(model.sequences):
        target = i
        seen = set()
        while model.sequences[target]["flags"] & 0x40:
            assert target not in seen
            seen.add(target)
            target = model.sequences[target]["alias_next"]
        if target != i:
            for track in model.bone_tracks():
                if track.global_sequence < 0 and i < len(track.timestamps):
                    assert track.timestamps[i] == track.timestamps[target]
                    assert track.values[i] == track.values[target]
    cache = repair.h.PROJECT / "sources/retail/races/highmountain_tauren"
    raw_data = (cache / f"{repair.h.MODELS[sex]}.m2").read_bytes()
    parent_id = 1839011 if sex == "male" else 1830371
    parent = parse_skel((cache / f"{parent_id}.skel").read_bytes())
    events = repair.parent_events(raw_data, parse_m2(raw_data).events, parent, model)
    assert model.events == events or all(a["enabled"].timestamps == b["enabled"].timestamps
                                       for a, b in zip(model.events, events, strict=True))
    for event in model.events:
        for i, times in enumerate(event["enabled"].timestamps):
            assert not times or times[-1] <= model.sequences[i]["duration"], (sex, event["identifier"], i)
    for identifier in (b"$SHL", b"$SHR"):
        event = next(e for e in model.events if e["identifier"] == identifier)
        for animation in (89, 90):
            assert event["enabled"].timestamps[model.sequence_lookups[animation]], (sex, identifier, animation)
    weight = model.texture_weights[0]["weight"]
    assert weight.global_sequence >= 0 and weight.timestamps == [[0]] and weight.values == [[32767]]
    source_path = repair.previous.STAGE / f"custom/highmountain/native/{sex}/highmountaintauren{sex}.m2"
    skeletal = repair.h.v.read_player_model(source_path)
    for aid in (1, 2):
        socket = next(a["bone"] for a in model.attachments if a["id"] == aid)
        hand = model.bones[model.bones[socket]["parent_bone"]]
        for animation in (0, 13, 16, 60, 69, 89, 90):
            i = model.sequence_lookups[animation]
            assert i != 65535
            track = hand["translation"]
            index = 0 if track.global_sequence >= 0 else i
            assert track.values[index], (sex, aid, animation, index)
            assert sum(v * v for v in track.values[index][0]) > .1
            if animation in (60, 69, 89, 90):
                bone_index = model.bones[socket]["parent_bone"]
                source = skeletal.bones[bone_index]["translation"]
                expected = source.values[i]
                if i in source.external:
                    count, offset = source.value_spans[i]
                    sequence = skeletal.sequences[i]
                    anim = source_path.with_name(
                        f"{source_path.stem}{sequence['id']:04d}-{sequence['variation_index']:02d}.anim")
                    blob = anim.read_bytes()
                    expected = [struct.unpack_from("<3f", blob, offset + j * 12) for j in range(count)]
                assert track.values[i] == expected
    return model


def main():
    report = repair.h.p.load_json(repair.STAGE / "build-report.json")
    storm = repair.h.p.Storm(repair.h.p.DLL_DEFAULT)
    installed = repair.STAGE / "last-install.json"
    before = (repair.h.p.Path(repair.h.p.load_json(installed)["backup"])
              if installed.exists() else repair.h.p.CLIENT_DEFAULT)
    for sex, row in report["models"].items():
        key = row["model_path"]
        data = repair.STAGE.joinpath(*repair.h.p.PureWindowsPath(key).parts).read_bytes()
        old = parse_m2(repair.h.p._read_archive_entry(storm, before / repair.h.p.GLOBAL_ARCHIVE_REL, key))
        check_model(data, old, sex)
        for relative in repair.installer.RELATIVES:
            stage = repair.STAGE / "pack" / relative
            assert stage.stat().st_size < 0x80000000
            assert repair.h.p._read_archive_entry(storm, stage, key) == data
        print(sex, "PASS: inline ranges, PEDC, sheath events, opaque material, hand keys, preserved art", flush=True)
    changed = {row["model_path"].lower() for row in report["models"].values()}
    for relative in repair.installer.RELATIVES:
        source = storm.open_archive(before / relative)
        staged = storm.open_archive(repair.STAGE / "pack" / relative)
        try:
            names = {row[0] for row in storm.list_files(source)}
            assert names == {row[0] for row in storm.list_files(staged)}
            preserved = 0
            for name in names:
                if name.lower() in changed or name.startswith("("):
                    continue
                assert storm.read(source, name) == storm.read(staged, name), (relative, name)
                preserved += 1
            print(relative, "PASS:", preserved, "unrelated entries identical", flush=True)
        finally:
            storm.dll.SFileCloseArchive(source)
            storm.dll.SFileCloseArchive(staged)


if __name__ == "__main__":
    main()
