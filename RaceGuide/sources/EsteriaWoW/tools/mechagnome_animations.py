"""Flatten Mechagnome's inherited Retail skeleton animations into its native M2."""

import copy
from pathlib import Path

from wotlkconv.m2 import write_md20
from wotlkconv.m2.convert import _collect_anims
from wotlkconv.m2.downgrade import downgrade_sequences
from wotlkconv.m2.model import M2Model
from wotlkconv.m2.skel import parse_skel
from wotlkconv.options import Options
from wotlkconv.report import FileResult
from wotlkconv.resolve import AssetSource

ROOT = Path(r"G:\RetroPorterWork\mechagnome\integration\source-audit")
PARENTS = {"male": 2184855, "female": 2564781}


def prepare_parents():
    from retroporter.config import DEFAULT
    from wotlkconv.casc import CascStorage, KeyRing

    ROOT.mkdir(parents=True, exist_ok=True)
    storage = CascStorage.open(DEFAULT.retail_root, product=DEFAULT.product, keys=KeyRing.load(DEFAULT.keys))
    try:
        source = AssetSource(casc=storage)
        for sex, file_id in PARENTS.items():
            raw = storage.read_file_id(file_id)
            (ROOT / f"{file_id}.skel").write_bytes(raw)
            skel = parse_skel(raw)
            model = M2Model(name=f"Mechagnome {sex} parent", bones=skel.bones, attachments=skel.attachments,
                            sequences=skel.sequences, sequence_lookups=skel.sequence_lookups,
                            key_bone_lookup=skel.key_bone_lookup, attachment_lookup=skel.attachment_lookup,
                            global_loops=skel.global_loops, sequence_schema=skel.sequence_schema,
                            anim_file_ids=skel.anim_file_ids, bones_from_skeleton=True,
                            attachments_from_skeleton=True)
            result = FileResult(source=str(file_id), kind="m2")
            downgrade_sequences(model, result)
            directory = ROOT / sex
            directory.mkdir(exist_ok=True)
            animations = _collect_anims(model, f"mechagnome{sex}", source, Options(), result)
            for animation in animations:
                if not animation.data or not animation.result.ok:
                    raise ValueError(f"Parent animation unavailable: {animation.filename}")
                (directory / animation.filename).write_bytes(animation.data)
            if any(note.code == "m2.anim.missing" for note in result.notes):
                raise ValueError(f"Incomplete parent animations: {sex}")
            (directory / "parent.m2").write_bytes(write_md20(model))
            print(sex, "parent prepared", len(model.sequences), "sequences", len(animations), "files", flush=True)
    finally:
        storage.close()


def merge(model, parent):
    if len(model.bones) != len(parent.bones) or any(
            a["bone_name_crc"] != b["bone_name_crc"] for a, b in zip(model.bones, parent.bones)):
        raise ValueError("Mechagnome parent bone identity/order differs")
    if model.global_loops[:len(parent.global_loops)] != parent.global_loops:
        raise ValueError("Mechagnome parent global animation loops differ")
    keys = {(s["id"], s["variation_index"]): i for i, s in enumerate(model.sequences)}
    child_count = len(model.sequences)
    parent_map = {}
    inherited = []
    for index, sequence in enumerate(parent.sequences):
        key = (sequence["id"], sequence["variation_index"])
        if key not in keys:
            keys[key] = len(model.sequences)
            model.sequences.append(copy.deepcopy(sequence))
            inherited.append(index)
        parent_map[index] = keys[key]
    for index in inherited:
        seq = model.sequences[parent_map[index]]
        for field in ("variation_next", "alias_next"):
            if seq[field] >= 0:
                seq[field] = parent_map[seq[field]]

    handled = set()

    def expand(track, donor=None):
        if id(track) in handled:
            return
        handled.add(id(track))
        if track.global_sequence >= 0:
            return
        def constant_default(candidate):
            populated = [i for i, values in enumerate(candidate.timestamps) if values]
            external_keys = any(i in candidate.external and count for i, (count, _) in
                                enumerate(candidate.timestamp_spans))
            return (populated == [0] and candidate.timestamps[0] == [0] and not external_keys
                    and (not hasattr(candidate, "values") or len(candidate.values[0]) == 1))

        donor_constant = donor and constant_default(donor)
        child_constant = constant_default(track)
        if child_constant and (donor_constant or donor is None):
            if not model.global_loops:
                model.global_loops.append(1)
            track.timestamps = [copy.deepcopy(track.timestamps[0])]
            track.timestamp_spans = [(0, 0)]
            if hasattr(track, "values"):
                track.values = [copy.deepcopy(track.values[0])]
                track.value_spans = [(0, 0)]
            track.global_sequence = 0
            return
        # Retail child skeletons omit inherited defaults. A one-key parent track is a bind transform,
        # shared by every animation (not an animation-zero-only override).
        if donor and not any(track.timestamps) and not any(n for n, _ in track.timestamp_spans):
            constant = donor_constant
            if donor.global_sequence >= 0 or constant:
                for name in ("kind", "interpolation", "global_sequence", "timestamps", "timestamp_spans",
                             "values", "value_spans", "external"):
                    if hasattr(donor, name):
                        setattr(track, name, copy.deepcopy(getattr(donor, name)))
                if constant and track.global_sequence < 0:
                    if not model.global_loops:
                        model.global_loops.append(1)
                    track.global_sequence = 0
                    track.external.clear()
                return
        names = ["timestamps", "timestamp_spans"]
        if hasattr(track, "values"):
            names += ["values", "value_spans"]
        for name in names:
            array = getattr(track, name)
            empty = (0, 0) if name.endswith("spans") else []
            while len(array) < child_count:
                array.append(copy.deepcopy(empty))
            for index in inherited:
                source = getattr(donor, name) if donor else array
                value = source[index] if donor and index < len(source) else empty
                if donor is None and name in ("timestamps", "values") and source:
                    value = source[0][:1]
                array.append(copy.deepcopy(value))
        if donor:
            track.external.update(parent_map[index] for index in inherited if index in donor.external)

    for bone, donor in zip(model.bones, parent.bones):
        for name in ("translation", "rotation", "scale"):
            expand(bone[name], donor[name])
    for attachment in model.attachments:
        donor = next((a for a in parent.attachments if a["id"] == attachment["id"]), None)
        expand(attachment["animate_attached"], donor["animate_attached"] if donor else None)
    for track in model.own_tracks():
        expand(track)
    model.sequence_lookups = [65535] * (max(s["id"] for s in model.sequences) + 1)
    for index, sequence in enumerate(model.sequences):
        if sequence["variation_index"] == 0:
            model.sequence_lookups[sequence["id"]] = index
    return {"child_sequences": child_count, "inherited_sequences": len(inherited),
            "total_sequences": len(model.sequences)}


def inherit(model, sex):
    from skyborne_visual_pack import read_player_model

    path = ROOT / sex / "parent.m2"
    if not path.is_file():
        raise FileNotFoundError("Prepare inherited skeletons with tools/mechagnome_animations.py first")
    return merge(model, read_player_model(path))


if __name__ == "__main__":
    prepare_parents()
