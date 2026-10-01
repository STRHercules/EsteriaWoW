"""Rebuild inherited skeletal tracks while preserving accepted Highmountain geometry and materials."""

import argparse
import copy
import json
import shutil

from wotlkconv.m2 import write_md20
from wotlkconv.m2.convert import _collect_anims
from wotlkconv.m2.downgrade import downgrade_sequences
from wotlkconv.m2.model import M2Model
from wotlkconv.m2.skel import parse_skel
from wotlkconv.options import Options
from wotlkconv.report import FileResult
from wotlkconv.resolve import AssetSource

import highmountain_head_repair as installer
import highmountain_race_pack as h
import mechagnome_animations as animations

STAGE = h.STAGE / "animation-repair"


def prepare():
    cache = h.PROJECT / "sources/retail/races/highmountain_tauren"
    source = AssetSource(roots=[cache])
    updates = {}
    report = {"source_hashes": {}, "stage_hashes": {}, "companion_hashes": {}, "models": {}}
    for sex, parent_id in (("male", 1839011), ("female", 1830371)):
        skel = parse_skel((cache / f"{parent_id}.skel").read_bytes())
        parent = M2Model(name=f"Highmountain {sex} parent", bones=skel.bones, attachments=skel.attachments,
            sequences=skel.sequences, sequence_lookups=skel.sequence_lookups,
            key_bone_lookup=skel.key_bone_lookup, attachment_lookup=skel.attachment_lookup,
            global_loops=skel.global_loops, sequence_schema=skel.sequence_schema,
            anim_file_ids=skel.anim_file_ids, bones_from_skeleton=True, attachments_from_skeleton=True)
        result = FileResult(source=str(parent_id), kind="m2")
        downgrade_sequences(parent, result)
        payloads = _collect_anims(parent, f"highmountaintauren{sex}", source, Options(), result)
        if any(not a.data or not a.result.ok for a in payloads):
            raise ValueError("Inherited animation conversion failed")
        base_path = h.SOURCE / f"custom/highmountain/character/highmountaintauren/{sex}/highmountaintauren{sex}.m2"
        base = h.v.read_player_model(base_path)
        merged = animations.merge(base, parent)
        key = f"{h.PREFIX}\\{sex}\\highmountaintauren{sex}.m2"
        current = h.v.read_player_model(h.art_path(key))
        current.bones = base.bones
        current.attachments = base.attachments
        current.sequences = base.sequences
        current.sequence_lookups = base.sequence_lookups
        current.global_loops = base.global_loops
        donor_data, provider = h.p._effective_file(h.p.CLIENT_DEFAULT / "Data",
            f"Character\\Tauren2\\{sex.title()}\\Tauren{sex.title()}2.m2")
        from wotlkconv.m2 import parse_m2
        donor = parse_m2(donor_data)
        socket_bones = []
        donor_by_crc = {b["bone_name_crc"]: b for b in donor.bones}
        for attachment in current.attachments:
            if attachment["id"] not in (0, 1, 2):
                continue
            bone = current.bones[attachment["bone"]]
            standard = donor_by_crc[bone["bone_name_crc"]]
            for name in ("translation", "rotation", "scale"):
                track = copy.deepcopy(standard[name])
                if track.global_sequence >= 0:
                    duration = donor.global_loops[track.global_sequence]
                    if duration not in current.global_loops:
                        current.global_loops.append(duration)
                    track.global_sequence = current.global_loops.index(duration)
                elif any(track.timestamps) or any(count for count, _ in track.timestamp_spans):
                    raise ValueError("Donor socket has sequence-specific keys requiring explicit remapping")
                track.external.clear()
                bone[name] = track
            socket_bones.append(attachment["bone"])
        # The authored material is fully opaque and has one in-model default, shared by all sequences.
        raw = h.v.read_player_model(base_path)
        for weight, authored in zip(current.texture_weights, raw.texture_weights, strict=True):
            track = copy.deepcopy(authored["weight"])
            if track.values != [[32767]] or track.timestamps != [[0]]:
                raise ValueError("Highmountain opacity is not an authored opaque default")
            track.timestamps = [[0] for _ in current.sequences]
            track.values = [[32767] for _ in current.sequences]
            track.timestamp_spans = [(0, 0) for _ in current.sequences]
            track.value_spans = [(0, 0) for _ in current.sequences]
            track.external.clear()
            weight["weight"] = track
        current.bones_from_skeleton = True
        current.attachments_from_skeleton = True
        updates[key] = write_md20(current)
        for payload in payloads:
            updates[f"{h.PREFIX}\\{sex}\\{payload.filename}"] = payload.data
        report["models"][sex] = {"model_path": key, **merged,
            "opacity": "authored 32767 for every sequence; in-model tracks",
            "weapon_socket_bones": socket_bones, "weapon_socket_donor": provider,
            "hand_parents": [current.bones[i]["parent_bone"] for i in socket_bones]}
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
                raise ValueError("Animation stage readback differs")
        if stage.stat().st_size >= 0x80000000:
            raise ValueError("Animation stage exceeds classic reader boundary")
        report["stage_hashes"][str(relative)] = h.p.sha256(stage)
    for key, data in updates.items():
        path = STAGE.joinpath(*h.p.PureWindowsPath(key).parts)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    h.save(STAGE / "build-report.json", report)
    return report


def install():
    installer.STAGE = STAGE
    report = installer.install("animations")
    for path in (STAGE / "custom").rglob("*"):
        if path.is_file():
            target = h.ART / path.relative_to(STAGE)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("prepare", "install"))
    args = parser.parse_args()
    print(json.dumps(prepare() if args.command == "prepare" else install(), indent=2))
