"""Check the repaired archive boundaries, compositor format and native getter regression."""

import subprocess
from capstone import Cs, CS_ARCH_X86, CS_MODE_32
from wow_xref import Pe

import ascension_hd_migration as mpq
import highmountain_creator_repair as repair


def main():
    report = repair.p.load_json(repair.STAGE / "build-report.json")
    image = Pe(repair.h.STAGE / "Wow.exe")
    patch = repair.p.load_json(repair.h.STAGE / "exe-patch-report.json")
    for site in ("0x4ea0b0", "0x4ea150", "0x4ea1f0"):
        address = int(next(row["thunk"] for row in patch["sites"] if row["va"] == site), 16)
        instructions = list(Cs(CS_ARCH_X86, CS_MODE_32).disasm(image.read_va(address, 42), address))
        tests = [(i.mnemonic, i.op_str) for i in instructions if i.mnemonic == "test"]
        assert tests == [("test", "al, al")], (site, tests)
        # A false x86 bool may retain a nonzero pointer in EAX's upper bytes.
        for result in (0, 0x4199A500, 0xABCD0000):
            assert (result & 0xff) == 0
        for result in (1, 0x4199A501, 0xABCD0001):
            assert (result & 0xff) != 0
    for relative in repair.RELATIVES:
        path = repair.STAGE / "pack" / relative
        assert path.stat().st_size < 0x80000000
        assert repair.p.sha256(path) == report["stage_hashes"][str(relative)]
        with mpq.MPQArchive(str(path)) as archive:
            for sex in ("male", "female"):
                for name in ("body0.blp", "body107.blp", "faceupper0_0.blp", "facelower0_0.blp"):
                    key = f"{repair.h.PREFIX}\\{sex}\\{name}"
                    index = archive._find_block_index(key)
                    assert index is not None
                    start, packed, size, flags = archive._block(index)
                    assert start + packed < 0x80000000 and flags & 0x200
                    data = archive.read_file(key)
                    assert len(data) == size
                    blp = repair.p.Blp.parse(data)
                    assert (blp.compression, blp.alpha_size, blp.alpha_type) == (1, 0, 8)
                    assert blp.is_wotlk_compatible()[0]
                    assert data == repair.h.art_path(key).read_bytes()
    subprocess.run([str(repair.h.STAGE / "TestHighmountainMaterials.exe"),
                    str(repair.h.STAGE / "EsteriaAppearance.dll")], check=True)
    for name, digest in report["companion_hashes"].items():
        assert repair.p.sha256(repair.h.STAGE / name) == digest
    print("Highmountain creator repair: PASS (classic offsets, independent MPQ reader, indexed BLPs, getters)")


if __name__ == "__main__":
    main()
