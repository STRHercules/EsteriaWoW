"""Verify every baked head variant is unconditional and only the intended SKIN IDs changed."""

import struct

from wotlkconv.m2 import parse_skin
import highmountain_head_repair as repair


def main():
    report = repair.p.load_json(repair.STAGE / "build-report.json")
    installed = repair.STAGE / "last-install.json"
    before = repair.p.Path(repair.p.load_json(installed)["backup"]) if installed.exists() else None
    repaired = (repair.STAGE / "EsteriaHighmountain.bin").read_bytes()
    original = ((before or repair.p.CLIENT_DEFAULT) / "EsteriaHighmountain.bin").read_bytes()
    a = list(struct.iter_unpack("<7I128s", original[12:]))
    b = list(struct.iter_unpack("<7I128s", repaired[12:]))
    expected = [(r[0], r[3], r[4] >> 16) for r in a if r[1] == 2 and r[2] == 3202]
    assert len(expected) == 9
    for gender, geoset, face in expected:
        row = next(r for r in b if r[0] == gender and r[1] == 2 and r[3] == geoset)
        assert row[2] == 0 and row[4] >> 16 == face
    for old, new in zip(a, b, strict=True):
        if old[1] == 2 and old[2] in (3201, 3202):
            assert new[:2] == old[:2] and new[2] == 0 and new[3:] == old[3:]
        else:
            assert old == new
    storm = repair.p.Storm(repair.p.DLL_DEFAULT)
    for relative in repair.RELATIVES:
        stage = repair.STAGE / "pack" / relative
        assert repair.p.sha256(stage) == report["stage_hashes"][str(relative)]
        for sex in ("male", "female"):
            key = f"{repair.h.PREFIX}\\{sex}\\highmountaintauren{sex}00.skin"
            baseline = before / relative if before else repair.h.STAGE / "pack" / relative
            assert repair.p.sha256(baseline) == report["source_hashes"][str(relative)]
            old_data = repair.p._read_archive_entry(storm, baseline, key)
            new_data = repair.p._read_archive_entry(storm, stage, key)
            old = parse_skin(old_data)
            new = parse_skin(new_data)
            assert len(old.submeshes) == len(new.submeshes)
            assert old.vertices == new.vertices and old.indices == new.indices and old.batches == new.batches
            for old_mesh, new_mesh in zip(old.submeshes, new.submeshes, strict=True):
                if repair.h.v.u16(old_mesh, 0) in (3201, 3202):
                    assert repair.h.v.u16(new_mesh, 0) == 0 and old_mesh[2:] == new_mesh[2:]
                else:
                    assert old_mesh == new_mesh
            assert all(any(repair.h.v.u16(m, 0) == geoset for m in new.submeshes)
                       for gender, geoset, _ in expected if gender == (sex == "female"))
    geometry = (repair.STAGE / "EsteriaAppearanceGeometry.bin").read_bytes()
    offset = 12
    while offset < len(geometry):
        key = geometry[offset:offset + 128].split(b"\0")[0].decode()
        size = struct.unpack_from("<I", geometry, offset + 128)[0]
        if key.startswith(repair.h.PREFIX):
            staged = repair.p._read_archive_entry(storm, repair.STAGE / "pack" / repair.p.GLOBAL_ARCHIVE_REL,
                                                key[:-3] + "00.skin")
            assert geometry[offset + 132:offset + 132 + size] == staged
        offset += 132 + size
    assert offset == len(geometry)
    print("Highmountain heads: PASS (all nine face variants, base head visibility, unchanged triangles/materials)")


if __name__ == "__main__":
    main()
