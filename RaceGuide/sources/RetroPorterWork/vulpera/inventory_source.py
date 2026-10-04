from collections import Counter, deque
import hashlib
import json
from pathlib import Path
import struct

from run_source import EXPECTED, REPORTS, ROOT, SOURCE, verify_source
from retroporter.config import DEFAULT
from retroporter.races import RACES
from retroporter.wotlk import load_db2
from wotlkconv.casc import CascStorage, KeyRing
from wotlkconv.casc import blte
from wotlkconv.casc.cdn import blte_header_md5
from wotlkconv.chunks import ChunkReader
from wotlkconv.listfile import Listfile


def references(data, skeleton=False):
    reader = ChunkReader(data, reverse=False) if skeleton else ChunkReader.auto(
        data, {"MD21", "SFID", "AFID", "BFID", "SKID", "TXID"}
    )
    found = []
    for chunk in reader:
        if chunk.name in ("SFID", "BFID", "SKID", "TXID"):
            found.extend((value[0], chunk.name) for value in struct.iter_unpack("<I", chunk.data))
        elif chunk.name == "AFID":
            found.extend((value[2], "AFID") for value in struct.iter_unpack("<HHI", chunk.data))
        elif chunk.name == "SKPD" and len(chunk.data) >= 12:
            found.append((struct.unpack_from("<I", chunk.data, 8)[0], "SKPD"))
    return [(file_id, role) for file_id, role in found if file_id]


if __name__ == "__main__":
    assert references(b"TXID" + struct.pack("<II", 4, 123)) == [(123, "TXID")]
    assert references(b"SKPD" + struct.pack("<IIII", 12, 0, 0, 456), True) == [(456, "SKPD")]
    verify_source()
    discovery = json.loads((REPORTS / "discovery.json").read_text(encoding="utf-8"))
    listfile = Listfile.load(DEFAULT.listfile)
    spec = RACES["vulpera"]
    pending = deque(sorted(set(discovery["file_data_ids"]) | set(spec.core_model_file_ids)))
    records = {}
    edges = []
    failures = []
    raw_dir = ROOT / "raw"
    raw_dir.mkdir(exist_ok=True)
    storage = CascStorage.open(SOURCE, product="wow", keys=KeyRing.load(DEFAULT.keys))
    try:
        while pending:
            file_id = pending.popleft()
            if file_id in records:
                continue
            logical_name = listfile.path_for(file_id)
            entry = {"file_data_id": file_id, "logical_name": logical_name}
            records[file_id] = entry
            content_key = storage.root.ckey_for(file_id)
            entry["content_key"] = content_key.hex() if content_key else None
            data, error = storage.try_read_file_id(file_id)
            if data is None and "not a BLTE stream" in error and content_key:
                encoding_key = storage.encoding.ekey_for(content_key)
                location = storage.index.find(encoding_key) if encoding_key else None
                if location:
                    archive = SOURCE / "Data" / "data" / f"data.{location.archive:03d}"
                    with archive.open("rb") as handle:
                        handle.seek(location.offset)
                        encoded = handle.read(location.size)
                    if encoded.startswith(b"BLTE") and blte_header_md5(encoded) == encoding_key:
                        recovered = blte.decode(encoded, storage.keys)
                        if hashlib.md5(recovered).digest() != content_key:
                            raise RuntimeError(f"Direct BLTE content hash mismatch for {file_id}")
                        data = recovered
                        entry["source_layout"] = "direct-blte"
            if data is None:
                entry["error"] = error
                failures.append(entry)
                continue
            digest = hashlib.sha256(data).hexdigest()
            if content_key and hashlib.md5(data).digest() != content_key:
                raise RuntimeError(f"Decoded source content hash mismatch for {file_id}")
            suffix = Path((logical_name or "").replace("\\", "/")).suffix or ".bin"
            destination = raw_dir / f"{file_id}{suffix}"
            if destination.exists():
                if hashlib.sha256(destination.read_bytes()).hexdigest() != digest:
                    raise RuntimeError(f"Refusing to overwrite changed source asset {destination}")
            else:
                destination.write_bytes(data)
            entry.update({"sha256": digest, "size": len(data), "raw_path": str(destination)})
            is_skeleton = suffix.lower() == ".skel"
            if file_id in spec.core_model_file_ids or is_skeleton:
                for dependency, role in references(data, is_skeleton):
                    edges.append({"owner": file_id, "dependency": dependency, "role": role})
                    pending.append(dependency)
        report = {
            "source_product": EXPECTED[0], "source_version": EXPECTED[1], "source_build_key": EXPECTED[2],
            "assets": list(records.values()), "dependencies": edges, "unreadable": failures,
            "role_counts": dict(Counter(edge["role"] for edge in edges)),
        }
        (REPORTS / "source-inventory.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        layouts = set(row["CharComponentTextureLayoutID"] for row in discovery["models"])
        models = set(row["ID"] for row in discovery["models"])
        layout_report = {}
        for name in ("CharComponentTextureLayouts", "CharComponentTextureSections", "ChrModelMaterial", "ChrModelTextureLayer"):
            rows = load_db2(DEFAULT, "vulpera", name)
            layout_report[name] = [
                {"_row_id": row_id, **row} for row_id, row in rows
                if (name == "CharComponentTextureLayouts" and row.get("ID", row_id) in layouts)
                or row.get("CharComponentTextureLayoutID") in layouts
                or row.get("ChrModelID") in models
            ]
        (REPORTS / "texture-layouts.json").write_text(json.dumps(layout_report, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"assets": len(records), "unreadable": len(failures), "role_counts": report["role_counts"]}))
    finally:
        storage.close()
        verify_source()
