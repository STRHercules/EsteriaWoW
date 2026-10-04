"""Restore PEDC gameplay events and embed all Highmountain animation keys into native MD20."""

import argparse
import copy
import json
import shutil
import struct

from wotlkconv.m2 import parse_m2, write_md20
from wotlkconv.m2.downgrade import downgrade_cameras
from wotlkconv.m2.types import TrackBase, VALUE_FORMATS
from wotlkconv.report import FileResult

import highmountain_animation_repair as previous
import highmountain_head_repair as installer
import highmountain_race_pack as h

STAGE = h.STAGE / "complete-tracks"


def parent_events(raw, events, parent, output):
    offset = 0
    payload = None
    while offset + 8 <= len(raw):
        name, size = struct.unpack_from("<4sI", raw, offset)
        if offset + 8 + size > len(raw):
            raise ValueError("Truncated source model chunk")
        if name == b"PEDC":
            payload = raw[offset + 8:offset + 8 + size]
        offset += 8 + size
    if payload is None:
        raise ValueError("Highmountain source has no parent event data")
    count, table_offset = struct.unpack_from("<2I", payload)
    if count != len(events) or table_offset + count * 12 > len(payload):
        raise ValueError("Parent event table does not match the child event identifiers")
    indices = {(s["id"], s["variation_index"]): i for i, s in enumerate(parent.sequences)}
    restored = []
    for j, event in enumerate(events):
        interpolation, global_sequence, length, arrays = struct.unpack_from("<HhII", payload, table_offset + j * 12)
        if global_sequence != -1 or length != len(parent.sequences) or arrays + length * 8 > len(payload):
            raise ValueError("Unexpected parent event track layout")
        keys = []
        for i in range(length):
            n, pos = struct.unpack_from("<2I", payload, arrays + i * 8)
            if pos + n * 4 > len(payload):
                raise ValueError("Parent event timestamp range invalid")
            keys.append(list(struct.unpack_from("<" + "I" * n, payload, pos)))
        track = TrackBase(interpolation=interpolation, global_sequence=-1)
        for sequence in output.sequences:
            i = indices[(sequence["id"], sequence["variation_index"])]
            track.timestamps.append(keys[i])
        track.timestamp_spans = [(0, 0)] * len(track.timestamps)
        event = copy.deepcopy(event)
        event["enabled"] = track
        restored.append(event)
    return restored


def embed(model, animation_directory, stem=None):
    files = {}
    for track in model.tracks():
        if track.global_sequence >= 0:
            track.external.clear()
            continue
        for i in list(track.external):
            if i >= len(model.sequences):
                raise ValueError("Track references an absent sequence")
            sequence = model.sequences[i]
            source_index = i
            visited = set()
            while sequence["flags"] & 0x40:
                target = sequence["alias_next"]
                if target < 0 or target >= len(model.sequences) or target in visited:
                    raise ValueError("Invalid animation alias chain")
                visited.add(target)
                source_index = target
                sequence = model.sequences[target]
            model_stem = stem or f"highmountaintauren{animation_directory.name}"
            path = animation_directory / (
                f"{model_stem}{sequence['id']:04d}-{sequence['variation_index']:02d}.anim")
            if source_index not in track.external:
                track.timestamps[i] = copy.deepcopy(track.timestamps[source_index])
                if hasattr(track, "values"):
                    track.values[i] = copy.deepcopy(track.values[source_index])
                continue
            # Alias chains use the final target's spans; the converter relocates only direct aliases.
            n, offset = track.timestamp_spans[source_index]
            if not n:
                track.timestamps[i] = []
                if hasattr(track, "values"):
                    track.values[i] = []
                continue
            if path not in files:
                files[path] = path.read_bytes()
            data = files[path]
            if offset + n * 4 > len(data):
                raise ValueError("External timestamp span exceeds its file")
            track.timestamps[i] = list(struct.unpack_from("<" + "I" * n, data, offset))
            if hasattr(track, "values"):
                count, value_offset = track.value_spans[source_index]
                fmt = VALUE_FORMATS[track.kind]
                stride = struct.calcsize("<" + fmt)
                if value_offset + count * stride > len(data):
                    raise ValueError("External value span exceeds its file")
                values = [struct.unpack_from("<" + fmt, data, value_offset + j * stride)
                          for j in range(count)]
                track.values[i] = [v[0] for v in values] if len(fmt) == 1 else values
        track.external.clear()
        track.timestamp_spans = [(0, 0)] * len(track.timestamps)
        if hasattr(track, "value_spans"):
            track.value_spans = [(0, 0)] * len(track.values)
    for sequence in model.sequences:
        sequence["flags"] |= 0x20


