"""Verify facial bone pivots and that the staged repair changes only vertex positions/normals."""

import math
import struct

import highmountain_faces as faces
import highmountain_race_pack as h


def main():
    vertex = bytearray(48)
    struct.pack_into("<3f", vertex, 0, 11.0, 0.0, 0.0)
    vertex[12] = 255
    struct.pack_into("<3f", vertex, 20, 0.0, 0.0, 1.0)
    rotate = (0, 1, 0, 0, -1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1)
    scale = (2, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1)
    assert struct.unpack_from("<3f", faces.deform(vertex, {0: rotate}, {0: (10, 0, 0)})) == (10, 1, 0)
    assert struct.unpack_from("<3f", faces.deform(vertex, {0: scale}, {0: (10, 0, 0)})) == (12, 0, 0)
    report = h.p.load_json(h.STAGE / "face-pivots/preparation.json")
    installed = h.STAGE / "face-pivots/last-install.json"
    before = h.p.Path(h.p.load_json(installed)["backup"]) if installed.exists() else None
    for sex, record in report["models"].items():
        source = h.p._read_archive_entry(h.p.Storm(h.p.DLL_DEFAULT), before / h.p.GLOBAL_ARCHIVE_REL,
                                        record["path"]) if before else h.art_path(record["path"]).read_bytes()
        staged = h.STAGE.joinpath("face-pivots", *h.p.PureWindowsPath(record["path"]).parts).read_bytes()
        count, offset = struct.unpack_from("<2I", source, 60)
        assert struct.unpack_from("<2I", staged, 60) == (count, offset)
        assert count == record["vertices"] and count <= 65535
        assert source[:offset] == staged[:offset] and source[offset + count * 48:] == staged[offset + count * 48:]
        moved = 0
        for i in range(count):
            at = offset + i * 48
            assert source[at + 12:at + 20] == staged[at + 12:at + 20]
            assert source[at + 32:at + 48] == staged[at + 32:at + 48]
            values = struct.unpack_from("<3f", staged, at)
            normal = struct.unpack_from("<3f", staged, at + 20)
            assert all(math.isfinite(v) for v in (*values, *normal))
            moved += source[at:at + 12] != staged[at:at + 12]
        assert moved > 1000 and record["maximum_origin_error_corrected"] > .5
    print("Highmountain face pivots: PASS (bone-local rotation/scale; weights, UVs, animations and materials unchanged)")


if __name__ == "__main__":
    main()
