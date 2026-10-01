"""Check the new update/free thunks, retained getter ABI and native lifetime behavior."""

import subprocess

from capstone import Cs, CS_ARCH_X86, CS_MODE_32
from wow_xref import Pe

import highmountain_teardown_repair as repair


def main():
    stage = repair.STAGE
    image = Pe(stage / "Wow.exe")
    patch = repair.h.p.load_json(stage / "exe-patch-report.json")
    sites = {int(row["va"], 16): int(row["thunk"], 16) for row in patch["sites"]}
    disassembler = Cs(CS_ARCH_X86, CS_MODE_32)
    update = list(disassembler.disasm(image.read_va(sites[0x4D6C86], 25), sites[0x4D6C86]))
    assert [(i.mnemonic, i.op_str) for i in update[:3]] == [("pushfd", ""), ("pushal", ""), ("push", "esi")]
    assert [(i.mnemonic, i.op_str) for i in update[-3:-1]] == [("pop", "esi"), ("mov", "eax, 1")]
    assert update[-1].mnemonic == "jmp" and update[-1].op_str == "0x4d6c8c"
    free = list(disassembler.disasm(image.read_va(sites[0x4F16C0], 31), sites[0x4F16C0]))
    assert [(i.mnemonic, i.op_str) for i in free[:5]] == [
        ("push", "ebp"), ("mov", "ebp, esp"), ("pushfd", ""), ("pushal", ""),
        ("push", "dword ptr [ebp + 8]")]
    assert free[-1].mnemonic == "jmp" and free[-1].op_str == "0x4f16ca"
    for address in (0x4EA0B0, 0x4EA150, 0x4EA1F0):
        instructions = list(disassembler.disasm(image.read_va(sites[address], 42), sites[address]))
        assert [(i.mnemonic, i.op_str) for i in instructions if i.mnemonic == "test"] == [("test", "al, al")]
    for name in ("TestNativeAppearance.exe", "TestHighmountainMaterials.exe"):
        subprocess.run([str(stage / name), str(stage / "EsteriaAppearance.dll")], check=True)
    report = repair.h.p.load_json(stage / "build-report.json")
    for name, digest in report["preserved_hashes"].items():
        assert repair.h.p.sha256(repair.h.p.CLIENT_DEFAULT / name) == digest
    print("Native teardown: PASS (update/free thunks, AL ABI, uncached padding, lifetime, accepted asset hashes)")


if __name__ == "__main__":
    main()
