"""Convert same-build Retail Vulpera helmet variants used by the installed Wrath items."""

import hashlib
import json
from pathlib import Path, PureWindowsPath

from retroporter.config import DEFAULT
from wotlkconv.casc import CascStorage, KeyRing, blte
from wotlkconv.casc.cdn import blte_header_md5
from wotlkconv.listfile import Listfile
from wotlkconv.m2 import convert_m2, parse_m2
from wotlkconv.blp import convert_blp
from wotlkconv.options import Options

import mechagnome_race_pack as db
import vulpera_race_pack as v


def prepare():
    listfile = Listfile.load(DEFAULT.listfile)
    with v.p.ClientFiles(str(v.p.CLIENT_DEFAULT / "Data"), "enUS") as client:
        table = v.p.RawWdbc(client.find("DBFilesClient\\ItemDisplayInfo.dbc")[0])
    displays = {int(x) for x in db.sql("SELECT DISTINCT displayid FROM item_template "
                                     "WHERE InventoryType=1 AND displayid<>0;").split()}
    stems = {PureWindowsPath(v.p._string(table.strings, v.p._value(row, 4)).decode()).stem
             for row in table.records if v.p._value(row, 0) in displays}
    stems.discard("")
    storage = CascStorage.open(DEFAULT.retail_root, product="wow", keys=KeyRing.load(DEFAULT.keys))
    if storage.build.build_key != "dcfc90fffd79ba00406ae46f5f657592":
        storage.close()
        raise ValueError("Pinned Vulpera equipment source changed")
    cache = v.ROOT / "equipment/raw"
    cache.mkdir(parents=True, exist_ok=True)
    inventory, models, missing = {}, [], []

    class Source:
        casc = storage

        def by_file_id(self, file_id, extension=""):
            if not file_id:
                return None
            suffix = extension or Path((listfile.path_for(file_id) or "").replace("\\", "/")).suffix
            target = cache / f"{file_id}{suffix}"
            content = storage.root.ckey_for(file_id)
            if not content:
                return None
            if target.exists():
                data = target.read_bytes()
            else:
                data, error = storage.try_read_file_id(file_id)
                if data is None and "not a BLTE stream" in error:
                    encoding = storage.encoding.ekey_for(content)
                    location = storage.index.find(encoding) if encoding else None
                    if location:
                        with (DEFAULT.retail_root / "Data/data" / f"data.{location.archive:03d}").open("rb") as handle:
                            handle.seek(location.offset)
                            encoded = handle.read(location.size)
                        if encoded.startswith(b"BLTE") and blte_header_md5(encoded) == encoding:
                            data = blte.decode(encoded, storage.keys)
                if data is None:
                    return None
                target.write_bytes(data)
            if hashlib.md5(data).digest() != content:
                raise ValueError("Equipment source content hash mismatch: " + str(file_id))
            inventory[str(file_id)] = {"content_key": content.hex(), "file": target.name,
                                       "sha256": hashlib.sha256(data).hexdigest()}
            return data

        def by_path(self, name):
            file_id = listfile.id_for(name)
            return self.by_file_id(file_id) if file_id else None

    source = Source()
    try:
        from retroporter.wotlk import load_db2
        metadata = {}
        for name, file_id in (("HelmetGeosetVisData", 1294216), ("HelmetGeosetData", 2821752)):
            data = source.by_file_id(file_id, ".db2")
            if data is None:
                metadata[name] = {"unavailable": file_id}
                continue
            (v.ROOT / "retail-db2/dbfilesclient" / (name.lower() + ".db2")).write_bytes(data)
            metadata[name] = [{"_row_id": row_id, **row} for row_id, row in load_db2(DEFAULT, "vulpera", name)]
        v.save(v.ROOT / "integration/helmet-visibility.json", metadata)
        for stem in sorted(stems):
            for gender in ("M", "F"):
                source_key = f"item/objectcomponents/head/{stem}_vu_{gender.lower()}.m2".lower()
                file_id = listfile.id_for(source_key)
                if not file_id:
                    missing.append({"stem": stem, "gender": gender, "reason": "no source variant"})
                    continue
                data = source.by_file_id(file_id, ".m2")
                if data is None:
                    missing.append({"stem": stem, "gender": gender, "file_id": file_id,
                                    "reason": "unavailable source"})
                    continue
                target_stem = f"{stem}_Vu{gender}"
                key = f"Item\\ObjectComponents\\Head\\{target_stem}.m2"
                converted, result, companions = convert_m2(data, source_key, Options(
                    path_prefix="custom\\vulpera\\equipment"), listfile, source, output_stem=target_stem)
                if not result.ok or any(not c.result.ok for c in companions):
                    missing.append({"stem": stem, "gender": gender, "file_id": file_id,
                                    "reason": "conversion failure", "details": str(result)})
                    continue
                model = parse_m2(converted)
                if model.num_skin_profiles and not any(c.filename.lower().endswith("00.skin") for c in companions):
                    raise ValueError("Helmet has no primary SKIN: " + key)
                target = v.path(v.ART, key)
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(converted)
                for companion in companions:
                    (target.parent / companion.filename).write_bytes(companion.data)
                raw = parse_m2(data)
                for texture, texture_id in zip(model.textures, raw.texture_file_ids, strict=True):
                    if texture["type"] or not texture["filename"]:
                        continue
                    target_texture = v.path(v.ART, texture["filename"])
                    if target_texture.exists():
                        continue
                    bitmap = (source.by_file_id(texture_id, ".blp") if texture_id
                              else source.by_path(texture["filename"]))
                    if bitmap is None:
                        raise ValueError("Helmet hard texture unavailable: " + texture["filename"])
                    encoded, texture_result = convert_blp(bitmap, texture["filename"], Options())
                    if not texture_result.ok:
                        raise ValueError("Helmet texture failed: " + texture["filename"])
                    target_texture.parent.mkdir(parents=True, exist_ok=True)
                    target_texture.write_bytes(encoded)
                models.append({"file_id": file_id, "source": source_key, "target": key,
                               "sha256": v.p.sha256(target), "companions": [c.filename for c in companions]})
                if len(models) % 50 == 0:
                    print("HELMETS", len(models), "missing", len(missing), flush=True)
    finally:
        storage.close()
        report = {"source_build": "12.1.0.69933", "stems": len(stems), "converted": models,
                  "missing": missing, "inventory": inventory}
        v.save(v.ROOT / "integration/equipment.json", report)
    return {"stems": len(stems), "converted": len(models), "missing": len(missing)}


if __name__ == "__main__":
    print(json.dumps(prepare(), indent=2))