def prepare():
    from wotlkconv.m2.skel import parse_skel
    cache = h.PROJECT / "sources/retail/races/highmountain_tauren"
    updates = {}
    report = {"source_hashes": {}, "stage_hashes": {}, "companion_hashes": {}, "models": {}}
    for sex, parent_id in (("male", 1839011), ("female", 1830371)):
        key = f"{h.PREFIX}\\{sex}\\highmountaintauren{sex}.m2"
        current = parse_m2(h.art_path(key).read_bytes())
        repaired_path = previous.STAGE.joinpath(*h.p.PureWindowsPath(key).parts)
        skeletal = h.v.read_player_model(repaired_path)
        raw_data = (cache / f"{h.MODELS[sex]}.m2").read_bytes()
        raw = parse_m2(raw_data)
        parent = parse_skel((cache / f"{parent_id}.skel").read_bytes())
        current.bones = skeletal.bones
        current.attachments = skeletal.attachments
        current.global_loops = skeletal.global_loops
        current.sequences = skeletal.sequences
        current.sequence_lookups = skeletal.sequence_lookups
        current.events = parent_events(raw_data, raw.events, parent, current)
        current.texture_transforms = raw.texture_transforms
        current.texture_weights = raw.texture_weights
        downgrade_cameras(raw, FileResult(source=str(h.MODELS[sex]), kind="m2"))
        current.cameras = raw.cameras
        for weight in current.texture_weights:
            track = weight["weight"]
            if track.values != [[32767]] or track.timestamps != [[0]]:
                raise ValueError("Source opacity is not fully opaque")
            track.global_sequence = 0
            track.external.clear()
        # PEDC event keys and constant materials are in-model; only skeletal keys need ANIM extraction.
        current.bones_from_skeleton = True
        current.attachments_from_skeleton = True
        embed(current, repaired_path.parent)
        payload = write_md20(current)
        updates[key] = payload
        report["models"][sex] = {"model_path": key, "sequences": len(current.sequences),
            "events": len(current.events), "event_timestamp_count": sum(len(t) for e in current.events
                for t in e["enabled"].timestamps), "bytes": len(payload), "all_keys_in_model": True}
        print(sex, report["models"][sex], flush=True)
    storm = h.p.Storm(h.p.DLL_DEFAULT)
    for relative in installer.RELATIVES:
        live = h.p.CLIENT_DEFAULT / relative
        stage = STAGE / "pack" / relative
        stage.parent.mkdir(parents=True, exist_ok=True)
        report["source_hashes"][str(relative)] = h.p.sha256(live)
        shutil.copy2(live, stage)
        storm.replace_archive_entries(stage, updates)
        for key, data in updates.items():
            if h.p._read_archive_entry(storm, stage, key) != data:
                raise ValueError("Complete animation stage readback differs")
        if stage.stat().st_size >= 0x80000000:
            raise ValueError("Archive exceeds classic reader boundary")
        report["stage_hashes"][str(relative)] = h.p.sha256(stage)
    for key, data in updates.items():
        path = STAGE.joinpath(*h.p.PureWindowsPath(key).parts)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    h.save(STAGE / "build-report.json", report)
    return report


def install():
    installer.STAGE = STAGE
    report = installer.install("complete-tracks")
    for row in report["models"].values():
        key = row["model_path"]
        shutil.copy2(STAGE.joinpath(*h.p.PureWindowsPath(key).parts), h.art_path(key))
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("prepare", "install"))
    args = parser.parse_args()
    print(json.dumps(prepare() if args.command == "prepare" else install(), indent=2))
