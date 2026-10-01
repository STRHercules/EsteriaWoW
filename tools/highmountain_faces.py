"""Bake Retail BIDA/BOMT face overrides into selectable Wrath meshes without altering animation tracks."""

import copy
import math
import struct

import highmountain_race_pack as h
import skyborne_visual_pack as v


def matrices(data):
    if len(data) < 4 or struct.unpack_from("<I", data)[0] != 1:
        raise ValueError("Unsupported BONE version")
    at, chunks = 4, {}
    while at < len(data):
        if at + 8 > len(data):
            raise ValueError("Truncated BONE chunk header")
        name, size = struct.unpack_from("<4sI", data, at)
        at += 8
        if at + size > len(data) or name in chunks:
            raise ValueError("Invalid BONE chunk")
        chunks[name] = data[at:at + size]
        at += size
    ids = chunks[b"BIDA"]
    transforms = chunks[b"BOMT"]
    if len(ids) % 2 or len(transforms) != len(ids) // 2 * 64:
        raise ValueError("BONE ID/matrix count mismatch")
    result = dict(zip(struct.unpack("<" + "H" * (len(ids) // 2), ids),
                      struct.iter_unpack("<16f", transforms), strict=True))
    if not all(math.isfinite(x) for m in result.values() for x in m):
        raise ValueError("Nonfinite BONE transform")
    return result


def deform(raw, transform, pivots=None):
    result = bytearray(raw)
    position = struct.unpack_from("<3f", raw)
    normal = struct.unpack_from("<3f", raw, 20)
    out_position, out_normal = [0.0] * 3, [0.0] * 3
    total = sum(raw[12:16])
    if not total:
        return raw
    for influence in range(4):
        weight = raw[12 + influence] / total
        if not weight:
            continue
        matrix = transform.get(raw[16 + influence])
        pivot = pivots.get(raw[16 + influence], (0.0, 0.0, 0.0)) if pivots else (0.0, 0.0, 0.0)
        for axis in range(3):
            if matrix:
                out_position[axis] += weight * (pivot[axis] + sum(
                    (position[j] - pivot[j]) * matrix[j * 4 + axis] for j in range(3)) + matrix[12 + axis])
                a, b, c = matrix[0], matrix[1], matrix[2]
                d, e, f = matrix[4], matrix[5], matrix[6]
                g, k, n = matrix[8], matrix[9], matrix[10]
                determinant = a * (e * n - f * k) - b * (d * n - f * g) + c * (d * k - e * g)
                if abs(determinant) < 1e-8:
                    raise ValueError("Singular face transform")
                inverse = ((e * n - f * k, c * k - b * n, b * f - c * e),
                           (f * g - d * n, a * n - c * g, c * d - a * f),
                           (d * k - e * g, b * g - a * k, a * e - b * d))
                out_normal[axis] += weight * sum(normal[j] * inverse[axis][j] / determinant for j in range(3))
            else:
                out_position[axis] += weight * position[axis]
                out_normal[axis] += weight * normal[axis]
    length = math.sqrt(sum(n * n for n in out_normal))
    if not length:
        raise ValueError("Degenerate face normal")
    struct.pack_into("<3f", result, 0, *out_position)
    struct.pack_into("<3f", result, 20, *(n / length for n in out_normal))
    return bytes(result)


def bake(model, skin, transforms):
    identity = tuple(1.0 if i in (0, 5, 10, 15) else 0.0 for i in range(16))
    changed = {bone for table in transforms for bone, matrix in table.items()
               if any(abs(matrix[i] - identity[i]) > 1e-6 for i in range(16))}
    vertices = bytearray(model.vertices)
    affected = {i for i in range(model.vertex_count) if any(model.vertices[i * 48 + 12 + j]
                and model.vertices[i * 48 + 16 + j] in changed for j in range(4))}
    source_vertices = model.vertices
    pivots = {index: bone["pivot"] for index, bone in enumerate(model.bones)}
    source_skin = copy.deepcopy(skin)
    mapped = {}
    new_indices, new_meshes, new_batches = [], [], []
    source_indices = source_skin.indices
    selectors = []
    original_count = len(source_skin.submeshes)
    for mesh_index, raw in enumerate(source_skin.submeshes):
        start = v.u16(raw, 8) | v.u16(raw, 2) << 16
        triangles = [source_indices[i:i + 3] for i in range(start, start + v.u16(raw, 10), 3)]
        base = [t for t in triangles if not any(source_skin.vertices[i] in affected for i in t)]
        face = [t for t in triangles if any(source_skin.vertices[i] in affected for i in t)]
        source_batches = [b for b in source_skin.batches if v.u16(b, 4) == mesh_index]

        def append(tris, geoset, face_index=None):
            if not tris:
                return
            remap = {}
            for lookup in sorted({i for triangle in tris for i in triangle}):
                if face_index is None:
                    remap[lookup] = lookup
                    continue
                vertex = source_skin.vertices[lookup]
                key = (face_index, vertex)
                if key not in mapped:
                    mapped[key] = len(vertices) // 48
                    vertices.extend(deform(source_vertices[vertex * 48:(vertex + 1) * 48],
                                           transforms[face_index], pivots))
                remap[lookup] = len(skin.vertices)
                skin.vertices.append(mapped[key])
                skin.bones += source_skin.bones[lookup * 4:lookup * 4 + 4]
            index_start = len(new_indices)
            new_indices.extend(remap[i] for t in tris for i in t)
            lookups = list(remap.values())
            mesh = bytearray(raw)
            v.patch16(mesh, 0, geoset)
            v.patch16(mesh, 2, index_start >> 16)
            v.patch16(mesh, 4, min(lookups))
            v.patch16(mesh, 6, max(lookups) - min(lookups) + 1)
            v.patch16(mesh, 8, index_start & 65535)
            v.patch16(mesh, 10, len(tris) * 3)
            new_index = len(new_meshes)
            new_meshes.append(bytes(mesh))
            for batch in source_batches:
                batch = bytearray(batch)
                v.patch16(batch, 4, new_index)
                v.patch16(batch, 6, new_index)
                new_batches.append(bytes(batch))

        append(base, v.u16(raw, 0))
        for face_index in range(len(transforms)):
            geoset = (100 + mesh_index) * 100 + face_index + 1
            append(face, geoset, face_index)
            if face:
                selectors.append((v.u16(raw, 0), geoset, face_index))
    model.vertices = bytes(vertices)
    model.vertex_count = len(vertices) // 48
    skin.indices, skin.submeshes, skin.batches = new_indices, new_meshes, new_batches
    if model.vertex_count > 65535 or len(skin.vertices) > 65535:
        raise ValueError("Baked Highmountain faces exceed the Wrath vertex limit")
    return selectors, {"original_meshes": original_count, "face_meshes": len(selectors),
                       "vertices": model.vertex_count, "lookups": len(skin.vertices),
                       "face_shapes": len(transforms)}


def prepare():
    from wotlkconv.m2 import parse_skin, write_md20
    from wotlkconv.m2.skin import write_skin
    import highmountain_appearance as codec

    profiles = codec.codec()
    discovery = h.p.load_json(h.ROOT / "reports/discovery.json")
    bone_sets = {r["ID"]: r for r in discovery["linked"]["ChrCustomizationBoneSet"]}
    cache = h.PROJECT / "sources/retail/races/highmountain_tauren"
    catalog = (h.STAGE / "EsteriaHighmountain.bin").read_bytes()
    magic, version, count = struct.unpack_from("<3I", catalog)
    records = []
    report = {}
    for gender, sex in enumerate(("male", "female")):
        profile = profiles[sex]
        face_option = next((i, o) for i, o in enumerate(profile["options"]) if o["label"] == "Face")
        transforms = []
        for choice in face_option[1]["choices"]:
            ids = {e["ChrCustomizationBoneSetID"] for e in choice["elements"] if e["ChrCustomizationBoneSetID"]}
            if len(ids) != 1:
                raise ValueError("Face choice has no unambiguous source bone override")
            file_id = bone_sets[ids.pop()]["BoneFileDataID"]
            transforms.append(matrices((cache / f"{file_id}.bone").read_bytes()))
        path = h.art_path(f"{h.PREFIX}\\{sex}\\highmountaintauren{sex}.m2")
        model = v.read_player_model(path)
        skin = parse_skin(path.with_name(path.stem + "00.skin").read_bytes())
        if any(v.u16(r, 0) >= 10000 for r in skin.submeshes):
            raise ValueError("Face shapes already baked; reprepare the base models before rebaking")
        # Group32 contains the base head, not an exclusive customization option. Keep both parts.
        # Group33 is the actual eyeball; its zero source selection means the base eyeball mesh.
        for i, raw in enumerate(skin.submeshes):
            if v.u16(raw, 0) in (3201, 3202, 3301):
                raw = bytearray(raw)
                v.patch16(raw, 0, 0)
                skin.submeshes[i] = bytes(raw)
        selections, model_report = bake(model, skin, transforms)
        skin = v.compact_bone_palettes(model, skin)
        for original, geoset, face in selections:
            records.append(struct.pack("<7I", gender, 2, original, geoset,
                face_option[0] | (face << 16), 0xffffffff, 0xffffffff) + bytes(128))
        path.write_bytes(write_md20(model))
        path.with_name(path.stem + "00.skin").write_bytes(write_skin(skin))
        model_report.update(model_hash=h.p.sha256(path), skin_hash=h.p.sha256(path.with_name(path.stem + "00.skin")))
        report[sex] = model_report
        print(sex, model_report, flush=True)
    (h.STAGE / "EsteriaHighmountain.bin").write_bytes(
        struct.pack("<3I", magic, version, count + len(records)) + catalog[12:] + b"".join(records))
    h.save(h.ROOT / "integration/face-shapes.json", report)


def repair_normals():
    from wotlkconv.m2 import parse_skin, write_md20
    import highmountain_appearance as codec
    discovery = h.p.load_json(h.ROOT / "reports/discovery.json")
    bone_sets = {r["ID"]: r for r in discovery["linked"]["ChrCustomizationBoneSet"]}
    cache = h.PROJECT / "sources/retail/races/highmountain_tauren"
    for sex, profile in codec.codec().items():
        transforms = []
        option = next(o for o in profile["options"] if o["label"] == "Face")
        for choice in option["choices"]:
            bone_id = next(e["ChrCustomizationBoneSetID"] for e in choice["elements"]
                           if e["ChrCustomizationBoneSetID"])
            transforms.append(matrices((cache / f"{bone_sets[bone_id]['BoneFileDataID']}.bone").read_bytes()))
        source = h.SOURCE / f"custom/highmountain/character/highmountaintauren/{sex}/highmountaintauren{sex}.m2"
        base = v.read_player_model(source)
        skin = v.compact_bone_palettes(base, parse_skin(source.with_name(source.stem + "00.skin").read_bytes()))
        for i, mesh in enumerate(skin.submeshes):
            if v.u16(mesh, 0) in (3201, 3202, 3301):
                mesh = bytearray(mesh)
                v.patch16(mesh, 0, 0)
                skin.submeshes[i] = bytes(mesh)
        bake(base, skin, transforms)
        target = h.art_path(f"{h.PREFIX}\\{sex}\\highmountaintauren{sex}.m2")
        model = v.read_player_model(target)
        if base.vertex_count != model.vertex_count:
            raise ValueError("Face repair changed the vertex mapping")
        vertices = bytearray(model.vertices)
        for i in range(base.vertex_count):
            at = i * 48
            if base.vertices[at:at + 12] != vertices[at:at + 12]:
                raise ValueError("Face repair changed the vertex order or position")
            vertices[at + 20:at + 32] = base.vertices[at + 20:at + 32]
        model.vertices = bytes(vertices)
        target.write_bytes(write_md20(model))
        print(sex, "inverse-transpose normals verified", flush=True)


def repair_pivots():
    from wotlkconv.m2 import parse_skin, write_md20
    import highmountain_appearance as codec
    discovery = h.p.load_json(h.ROOT / "reports/discovery.json")
    bone_sets = {r["ID"]: r for r in discovery["linked"]["ChrCustomizationBoneSet"]}
    cache = h.PROJECT / "sources/retail/races/highmountain_tauren"
    output = h.STAGE / "face-pivots"
    report = {"models": {}}
    for sex, profile in codec.codec().items():
        transforms = []
        option = next(o for o in profile["options"] if o["label"] == "Face")
        for choice in option["choices"]:
            bone_id = next(e["ChrCustomizationBoneSetID"] for e in choice["elements"]
                           if e["ChrCustomizationBoneSetID"])
            transforms.append(matrices((cache / f"{bone_sets[bone_id]['BoneFileDataID']}.bone").read_bytes()))
        source = h.SOURCE / f"custom/highmountain/character/highmountaintauren/{sex}/highmountaintauren{sex}.m2"
        base = v.read_player_model(source)
        skin = v.compact_bone_palettes(base, parse_skin(source.with_name(source.stem + "00.skin").read_bytes()))
        for i, mesh in enumerate(skin.submeshes):
            if v.u16(mesh, 0) in (3201, 3202, 3301):
                mesh = bytearray(mesh)
                v.patch16(mesh, 0, 0)
                skin.submeshes[i] = bytes(mesh)
        original_count = base.vertex_count
        bake(base, skin, transforms)
        key = f"{h.PREFIX}\\{sex}\\highmountaintauren{sex}.m2"
        current_path = h.art_path(key)
        model = v.read_player_model(current_path)
        if base.vertex_count != model.vertex_count:
            raise ValueError("Pivot repair changed the vertex mapping")
        vertices = bytearray(model.vertices)
        moved = 0
        max_correction = 0.0
        for i in range(base.vertex_count):
            at = i * 48
            if base.vertices[at + 12:at + 20] != vertices[at + 12:at + 20]:
                raise ValueError("Pivot repair changed bone weights or vertex order")
            old_position = struct.unpack_from("<3f", vertices, at)
            new_position = struct.unpack_from("<3f", base.vertices, at)
            distance = math.dist(old_position, new_position)
            if i < original_count and distance > 1e-6:
                raise ValueError("Pivot repair changed an original body vertex")
            moved += distance > 1e-6
            max_correction = max(max_correction, distance)
            vertices[at:at + 12] = base.vertices[at:at + 12]
            vertices[at + 20:at + 32] = base.vertices[at + 20:at + 32]
        model.vertices = bytes(vertices)
        target = output.joinpath(*h.p.PureWindowsPath(key).parts)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(write_md20(model))
        report["models"][sex] = {"path": key, "vertices": model.vertex_count,
            "face_shapes": len(transforms), "corrected_vertices": moved,
            "maximum_origin_error_corrected": max_correction, "sha256": h.p.sha256(target),
            "source_sha256": h.p.sha256(current_path)}
        print(sex, report["models"][sex], flush=True)
    h.save(output / "preparation.json", report)
    return report


def prepare_pivot_archives():
    import shutil
    output = h.STAGE / "face-pivots"
    preparation = h.p.load_json(output / "preparation.json")
    updates = {}
    for sex, record in preparation["models"].items():
        key = record["path"]
        path = output.joinpath(*h.p.PureWindowsPath(key).parts)
        if h.p.sha256(path) != record["sha256"] or h.p.sha256(h.art_path(key)) != record["source_sha256"]:
            raise ValueError("Face pivot model stage/source changed")
        updates[key] = path.read_bytes()
    storm = h.p.Storm(h.p.DLL_DEFAULT)
    report = {"source_hashes": {}, "stage_hashes": {}, "companion_hashes": {}, "models": preparation["models"]}
    for relative in (h.p.GLOBAL_ARCHIVE_REL, h.p.LOCALE_ARCHIVE_REL, h.p.ASSET_ARCHIVE_REL):
        live = h.p.CLIENT_DEFAULT / relative
        stage = output / "pack" / relative
        stage.parent.mkdir(parents=True, exist_ok=True)
        report["source_hashes"][str(relative)] = h.p.sha256(live)
        shutil.copy2(live, stage)
        storm.replace_archive_entries(stage, updates)
        for key, data in updates.items():
            if h.p._read_archive_entry(storm, stage, key) != data:
                raise ValueError("Face pivot archive readback differs")
        if stage.stat().st_size >= 0x80000000:
            raise ValueError("Face pivot archive exceeds classic reader boundary")
        report["stage_hashes"][str(relative)] = h.p.sha256(stage)
    h.save(output / "build-report.json", report)
    return report


def install_pivots():
    import highmountain_head_repair as installer
    import shutil
    installer.STAGE = h.STAGE / "face-pivots"
    report = installer.install("face-pivots")
    for sex, record in report["models"].items():
        key = record["path"]
        shutil.copy2(installer.STAGE.joinpath(*h.p.PureWindowsPath(key).parts), h.art_path(key))
    return report


if __name__ == "__main__":
    import sys
    if "repair-pivots" in sys.argv:
        repair_pivots()
    elif "prepare-pivot-archives" in sys.argv:
        prepare_pivot_archives()
    elif "install-pivots" in sys.argv:
        install_pivots()
    elif "repair-normals" in sys.argv:
        repair_normals()
    else:
        prepare()
